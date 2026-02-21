# Clone Audit Checklist

Systematic framework for identifying and eliminating unnecessary `.clone()` calls in Rust codebases.

## Quick Classification System

Use this to triage clone operations:

| Category | Priority | Action |
|----------|----------|--------|
| **High-Frequency** | 🔴 Critical | Optimize immediately |
| **Medium-Frequency** | 🟡 Important | Optimize after high-priority |
| **Necessary** | ⚪ Informational | Document why needed |
| **Low-Impact** | ⚪ Optional | Skip unless profiling shows issue |

## Audit Process

### Step 1: Find All Clones

```bash
# Find all .clone() calls
rg '\.clone\(\)' --type rust

# Find clone in specific contexts
rg 'to_vec\(\)' --type rust  # Vec cloning
rg 'to_string\(\)' --type rust  # String cloning
rg 'clone\(\).*serde' --type rust  # Serialization clones
```

### Step 2: Categorize by Location

For each clone, determine its context:

1. **Serialization context** (save/persist/export methods)
2. **Loop context** (inside loops or iterations)
3. **API boundary** (function parameters/returns)
4. **Closure capture** (moving data into closures)
5. **Collection transformation** (map/filter/collect chains)
6. **Field assignment** (struct field initialization)

### Step 3: Determine Frequency

For each clone, estimate call frequency:

**High Frequency (Optimize First):**
- [ ] Called on every mutation (add/update/remove operations)
- [ ] In save/persist methods called frequently
- [ ] In hot loops (tight inner loops)
- [ ] In event handlers called many times per second

**Medium Frequency:**
- [ ] In CLI commands (user interaction rate)
- [ ] In API request handlers (request rate)
- [ ] In background tasks (task frequency)

**Low Frequency:**
- [ ] In initialization code (once per program)
- [ ] In error paths (only on failures)
- [ ] In setup/teardown (occasional)

### Step 4: Analysis by Context

#### Serialization Clones

**Pattern to look for:**
```rust
// Potential optimization
pub fn save(&self) -> Result<()> {
    let data = SomeStruct {
        field: self.field.clone(),  // ❓ Is this necessary?
    };
    serde_json::to_string(&data)?;
}
```

**Questions to ask:**
- [ ] Can serde serialize from a reference instead?
- [ ] Can we use a lifetime-parameterized wrapper?
- [ ] Can we serialize `self` directly?
- [ ] Is this save() method called frequently?

**Optimization strategies:**
1. Use `&'a T` in serialization struct
2. Use `serde_json::json!({ "field": &self.field })`
3. Serialize `self` directly if possible

#### Loop Clones

**Pattern to look for:**
```rust
for item in &collection {
    let cloned = item.clone();  // ❓ Why clone in loop?
    process(cloned);
}
```

**Questions to ask:**
- [ ] Does `process()` actually need ownership?
- [ ] Can we change `process()` to take `&T`?
- [ ] Is the clone moved into a thread/closure?
- [ ] How many iterations typically occur?

**Optimization strategies:**
1. Change callee to accept `&T` instead of `T`
2. Use `Arc<T>` if data is shared across threads
3. Only clone when absolutely necessary (conditional)

#### API Boundary Clones

**Pattern to look for:**
```rust
pub fn get_items(&self) -> Vec<Item> {
    self.items.clone()  // ❓ Can we return reference?
}
```

**Questions to ask:**
- [ ] Can we return `&[T]` instead of `Vec<T>`?
- [ ] Can caller work with a reference?
- [ ] Is this a public API (harder to change)?
- [ ] How often is this called?

**Optimization strategies:**
1. Return `&[T]` when lifetimes allow
2. Return `Arc<[T]>` for shared ownership
3. Accept callback: `fn with_items<F>(&self, f: F) where F: FnOnce(&[T])`

#### Closure Capture Clones

**Pattern to look for:**
```rust
let data = self.data.clone();  // ❓ Can we avoid clone?
thread::spawn(move || {
    process(data);
});
```

**Questions to ask:**
- [ ] Does closure actually need owned data?
- [ ] Can we use `Arc` for shared ownership?
- [ ] Can thread borrow with scoped threads?
- [ ] Is this a one-time spawn or frequent?

**Optimization strategies:**
1. Use `Arc::clone(&self.data)` for shared ownership
2. Use scoped threads to borrow: `thread::scope(|s| { s.spawn(|| { &self.data }) })`
3. Only clone what's needed, not entire structs

#### Field Assignment Clones

**Pattern to look for:**
```rust
let config = Config {
    name: input.name.clone(),  // ❓ Unavoidable?
    path: input.path.clone(),
};
```

**Questions to ask:**
- [ ] Do we own `input` and can move fields?
- [ ] Are these fields immutable? (candidate for `Arc<str>`)
- [ ] How often are these structs created?
- [ ] Are structs frequently cloned after creation?

**Optimization strategies:**
1. Move fields if `input` is owned: `name: input.name`
2. Use `Arc<str>` for immutable strings if struct is cloned often
3. Use builder pattern to avoid intermediate clones

## Optimization Decision Matrix

Use this matrix to decide if optimization is worth it:

| Frequency | Clone Size | Impact | Action |
|-----------|------------|--------|--------|
| High | Large | 🔴 Critical | Optimize immediately |
| High | Small | 🟡 Important | Optimize if easy |
| Medium | Large | 🟡 Important | Optimize after critical |
| Medium | Small | ⚪ Optional | Profile first |
| Low | Large | ⚪ Optional | Only if profiling shows |
| Low | Small | ⚪ Skip | Not worth it |

**Clone size categories:**
- **Large:** Collections (Vec, HashMap), large structs (>100 bytes)
- **Small:** Primitives, small structs (<24 bytes), single strings

## Specific Patterns to Audit

### Pattern 1: Clone for Serialization

```bash
# Find potential serialization clones
rg 'clone.*serde_' --type rust
rg 'clone.*to_string.*serde' --type rust
```

**Check for:**
- [ ] save/persist methods that clone before serializing
- [ ] to_json/to_yaml methods with intermediate clones
- [ ] wrapper structs that clone instead of borrow

**Typical fix:** Use lifetime-parameterized wrapper or serialize `self`.

### Pattern 2: Clone in Getters

```bash
# Find getters that return owned values
rg 'pub fn get.*\(&self\) -> Vec' --type rust
rg 'pub fn get.*\(&self\) -> String' --type rust
```

**Check for:**
- [ ] Getters returning `Vec<T>` instead of `&[T]`
- [ ] Getters returning `String` instead of `&str`
- [ ] Getters that clone collections unnecessarily

**Typical fix:** Return reference or use `Arc`.

### Pattern 3: Clone Before Map/Filter

```bash
# Find potential iterator clones
rg 'clone\(\).*\.iter' --type rust
rg 'to_vec\(\).*\.iter' --type rust
```

**Check for:**
- [ ] Cloning collections before iterating
- [ ] Using `to_vec()` when `&[T]` would work
- [ ] Collecting unnecessarily

**Typical fix:** Iterate over reference directly.

### Pattern 4: Clone in Constructors

```bash
# Find clones in new/from/into methods
rg 'fn (new|from|into).*\{' -A 20 --type rust | rg clone
```

**Check for:**
- [ ] Cloning when could move owned values
- [ ] Cloning immutable strings (consider `Arc<str>`)
- [ ] Unnecessary defensive cloning

**Typical fix:** Move instead of clone, or use `Arc` for immutable data.

## Verification After Optimization

For each optimization, verify:

### Functional Correctness

- [ ] All tests pass
- [ ] Manual smoke testing succeeds
- [ ] No behavioral changes (only performance)
- [ ] Error handling unchanged

### Output Validation

For serialization optimizations:
- [ ] YAML/JSON output format identical
- [ ] Can deserialize old files
- [ ] Round-trip works (save then load)

```bash
# Compare outputs
diff <(cargo run -- save --before) <(cargo run -- save --after)
```

### Performance Impact

Optional benchmarking:
```rust
#[bench]
fn bench_save(b: &mut Bencher) {
    let state = SessionState::new();
    b.iter(|| state.save());
}
```

Or simple timing:
```bash
# Before
time cargo run -- save-1000-sessions
# After
time cargo run -- save-1000-sessions
```

## Red Flags (Keep These Clones)

Don't optimize clones in these cases:

### 🚫 Necessary for Ownership Semantics

```rust
// ✅ Correct: Need owned value for thread
let data = self.data.clone();
thread::spawn(move || process(data));
```

### 🚫 Required by API Contract

```rust
// ✅ Correct: Public API can't change without breaking users
pub fn get_config(&self) -> Config {
    self.config.clone()  // Users expect owned value
}
```

### 🚫 Safety-Critical Defensive Clone

```rust
// ✅ Correct: Prevent mutation of internal state
pub fn get_sessions(&self) -> Vec<Session> {
    self.sessions.clone()  // Don't expose internal Vec
}
```

### 🚫 Clone-on-Write Pattern

```rust
// ✅ Correct: COW pattern intentionally clones
use std::borrow::Cow;
pub fn get_or_default(&self, key: &str) -> Cow<str> {
    self.map.get(key)
        .map(|s| Cow::Borrowed(s.as_str()))
        .unwrap_or(Cow::Owned(String::from("default")))
}
```

### 🚫 Error Context Cloning

```rust
// ✅ Correct: Error needs owned data
Err(anyhow!("Failed to process {}", item.name.clone()))
```

## Documentation Template

For clones you keep, document why:

```rust
pub fn save(&self) -> Result<()> {
    // CLONE: Necessary because serde needs owned SessionsFile
    // Alternative considered: lifetime-parameterized wrapper (TODO for v2.0)
    let file = SessionsFile {
        sessions: self.sessions.clone(),
    };
    serde_yaml::to_string(&file)?
}
```

## Prioritization Example

Real-world example from maestro-cli:

### High Priority (Optimized First)

```rust
// ❌ Before: Clone on every save (called by 11 methods)
pub fn save(&self) -> Result<()> {
    let file = SessionsFile {
        sessions: self.sessions.clone(),  // Clone 1000s of times
    };
}

// ✅ After: Zero-copy serialization
pub fn save(&self) -> Result<()> {
    let file = SessionsFileRef {
        sessions: &self.sessions,  // Borrow instead
    };
}
```

**Impact:** Called on every add/update/remove → 10-100x frequency

### Medium Priority (Next)

```rust
// Commands that clone for user display
pub fn list_sessions(&self) -> Vec<Session> {
    self.sessions.to_vec()  // Clone for picker
}
```

**Impact:** User interaction rate (1-10x per minute)

### Low Priority (Skipped)

```rust
// One-time initialization
pub fn from_config(config: Config) -> Self {
    Self {
        name: config.name.clone(),  // Once per program
    }
}
```

**Impact:** Initialization only (1x per lifetime)

## Summary Checklist

For each clone found:

1. **Context**
   - [ ] Identify where clone occurs (serialization, loop, API, etc.)
   - [ ] Understand why it was added originally

2. **Frequency**
   - [ ] Estimate call frequency (high/medium/low)
   - [ ] Determine if it's in a hot path

3. **Necessity**
   - [ ] Is clone truly necessary for ownership/safety?
   - [ ] Can we use borrowing instead?
   - [ ] Would `Arc` help for sharing?

4. **Impact**
   - [ ] What's the size of cloned data?
   - [ ] Is this in a hot path?
   - [ ] What's the performance multiplier?

5. **Action**
   - [ ] Optimize (high priority)
   - [ ] Defer (medium priority)
   - [ ] Document (necessary clone)
   - [ ] Skip (low impact)

## Quick Wins to Look For

These patterns almost always indicate opportunities:

1. **`.clone()` immediately before serde**
   ```rust
   let data = self.data.clone();
   serde_json::to_string(&data)?;  // Can serialize &self.data
   ```

2. **`.to_vec()` for iteration**
   ```rust
   for item in self.items.to_vec() {  // Can use &self.items
       process(item);
   }
   ```

3. **Clone in getter returning collection**
   ```rust
   pub fn items(&self) -> Vec<T> {
       self.items.clone()  // Can return &[T]
   }
   ```

4. **Clone before moving into owned position**
   ```rust
   let name = input.name.clone();  // If input is owned, can move
   Config { name, .. }
   ```

These four patterns account for 70-80% of unnecessary clones in typical Rust codebases.

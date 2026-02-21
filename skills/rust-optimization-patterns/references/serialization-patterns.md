# Serialization Patterns for Zero-Copy Performance

Comprehensive guide for optimizing Rust serialization without unnecessary clones.

## Core Principle

**Serde can serialize from references - you don't need to own the data.**

Most serialization operations should work with `&T`, not require cloning to `T`.

## Pattern Categories

### Pattern 1: Serialize Self Directly (Cleanest)

**When to use:**
- Serializing entire struct without transformation
- No special YAML/JSON structure required
- struct fields match desired output format

**Example:**
```rust
#[derive(Serialize, Deserialize)]
pub struct ProxyState {
    pub proxies: Vec<Proxy>,
    pub active_count: usize,
}

impl ProxyState {
    // ✅ Best: Serialize self directly
    pub fn save(&self) -> Result<()> {
        let content = serde_yaml::to_string(self)?;
        fs::write(&self.file_path, content)?;
        Ok(())
    }
}
```

**Output:**
```yaml
proxies:
  - id: 1
    name: proxy1
active_count: 2
```

**Precedent:** Used in `maestro-cli/src/proxy/state.rs:128`

### Pattern 2: Lifetime-Parameterized Wrapper (Type-Safe)

**When to use:**
- Need specific YAML/JSON structure (e.g., `sessions: [...]`)
- Want clear separation between serialization and deserialization types
- Type safety matters more than code simplicity

**Example:**
```rust
// Serialization wrapper (borrows data)
#[derive(Serialize)]
struct SessionsFileRef<'a> {
    sessions: &'a [Session],
}

// Deserialization type (owns data)
#[derive(Deserialize)]
struct SessionsFile {
    sessions: Vec<Session>,
}

impl SessionState {
    // ✅ Good: Zero-copy serialization
    pub fn save(&self) -> Result<()> {
        let file = SessionsFileRef {
            sessions: &self.sessions,  // Borrow, don't clone
        };
        let yaml = serde_yaml::to_string(&file)?;
        fs::write(&self.file_path, yaml)?;
        Ok(())
    }

    pub fn load(path: &Path) -> Result<Self> {
        let content = fs::read_to_string(path)?;
        let file: SessionsFile = serde_yaml::from_str(&content)?;
        Ok(Self {
            file_path: path.to_path_buf(),
            sessions: file.sessions,  // Takes ownership
        })
    }
}
```

**Output:**
```yaml
sessions:
  - uuid: "..."
    name: "session1"
```

**Benefits:**
- Type-safe: compiler enforces correct usage
- Clear separation: different types for save/load
- Zero clones: serializes from reference

### Pattern 3: Inline JSON/YAML Builder (Simpler)

**When to use:**
- Need dynamic structure
- One-off serialization without reusable types
- Prefer conciseness over type safety

**Example:**
```rust
impl SessionState {
    // ✅ Good: Simple inline serialization
    pub fn save(&self) -> Result<()> {
        let data = serde_json::json!({
            "sessions": &self.sessions,
            "version": "1.0",
        });
        let yaml = serde_yaml::to_string(&data)?;
        fs::write(&self.file_path, yaml)?;
        Ok(())
    }
}
```

**Benefits:**
- Concise: no separate struct definition
- Flexible: easy to add computed fields
- Still zero-copy: macro uses references

**Drawbacks:**
- Less type-safe: compiler can't verify structure
- No reusable type for deserialization

### Pattern 4: Custom Serialize Impl (Advanced)

**When to use:**
- Complex transformations needed
- Performance-critical hot path
- Non-standard output format

**Example:**
```rust
use serde::ser::{Serialize, Serializer, SerializeStruct};

impl Serialize for SessionState {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        let mut state = serializer.serialize_struct("SessionsFile", 1)?;
        state.serialize_field("sessions", &self.sessions)?;  // Reference
        state.end()
    }
}
```

**Benefits:**
- Maximum control over serialization
- Can add computed fields efficiently
- Zero-copy by design

**Drawbacks:**
- More boilerplate
- Manual maintenance
- Overkill for simple cases

## Anti-Patterns to Avoid

### ❌ Anti-Pattern 1: Clone for Wrapper

```rust
// Bad: Unnecessary clone
pub fn save(&self) -> Result<()> {
    let file = SessionsFile {
        sessions: self.sessions.clone(),  // Expensive!
    };
    let yaml = serde_yaml::to_string(&file)?;
    fs::write(&self.file_path, yaml)?;
    Ok(())
}
```

**Problem:** Clones entire collection even though serialization only needs to read it.

**Fix:** Use Pattern 2 (lifetime-parameterized wrapper).

### ❌ Anti-Pattern 2: Intermediate Clone for Transformation

```rust
// Bad: Clone then transform
pub fn save(&self) -> Result<()> {
    let sessions_clone = self.sessions.clone();  // Unnecessary
    let transformed: Vec<_> = sessions_clone.iter()
        .map(|s| SessionDTO::from(s))
        .collect();
    serde_json::to_string(&transformed)?;
}
```

**Fix:** Transform while iterating over reference:
```rust
// Good: Transform from reference
pub fn save(&self) -> Result<()> {
    let transformed: Vec<_> = self.sessions.iter()  // Iterate reference
        .map(SessionDTO::from)  // Transform during iteration
        .collect();
    serde_json::to_string(&transformed)?;
}
```

### ❌ Anti-Pattern 3: Clone Before Serialize

```rust
// Bad: Clone before serialization
let data = self.data.clone();
serde_json::to_string(&data)?;

// Good: Serialize from reference
serde_json::to_string(&self.data)?;
```

**Problem:** Serde works fine with references - no clone needed.

## Serde Features for Arc

If using `Arc<T>` for shared ownership, enable serde's `rc` feature:

**Cargo.toml:**
```toml
[dependencies]
serde = { version = "1.0", features = ["derive", "rc"] }
```

**Code:**
```rust
use std::sync::Arc;

#[derive(Serialize, Deserialize)]
pub struct Config {
    #[serde(with = "arc_str_option")]
    pub name: Option<Arc<str>>,
}

mod arc_str_option {
    use serde::{Deserialize, Deserializer, Serialize, Serializer};
    use std::sync::Arc;

    pub fn serialize<S>(value: &Option<Arc<str>>, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        value.as_deref().serialize(serializer)  // Serialize as &str
    }

    pub fn deserialize<'de, D>(deserializer: D) -> Result<Option<Arc<str>>, D::Error>
    where
        D: Deserializer<'de>,
    {
        Option::<String>::deserialize(deserializer)
            .map(|opt| opt.map(|s| Arc::from(s.as_str())))  // Wrap in Arc
    }
}
```

**Important:** Arc loses sharing across serialization boundaries. Deserializing creates new Arc instances.

## Performance Comparison

### Scenario: Saving 1000 Sessions

**Anti-pattern (clone):**
```rust
let file = SessionsFile {
    sessions: self.sessions.clone(),  // Clone 1000 sessions
};
serde_yaml::to_string(&file)?;
```
- Allocations: 1000+ (one per session + Vec)
- Memory: 2x session size (original + clone)
- Time: O(n) clone + O(n) serialize

**Optimized (reference):**
```rust
let file = SessionsFileRef {
    sessions: &self.sessions,  // Zero clones
};
serde_yaml::to_string(&file)?;
```
- Allocations: 0 (just borrows)
- Memory: 1x session size (only original)
- Time: O(n) serialize only

**Improvement:** ~50% faster, ~50% less memory

### Frequency Matters

If `save()` is called on every mutation (maestro-cli pattern):

```rust
// 11 mutation methods all call save()
pub fn add_session(&mut self, session: Session) {
    self.sessions.push(session);
    self.save()?;  // Called on EVERY add
}

pub fn mark_active(&mut self, uuid: Uuid) {
    // ... update session ...
    self.save()?;  // Called on EVERY update
}
```

**Impact of optimization:**
- Low frequency (e.g., user commands): 2-5x improvement
- High frequency (e.g., every mutation): 10-100x improvement

## Pattern Selection Guide

Use this flowchart:

```
Do you need specific YAML/JSON structure?
├─ NO → Use Pattern 1 (serialize self directly)
│        Cleanest, most idiomatic
│
└─ YES → Is the structure dynamic/computed?
    ├─ YES → Use Pattern 3 (inline json! macro)
    │        Simple, flexible
    │
    └─ NO → Do you value type safety?
        ├─ YES → Use Pattern 2 (lifetime wrapper)
        │        Type-safe, separate save/load types
        │
        └─ NO → Use Pattern 3 (inline json! macro)
                 Simpler, less boilerplate
```

## Validation Checklist

After implementing optimization:

- [ ] **YAML/JSON format unchanged**
  ```bash
  # Before optimization
  cargo run -- save
  cp sessions.yaml sessions-before.yaml

  # After optimization
  cargo run -- save
  diff sessions-before.yaml sessions.yaml  # Should be identical
  ```

- [ ] **Tests pass**
  ```bash
  cargo test --lib state
  cargo test --test '*'
  ```

- [ ] **Backward compatibility**
  ```bash
  # Can load old files
  cp sessions-old.yaml sessions.yaml
  cargo run -- load  # Should work
  ```

- [ ] **No regressions**
  - Manual smoke testing
  - Check for changed behavior
  - Verify error handling preserved

## Real-World Examples

### maestro-cli: SessionState (Before)

```rust
// Anti-pattern: Clone before serialize
#[derive(Debug, Deserialize)]
struct SessionsFile {
    sessions: Vec<Session>,
}

pub fn save(&self) -> Result<()> {
    let file = SessionsFile {
        sessions: self.sessions.clone(),  // ❌ Expensive clone
    };
    let yaml = serde_yaml::to_string(&file)?;
    fs::write(&self.file_path, yaml)?;
    Ok(())
}
```

### maestro-cli: SessionState (After - Recommended)

```rust
// Pattern 2: Lifetime wrapper
#[derive(Debug, Serialize)]
struct SessionsFileRef<'a> {
    sessions: &'a [Session],
}

#[derive(Debug, Deserialize)]
struct SessionsFile {
    sessions: Vec<Session>,
}

pub fn save(&self) -> Result<()> {
    let file = SessionsFileRef {
        sessions: &self.sessions,  // ✅ Zero-copy borrow
    };
    let yaml = serde_yaml::to_string(&file)?;
    fs::write(&self.file_path, yaml)?;
    Ok(())
}
```

### maestro-cli: ProxyState (Already Optimized)

```rust
// Pattern 1: Serialize self directly
pub fn save(&self) -> Result<()> {
    let content = serde_yaml::to_string(self)?;  // ✅ Already optimal
    fs::write(&self.file_path, content)?;
    Ok(())
}
```

## Key Insights

1. **Serde works with references** - don't clone data just to serialize it
2. **Separate save/load types** - use lifetime parameters for save, owned types for load
3. **Frequency drives optimization** - high-frequency save() calls benefit most
4. **YAML format can stay identical** - optimizations are implementation details
5. **Type safety vs simplicity** - choose based on team preferences and codebase size

---
name: rust-optimization-patterns
description: Rust performance optimization patterns for eliminating unnecessary clones, choosing optimal collection types, and leveraging Arc for zero-cost abstractions
---

# Rust Optimization Patterns

Expert guidance for optimizing Rust code performance through strategic use of ownership, borrowing, and smart pointers.

## When to Use This Skill

Use this skill when:
- Analyzing Rust code for performance bottlenecks
- Deciding between `Arc<T>`, `Arc<[T]>`, `Vec<Arc<T>>`, or `Vec<T>`
- Eliminating unnecessary `.clone()` calls
- Optimizing serialization/deserialization patterns
- Refactoring read-heavy or write-heavy collections
- Reviewing Rust code for allocation overhead

## Core Optimization Principles

### 1. Serialization Without Cloning

**Anti-pattern:** Cloning data to create serializable wrappers
```rust
// ❌ Bad: Unnecessary clone
pub fn save(&self) -> Result<()> {
    let file = SessionsFile {
        sessions: self.sessions.clone(),  // Expensive clone
    };
    let yaml = serde_yaml::to_string(&file)?;
    fs::write(&self.file_path, yaml)?;
    Ok(())
}
```

**Pattern A:** Use lifetime-parameterized wrapper (type-safe, clean separation)
```rust
// ✅ Good: Serialize from reference
#[derive(Debug, Serialize)]
struct SessionsFileRef<'a> {
    sessions: &'a [Session],
}

pub fn save(&self) -> Result<()> {
    let file = SessionsFileRef {
        sessions: &self.sessions,  // No clone, just borrow
    };
    let yaml = serde_yaml::to_string(&file)?;
    fs::write(&self.file_path, yaml)?;
    Ok(())
}
```

**Pattern B:** Inline serialization (simpler, no new struct)
```rust
// ✅ Good: Direct serialization
pub fn save(&self) -> Result<()> {
    let data = serde_json::json!({ "sessions": &self.sessions });
    let yaml = serde_yaml::to_string(&data)?;
    fs::write(&self.file_path, yaml)?;
    Ok(())
}
```

**Pattern C:** Serialize self directly (cleanest when possible)
```rust
// ✅ Best: No wrapper needed
pub fn save(&self) -> Result<()> {
    let content = serde_yaml::to_string(self)?;
    fs::write(&self.file_path, content)?;
    Ok(())
}
```

**When to use each:**
- Pattern A: When you need specific YAML structure (e.g., `sessions: [...]`)
- Pattern B: When you need dynamic structure or multiple fields
- Pattern C: When serializing entire struct without transformations

### 2. Smart Pointer Selection Matrix

Load `references/smart-pointers-guide.md` for detailed decision trees.

**Quick Reference:**

| Type | Use Case | Clone Cost | Mutation Cost |
|------|----------|------------|---------------|
| `Vec<T>` | Mutable collections, frequent add/remove | Deep copy | O(1) amortized |
| `Arc<[T]>` | Immutable shared slices | Ref count++ | Full copy (COW) |
| `Vec<Arc<T>>` | Independent item sharing | Vec spine | O(1) per item |
| `Arc<str>` | Immutable strings, many clones | Ref count++ | N/A (immutable) |

**Decision Tree:**

```
Is data mutable after creation?
├─ YES → Use Vec<T> (allow mutations)
└─ NO → Is entire collection shared?
    ├─ YES → Use Arc<[T]> (share whole slice)
    └─ NO → Are individual items shared independently?
        ├─ YES → Use Vec<Arc<T>> (share items)
        └─ NO → Use Vec<T> (no sharing needed)
```

### 3. Arc for Immutable String Fields

**When to use `Arc<str>` or `Arc<String>`:**
- Field is immutable after creation
- Struct is cloned frequently
- String data is non-trivial size (>24 bytes typically)
- NOT mutated after initialization

**Implementation:**

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Session {
    pub uuid: Uuid,

    // Immutable strings → Arc
    #[serde(with = "arc_str_option")]
    pub name: Option<Arc<str>>,

    #[serde(with = "arc_str_option")]
    pub branch: Option<Arc<str>>,

    // Mutable string → Keep as String
    pub container_id: String,

    pub active: bool,
}

// Serde support module
mod arc_str_option {
    use serde::{Deserialize, Deserializer, Serialize, Serializer};
    use std::sync::Arc;

    pub fn serialize<S>(value: &Option<Arc<str>>, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        value.as_deref().serialize(serializer)
    }

    pub fn deserialize<'de, D>(deserializer: D) -> Result<Option<Arc<str>>, D::Error>
    where
        D: Deserializer<'de>,
    {
        Option::<String>::deserialize(deserializer)
            .map(|opt| opt.map(|s| Arc::from(s.as_str())))
    }
}
```

**Prerequisites:**
- Add `serde = { version = "1.0", features = ["derive", "rc"] }` to Cargo.toml

### 4. Frequency-Based Optimization Priority

**High Priority (10-100x frequency):**
- Clone operations in save/persist methods called on every mutation
- Serialization patterns in hot paths
- Collection clones in loops

**Medium Priority (User interaction frequency):**
- Clone operations in CLI commands
- Data transformations in request handlers
- UI picker/selector operations

**Low Priority (Infrequent or necessary):**
- Clones for moving data into closures (often necessary)
- Clones for owned field assignment (unavoidable)
- One-time initialization clones

**Optimization Strategy:**
1. Profile or analyze call frequency first
2. Optimize high-frequency operations (e.g., save() called on every mutation)
3. Consider medium-frequency after measuring impact
4. Skip low-frequency unless profiling shows bottleneck

## Common Anti-Patterns

### ❌ Arc for Mutable Data

```rust
// Bad: Arc doesn't help if data is mutable
pub struct State {
    sessions: Arc<[Session]>,  // Immutable slice
}

// Every mutation requires full copy
pub fn add_session(&mut self, session: Session) {
    let mut new_sessions = self.sessions.to_vec();
    new_sessions.push(session);
    self.sessions = Arc::from(new_sessions);  // Full copy!
}
```

**Fix:** Use `Vec<T>` for mutable collections.

### ❌ Vec<Arc<T>> for Collection Sharing

```rust
// Bad: Sharing individual items when you want to share the collection
pub fn get_sessions(&self) -> Vec<Arc<Session>> {
    self.sessions.iter().map(|s| Arc::new(s.clone())).collect()  // Still clones!
}
```

**Fix:** Use `Arc<[T]>` to share entire collection, or return `&[T]` if lifetime allows.

### ❌ Unnecessary Intermediate Clones

```rust
// Bad: Clone just to pass to serialization
let data = self.data.clone();
serde_json::to_string(&data)?;

// Good: Serialize from reference
serde_json::to_string(&self.data)?;
```

## Verification Checklist

When optimizing:

- [ ] Identify operation frequency (high/medium/low)
- [ ] Determine if data is mutable or immutable
- [ ] Check if entire collection or individual items are shared
- [ ] Verify serde features if using Arc (`features = ["rc"]`)
- [ ] Ensure YAML/JSON format unchanged after refactor
- [ ] Run existing tests to verify behavior preserved
- [ ] Add benchmarks for high-frequency operations (optional)

## Integration with Existing Code

**Before changing:**
1. Read existing serialization patterns in codebase
2. Check if other save() methods already use optimized pattern
3. Verify serde features in Cargo.toml
4. Identify all call sites of the method being optimized

**After changing:**
1. Compare generated output (YAML/JSON) before/after
2. Run full test suite
3. Test backward compatibility (load old persisted files)
4. Manual smoke testing for user-facing operations

## References

For detailed guidance on specific topics:

- Load `references/smart-pointers-guide.md` for Arc decision trees
- Load `references/serialization-patterns.md` for serde optimization patterns
- Load `references/clone-audit-checklist.md` for systematic clone analysis

## Related Patterns

- **maestro-companion precedent:** Achieved 77-79% improvement using `Vec<Arc<Event>>` for immutable event buffer with frequent replay operations
- **ProxyState pattern:** Already optimized - serializes `self` directly without intermediate wrappers
- **Copy-on-write (COW):** Use `Arc<[T]>` for read-heavy, occasionally-written collections

## Key Insights

1. **Different use cases need different solutions:** maestro-companion's Arc optimization worked for immutable events; maestro-cli needs Vec for mutable sessions
2. **Serialization is often the biggest win:** Eliminate clones in save() methods called on every mutation
3. **Arc is not always the answer:** Vec is correct for mutable collections with frequent mutations
4. **Serde can serialize from references:** No need to clone data just to pass to serialization
5. **Optimize for actual usage patterns:** Read-heavy vs write-heavy determines optimal data structure

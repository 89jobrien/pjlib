# Smart Pointers Decision Guide

Comprehensive guide for choosing between Arc, Vec, and their combinations in Rust.

## Decision Tree

```
┌─ Is the data mutable after creation?
│
├─ YES (mutable data)
│  │
│  └─ Use Vec<T>
│     - Allows in-place mutations
│     - O(1) amortized insertions
│     - Correct for read-write workloads
│
└─ NO (immutable data)
   │
   ├─ Is the entire collection shared across contexts?
   │  │
   │  ├─ YES → Use Arc<[T]>
   │  │   - Cheap clones (ref count++)
   │  │   - Share entire slice
   │  │   - Read-only access
   │  │
   │  └─ NO → Are individual items shared independently?
   │     │
   │     ├─ YES → Use Vec<Arc<T>>
   │     │   - Each item independently shared
   │     │   - Different lifetimes per item
   │     │   - Clone increments item ref count
   │     │
   │     └─ NO → Use Vec<T>
   │         - No sharing overhead
   │         - Direct ownership
```

## Type Comparison Matrix

| Type | Clone Cost | Mutation Cost | Best For | Avoid When |
|------|------------|---------------|----------|------------|
| `Vec<T>` | O(n) deep copy | O(1) amortized | Mutable collections | Frequent clones |
| `Arc<[T]>` | O(1) ref count | O(n) full copy | Immutable shared slices | Any mutations |
| `Vec<Arc<T>>` | O(n) ref counts | O(1) per item | Independent item sharing | Sharing whole collection |
| `Arc<str>` | O(1) ref count | N/A (immutable) | Immutable strings | Mutable strings |

## Detailed Use Cases

### Vec<T> - Mutable Collections

**Best for:**
- Collections with frequent add/remove/update operations
- Read-write workloads
- Local ownership without sharing

**Example:**
```rust
pub struct SessionState {
    sessions: Vec<Session>,  // Mutable: add, remove, update
}

impl SessionState {
    pub fn add_session(&mut self, session: Session) {
        self.sessions.push(session);  // O(1) amortized
    }

    pub fn remove_session(&mut self, uuid: Uuid) {
        self.sessions.retain(|s| s.uuid != uuid);  // In-place mutation
    }
}
```

**When to avoid:**
- Frequent cloning of entire collection (consider Arc<[T]> for read-heavy)

### Arc<[T]> - Immutable Shared Slices

**Best for:**
- Immutable collections shared across threads or contexts
- Read-heavy workloads where collection rarely changes
- Sharing entire collection with cheap clones

**Example:**
```rust
pub struct EventBuffer {
    events: Arc<[Event]>,  // Immutable, shared
}

impl EventBuffer {
    pub fn get_events(&self) -> Arc<[Event]> {
        Arc::clone(&self.events)  // O(1) ref count increment
    }

    // Mutation requires full copy (copy-on-write)
    pub fn add_event(&mut self, event: Event) {
        let mut new_events = self.events.to_vec();
        new_events.push(event);
        self.events = Arc::from(new_events);  // O(n) full copy
    }
}
```

**When to avoid:**
- Frequent mutations (every change requires full copy)
- Mutable workloads (use Vec<T> instead)

### Vec<Arc<T>> - Independent Item Sharing

**Best for:**
- Individual items shared independently across contexts
- Items with different lifetimes or ownership
- Subsets of collection shared selectively

**Example:**
```rust
pub struct Cache {
    entries: Vec<Arc<CacheEntry>>,  // Each entry independently shared
}

impl Cache {
    pub fn get_entry(&self, id: usize) -> Option<Arc<CacheEntry>> {
        self.entries.get(id).map(Arc::clone)  // Share individual item
    }

    pub fn add_entry(&mut self, entry: CacheEntry) {
        self.entries.push(Arc::new(entry));  // O(1)
    }
}
```

**When to avoid:**
- Sharing entire collection together (use Arc<[T]> instead)
- No sharing needed (use Vec<T> for simpler code)

### Arc<str> - Immutable Strings

**Best for:**
- Immutable string fields in frequently-cloned structs
- Strings > 24 bytes (typical String inline capacity)
- Shared string data across multiple owners

**Example:**
```rust
#[derive(Clone)]
pub struct Config {
    pub name: Arc<str>,      // Immutable string, cheap clone
    pub branch: Arc<str>,    // Immutable string, cheap clone
    pub project_id: String,  // Mutable string, keep as String
}

impl Config {
    pub fn clone_for_fork(&self) -> Self {
        // Arc fields: O(1) ref count++
        // String fields: O(n) deep copy
        self.clone()
    }
}
```

**When to avoid:**
- Mutable strings (use String)
- Small strings (<24 bytes) cloned infrequently
- No cloning (use &str or String)

## Common Mistakes

### ❌ Mistake 1: Arc for Mutable Data

```rust
// Bad: Arc makes mutations expensive
struct State {
    items: Arc<Vec<Item>>,  // Wrong: Vec is mutable
}

// Every mutation requires cloning entire Vec
fn add_item(&mut self, item: Item) {
    let mut items = (*self.items).clone();  // Full deep copy!
    items.push(item);
    self.items = Arc::new(items);
}
```

**Fix:** Use `Vec<T>` directly for mutable collections.

### ❌ Mistake 2: Vec<Arc<T>> for Collection Sharing

```rust
// Bad: Wrapping each item when you want to share the whole collection
fn get_sessions(&self) -> Vec<Arc<Session>> {
    self.sessions.iter()
        .map(|s| Arc::new(s.clone()))  // Still clones each Session!
        .collect()
}
```

**Fix:** Use `Arc<[T]>` to share entire collection, or return `&[T]` if lifetimes allow.

### ❌ Mistake 3: Arc When No Sharing Needed

```rust
// Bad: Arc overhead with no benefit
struct LocalCache {
    items: Vec<Arc<Item>>,  // No sharing across threads/contexts
}

fn process(&self) {
    for item in &self.items {
        // Arc overhead but items never leave this context
        self.process_item(item);
    }
}
```

**Fix:** Use `Vec<T>` when data isn't shared beyond single owner.

## Workload Patterns

### Read-Heavy Workload

**Characteristics:**
- Frequent reads, infrequent writes
- Collection shared across multiple contexts
- Mutations are batched or rare

**Recommended:** `Arc<[T]>`

**Example:** Event replay buffer, configuration cache, immutable lookup tables

### Write-Heavy Workload

**Characteristics:**
- Frequent insertions, updates, deletions
- Mutations on every operation
- Local ownership within single context

**Recommended:** `Vec<T>`

**Example:** Session state, active task queue, mutation log

### Mixed Workload

**Characteristics:**
- Moderate reads and writes
- Some items shared independently
- Dynamic collection size

**Recommended:** Depends on specifics
- `Vec<T>` if mutations dominate
- `Arc<[T]>` if reads dominate and writes can use COW
- `Vec<Arc<T>>` if individual items have independent lifetimes

**Example:** Cache with eviction policy, partially-shared collections

## Performance Considerations

### Memory Overhead

| Type | Overhead per Item | Overhead per Collection |
|------|-------------------|-------------------------|
| `Vec<T>` | 0 bytes | 24 bytes (ptr, len, cap) |
| `Arc<[T]>` | 0 bytes | 16 bytes (ptr to header) + 16 bytes (ref counts) |
| `Vec<Arc<T>>` | 16 bytes (Arc) | 24 bytes (Vec) |
| `Arc<str>` | 16 bytes (Arc) | Header overhead |

### Clone Performance

**Vec<T>**: O(n) - deep copy of all items
```rust
let cloned = vec.clone();  // Copies all items
```

**Arc<[T]>**: O(1) - atomic ref count increment
```rust
let shared = Arc::clone(&arc_slice);  // Just increments counter
```

**Vec<Arc<T>>**: O(n) - copies Vec spine, increments each Arc
```rust
let cloned = vec_arc.clone();  // O(n) ref count increments
```

### Mutation Performance

**Vec<T>**: O(1) amortized for push, O(n) for general mutations
```rust
vec.push(item);           // O(1) amortized
vec.remove(index);        // O(n) shift elements
```

**Arc<[T]>**: O(n) - full copy (copy-on-write)
```rust
let mut new_vec = arc_slice.to_vec();  // O(n) copy
new_vec.push(item);
arc_slice = Arc::from(new_vec);
```

**Vec<Arc<T>>**: O(1) for collection ops, O(1) for item replacement
```rust
vec_arc.push(Arc::new(item));     // O(1)
vec_arc[i] = Arc::new(new_item);  // O(1)
```

## Checklist for Choosing

Use this checklist to decide:

- [ ] **Is data mutable after creation?**
  - Yes → Eliminate `Arc<[T]>` (expensive mutations)
  - No → Consider `Arc<[T]>` for sharing

- [ ] **Is entire collection shared?**
  - Yes → Prefer `Arc<[T]>` (if immutable)
  - No → Consider `Vec<T>` or `Vec<Arc<T>>`

- [ ] **Are items shared independently?**
  - Yes → Consider `Vec<Arc<T>>`
  - No → Prefer `Vec<T>` (simpler)

- [ ] **What's the read/write ratio?**
  - Read-heavy → `Arc<[T]>` (if immutable)
  - Write-heavy → `Vec<T>`
  - Mixed → Profile and measure

- [ ] **Is this data shared across threads?**
  - Yes → `Arc` required for thread-safety
  - No → Consider `Rc` or just `Vec<T>`

## Real-World Examples

### maestro-companion: Event Buffer (Arc<[T]>)

```rust
// Immutable events, read-heavy (replay on every reconnect)
pub struct EventBuffer {
    events: Vec<Arc<BufferedBrowserEvent>>,  // Individual events shared
}

// Why Arc here: Events are immutable, replayed frequently
// Why Vec<Arc>: Individual events shared across protocol messages
```

**Lesson:** Immutable data with frequent sharing benefits from Arc.

### maestro-cli: Session State (Vec<T>)

```rust
// Mutable sessions, write-heavy (add/update/remove)
pub struct SessionState {
    sessions: Vec<Session>,  // Mutable collection
}

// Why Vec: Frequent mutations (11 different mutation methods)
// Why not Arc: Would require full copy on every mutation
```

**Lesson:** Mutable collections with frequent writes need Vec<T>.

### ProxyState: Direct Serialization (Vec<T>)

```rust
// Serialize self directly without intermediate wrapper
pub fn save(&self) -> Result<()> {
    let content = serde_yaml::to_string(self)?;  // Serialize from &self
    fs::write(&self.file_path, content)?;
    Ok(())
}
```

**Lesson:** Serde can serialize from references - no clone needed.

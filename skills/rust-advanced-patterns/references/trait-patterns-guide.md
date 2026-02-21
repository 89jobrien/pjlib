# Trait Patterns Guide

Comprehensive guide to Rust trait design patterns for 2026.

## Table of Contents

1. [Extension Traits](#extension-traits)
2. [Trait Objects vs Generics](#trait-objects-vs-generics)
3. [Associated Types](#associated-types)
4. [Generic Associated Types (GATs)](#generic-associated-types-gats)
5. [Higher-Ranked Trait Bounds (HRTB)](#higher-ranked-trait-bounds-hrtb)
6. [Blanket Implementations](#blanket-implementations)
7. [Coherence and Orphan Rules](#coherence-and-orphan-rules)
8. [Sealed Traits](#sealed-traits)

---

## Extension Traits

**Purpose**: Add methods to types you don't own

**Pattern**:
```rust
pub trait IteratorExt: Iterator {
    fn collect_result<T, E>(self) -> Result<Vec<T>, E>
    where
        Self: Iterator<Item = Result<T, E>> + Sized,
    {
        self.collect()
    }
}

// Blanket implementation for all iterators
impl<I: Iterator> IteratorExt for I {}

// Usage
let results: Vec<_> = items.into_iter()
    .map(|x| x.process())
    .collect_result()?;
```

**When to use**:
- Adding methods to std library types
- Providing domain-specific operations
- Non-breaking API evolution

**Examples in the wild**:
- `tokio::io::AsyncReadExt`
- `futures::stream::StreamExt`
- `itertools::Itertools`

---

## Trait Objects vs Generics

### Static Dispatch (Generics)

**Zero overhead, compile-time monomorphization**:
```rust
fn process<T: Display>(item: &T) {
    println!("{}", item);
}

// Compiler generates:
// fn process_i32(item: &i32) { println!("{}", item); }
// fn process_String(item: &String) { println!("{}", item); }
```

**Performance**: 0ns overhead, ~15ns per 100 elements

**Trade-offs**:
- ✅ Zero runtime cost
- ✅ Inline optimization
- ❌ Code bloat (one copy per type)
- ❌ Cannot store in collections
- ❌ Cannot choose at runtime

### Dynamic Dispatch (Trait Objects)

**Runtime polymorphism via vtable**:
```rust
fn process(item: &dyn Display) {
    println!("{}", item);
}

// Storage
let items: Vec<Box<dyn Display>> = vec![
    Box::new(42),
    Box::new("hello"),
];
```

**Performance**: 2-5ns per call overhead, ~45ns per 100 elements (3x slower)

**Trade-offs**:
- ✅ No code bloat
- ✅ Runtime selection
- ✅ Heterogeneous collections
- ❌ Virtual call overhead
- ❌ No inline optimization
- ❌ Object safety requirements

### Decision Matrix

| Use Case | Recommendation |
|----------|---------------|
| Hot path, performance critical | Generics |
| Plugin system | Trait objects |
| Library API (compile-time known) | Generics |
| Heterogeneous collections | Trait objects |
| Code size critical | Trait objects |

---

## Associated Types

**Pattern**: Use for ONE canonical type per implementation

```rust
trait Iterator {
    type Item;  // One Item type per Iterator
    fn next(&mut self) -> Option<Self::Item>;
}

impl Iterator for Counter {
    type Item = u32;  // Counter always yields u32
    fn next(&mut self) -> Option<u32> { /* ... */ }
}
```

**vs Generic Parameters** (multiple possibilities):
```rust
trait From<T> {  // Can implement many From<T>
    fn from(value: T) -> Self;
}

impl From<String> for MyType { /* ... */ }
impl From<i32> for MyType { /* ... */ }
impl From<&str> for MyType { /* ... */ }
```

**Decision rule**:
- **Associated type**: "There is one natural type for this operation"
- **Generic parameter**: "This operation works with many types"

**Examples**:
- `Iterator::Item` - One item type per iterator
- `Future::Output` - One output type per future
- `Add::Output` - Result type of addition
- `From<T>` / `Into<T>` - Convert from/to many types

---

## Generic Associated Types (GATs)

**Stabilized**: Rust 1.65 (November 2022)

**Purpose**: Associated types with lifetime or type parameters

### Lending Iterator

```rust
trait LendingIterator {
    type Item<'a> where Self: 'a;
    fn next(&mut self) -> Option<Self::Item<'_>>;
}

// Can return references to self
impl LendingIterator for Windows<'_> {
    type Item<'a> = &'a [u8] where Self: 'a;
    fn next(&mut self) -> Option<&[u8]> { /* ... */ }
}
```

**Before GATs**, this required HRTB workarounds or was impossible.

### Async Traits (Built on GATs)

```rust
// Native async trait (Rust 1.75+)
trait AsyncRead {
    async fn read(&mut self, buf: &mut [u8]) -> io::Result<usize>;
}

// Desugars to GAT internally
trait AsyncRead {
    type ReadFuture<'a>: Future<Output = io::Result<usize>>
    where
        Self: 'a;

    fn read<'a>(&'a mut self, buf: &'a mut [u8]) -> Self::ReadFuture<'a>;
}
```

---

## Higher-Ranked Trait Bounds (HRTB)

**Pattern**: Trait bounds that work for **all** lifetimes

```rust
// Function that works with closures taking any lifetime
fn apply<F>(f: F)
where
    F: for<'a> Fn(&'a str) -> &'a str,
{
    let result = f("hello");
    println!("{}", result);
}

// Without HRTB, you'd need:
// fn apply<'a, F>(f: F) where F: Fn(&'a str) -> &'a str
// But then 'a is fixed at call site!
```

**Common use cases**:
- Closures with generic lifetimes
- Iterator adapters
- Trait bounds on functions

**Example from std**:
```rust
pub trait FnOnce<Args> {
    type Output;
    fn call_once(self, args: Args) -> Self::Output;
}

// FnMut is HRTB over Args
pub trait FnMut<Args>: FnOnce<Args> {
    fn call_mut(&mut self, args: Args) -> Self::Output;
}
```

---

## Blanket Implementations

**Pattern**: Implement trait for all types matching constraints

```rust
// Implement IteratorExt for ALL iterators
impl<I: Iterator> IteratorExt for I {
    // Methods available on all Iterator types
}

// Implement ToString for all Display types
impl<T: Display> ToString for T {
    fn to_string(&self) -> String {
        format!("{}", self)
    }
}
```

**Use cases**:
- Extension traits
- Automatic trait derivation
- Adapter patterns

**Caution**: Can create coherence conflicts. See next section.

---

## Coherence and Orphan Rules

**Orphan Rule**: You can implement a trait for a type only if:
- You own the trait, OR
- You own the type

**This is invalid**:
```rust
// Cannot implement foreign trait for foreign type
impl Display for Vec<String> {  // ❌ Orphan rule violation
    // ...
}
```

**Workarounds**:

### 1. Newtype Pattern
```rust
struct MyVec(Vec<String>);

impl Display for MyVec {  // ✅ We own MyVec
    fn fmt(&self, f: &mut Formatter) -> fmt::Result {
        write!(f, "{:?}", self.0)
    }
}
```

### 2. Extension Trait
```rust
trait VecExt {
    fn display(&self) -> String;
}

impl VecExt for Vec<String> {  // ✅ We own VecExt
    fn display(&self) -> String {
        format!("{:?}", self)
    }
}
```

**Coherence**: Prevents conflicting implementations

```rust
// If both allowed, which to use?
impl<T> MyTrait for T { /* ... */ }        // Blanket impl
impl MyTrait for String { /* ... */ }      // Specific impl

// Rust prevents this at compile time
```

---

## Sealed Traits

**Purpose**: Prevent external implementations while keeping trait public

**Pattern**:
```rust
mod private {
    pub trait Sealed {}
}

pub trait MyTrait: private::Sealed {
    fn method(&self);
}

// Implementations (in your crate)
impl private::Sealed for MyType {}
impl MyTrait for MyType {
    fn method(&self) { /* ... */ }
}

// External crates cannot implement MyTrait
// because they cannot implement private::Sealed
```

**Use cases**:
- Maintaining invariants
- Future-proofing APIs
- Preventing misuse

**Examples in std**:
- `std::io::Seek` (sealed in some contexts)
- Iterator extension traits

---

## Best Practices Summary

1. **Extension Traits**: Add methods to foreign types
2. **Generics**: Default for performance (static dispatch)
3. **Trait Objects**: Use for flexibility (plugins, collections)
4. **Associated Types**: One canonical type per implementation
5. **GATs**: Lending patterns, async traits
6. **HRTB**: Functions with lifetime-polymorphic closures
7. **Blanket Impls**: Powerful but watch for coherence issues
8. **Sealed Traits**: Control your API surface

## Performance Guidelines

- **Generics**: 0 overhead, potential code bloat
- **Trait Objects**: 2-5ns call overhead, better code size
- **Associated Types**: 0 overhead (compile-time resolution)
- **GATs**: 0 overhead (compile-time resolution)

## Further Reading

- Rust Book: [Traits](https://doc.rust-lang.org/book/ch10-02-traits.html)
- Rust Reference: [Trait Objects](https://doc.rust-lang.org/reference/types/trait-object.html)
- RFC 2145: [GATs](https://rust-lang.github.io/rfcs/2145-type-alias-impl-trait.html)

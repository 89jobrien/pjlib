---
name: rust-advanced-patterns
description: Comprehensive Rust advanced patterns covering trait design, macros (declarative & procedural), type-level programming, and generic programming techniques
---

# Rust Advanced Patterns

Use this skill when designing Rust APIs, implementing macros, creating type-safe abstractions, or applying advanced Rust programming techniques.

## When to Use This Skill

**Use PROACTIVELY when:**
- Designing trait-based APIs
- Implementing declarative or procedural macros
- Creating type-safe state machines or protocols
- Using type-level programming for compile-time guarantees
- Implementing zero-cost abstractions
- Working with const generics or phantom types

**Use when users request:**
- Help with trait design
- Macro implementation guidance
- Type-level safety patterns
- Generic programming techniques
- API design advice

## Quick Reference

### Trait Design Decision Tree

```
Need to add methods to existing type?
├─ Own the type? → Add methods directly
└─ Don't own? → Extension trait

Need runtime polymorphism?
├─ Yes → Trait object (Box<dyn Trait>)
└─ No → Generics (static dispatch)

Multiple possible types for trait method?
├─ One canonical type → Associated type
└─ Multiple possibilities → Generic parameter

Need to constrain lifetimes?
├─ For closures/functions → HRTB (for<'a>)
└─ For data → Generic lifetimes

Want to prevent external implementations?
└─ Sealed trait pattern
```

### Macro Decision Tree

```
What do you need?
│
├─ Simple syntax sugar (<150 lines)
│  └─ Declarative macro (macro_rules!)
│
├─ Custom derive (#[derive(MyTrait)])
│  └─ Procedural derive macro
│
├─ Modify function/struct (#[my_attr])
│  └─ Procedural attribute macro
│
└─ Complex DSL or code generation
   └─ Procedural function-like macro
```

### Type-Level Pattern Selection

| Goal | Pattern | Zero-Cost? |
|------|---------|------------|
| Type-safe IDs | Newtype | ✅ |
| Units of measure | Newtype + Phantom | ✅ |
| State machines | Type-State | ✅ |
| Protocol safety | Type-State Machine | ✅ |
| Fixed-size arrays | Const Generics | ✅ |
| Capability tokens | Zero-Sized Types (ZSTs) | ✅ |

## Core Patterns

### 1. Trait Patterns

**Extension Trait** (Add methods to foreign types):
```rust
pub trait IteratorExt: Iterator {
    fn collect_result<T, E>(self) -> Result<Vec<T>, E>
    where
        Self: Iterator<Item = Result<T, E>> + Sized,
    {
        self.collect()
    }
}

// Blanket implementation
impl<I: Iterator> IteratorExt for I {}
```

**Trait Objects vs Generics**:
```rust
// Static dispatch (monomorphization) - Zero overhead
fn process<T: Display>(item: &T) {
    println!("{}", item);
}

// Dynamic dispatch - 2-5ns overhead per call
fn process_dyn(item: &dyn Display) {
    println!("{}", item);
}

// Rule: Use generics for performance, trait objects for flexibility
```

**Associated Types**:
```rust
// Use for ONE canonical output type
trait Iterator {
    type Item;  // Only one Item type per implementation
    fn next(&mut self) -> Option<Self::Item>;
}

// Use generics for MULTIPLE possibilities
trait From<T> {  // Can implement From<String>, From<i32>, etc.
    fn from(value: T) -> Self;
}
```

**For complete trait patterns**, load `references/trait-patterns-guide.md`

### 2. Macro Patterns

**Declarative Macro** (Simple repetition):
```rust
macro_rules! vec_of_strings {
    ($($element:expr),* $(,)?) => {
        vec![$($element.to_string()),*]
    };
}

// Usage
let v = vec_of_strings!["hello", "world"];
```

**Procedural Derive Macro** (Custom #[derive]):
```rust
use proc_macro::TokenStream;
use quote::quote;
use syn::{parse_macro_input, DeriveInput};

#[proc_macro_derive(Builder)]
pub fn derive_builder(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    let name = input.ident;

    let expanded = quote! {
        impl #name {
            pub fn builder() -> #name Builder {
                Default::default()
            }
        }
    };

    TokenStream::from(expanded)
}
```

**For complete macro patterns**, load `references/macro-patterns-guide.md`

### 3. Type-Level Programming

**Newtype Pattern** (Type-safe IDs):
```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct UserId(u64);

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct OrderId(u64);

// Cannot mix up user IDs and order IDs
fn get_user(id: UserId) -> User { /* ... */ }
// get_user(OrderId(123));  // Compile error!
```

**Type-State Pattern** (Compile-time state verification):
```rust
use std::marker::PhantomData;

struct Open;
struct Closed;

struct Connection<State> {
    socket: TcpStream,
    _state: PhantomData<State>,
}

impl Connection<Closed> {
    pub fn connect(self) -> Connection<Open> {
        // Connection logic
        Connection { socket: self.socket, _state: PhantomData }
    }
}

impl Connection<Open> {
    pub fn send(&mut self, data: &[u8]) -> io::Result<()> {
        // Only available in Open state
        self.socket.write_all(data)
    }
}

// Cannot call send() on Closed connection - compile error!
```

**Const Generics** (Compile-time array sizing):
```rust
struct Buffer<T, const SIZE: usize> {
    data: [T; SIZE],
}

impl<T: Default + Copy, const SIZE: usize> Buffer<T, SIZE> {
    pub fn new() -> Self {
        Self {
            data: [T::default(); SIZE],
        }
    }
}

// Type-safe, no heap allocation
let buf: Buffer<u8, 1024> = Buffer::new();
```

**For complete type-level patterns**, load `references/type-level-programming-guide.md`

## Performance Guarantees

All patterns in this skill are **zero-cost abstractions**:

```rust
// Runtime cost comparisons:
assert_eq!(size_of::<UserId>(), size_of::<u64>());  // Newtype: 0 bytes overhead
assert_eq!(size_of::<Connection<Open>>(), size_of::<TcpStream>());  // Type-State: 0 bytes
assert_eq!(size_of::<PhantomData<T>>(), 0);  // Phantom: literally zero
```

## Common Anti-Patterns

### Trait Anti-Patterns

❌ **Over-abstraction**:
```rust
// BAD: Trait with only one implementation
trait UserRepository {
    fn find(&self, id: u64) -> Option<User>;
}

struct PostgresUserRepository;
impl UserRepository for PostgresUserRepository { /* ... */ }

// GOOD: Just use the concrete type
struct UserRepository;
impl UserRepository {
    fn find(&self, id: u64) -> Option<User> { /* ... */ }
}
```

❌ **God traits** (too many methods):
```rust
// BAD: 20+ methods in one trait
trait DataAccess {
    fn find_user(...);
    fn create_user(...);
    fn delete_user(...);
    fn find_order(...);
    // ... 16 more methods
}

// GOOD: Split into focused traits
trait UserRepository { /* user methods */ }
trait OrderRepository { /* order methods */ }
```

### Macro Anti-Patterns

❌ **God macros** (>500 lines):
```rust
// BAD: Massive declarative macro
macro_rules! huge_macro {
    // 500+ lines of TT munching
}

// GOOD: Use procedural macro with syn/quote
```

❌ **Hidden unsafe**:
```rust
// BAD: Unsafe hidden in macro
macro_rules! deref {
    ($ptr:expr) => { unsafe { *$ptr } };
}

// GOOD: Make unsafe explicit
macro_rules! deref {
    ($ptr:expr) => {{
        // Safety: Caller must ensure ptr is valid
        unsafe { *$ptr }
    }};
}
```

### Type-Level Anti-Patterns

❌ **Type-state explosion**:
```rust
// BAD: Too many states
struct Connection<Auth, Tls, Compress, Retry> { /* ... */ }

// GOOD: Use builder or nested states
struct Connection<State> { /* ... */ }
```

## Reference Files

This skill includes comprehensive references:

- **`references/trait-patterns-guide.md`** - Extension traits, trait objects vs generics, associated types, GATs, HRTB, blanket impls, coherence rules
- **`references/macro-patterns-guide.md`** - Declarative macros (macro_rules!), procedural macros (derive, attribute, function-like), syn/quote, testing
- **`references/type-level-programming-guide.md`** - Newtype, type-state, phantom types, const generics, ZSTs, compile-time guarantees, state machines

Load these files when you need detailed implementation guidance beyond the quick reference above.

## Integration with Other Skills

- **rust-safety-engineering**: Use type-state patterns for safety guarantees
- **rust-async-patterns**: Apply trait patterns to async code design
- **rust-testing-strategies**: Test macros with trybuild, test trait implementations
- **rust-optimization-patterns**: Understand performance implications of trait dispatch

## Real-World Examples

**Popular crates using these patterns:**

- **serde**: Procedural derive macros, associated types, trait objects
- **tokio**: Extension traits, GATs for async, type-state for tasks
- **diesel**: Type-level SQL safety, const generics, newtype pattern
- **rocket**: Type-state routing, procedural macros
- **anyhow/thiserror**: Extension traits, procedural derives

## Success Criteria

You're using advanced patterns effectively when:

- Traits are focused (single responsibility)
- Type-level guarantees prevent runtime errors
- Macros are maintainable (<150 lines for declarative, well-tested for procedural)
- Zero runtime overhead maintained
- API is ergonomic and hard to misuse
- Compile errors guide users to correct usage

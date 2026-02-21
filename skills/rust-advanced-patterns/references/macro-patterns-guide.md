# Macro Patterns Guide

Comprehensive guide to Rust macro patterns for 2026.

## Table of Contents

1. [Declarative Macros (macro_rules!)](#declarative-macros)
2. [Procedural Derive Macros](#procedural-derive-macros)
3. [Procedural Attribute Macros](#procedural-attribute-macros)
4. [Procedural Function-Like Macros](#procedural-function-like-macros)
5. [Testing Macros](#testing-macros)
6. [Best Practices](#best-practices)

---

## Declarative Macros

**Use for**: Simple syntax sugar, repetitive implementations (<150 lines)

### Basic Pattern

```rust
macro_rules! vec_of_strings {
    // Support trailing comma
    ($($element:expr),* $(,)?) => {
        vec![$($element.to_string()),*]
    };
}

// Usage
let v = vec_of_strings!["hello", "world"];
```

### Fragment Specifiers (2026)

| Specifier | Matches | Example |
|-----------|---------|---------|
| `expr` | Expression | `x + 1`, `foo()` |
| `ty` | Type | `i32`, `Vec<String>` |
| `ident` | Identifier | `foo`, `bar` |
| `path` | Path | `std::io::Read` |
| `pat` | Pattern | `Some(x)`, `_` |
| `stmt` | Statement | `let x = 5;` |
| `block` | Block | `{ ... }` |
| `item` | Item | `fn foo() {}` |
| `meta` | Meta | `#[derive(Debug)]` |
| `tt` | Token tree | Any single token |
| `literal` | Literal | `42`, `"hello"` |
| `lifetime` | Lifetime | `'a`, `'static` |
| `vis` | Visibility | `pub`, `pub(crate)` |

### Repetition Patterns

```rust
macro_rules! create_functions {
    // Zero or more ($(...)*), one or more ($(...)+), optional ($(...)?
    ($($fn_name:ident),+ $(,)?) => {
        $(
            pub fn $fn_name() {
                println!("{}!", stringify!($fn_name));
            }
        )+
    };
}

create_functions!(foo, bar, baz);
```

### Internal Macros (Best Practice)

```rust
/// Public macro
#[macro_export]
macro_rules! public_api {
    ($($tt:tt)*) => {
        $crate::__internal_api!(@start $($tt)*)
    };
}

/// Implementation detail
#[macro_export]
#[doc(hidden)]
macro_rules! __internal_api {
    (@start $x:expr) => {
        // Complex logic here
    };
}
```

### Hygiene

```rust
macro_rules! five {
    () => { 5 }; // Hygienic: Always returns 5
}

macro_rules! broken {
    () => { x }; // ❌ Unhygienic: references external x
}

// Use $crate for paths
macro_rules! use_function {
    () => {
        $crate::internal::helper()  // ✅ Always resolves correctly
    };
}
```

### Metavariable Expressions (Rust 1.75+)

```rust
macro_rules! count_items {
    ($($item:expr),*) => {
        {
            // New in 2026
            let count = ${count($item)};
            println!("Got {} items", count);
        }
    };
}
```

### When to Use Declarative vs Procedural

| Criteria | Declarative | Procedural |
|----------|-------------|------------|
| Lines of code | < 150 | > 150 |
| Complexity | Simple patterns | Complex logic |
| Error messages | Basic | Rich, helpful |
| IDE support | Limited | Full |
| Debugging | cargo-expand | Step-through |
| Compile time | Fast | Slower |

---

## Procedural Derive Macros

**Use for**: Custom `#[derive]` implementations

### Setup

```toml
# Cargo.toml
[lib]
proc-macro = true

[dependencies]
syn = { version = "2.0", features = ["full"] }
quote = "1.0"
proc-macro2 = "1.0"
```

### Basic Derive

```rust
use proc_macro::TokenStream;
use quote::quote;
use syn::{parse_macro_input, DeriveInput};

#[proc_macro_derive(Builder)]
pub fn derive_builder(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    let name = &input.ident;
    let builder_name = format!("{}Builder", name);
    let builder_ident = syn::Ident::new(&builder_name, name.span());

    let expanded = quote! {
        impl #name {
            pub fn builder() -> #builder_ident {
                #builder_ident::default()
            }
        }

        #[derive(Default)]
        pub struct #builder_ident {
            // Fields would go here
        }
    };

    TokenStream::from(expanded)
}
```

### With Attributes

```rust
#[proc_macro_derive(Builder, attributes(builder))]
pub fn derive_builder(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);

    // Parse attributes
    for attr in &input.attrs {
        if attr.path().is_ident("builder") {
            // Handle #[builder(...)]
        }
    }

    // Generate code
    // ...
}

// Usage
#[derive(Builder)]
struct User {
    #[builder(default = "Unknown")]
    name: String,
}
```

### Error Handling

```rust
use syn::Error;

#[proc_macro_derive(MyDerive)]
pub fn my_derive(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);

    match generate_impl(&input) {
        Ok(tokens) => tokens.into(),
        Err(e) => e.to_compile_error().into(),
    }
}

fn generate_impl(input: &DeriveInput) -> syn::Result<proc_macro2::TokenStream> {
    if !matches!(input.data, syn::Data::Struct(_)) {
        return Err(Error::new_spanned(
            input,
            "MyDerive can only be derived for structs"
        ));
    }

    Ok(quote! { /* generated code */ })
}
```

---

## Procedural Attribute Macros

**Use for**: Modifying functions, structs, or modules

### Basic Attribute

```rust
use proc_macro::TokenStream;
use quote::quote;
use syn::{parse_macro_input, ItemFn};

#[proc_macro_attribute]
pub fn log_calls(attr: TokenStream, item: TokenStream) -> TokenStream {
    let input = parse_macro_input!(item as ItemFn);
    let fn_name = &input.sig.ident;
    let fn_block = &input.block;
    let sig = &input.sig;

    let expanded = quote! {
        #sig {
            println!("Calling {}", stringify!(#fn_name));
            let result = (|| #fn_block)();
            println!("Finished {}", stringify!(#fn_name));
            result
        }
    };

    TokenStream::from(expanded)
}

// Usage
#[log_calls]
fn my_function() {
    println!("Hello!");
}
```

### With Arguments

```rust
#[proc_macro_attribute]
pub fn timeout(attr: TokenStream, item: TokenStream) -> TokenStream {
    let timeout_ms: u64 = parse_macro_input!(attr as syn::LitInt)
        .base10_parse()
        .unwrap();

    let input = parse_macro_input!(item as ItemFn);

    let expanded = quote! {
        #[tokio::time::timeout(std::time::Duration::from_millis(#timeout_ms))]
        #input
    };

    TokenStream::from(expanded)
}

// Usage
#[timeout(5000)]
async fn fetch_data() { /* ... */ }
```

---

## Procedural Function-Like Macros

**Use for**: Custom DSLs, complex code generation

### Basic Function-Like

```rust
use proc_macro::TokenStream;
use quote::quote;
use syn::parse::{Parse, ParseStream};

struct SqlQuery {
    query: String,
}

impl Parse for SqlQuery {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let query: syn::LitStr = input.parse()?;
        Ok(SqlQuery {
            query: query.value(),
        })
    }
}

#[proc_macro]
pub fn sql(input: TokenStream) -> TokenStream {
    let SqlQuery { query } = parse_macro_input!(input as SqlQuery);

    // Validate SQL at compile time
    // Generate code
    let expanded = quote! {
        {
            let query = #query;
            Query::new(query)
        }
    };

    TokenStream::from(expanded)
}

// Usage
let q = sql!("SELECT * FROM users WHERE id = ?");
```

---

## Testing Macros

### Unit Testing with trybuild

```rust
// tests/ui/pass/simple.rs
use my_macro::MyDerive;

#[derive(MyDerive)]
struct Simple {
    field: i32,
}

fn main() {}

// tests/ui.rs
#[test]
fn ui() {
    let t = trybuild::TestCases::new();
    t.pass("tests/ui/pass/*.rs");
    t.compile_fail("tests/ui/fail/*.rs");
}
```

### Compile-Fail Tests

```rust
// tests/ui/fail/not_a_struct.rs
use my_macro::MyDerive;

#[derive(MyDerive)]  // Should fail
enum NotAStruct {
    A,
    B,
}

fn main() {}

// tests/ui/fail/not_a_struct.stderr (expected output)
error: MyDerive can only be derived for structs
 --> tests/ui/fail/not_a_struct.rs:4:10
  |
4 | #[derive(MyDerive)]
  |          ^^^^^^^^
```

---

## Best Practices

### 1. Error Messages

```rust
// ❌ BAD: Vague error
return Err(Error::new_spanned(&field, "invalid field"));

// ✅ GOOD: Specific, actionable
return Err(Error::new_spanned(
    &field,
    format!(
        "field `{}` must have type `String`, found `{}`",
        field_name,
        field_type
    )
));
```

### 2. Span Preservation

```rust
// Preserve spans for IDE support (go-to-definition, errors)
let field_name = &field.ident;  // Keep original span
quote! {
    pub fn #field_name(&self) -> &#field_ty {
        &self.#field_name
    }
}
```

### 3. Documentation

```rust
/// Derives a builder pattern for the struct.
///
/// # Example
///
/// ```
/// #[derive(Builder)]
/// struct User {
///     name: String,
///     age: u32,
/// }
///
/// let user = User::builder()
///     .name("Alice")
///     .age(30)
///     .build();
/// ```
#[proc_macro_derive(Builder)]
pub fn derive_builder(input: TokenStream) -> TokenStream {
    // ...
}
```

### 4. Use darling for Attributes

```rust
use darling::FromDeriveInput;

#[derive(FromDeriveInput)]
#[darling(attributes(builder))]
struct BuilderOpts {
    ident: syn::Ident,
    #[darling(default)]
    name: Option<String>,
}

#[proc_macro_derive(Builder, attributes(builder))]
pub fn derive_builder(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    let opts = BuilderOpts::from_derive_input(&input).unwrap();
    // ...
}
```

### 5. Keep Macros Focused

```rust
// ❌ BAD: One macro does everything
#[derive(Everything)]  // Generates builders, serialization, validation, etc.

// ✅ GOOD: Focused, composable macros
#[derive(Builder, Serialize, Validate)]
```

## Common Patterns from Popular Crates

### serde

- Attribute parsing with darling
- Field visitors
- Generic handling
- Compile-time format selection

### tokio

- Function transformation (#[tokio::main], #[tokio::test])
- Async block rewriting
- Runtime configuration

### thiserror

- Error message formatting
- From implementations
- Display implementations

## Tools

- **cargo-expand**: View macro expansion
- **rust-analyzer**: IDE support
- **trybuild**: Compile-fail testing
- **darling**: Attribute parsing
- **syn**: AST parsing
- **quote**: Code generation

## Further Reading

- [The Little Book of Rust Macros](https://danielkeep.github.io/tlborm/book/)
- [Procedural Macros Workshop](https://github.com/dtolnay/proc-macro-workshop)
- [syn Documentation](https://docs.rs/syn/)
- [quote Documentation](https://docs.rs/quote/)

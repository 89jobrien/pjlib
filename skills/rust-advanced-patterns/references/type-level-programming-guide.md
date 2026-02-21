# Type-Level Programming Guide

Comprehensive guide to Rust type-level programming patterns for 2026.

## Table of Contents

1. [Newtype Pattern](#newtype-pattern)
2. [Type-State Pattern](#type-state-pattern)
3. [Phantom Types](#phantom-types)
4. [Const Generics](#const-generics)
5. [Zero-Sized Types (ZSTs)](#zero-sized-types-zsts)
6. [Type-Level State Machines](#type-level-state-machines)

---

## Newtype Pattern

**Purpose**: Create type-safe wrappers with zero runtime cost

### Basic Pattern

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct UserId(u64);

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct OrderId(u64);

// Cannot accidentally mix IDs
fn get_user(id: UserId) -> User { /*...*/ }
// get_user(OrderId(123));  // Compile error!

// Zero overhead
assert_eq!(size_of::<UserId>(), size_of::<u64>());
```

### With Validation (Smart Constructor)

```rust
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Email(String);

impl Email {
    pub fn new(s: impl Into<String>) -> Result<Self, ValidationError> {
        let email = s.into();
        if email.contains('@') && email.contains('.') {
            Ok(Self(email))
        } else {
            Err(ValidationError::InvalidEmail)
        }
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }
}

// Cannot create invalid emails
let email = Email::new("test@example.com")?;
```

### Ergonomics with Deref

```rust
use std::ops::Deref;

impl Deref for Email {
    type Target = str;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

// Now Email can be used like &str
let email = Email::new("test@example.com")?;
assert!(email.contains('@'));  // Uses Deref
println!("Length: {}", email.len());  // Uses Deref
```

### Units of Measure

```rust
#[derive(Debug, Clone, Copy)]
pub struct Meters(f64);

#[derive(Debug, Clone, Copy)]
pub struct Feet(f64);

impl Meters {
    pub fn to_feet(self) -> Feet {
        Feet(self.0 * 3.28084)
    }
}

impl Feet {
    pub fn to_meters(self) -> Meters {
        Meters(self.0 / 3.28084)
    }
}

// Type-safe conversions
let m = Meters(100.0);
let ft = m.to_feet();
```

---

## Type-State Pattern

**Purpose**: Enforce state machine transitions at compile time

### Basic Pattern

```rust
use std::marker::PhantomData;

// State markers
pub struct Open;
pub struct Closed;

pub struct Connection<State> {
    socket: TcpStream,
    _state: PhantomData<State>,
}

impl Connection<Closed> {
    pub fn new(addr: &str) -> io::Result<Self> {
        Ok(Connection {
            socket: TcpStream::connect(addr)?,
            _state: PhantomData,
        })
    }

    pub fn open(self) -> Connection<Open> {
        Connection {
            socket: self.socket,
            _state: PhantomData,
        }
    }
}

impl Connection<Open> {
    pub fn send(&mut self, data: &[u8]) -> io::Result<()> {
        self.socket.write_all(data)
    }

    pub fn close(self) -> Connection<Closed> {
        Connection {
            socket: self.socket,
            _state: PhantomData,
        }
    }
}

// Usage enforces state machine
let conn = Connection::new("127.0.0.1:8080")?;
// conn.send(b"data");  // ❌ Cannot send on Closed connection
let mut conn = conn.open();
conn.send(b"data")?;  // ✅ OK
let conn = conn.close();
```

### Zero Overhead

```rust
// All states have same size
assert_eq!(
    size_of::<Connection<Open>>(),
    size_of::<Connection<Closed>>()
);

// PhantomData is zero-sized
assert_eq!(size_of::<PhantomData<Open>>(), 0);
```

### Builder Pattern with Type-State

```rust
pub struct Unset;
pub struct Set;

pub struct RequestBuilder<Url, Method, Body> {
    url: Option<String>,
    method: Option<String>,
    body: Option<String>,
    _url: PhantomData<Url>,
    _method: PhantomData<Method>,
    _body: PhantomData<Body>,
}

impl RequestBuilder<Unset, Unset, Unset> {
    pub fn new() -> Self {
        Self {
            url: None,
            method: None,
            body: None,
            _url: PhantomData,
            _method: PhantomData,
            _body: PhantomData,
        }
    }
}

impl<Method, Body> RequestBuilder<Unset, Method, Body> {
    pub fn url(self, url: String) -> RequestBuilder<Set, Method, Body> {
        RequestBuilder {
            url: Some(url),
            method: self.method,
            body: self.body,
            _url: PhantomData,
            _method: self._method,
            _body: self._body,
        }
    }
}

// Only allow build when all required fields are set
impl RequestBuilder<Set, Set, Set> {
    pub fn build(self) -> Request {
        Request {
            url: self.url.unwrap(),
            method: self.method.unwrap(),
            body: self.body.unwrap(),
        }
    }
}

// Cannot compile without all required fields
let req = RequestBuilder::new()
    .url("https://api.example.com".into())
    .method("POST".into())
    .body("data".into())
    .build();  // ✅ OK

// let req = RequestBuilder::new().build();  // ❌ Compile error!
```

---

## Phantom Types

**Purpose**: Type-level markers with zero runtime cost

### Type-Safe Identifiers

```rust
use std::marker::PhantomData;

pub struct Id<T> {
    value: u64,
    _marker: PhantomData<T>,
}

pub struct User;
pub struct Order;

type UserId = Id<User>;
type OrderId = Id<Order>;

fn get_user(id: UserId) -> User { /*...*/ }
fn get_order(id: OrderId) -> Order { /*...*/ }

// Cannot mix IDs
let user_id = UserId { value: 1, _marker: PhantomData };
let order_id = OrderId { value: 1, _marker: PhantomData };
// get_user(order_id);  // ❌ Type error!
```

### Units of Measure (Type-Level)

```rust
pub struct Meters;
pub struct Feet;

pub struct Distance<Unit> {
    value: f64,
    _unit: PhantomData<Unit>,
}

impl Distance<Meters> {
    pub fn meters(value: f64) -> Self {
        Self { value, _unit: PhantomData }
    }

    pub fn to_feet(self) -> Distance<Feet> {
        Distance {
            value: self.value * 3.28084,
            _unit: PhantomData,
        }
    }
}

// Type-safe conversions
let d = Distance::meters(100.0);
let d_feet = d.to_feet();
```

### Sanitized vs Unsanitized

```rust
pub struct Sanitized;
pub struct Unsanitized;

pub struct Html<State> {
    content: String,
    _state: PhantomData<State>,
}

impl Html<Unsanitized> {
    pub fn new(content: String) -> Self {
        Self { content, _state: PhantomData }
    }

    pub fn sanitize(self) -> Html<Sanitized> {
        Html {
            content: sanitize_html(&self.content),
            _state: PhantomData,
        }
    }
}

impl Html<Sanitized> {
    pub fn render(&self) -> &str {
        &self.content
    }
}

// Only sanitized HTML can be rendered
let html = Html::new("<script>alert('xss')</script>".into());
// html.render();  // ❌ Cannot render unsanitized
let safe = html.sanitize();
safe.render();  // ✅ OK
```

---

## Const Generics

**Purpose**: Compile-time value parameterization

**Stabilized**: Rust 1.51 (March 2021)
**Enhanced**: Const generics in impl blocks (Rust 1.59, Feb 2022)

### Fixed-Size Arrays

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

    pub fn len(&self) -> usize {
        SIZE  // Compile-time constant
    }
}

// Different sizes are different types
let buf1: Buffer<u8, 1024> = Buffer::new();
let buf2: Buffer<u8, 2048> = Buffer::new();
// buf1 and buf2 are different types!
```

### Matrix Arithmetic (Compile-Time Dimension Checking)

```rust
struct Matrix<T, const ROWS: usize, const COLS: usize> {
    data: [[T; COLS]; ROWS],
}

impl<T: Default + Copy, const ROWS: usize, const COLS: usize>
    Matrix<T, ROWS, COLS>
{
    pub fn new() -> Self {
        Self {
            data: [[T::default(); COLS]; ROWS],
        }
    }
}

impl<T, const N: usize, const M: usize, const P: usize> Matrix<T, N, M>
where
    T: Copy + std::ops::Add<Output = T> + std::ops::Mul<Output = T> + Default,
{
    pub fn multiply(&self, other: &Matrix<T, M, P>) -> Matrix<T, N, P> {
        // Matrix multiplication
        // Dimensions checked at compile time!
        todo!()
    }
}

// Compile-time dimension checking
let a: Matrix<f64, 2, 3> = Matrix::new();
let b: Matrix<f64, 3, 4> = Matrix::new();
let c = a.multiply(&b);  // Result is Matrix<f64, 2, 4>
// let d = b.multiply(&a);  // ❌ Compile error! Dimension mismatch
```

### Generic Constants (Rust 1.79+)

```rust
// Can now use const generics in more places
const fn double<const N: usize>() -> usize {
    N * 2
}

struct Pair<T, const SIZE: usize> {
    first: [T; SIZE],
    second: [T; double::<SIZE>()],  // Uses const fn!
}
```

---

## Zero-Sized Types (ZSTs)

**Purpose**: Type-level markers with literally zero runtime cost

### Capability Tokens

```rust
pub struct CanRead;
pub struct CanWrite;

pub struct File<Perms> {
    handle: std::fs::File,
    _perms: PhantomData<Perms>,
}

impl File<CanRead> {
    pub fn read(&self) -> io::Result<Vec<u8>> {
        // Read implementation
        todo!()
    }
}

impl File<CanWrite> {
    pub fn write(&self, data: &[u8]) -> io::Result<()> {
        // Write implementation
        todo!()
    }
}

// Zero overhead
assert_eq!(size_of::<File<CanRead>>(), size_of::<std::fs::File>());
assert_eq!(size_of::<PhantomData<CanRead>>(), 0);
```

### Marker Traits

```rust
// ZST markers for different behaviors
pub struct Sync;
pub struct Async;

pub struct Client<Mode> {
    conn: Connection,
    _mode: PhantomData<Mode>,
}

impl Client<Sync> {
    pub fn request(&self, req: Request) -> Response {
        // Synchronous implementation
        todo!()
    }
}

impl Client<Async> {
    pub async fn request(&self, req: Request) -> Response {
        // Asynchronous implementation
        todo!()
    }
}
```

---

## Type-Level State Machines

**Purpose**: Encode protocols and workflows at type level

### HTTP Request State Machine

```rust
pub struct NoMethod;
pub struct Get;
pub struct Post;

pub struct NoUrl;
pub struct HasUrl;

pub struct HttpRequest<Method, Url> {
    url: Option<String>,
    method: Option<&'static str>,
    headers: HashMap<String, String>,
    body: Option<String>,
    _method: PhantomData<Method>,
    _url: PhantomData<Url>,
}

impl HttpRequest<NoMethod, NoUrl> {
    pub fn new() -> Self {
        Self {
            url: None,
            method: None,
            headers: HashMap::new(),
            body: None,
            _method: PhantomData,
            _url: PhantomData,
        }
    }
}

impl<Url> HttpRequest<NoMethod, Url> {
    pub fn get(mut self) -> HttpRequest<Get, Url> {
        self.method = Some("GET");
        HttpRequest {
            url: self.url,
            method: self.method,
            headers: self.headers,
            body: self.body,
            _method: PhantomData,
            _url: PhantomData,
        }
    }

    pub fn post(mut self) -> HttpRequest<Post, Url> {
        self.method = Some("POST");
        HttpRequest {
            url: self.url,
            method: self.method,
            headers: self.headers,
            body: self.body,
            _method: PhantomData,
            _url: PhantomData,
        }
    }
}

impl<Method> HttpRequest<Method, NoUrl> {
    pub fn url(mut self, url: String) -> HttpRequest<Method, HasUrl> {
        self.url = Some(url);
        HttpRequest {
            url: self.url,
            method: self.method,
            headers: self.headers,
            body: self.body,
            _method: self._method,
            _url: PhantomData,
        }
    }
}

// Can only send when both method and URL are set
impl HttpRequest<Get, HasUrl> {
    pub async fn send(self) -> Result<Response, Error> {
        // Send GET request
        todo!()
    }
}

impl HttpRequest<Post, HasUrl> {
    pub fn body(mut self, body: String) -> Self {
        self.body = Some(body);
        self
    }

    pub async fn send(self) -> Result<Response, Error> {
        // Send POST request
        todo!()
    }
}

// Usage - compile-time enforced
let resp = HttpRequest::new()
    .get()
    .url("https://api.example.com".into())
    .send()
    .await?;

let resp = HttpRequest::new()
    .post()
    .url("https://api.example.com".into())
    .body(r#"{"key": "value"}"#.into())
    .send()
    .await?;

// These won't compile:
// HttpRequest::new().send();  // ❌ No method or URL
// HttpRequest::new().get().send();  // ❌ No URL
```

---

## Best Practices

### 1. Prefer Type-Level Safety

```rust
// ❌ BAD: Runtime checks
struct Connection {
    is_open: bool,
}

impl Connection {
    fn send(&self, data: &[u8]) {
        assert!(self.is_open, "Connection not open");
        // ...
    }
}

// ✅ GOOD: Compile-time checks
struct Connection<State> { _state: PhantomData<State> }
impl Connection<Open> {
    fn send(&self, data: &[u8]) { /* ... */ }
}
```

### 2. Use Smart Constructors

```rust
// Always validate in constructor
impl Email {
    pub fn new(s: impl Into<String>) -> Result<Self, Error> {
        // Validate
        Ok(Self(s.into()))
    }

    // Keep inner value private
    fn as_str(&self) -> &str {
        &self.0
    }
}
```

### 3. Zero-Cost Guarantee

```rust
// Always verify zero overhead
assert_eq!(size_of::<Newtype>(), size_of::<Inner>());
assert_eq!(size_of::<PhantomData<T>>(), 0);
```

### 4. Don't Over-Engineer

```rust
// ❌ TOO MUCH: 10+ type parameters
struct Connection<Auth, Tls, Compress, Timeout, ...> { /* ... */ }

// ✅ REASONABLE: 1-3 type parameters
struct Connection<State> { /* ... */ }
```

---

## Real-World Examples

### Diesel (SQL Type Safety)

```rust
users::table
    .filter(users::id.eq(1))
    .select(users::name)
    .load::<String>(&conn)?;
// All type-checked at compile time!
```

### Tokio (Task State)

```rust
let task = tokio::spawn(async { /* ... */ });
// task has type JoinHandle<T>
```

### std::marker::PhantomData

```rust
pub struct Vec<T> {
    ptr: *mut T,
    len: usize,
    cap: usize,
    _marker: PhantomData<T>,  // For drop checker
}
```

---

## Performance Guarantees

All patterns in this guide are **zero-cost**:

| Pattern | Runtime Overhead |
|---------|------------------|
| Newtype | 0 bytes |
| Type-State | 0 bytes (PhantomData) |
| Phantom Types | 0 bytes |
| Const Generics | 0 bytes (compile-time) |
| ZSTs | 0 bytes (literally) |

```rust
// Proof
assert_eq!(size_of::<UserId>(), size_of::<u64>());
assert_eq!(size_of::<Connection<Open>>(), size_of::<TcpStream>());
assert_eq!(size_of::<PhantomData<T>>(), 0);
assert_eq!(size_of::<Buffer<u8, 1024>>(), 1024);
```

---

## Further Reading

- [Rust Book: Advanced Types](https://doc.rust-lang.org/book/ch19-04-advanced-types.html)
- [Const Generics MVP](https://blog.rust-lang.org/2021/02/26/const-generics-mvp-beta.html)
- [PhantomData Documentation](https://doc.rust-lang.org/std/marker/struct.PhantomData.html)
- [Type-State Pattern](https://cliffle.com/blog/rust-typestate/)

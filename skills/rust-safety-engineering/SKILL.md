---
name: rust-safety-engineering
description: Comprehensive Rust safety engineering covering unsafe code auditing, Miri verification, safety invariants, GhostCell patterns, and CI/CD safety pipeline integration
---

# Rust Safety Engineering

Use this skill when auditing Rust code for safety, reviewing unsafe code, or setting up comprehensive safety verification workflows.

## When to Use This Skill

**Use PROACTIVELY when:**
- Reviewing code with unsafe blocks
- Setting up CI/CD for Rust projects
- Auditing memory safety in existing codebases
- Implementing critical systems requiring high assurance
- Encountering undefined behavior or memory corruption

**Use when users request:**
- Safety audits or security reviews
- Unsafe code verification
- Miri or safety tooling setup
- Help with memory safety patterns

## Core Safety Principles (2026)

### 1. Unsafe Code Guidelines

**Target**: Keep unsafe code under 5% of codebase

**Required for every unsafe block:**
- Document ALL safety invariants with `SAFETY:` comments
- Keep blocks minimal (< 10 lines)
- Provide safe wrapper functions
- Test with Miri and cargo-careful

**Example:**
```rust
/// Creates a new Widget from raw parts
///
/// # Safety
///
/// - `ptr` must be valid for reads of `len` bytes
/// - `ptr` must point to `len` consecutive properly initialized values
/// - The memory referenced by `ptr` must not be accessed through any other pointer
/// - `len` must not exceed `isize::MAX`
pub unsafe fn from_raw_parts(ptr: *const u8, len: usize) -> Self {
    // SAFETY: Caller guarantees ptr is valid for len bytes
    let slice = unsafe { std::slice::from_raw_parts(ptr, len) };
    Self { data: slice.to_vec() }
}
```

### 2. Safety Verification Workflow

Run this workflow for all unsafe code:

1. **Document** - Write SAFETY comments explaining invariants
2. **Test** - Write tests covering all edge cases
3. **Miri** - Run Miri to detect undefined behavior
4. **Review** - Manual code review of unsafe blocks
5. **Monitor** - Track unsafe code percentage in CI/CD

### 3. Advanced Safety Patterns

For detailed patterns, load **`references/advanced-safety-patterns.md`** which covers:
- GhostCell for zero-cost interior mutability
- Branded indices for compile-time safety
- Generative lifetimes for safe arena allocation
- Session types for protocol correctness

### 4. Safety Tooling Stack

**Essential (run in CI/CD):**
- **Clippy** with `pedantic` and `nursery` lints
- **Miri** for undefined behavior detection (on unsafe code)
- **cargo-careful** for strict validity checks
- **ASan** for runtime memory error detection

**Advanced (critical systems):**
- **Prusti** for formal verification
- **Loom** for concurrency testing
- **Kani** for bounded model checking

Load **`references/safety-tooling-setup.md`** for complete configuration.

### 5. Unsafe Code Audit Checklist

When auditing unsafe code, check:

- [ ] All unsafe blocks documented with SAFETY comments
- [ ] Unsafe blocks are minimal (<10 lines)
- [ ] Safe wrapper functions provided
- [ ] All pointer dereferences validated
- [ ] Lifetime requirements documented
- [ ] Aliasing rules respected
- [ ] Send/Sync bounds correct
- [ ] Tested with Miri (zero failures)
- [ ] No panics in unsafe code
- [ ] Unsafe percentage <5% of codebase

Load **`references/audit-checklist.md`** for complete checklist.

## Safety Decision Matrix

| Scenario | Recommendation | Pattern |
|----------|---------------|---------|
| Shared mutable state (single-thread) | Avoid if possible, use RefCell if needed | Interior mutability |
| Shared mutable state (multi-thread) | Use Mutex/RwLock or message passing | Synchronization |
| Zero-cost interior mutability | Use GhostCell | Advanced pattern |
| FFI boundary | Validate all inputs, document invariants | Unsafe required |
| Performance-critical section | Profile first, use unsafe only if necessary | Optimization |
| Memory-mapped I/O | Use unsafe with careful validation | Systems programming |

## Common Safety Anti-Patterns

**Never do this:**

```rust
// ❌ Undocumented unsafe
unsafe {
    *ptr = value;
}

// ❌ Large unsafe blocks
unsafe {
    // 50 lines of code...
}

// ❌ Panic in unsafe code
unsafe {
    assert!(condition); // Can leave invariants violated
}

// ❌ Unchecked transmute
unsafe {
    std::mem::transmute::<T, U>(value) // Without size check
}
```

**Do this instead:**

```rust
// ✅ Documented, minimal, safe wrapper
/// # Safety
///
/// `ptr` must be valid and properly aligned
unsafe fn write_value(ptr: *mut i32, value: i32) {
    // SAFETY: Caller guarantees ptr is valid
    unsafe { *ptr = value; }
}

pub fn safe_write(ptr: &mut i32, value: i32) {
    unsafe { write_value(ptr as *mut i32, value); }
}
```

## Implementation Workflow

### Phase 1: Assessment (Week 1)
1. Grep for `unsafe` blocks in codebase
2. Count unsafe percentage
3. Identify undocumented unsafe code
4. Set up safety tooling

### Phase 2: Documentation (Week 2)
1. Add SAFETY comments to all unsafe blocks
2. Document safety invariants
3. Write tests for unsafe code
4. Run Miri on tests

### Phase 3: Verification (Week 3-4)
1. Run cargo-careful in CI/CD
2. Enable ASan for testing
3. Review all unsafe code manually
4. Consider Prusti for critical sections

### Phase 4: Monitoring (Ongoing)
1. Track unsafe percentage
2. Require safety review for new unsafe code
3. Run Miri on PR builds
4. Periodic safety audits

## Reference Files

This skill includes detailed references:

- **`references/advanced-safety-patterns.md`** - GhostCell, branded indices, generative lifetimes, session types
- **`references/safety-tooling-setup.md`** - Complete CI/CD configuration for all safety tools
- **`references/audit-checklist.md`** - Comprehensive safety audit checklist
- **`references/memory-safety-patterns.md`** - Smart pointer selection, ownership patterns, lifetime management
- **`references/ffi-safety.md`** - Safe FFI patterns and validation

Load these files when you need detailed implementation guidance beyond the quick reference above.

## Success Metrics

- Unsafe code < 5% of codebase
- Zero Clippy warnings (pedantic)
- Zero Miri failures
- All unsafe blocks documented
- Safety tooling in CI/CD
- Regular safety audits scheduled

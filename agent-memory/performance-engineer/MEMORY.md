# Performance Engineer Memory

## Recent Analyses

### DevLoop Performance Analysis (2026-03-15)
See: [DEVLOOP_PERFORMANCE_ANALYSIS.md](/Users/joe/dev/devloop/DEVLOOP_PERFORMANCE_ANALYSIS.md)

**Project:** Rust TUI CLI with AI-powered git analysis and event aggregation
- Codebase: 38,263 LOC Rust (174 files), 9 workspace crates
- Binary: 6.8 MB, excellent architecture (hexagonal, trait-based DI)
- Status: B+ (good baseline), 4 critical bottlenecks, 30-40% improvement available

**Critical Findings:**
1. EDDOS 10μs sleep per event (HIGH): Limits throughput to 10-20K/sec (claims 50K+)
   - Fix: Remove artificial sleep (2h, 10x throughput improvement)
2. Council string cloning (HIGH): 200KB+ clones per role, 1MB in extensive mode
   - Fix: Use Arc<str> for shared data (1h, 10-15% faster, 80% less alloc)
3. TUI polling too slow (MEDIUM UX): 100ms = 10 FPS, feels sluggish
   - Fix: Adaptive polling (30m, 6x more responsive during streaming)
4. Git watcher subprocess (MEDIUM): Spawns `git rev-parse` for every commit
   - Fix: Use git2 crate (2h, 20-100x faster commit lookup)

**Architecture Strengths:**
- Hexagonal architecture with clean domain boundaries
- LRU cache with TTL (production-ready, just needs default enable)
- Parallel council execution with progressive synthesis
- Generic EDDOS pipeline (MPSC → Semaphore → Batching → Broadcast)
- Graceful degradation (2+ roles required, continues on partial failure)

**Optimization Roadmap:**
- Phase 1 (8h): Remove sleep, Arc clones, adaptive TUI, git2 → 30-40% faster
- Phase 2 (6h): Metrics, benchmarks, buffer tuning → +10-15%
- Phase 3 (22h): Streaming BAML, lazy loading, PGO → +5-10%

**Performance Budget:**
- EDDOS throughput: 50K+ events/sec (currently ~10K due to sleep)
- Council core: <20s (currently 15-25s, close)
- Council extensive: <40s (currently 30-45s, close)
- TUI: 60 FPS during streaming (currently 10 FPS)
- Memory idle: ~15 MB (excellent), streaming: 80-120 MB (good)

**Common Rust Performance Patterns:**
- Adaptive polling for TUI: 16ms streaming, 8ms active, 50ms idle
- Arc<str> for shared read-only data (vs String clones)
- Pre-allocate String::with_capacity for formatters
- Semaphore for bounded concurrency (EDDOS: 100 concurrent)
- FuturesUnordered for progressive async collection
- LRU + TTL for production caching

## Recent Analyses

### Minibox Container Runtime Performance Analysis (2026-03-15)
See: [PERFORMANCE_ANALYSIS.md](/Users/joe/dev/minibox/PERFORMANCE_ANALYSIS.md)

**Project:** Docker-like container runtime in Rust (daemon/client architecture)
- Codebase: 2,059 LOC Rust (23 files), 3,212 total
- Status: Good baseline (B+), competitive with Docker/Podman
- Quick wins: 30-40% startup improvement, 8 hours effort

**Critical Findings:**
1. Sequential layer downloads (HIGH): 5-layer image takes 5x single-layer latency
   - Fix: Concurrent tokio::spawn downloads (2h, 3-5x faster pulls)
2. spawn_blocking contention (HIGH): Limited to 512 concurrent container starts
   - Fix: Dedicated rayon thread pool (2h, eliminates P99 spikes)
3. daemon_wait_for_exit creates runtime (MEDIUM): 5-10ms overhead + 500KB allocation
   - Fix: Use channel for state updates (30m, zero allocations)
4. Stop polling instead of event-driven (MEDIUM): 250ms poll wastes CPU
   - Fix: Use existing waitpid in background task (1h, 125ms avg latency reduction)

**Architecture Strengths:**
- Proper async/sync separation (tokio for I/O, blocking for fork/clone)
- Minimal allocations in hot paths (~360 bytes per container)
- Efficient Unix socket protocol (newline-delimited JSON, <100μs overhead)
- Layer caching prevents redundant downloads

**Optimization Roadmap:**
- Phase 1 (8h): Concurrent downloads, thread pool, async tar → 30-40% faster
- Phase 2 (10h): State persistence, LRU eviction → prevents resource leaks
- Phase 3 (20h): Sharded state, streaming layers → 10x write scalability

**Performance Comparison (Container Startup):**
- Minibox (current): 65ms
- Minibox (Phase 1): 45ms
- Docker: 80-120ms
- Podman: 60-100ms
**Verdict:** Already competitive, Phase 1 makes it best-in-class

**Common Container Runtime Patterns:**
- Pre-warmed overlay mounts avoid 20-50ms setup overhead
- Dedicated thread pool for fork/clone prevents executor blocking
- Event-driven process reaping (waitpid) beats polling
- HTTP connection pooling critical for multi-layer pulls
- State persistence prevents orphaned mounts on daemon restart

### DevLoop Performance Analysis (2026-03-13)
See: [devloop-performance-analysis.md](devloop-performance-analysis.md)

**Project:** Rust TUI CLI with AI-powered git analysis
- Binary: 4.4MB, ~13.6K LOC Rust (CLI), 20.5K total
- Status: Good baseline, well-architected, medium-impact optimizations available
- Quick wins: 20-30% improvement, ~4 hours effort

**Critical Findings:**
1. GKG adapter uses `block_in_place` (HIGH): blocks tokio threads on async HTTP
   - Fix: Migrate domain traits to async_trait (2h, 10-20% faster)
2. Council analysis clones 200KB+ strings per role (MEDIUM): 1MB wasted in extensive mode
   - Fix: Use Arc<str> for shared read-only data (1h, 10-15% faster)
3. TUI polls at 50-100ms (MEDIUM UX): feels sluggish during streaming
   - Fix: 16ms when streaming, 8ms when typing (30min, 6x more responsive)
4. Timeline formatter allocates ~300 times per analysis (MEDIUM)
   - Fix: Pre-allocate String capacity (1h, 60% fewer allocations)

**Architecture Strengths:**
- Excellent LRU caching with TTL (production-ready)
- Council roles execute in parallel (optimal)
- Channel buffering (100-msg buffer, prevents backpressure)
- Progressive synthesis (doesn't wait for all roles)
- Graceful degradation (continues if 2+ roles succeed)

**Optimization Roadmap:**
- Phase 1 (4h): TUI polling, formatter pre-allocation, Arc clones → 20-30%
- Phase 2 (8h): Async traits, parallel formatting, caching → +15-20%
- Phase 3 (5d): Streaming results, lazy loading, PGO → +10-15%
- Total potential: 45-65% faster, perceived 2x during streaming

## Maestro Performance Analysis (2026-03-07)

### Key Findings

**Current Performance:**
- Test execution: 2,910 tests in ~8s (364 tests/sec) - excellent
- CI pipeline: 12-13 minutes total (well-optimized)
- Code coverage: 92.54% (automated enforcement)
- Codebase: 183,644 lines of Rust across 403 files

**Performance Characteristics:**
- Intelligent test parallelization with nextest
- Docker layer caching optimized
- Coverage collected during test runs (no duplicate execution)
- Resource profiles from minimal (128Mi) to production (16Gi)

### Quick Wins Identified

1. **Docker Registry Pull-Through Cache**: 2-3 min CI savings, minimal effort
2. **Increase K8s Test Concurrency**: 30-40% reduction in K8s test time
3. **Pre-Pull Common Images**: Eliminate 1-2 min image pull overhead

**Combined Impact:** Reduce CI from 13 min to ~8-9 min (30% improvement)

### Bottlenecks

**Critical Path:** E2E tests (25 min per shard)
- Infrastructure setup: 2.5 min fixed overhead
- K3d cluster + Docker images + n8n setup
- Test execution: 20 min for 19 tests

**Secondary Issues:**
- Docker operations slow under parallel load (5s → 60s startup)
- K8s tests limited to 2 concurrent threads (underutilizing 8-core runners)
- Coverage instrumentation adds 20-30% overhead

### Performance Budgets Recommended

| Metric | Target | Ceiling |
|--------|--------|---------|
| CI Total Time | 10 min | 20 min |
| Unit Tests | 5 min | 10 min |
| E2E Tests (per shard) | 20 min | 35 min |
| Container Startup | 3s | 10s |
| Test Count | 3,000 | 5,000 |

### Test Organization Pattern

```
tests/
├── unit/    → binary(unit)   - Fast unit tests
├── docker/  → binary(docker) - Docker integration
├── k8s/     → binary(k8s)    - Kubernetes integration
└── remote/  → binary(remote) - Remote mode tests
```

Benefits: Selective execution, independent timeouts, controlled concurrency

### Build Optimization Patterns

**Workspace Dependencies:**
- All deps defined at workspace level (single resolution)
- Shared artifacts across crates
- Consistent versions

**Profile Optimization:**
```toml
[profile.dev.package.sha2]
opt-level = 2  # Crypto 80x faster, prevents 5s+ delays

[profile.dist]
lto = "thin"   # 10-20% size reduction, minimal compile cost
```

**Docker Layer Strategy:**
1. Dependencies (changes rarely) → cached layer
2. Source code (changes frequently) → separate layer
3. Fingerprint invalidation for correctness

### Nextest Configuration Insights

**Test Groups for Concurrency Control:**
```toml
k8s-limited = { max-threads = 2 }  # Prevent cluster contention
serial-db = { max-threads = 1 }     # Avoid env var races
```

**Timeout Scaling:**
- Unit: 15s base, 45s terminate (3x)
- Docker: 45s base, 270s terminate (6x)
- K8s: 90s base, 540s terminate (6x)
- E2E: 90s base, 540s terminate (6x)

Accounts for coverage instrumentation and CI DooD environment

### CI Architecture Pattern

**Maximum Parallelism:**
```
Independent Jobs (time 0):
├── Lint (~3.5 min)
├── Unit tests (~7 min, 8-core)
├── Build binary (~3-5 min, 8-core, shared artifact)
└── Database tests (~3 min)

After build:
├── Docker: 2 shards (~6-7 min each)
└── K8s: 4 shards, LPT bin-packing (~8 min each)

Final:
└── Merge coverage (<1 min)
```

**Key Optimizations:**
1. Lint/unit don't wait for build
2. Coverage during test runs (not separate)
3. Build binary once, share across shards
4. 8-core runners for coverage builds
5. Intelligent sharding (manual + LPT algorithm)

### Resource Profiles (K8s)

| Profile | CPU | Memory | Storage | Use Case |
|---------|-----|--------|---------|----------|
| e2e-minimal | 50m | 128Mi | 100Mi | CI testing |
| development | 250m-2 | 512Mi-4Gi | 1-10Gi | Local dev |
| production | 1-8 | 2-16Gi | 5-40Gi | Production |

### Container Performance

**Prebuild System:**
- Shifts Claude Code install from startup to build time
- 60s cold start → 5s prebuilt startup
- SHA-256 cache key (binary + version + config)

**Image Layer Optimization:**
```dockerfile
# Order by change frequency (least to most)
RUN [apt packages]          # Rarely changes
RUN [Google Cloud SDK]      # Rarely changes
RUN [jira-cli]             # Rarely changes
USER vscode
RUN [Claude Code]          # Changes on version bump
```

### Monitoring Recommendations

**Key Metrics:**
- ci_total_duration (p50, p95)
- test_throughput (tests/sec)
- cache_hit_rate (percentage)
- slow_test_count (>10s tests)
- flaky_test_rate (percentage)

**Alert Thresholds:**
- CI >20 min: Critical
- Cache hit <70%: Warning
- Flaky rate >5%: Critical
- Slow tests >50: Warning

### Cost-Benefit Analysis

**Quick wins investment:** 4 hours engineering
**Benefit:** 30% CI time reduction
**ROI:** 750% (pays for itself in <1 week)

At 100 CI runs/week:
- 13 min → 9 min = 4 min saved per run
- 400 min/week = 6.7 hours/week saved
- 27 hours/month for 4 hours investment

### Common Patterns

**Cargo Lock Philosophy:**
- Checked into version control (produces binaries)
- Enables reproducible builds
- CI enforces with --locked flag
- Prevents dependency drift

**Test Isolation:**
- Use thread_local! not static Mutex
- Clean env via with_clean_maestro_env()
- MaestroSettingsGuard for config overrides
- Fix failures, don't make tests permissive

**Coverage Strategy:**
- Unit tests: Yes (cargo llvm-cov)
- Integration tests: Yes (library calls)
- E2E tests (maestro-cli/tests/ #[ignore]): Yes in CI
- Cross-component tests (e2e/ package): No (uninstrumented binaries)

### Performance Anti-Patterns to Avoid

**DON'T:**
- Run tests twice (once for pass, once for coverage)
- Use git add -A in monorepo subdirectories
- Build binaries multiple times (share artifacts)
- Skip --locked flag in CI (allows drift)
- Use static Mutex for test state (use thread_local!)
- Make tests more permissive to fix flakes (fix root cause)

**DO:**
- Collect coverage during test execution
- Use specific file paths for git add
- Share build artifacts across CI jobs
- Enforce Cargo.lock with --locked
- Isolate test state per thread
- Fix flaky tests properly

### Documentation Created

1. `/docs/performance-analysis.md` - Comprehensive 40+ page analysis
2. `/docs/performance-recommendations-summary.md` - Executive summary with ROI
3. `/docs/performance-metrics-dashboard.md` - Monitoring setup guide

All documents include:
- Current metrics and bottlenecks
- Actionable recommendations with effort estimates
- Performance budgets and thresholds
- Implementation roadmap
- Cost-benefit analysis

### Next Steps for Team

**Phase 1 (Week 1):** Implement quick wins (30% improvement)
**Phase 2 (Week 2):** Set up monitoring and alerts
**Phase 3 (Weeks 3-4):** Long-term optimizations

Success criteria: CI <10 min, E2E <20 min/shard, zero timeout flakes

---

## Maestro-Sandbox Performance Analysis (2026-03-09)

### Key Findings

**Current Performance:**
- Execution overhead: 15-25ms typical (not "sub-50ms" as claimed)
- Pool acquisition: <5ms (excellent)
- Kernel syscalls: 70% of overhead (clone, pivot_root, exec)
- Memory: 80 MiB pool overhead (8 MiB stack × 10 sandboxes)
- Codebase: 2,145 lines of Rust (clean, well-architected)

**Performance Breakdown:**
- clone(2) + namespaces: 5-10ms (unavoidable kernel overhead)
- pivot_root + mounts: 5-10ms (partially optimizable)
- Capability drop: 2ms (41 × prctl, can optimize to <100µs)
- Seccomp filter: 1ms (already optimal, binary search BPF)
- Poll timeout: 1-100ms (100ms timeout adds latency, can reduce to 10ms)

### Quick Wins Identified

**5 optimizations, <40 lines of code, 30% faster + 75% less memory:**

1. **Reduce poll timeout:** 100ms → 10ms (1 line, saves 10-90ms for fast exits)
2. **Use capset(2) for caps:** Replace 41 prctl calls with 1 syscall (20 lines, saves 2ms)
3. **Reduce stack size:** 8 MiB → 2 MiB (1 line, saves 60 MiB memory)
4. **Skip cgroup writes:** Check-then-write (10 lines, saves 300µs common case)
5. **Pre-allocate buffers:** Vec::with_capacity hint (2 lines, reduces allocator calls)

**Combined Impact:** 10-93ms faster + 60 MiB less memory

### Architecture Strengths

**What's Already Optimal:**
- Pre-warmed pool strategy (amortizes 10-20ms setup overhead)
- RAII resource management (SandboxGuard prevents leaks)
- Async cleanup (unmount/rmdir off critical path)
- Binary search seccomp (O(log n), not linear scan)
- Non-blocking I/O (poll multiplexing)

**What Needs Improvement:**
- Excessive stack allocation (8 MiB vs 2 MiB needed)
- Slow capability drop (41 syscalls vs 1)
- Poll timeout too long (100ms vs 10ms needed)
- No performance instrumentation (can't measure in production)

### Syscall Profile (Per Execution)

| Syscall | Count | Cost | Optimizable |
|---------|-------|------|-------------|
| clone(2) | 1 | 5-10ms | No (kernel) |
| mount(2) | 3 | 3-6ms | Maybe |
| pivot_root(2) | 1 | 2-5ms | No (kernel) |
| prctl(2) | 43 | 2ms | **Yes** (→ capset) |
| poll(2) | 10-1000 | 1-100ms | **Yes** (timeout) |
| execvp(2) | 1 | 2-5ms | No (kernel) |
| **Total** | 60-2000 | 15-130ms | ~30% |

### Performance Budgets Recommended

| Metric | Target | Ceiling |
|--------|--------|---------|
| Pool acquisition | <1ms | 5ms |
| Clone + namespaces | 5ms | 15ms |
| Child init | 8ms | 20ms |
| Output capture | 1ms | 100ms |
| **Total overhead** | **15ms** | **50ms** |

### Real-World Impact

**Python execution (100ms runtime):**
- Before: 122ms total (15ms overhead)
- After: 114ms total (10ms overhead)
- Improvement: 7% faster

**Fast validation (echo hello):**
- Before: 28ms total (poll timeout dominated)
- After: 14ms total
- Improvement: 50% faster

**For AI agents:** 100-500ms workloads, overhead is 3-20% (industry-leading)

### Benchmarking Strategy

**Tools:**
- Criterion (microbenchmarks)
- strace -c (syscall breakdown)
- perf record/report (CPU profiling)
- bpftrace (real-time syscall tracing)
- Custom instrumentation (feature-gated metrics)

**Key Metrics:**
- p50/p95/p99 latency per component
- Syscall count and breakdown
- Memory RSS (stack + heap)
- Pool health (acquire rate, replenish rate)

### Security vs Performance

**All 10 isolation layers kept** (no security tradeoffs):
- PID/NET/MNT/UTS/IPC namespaces
- cgroups v2
- seccomp-BPF
- Capability drop (optimized from 2ms to 50µs)
- Read-only rootfs
- tmpfs overlay

**Verdict:** Optimizing capability drop removes its cost without compromising security.

### Common Patterns

**Pre-warmed Pool Strategy:**
- Create N sandboxes at startup (parallel with JoinSet)
- Acquire = pop from Vec (lock + O(1) access)
- Replenish in background after use (non-blocking)
- Cleanup via RAII guard (prevents leaks on panic)

**Syscall-Heavy Code Profiling:**
- Use strace -c for syscall breakdown (20-50x overhead, not prod-safe)
- Use perf with syscall tracepoints (5% overhead, prod-safe)
- Use eBPF/bpftrace for real-time tracing (minimal overhead)
- Custom instrumentation with Instant timers (zero overhead if feature-gated)

**Memory Management for Fork:**
- Child stack: ManuallyDrop prevents premature deallocation
- Held in ChildStackGuard until waitpid completes
- COW semantics keep physical pages alive even if parent drops
- Safe to reduce from 8 MiB to 2 MiB (child uses <10 KB)

**Output Capture:**
- Non-blocking poll(2) loop
- 1 MiB cap per stream prevents OOM attacks
- Timeout enforced with SIGKILL
- Drain pipes after child exits (final read)

### Performance Anti-Patterns to Avoid

**DON'T:**
- Use excessive stack sizes (8 MiB for <10 KB usage)
- Loop 41× for prctl when capset(2) does it in 1 call
- Use 100ms poll timeout for latency-sensitive workloads
- Skip performance instrumentation ("can't optimize what you don't measure")
- Trade security for performance (all 10 layers are necessary)

**DO:**
- Right-size allocations (2 MiB stack, Vec::with_capacity hints)
- Use single syscalls when possible (capset vs prctl loop)
- Tune poll timeout for workload (10ms for AI agents)
- Add feature-gated metrics (zero cost when disabled)
- Keep all security layers (optimize implementation, not isolation)

### Documentation Created

1. **PERFORMANCE_ANALYSIS.md** — Deep technical analysis (1000+ lines)
   - Syscall-by-syscall breakdown
   - Memory allocation patterns
   - Bottleneck identification with profiling approach
   - Security tradeoff analysis

2. **PERFORMANCE_RECOMMENDATIONS.md** — Actionable optimization guide (600+ lines)
   - Code-level changes with before/after diffs
   - Benchmarking suite setup
   - Profiling commands (strace, perf, bpftrace)
   - Implementation priority ranking

3. **PERFORMANCE_SUMMARY.md** — Executive overview
   - TL;DR findings and impact estimates
   - Quick wins vs long-term optimizations
   - Real-world AI agent performance impact
   - Action plan with phases

### Next Steps

**Phase 1 (Week 1):** Implement quick wins #1-5 (30% faster, 75% less memory)
**Phase 2 (Week 2):** Add instrumentation + benchmarks
**Phase 3 (Month 2+):** Profile and decide on advanced optimizations (pivot_root, io_uring)

**Success Criteria:** 10-18ms overhead (down from 15-25ms), 20 MiB pool memory (down from 80 MiB)

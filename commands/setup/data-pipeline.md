---
argument-hint: [--streaming] | [--batch] | [--channels]
description: Data Pipeline Architecture for Rust using Tokio streams, channels, and async patterns
---

# Data Pipeline Architecture

Design scalable data pipelines for Rust using Tokio async patterns: **$ARGUMENTS**

## Requirements

$ARGUMENTS

## Current State

Confirm the working directory before designing pipeline architecture.

!`pwd`

## Rust Data Pipeline Patterns

### Dependencies

```toml
[dependencies]
# Async runtime
tokio = { version = "1.48", features = ["full"] }
tokio-stream = "0.1"

# Channels and concurrency
async-channel = "2.3"
crossbeam-channel = "0.5"

# Serialization
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"

# Error handling
anyhow = "1.0"
thiserror = "2.0"
```

## 1. Streaming Data Pipeline with Tokio Streams

### Basic Stream Processing

```rust
use tokio_stream::{Stream, StreamExt};
use std::time::Duration;

async fn process_stream<S>(mut stream: S)
where
    S: Stream<Item = String> + Unpin,
{
    while let Some(item) = stream.next().await {
        // Process each item
        println!("Processing: {}", item);
    }
}

// Create a stream from a channel
use tokio::sync::mpsc;

async fn channel_to_stream() {
    let (tx, rx) = mpsc::channel(100);

    tokio::spawn(async move {
        for i in 0..10 {
            tx.send(format!("Item {}", i)).await.unwrap();
        }
    });

    let stream = tokio_stream::wrappers::ReceiverStream::new(rx);
    process_stream(stream).await;
}
```

### Stream Transformation Pipeline

```rust
use tokio_stream::StreamExt;

async fn transform_pipeline() {
    let stream = tokio_stream::iter(0..100)
        .map(|x| x * 2)                    // Transform
        .filter(|x| x % 3 == 0)            // Filter
        .take(10)                          // Limit
        .chunks_timeout(5, Duration::from_secs(1)); // Batch

    tokio::pin!(stream);

    while let Some(batch) = stream.next().await {
        println!("Batch: {:?}", batch);
    }
}
```

## 2. Channel-Based Pipeline Architecture

### MPSC Channel Pattern (Multiple Producers, Single Consumer)

```rust
use tokio::sync::mpsc;
use std::time::Duration;

#[derive(Debug)]
struct Event {
    id: u64,
    data: String,
}

async fn producer(tx: mpsc::Sender<Event>, id: u64) {
    for i in 0..10 {
        let event = Event {
            id: id * 100 + i,
            data: format!("Event from producer {}", id),
        };

        tx.send(event).await.unwrap();
        tokio::time::sleep(Duration::from_millis(100)).await;
    }
}

async fn consumer(mut rx: mpsc::Receiver<Event>) {
    while let Some(event) = rx.recv().await {
        println!("Consumed: {:?}", event);
        // Process event
    }
}

async fn mpsc_pipeline() {
    let (tx, rx) = mpsc::channel(100);

    // Spawn multiple producers
    for i in 0..3 {
        let tx_clone = tx.clone();
        tokio::spawn(async move {
            producer(tx_clone, i).await;
        });
    }

    drop(tx); // Close channel when all producers are done

    consumer(rx).await;
}
```

### Broadcast Channel (One Producer, Multiple Consumers)

```rust
use tokio::sync::broadcast;

async fn broadcast_pipeline() {
    let (tx, _rx) = broadcast::channel(100);

    // Spawn multiple consumers
    for i in 0..3 {
        let mut rx = tx.subscribe();
        tokio::spawn(async move {
            while let Ok(msg) = rx.recv().await {
                println!("Consumer {} received: {}", i, msg);
            }
        });
    }

    // Producer
    for i in 0..10 {
        tx.send(format!("Message {}", i)).unwrap();
        tokio::time::sleep(Duration::from_millis(100)).await;
    }
}
```

## 3. ETL Pipeline Pattern

```rust
use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize)]
struct RawData {
    id: u64,
    value: String,
}

#[derive(Debug, Serialize)]
struct TransformedData {
    id: u64,
    value: String,
    processed_at: chrono::DateTime<chrono::Utc>,
}

struct EtlPipeline {
    extract_tx: mpsc::Sender<RawData>,
    load_rx: mpsc::Receiver<TransformedData>,
}

impl EtlPipeline {
    fn new(buffer_size: usize) -> Self {
        let (extract_tx, extract_rx) = mpsc::channel(buffer_size);
        let (transform_tx, transform_rx) = mpsc::channel(buffer_size);
        let (load_tx, load_rx) = mpsc::channel(buffer_size);

        // Transform stage
        tokio::spawn(async move {
            Self::transform_stage(extract_rx, load_tx).await;
        });

        Self { extract_tx, load_rx }
    }

    async fn transform_stage(
        mut rx: mpsc::Receiver<RawData>,
        tx: mpsc::Sender<TransformedData>,
    ) {
        while let Some(raw) = rx.recv().await {
            let transformed = TransformedData {
                id: raw.id,
                value: raw.value.to_uppercase(),
                processed_at: chrono::Utc::now(),
            };

            tx.send(transformed).await.unwrap();
        }
    }

    async fn extract(&self, data: RawData) -> Result<(), mpsc::error::SendError<RawData>> {
        self.extract_tx.send(data).await
    }

    async fn load(&mut self) -> Option<TransformedData> {
        self.load_rx.recv().await
    }
}
```

## 4. Backpressure Handling

```rust
use tokio::sync::Semaphore;
use std::sync::Arc;

async fn bounded_pipeline() {
    let semaphore = Arc::new(Semaphore::new(10)); // Max 10 concurrent tasks

    let (tx, mut rx) = mpsc::channel(100);

    // Producer with backpressure
    tokio::spawn(async move {
        for i in 0..100 {
            let permit = semaphore.clone().acquire_owned().await.unwrap();

            let tx_clone = tx.clone();
            tokio::spawn(async move {
                // Simulate work
                tokio::time::sleep(Duration::from_millis(100)).await;
                tx_clone.send(i).await.unwrap();
                drop(permit); // Release permit
            });
        }
    });

    // Consumer
    while let Some(item) = rx.recv().await {
        println!("Processed: {}", item);
    }
}
```

## 5. Error Handling and Retry

```rust
use std::time::Duration;

async fn retry_with_backoff<F, Fut, T, E>(
    mut operation: F,
    max_retries: u32,
) -> Result<T, E>
where
    F: FnMut() -> Fut,
    Fut: std::future::Future<Output = Result<T, E>>,
{
    let mut retries = 0;

    loop {
        match operation().await {
            Ok(result) => return Ok(result),
            Err(e) if retries < max_retries => {
                retries += 1;
                let delay = Duration::from_secs(2_u64.pow(retries));
                tokio::time::sleep(delay).await;
            }
            Err(e) => return Err(e),
        }
    }
}
```

## 6. Graceful Shutdown

```rust
use tokio::signal;
use tokio::sync::oneshot;

async fn graceful_shutdown_pipeline() {
    let (shutdown_tx, shutdown_rx) = oneshot::channel();

    // Spawn worker
    let worker = tokio::spawn(async move {
        tokio::select! {
            _ = shutdown_rx => {
                println!("Shutting down gracefully...");
            }
            _ = async {
                loop {
                    // Do work
                    tokio::time::sleep(Duration::from_secs(1)).await;
                }
            } => {}
        }
    });

    // Wait for ctrl-c
    signal::ctrl_c().await.unwrap();

    // Send shutdown signal
    let _ = shutdown_tx.send(());

    // Wait for worker to finish
    worker.await.unwrap();
}
```

## 7. Parallel Processing with FuturesUnordered

```rust
use futures::stream::{FuturesUnordered, StreamExt};

async fn parallel_processing() {
    let tasks = FuturesUnordered::new();

    for i in 0..10 {
        tasks.push(async move {
            tokio::time::sleep(Duration::from_millis(100)).await;
            format!("Task {} complete", i)
        });
    }

    let results: Vec<_> = tasks.collect().await;
    println!("Results: {:?}", results);
}
```

## 8. Complete Pipeline Example

```rust
use tokio::sync::mpsc;
use tokio_stream::StreamExt;

struct DataPipeline {
    ingestion_tx: mpsc::Sender<RawEvent>,
    output_rx: mpsc::Receiver<ProcessedEvent>,
}

#[derive(Debug)]
struct RawEvent {
    id: u64,
    payload: String,
}

#[derive(Debug)]
struct ProcessedEvent {
    id: u64,
    result: String,
}

impl DataPipeline {
    fn new() -> Self {
        let (ingestion_tx, ingestion_rx) = mpsc::channel(1000);
        let (processing_tx, processing_rx) = mpsc::channel(1000);
        let (output_tx, output_rx) = mpsc::channel(1000);

        // Ingestion -> Processing
        tokio::spawn(async move {
            let stream = tokio_stream::wrappers::ReceiverStream::new(ingestion_rx)
                .chunks_timeout(100, Duration::from_secs(1));

            tokio::pin!(stream);

            while let Some(batch) = stream.next().await {
                for event in batch {
                    processing_tx.send(event).await.unwrap();
                }
            }
        });

        // Processing -> Output
        tokio::spawn(async move {
            let mut rx = processing_rx;

            while let Some(event) = rx.recv().await {
                let processed = ProcessedEvent {
                    id: event.id,
                    result: event.payload.to_uppercase(),
                };

                output_tx.send(processed).await.unwrap();
            }
        });

        Self { ingestion_tx, output_rx }
    }

    async fn ingest(&self, event: RawEvent) {
        self.ingestion_tx.send(event).await.unwrap();
    }
}
```

## Output Deliverables

1. **Pipeline Architecture**: Tokio-based async data processing
2. **Stream Processing**: tokio-stream for data transformation
3. **Channel Patterns**: MPSC, broadcast, and bounded channels
4. **Backpressure**: Semaphore-based flow control
5. **Error Handling**: Retry with exponential backoff
6. **Graceful Shutdown**: Signal handling and cleanup
7. **Parallel Processing**: FuturesUnordered for concurrent tasks
8. **Testing**: Integration tests for pipeline stages

## Success Criteria

- Pipeline processes data with bounded memory usage
- Backpressure prevents overwhelming downstream systems
- Errors trigger retries with exponential backoff
- Graceful shutdown ensures no data loss
- Comprehensive observability with tracing
- High throughput with parallel processing
- Type-safe data transformations

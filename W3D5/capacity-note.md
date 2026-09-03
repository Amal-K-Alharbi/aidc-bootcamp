# W3D5 Capacity Note

## Benchmark configuration

- Model: Qwen/Qwen2.5-1.5B-Instruct-AWQ
- Target p95 latency: 2.0 s
- Concurrency levels: 1, 2, 4, 8, 16
- Requests per level: 20
- Run used for capacity decision: Run 2

## Results

| Concurrency | Throughput (tokens/s) | p95 latency (s) | Errors |
|---:|---:|---:|---:|
| 1 | 84.49 | 1.525 | 0 |
| 2 | 167.00 | 1.534 | 0 |
| 4 | 280.33 | 1.732 | 0 |
| 8 | 473.88 | 1.944 | 0 |
| 16 | 670.76 | 2.489 | 0 |

## Capacity decision

The knee is **8 concurrent requests** because concurrency 8 is the highest tested level with p95 latency below the 2.0 s target.

At the knee, the maximum sustainable throughput is approximately **473.88 tokens/s** with a p95 latency of **1.944 s**.

At concurrency 16, throughput increases to **670.76 tokens/s**, but p95 latency increases to **2.489 s**, exceeding the target.

## Limiting factor

The results indicate a **compute/queueing saturation** limit: increasing concurrency continues to improve aggregate throughput, but queueing and contention increase tail latency enough to cross the p95 SLO between concurrency 8 and 16.

## Recommendation

Use **8 concurrent requests** as the sustainable operating point for the 2.0 s p95 target. Concurrency 16 may provide higher peak throughput, but it does not satisfy the selected latency SLO.

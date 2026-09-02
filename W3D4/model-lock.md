# Model lock (team record)

## The locked model

- Model id: Qwen/Qwen2.5-1.5B-Instruct-AWQ
- Quantisation: awq
- Why this one: Passed the function-calling smoke test with 10/10 while providing strong VRAM headroom.

## The launch flags

--model Qwen/Qwen2.5-1.5B-Instruct-AWQ --dtype half --max-model-len 4096
--gpu-memory-utilization 0.85
--quantization awq --enable-auto-tool-choice --tool-call-parser hermes

- Tool-call parser: hermes

## The smoke score

- Score (valid behaviours out of 10): 10
- Distractor stayed call-free in the majority: yes
- Passed the gate (>= 8/10 and distractor majority clean): yes
- Measured against: AWQ — 10/10

## Quality spot check note

The AWQ build generally held up on the five-prompt side-by-side check, with good performance on summarisation, refactoring, and rollback prompts. It showed some degradation in instruction following and explanation quality on the tool-call and quantisation prompts compared with FP16, but it passed the official function-calling smoke test with 10/10.


````markdown
# W2D4 - GPU Image

## Objective

Build a GPU-enabled Docker image using a CUDA base image, while keeping CPU fallback support for machines without an NVIDIA GPU. The image was pushed to Docker Hub and tested on both a CPU-only laptop and a Google Colab T4 GPU.

## 1. GPU Docker Image

Created `Dockerfile.gpu` using:

- CUDA: `nvidia/cuda:12.4.1-runtime-ubuntu22.04`
- Python: `3.11`
- The existing application code from `app/`
- The existing requirements from `app/requirements.txt`

Built the image with:

```bash
docker build -f Dockerfile.gpu -t amalk54/aidc-serving:gpu-v1 .
````

The final GPU image size was approximately:

```text
12.6 GB
```

The large size is expected because the image contains the CUDA runtime and GPU-enabled PyTorch dependencies.

## 2. CPU Fallback Test

The image was run on my laptop without using `--gpus all`:

```bash
docker run -d --name serving-gpu -p 8000:8000 \
  -v hf-cache:/home/app/.cache/huggingface \
  amalk54/aidc-serving:gpu-v1
```

The container detected that no NVIDIA driver was available and automatically used the CPU fallback.

The health endpoint returned:

```text
HTTP/1.1 200 OK
```

Response:

```json
{
  "status": "ok",
  "model": "Qwen/Qwen2.5-0.5B-Instruct"
}
```

This confirmed that the GPU image can still run on a machine without a GPU.

## 3. Push to Docker Hub

Logged in to Docker Hub and pushed the image:

```bash
docker push amalk54/aidc-serving:gpu-v1
```

The push completed successfully.

Image:

```text
amalk54/aidc-serving:gpu-v1
```

## 4. Colab T4 Test

A Google Colab runtime was configured with a Tesla T4 GPU.

Verified that CUDA was available:

```text
CUDA available: True
GPU: Tesla T4
```

Installed the required packages:

```bash
pip install "transformers==4.46.*" "accelerate==1.1.*"
```

The existing `torch` installation in Colab was kept because Colab already provides a CUDA-enabled PyTorch version.

Ran the same probe:

```bash
python app/generate_probe.py
```

The probe generated:

```json
{
  "cuda": true,
  "device_name": "Tesla T4",
  "tokens_per_s": 32.2,
  "model": "Qwen/Qwen2.5-1.5B-Instruct"
}
```

The evidence file was saved as:

```text
gpu_evidence.json
```

and copied back to the local `serving-stack` directory.

## 5. Final Verification

The final verifier was run with a longer timeout because the CPU fallback needed more time to load the model:

```bash
TIMEOUT=1200 IMAGE=amalk54/aidc-serving:gpu-v1 ./verify.sh
```

Final result:

```text
image: amalk54/aidc-serving:gpu-v1
health: 200
completion: ok
GREEN CHECK: PASS
```

## Results

| Test                   | Result                |
| ---------------------- | --------------------- |
| GPU image build        | PASS                  |
| CPU fallback           | PASS                  |
| `/health`              | 200 OK                |
| `/v1/chat/completions` | PASS                  |
| Docker Hub push        | PASS                  |
| Colab GPU              | Tesla T4              |
| CUDA detected          | `true`                |
| T4 throughput          | 32.2 tokens/s         |
| Final verifier         | **GREEN CHECK: PASS** |

## Key Takeaway

The main idea of this lab was to build one portable GPU image that can use CUDA when a GPU is available and automatically fall back to CPU when it is not.

The same application image was successfully tested on a CPU-only laptop and on a Tesla T4 GPU in Colab.

````

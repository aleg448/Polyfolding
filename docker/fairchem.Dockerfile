FROM pytorch/pytorch:2.8.0-cuda12.6-cudnn9-devel

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/workspace/.cache/huggingface \
    MPLBACKEND=Agg

WORKDIR /workspace

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git \
        build-essential \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY tests ./tests
COPY scripts ./scripts
COPY data/benchmark ./data/benchmark
COPY examples ./examples

RUN python -m pip install --upgrade pip setuptools wheel \
    && python -m pip install -e "." \
    && python -m pip install ase fairchem-core huggingface_hub requests

CMD ["python", "-m", "crystalprobe.benchmark.cli", "doctor"]


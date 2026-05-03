FROM pytorch/pytorch:2.8.0-cuda12.6-cudnn9-devel

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONUNBUFFERED=1 \
    WARP_CACHE_PATH=/workspace/.cache/warp \
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
    && python -m pip install -e ".[dev]" \
    && python -m pip install ase mace-torch "aimnet[ase]" huggingface_hub requests

CMD ["python", "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider"]


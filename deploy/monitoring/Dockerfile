ARG BASE_IMAGE
FROM ${BASE_IMAGE}
ARG SOURCE_COMMIT
ARG RELEASE_ID
LABEL org.opencontainers.image.title="TokenScope" \
      org.opencontainers.image.revision=${SOURCE_COMMIT} \
      org.opencontainers.image.version=${RELEASE_ID}
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app/src \
    HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
    HF_HOME=/tmp/huggingface XDG_CACHE_HOME=/tmp/cache \
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 RAYON_NUM_THREADS=8
WORKDIR /app
COPY env/requirements.runtime.txt /app/env/requirements.runtime.txt
COPY wheelhouse /wheelhouse
RUN python -m pip install --no-index --find-links=/wheelhouse --require-hashes --no-cache-dir -r env/requirements.runtime.txt && rm -rf /wheelhouse
COPY src /app/src
COPY models /app/models
COPY env/encoding-assets.lock.json /app/env/encoding-assets.lock.json
COPY configs /app/configs
COPY pyproject.toml uv.lock /app/
COPY apps/viewer/dist /app/apps/viewer/dist
COPY scripts/validation/generate_monitoring_data.py /app/scripts/validation/generate_monitoring_data.py
COPY scripts/release/verify_service.py /app/scripts/release/verify_service.py
COPY candidate.json /app/candidate.json
ENTRYPOINT ["python", "-m", "tokenscope.cli"]

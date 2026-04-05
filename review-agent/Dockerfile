FROM python:3.14-slim AS builder

WORKDIR /app

COPY . .

RUN pip install uv \
    && uv build

FROM python:3.14-slim

WORKDIR /app

COPY --from=builder /app/dist/*.whl /tmp/

RUN pip install uv \
    && uv pip install /tmp/*.whl --system

EXPOSE 8000

CMD ["review-agent"]

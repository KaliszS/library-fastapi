FROM python:3.13-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

WORKDIR /app
COPY . .

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin/:$PATH"
RUN uv sync

COPY ./scripts/start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"]
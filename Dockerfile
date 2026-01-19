FROM python:3.14.2-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt

COPY src ./src
COPY alembic ./alembic
COPY alembic.ini ./alembic.ini

ENV MCP_PORT=8080
ENV MCP_HOST="0.0.0.0"
ENV PYTHONPATH=/app/src

VOLUME /app/data

EXPOSE 8080

CMD ["sh", "-c", "alembic upgrade head && exec python src/mcp_lab/server.py"]
#CMD ["python", "src/mcp_lab/server.py"]

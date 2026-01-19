# mcp-lab MCP server

A MCP server project

## Description

The API is an MCP server that provides structured search over Polish administrative locations and addresses using official data from the Polish GOV systems (TERYT, SIMC, ULIC).

The server exposes tools that allow searching for provinces, districts, municipalities, localities, and streets with detailed hierarchical context.

A typical use case is connecting the MCP server to an LLM, enabling the model to analyze documents or articles and infer which geographical areas in Poland the content refers to.

## Install & Running on Ubuntu

1. Run fully Locally

run server(get inside project): `uv run src/mcp_lab/server.py` \
open client UI: `npx @modelcontextprotocol/inspector uv run my-mcp`

2. Run with dockerfile and verify at UI

build image: `docker build -t mcp-lab .` \
create/run container: `docker run --rm --network host mcp-lab` \
OR create/run container(along with separate volume): `docker run --rm --network host -v mcp_lab_data:/app/data mcp-lab` \
open client UI(separate CMD): `npx @modelcontextprotocol/inspector`

set UI:
Transport type: `SEE`
URL: `http://localhost:8080/sse`

3. publish with cloudflared

build image: `docker build -t mcp-lab .` \
create/run container: `docker run --rm --network host mcp-lab` \
publish: `cloudflared tunnel --url http://localhost:8080`

## Testing with Postman

to simply test crete `new workspace` -> `MCP` -> `tools` -> set url: `http://localhost:8080/sse`

to test with LLM: `new workspace` -> `AI` -> select model -> set API key & set url: `http://localhost:8080/sse`

prompts e.g.:
- `Please tell me where every town with name Kolno is located.`
- `Find every location in Poland, which starts with "Nowa".`
- 

## Update database models/migrations with Alembic

- Create basic alembic files: \
  `alembic init alembic`
- Generates a new migration file based on current SQLAlchemy models: \
  `alembic revision --autogenerate -m "initial schema"`
- Applies all pending migrations to the database: \
  `alembic upgrade head`  


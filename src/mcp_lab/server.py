import os

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP, Context
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

import mcp_lab.db.records as re
from mcp_lab.db.migration.db_files import DatabaseFiles
from mcp_lab.logger_cfg import logg
from mcp_lab.my_service import LocationService

__import_db_done = False

async def import_data(session: AsyncSession, service: LocationService):
    global __import_db_done

    if __import_db_done:
        logg.info("Import db data is already doing or done, skipping")
        return

    logg.info("Import db data start")
    __import_db_done = True
    await service.import_data(session=session)
    logg.info("Import db data finished")

@dataclass
class AppContext:
    """Application context with typed dependencies."""
    service: LocationService
    session_factory: sessionmaker

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with type-safe context."""
    logg.info("app lifespan and service start")
    DATABASE_URL = DatabaseFiles.get_db_path_mcp()

    engine = create_async_engine(DATABASE_URL, echo=False, future=True)
    async_session = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        future=True
    )
    service = LocationService()
    async with async_session() as session:
        await import_data(session, service)

    try:
        yield AppContext(service=service, session_factory=async_session)
    finally:
        await engine.dispose()
        logg.info("app lifespan shutdown")

mcp_host = os.environ.get("MCP_HOST", "127.0.0.1")
mcp_port = int(os.environ.get("MCP_PORT", 8080))

mcp = FastMCP(name="Location search Tool", port=mcp_port, host=mcp_host, lifespan=app_lifespan, json_response=True, debug=True)

PAGE_SIZE = 10

@mcp.resource("file://documents/{name}")
def read_document(ctx: Context, name: str) -> str:
    """Read a document by name."""
    path: Path = ctx.request_context.lifespan_context.service.get_documents_folder() / name
    return path.read_text(encoding="utf-8")

@mcp.resource("data://app/{entity_type}/{cursor}")
async def get_records(ctx: Context, entity_type: str, cursor: str) -> re.Page[re.Province | re.District | re.Municipality | re.Locality | re.Street]:
    """
    Fetch records by type with pagination.

    entity_type: one of "provinces", "districts", "municipalities", "localities", "streets"
    cursor: pagination cursor
    """
    logg.info(f"get_records for {entity_type} with cursor {cursor}")
    current_cursor = __current_cursor(cursor)
    async with ctx.request_context.lifespan_context.session_factory() as session:
        return await ctx.request_context.lifespan_context.service.find_all_paginated(
            session, entity_type, current_cursor, PAGE_SIZE
        )

@mcp.tool()
async def search_by_id(ctx: Context, entity_type: str, id: str, cursor: Optional[str] = None) -> re.Page[re.ProvinceDetails | re.DistrictDetails | re.MunicipalityDetails | re.LocalityDetails | re.StreetDetails]:
    """
    Search records by type and id with pagination.

    entity_type: one of "provinces", "districts", "municipalities", "localities", "streets"
    id: entity database identifier
    cursor: pagination cursor
    """
    logg.info(f"search {entity_type} with id '{id}', cursor {cursor}")
    current_id, _, current_cursor = __details_input(id, None, cursor)
    async with ctx.request_context.lifespan_context.session_factory() as session:
        return await ctx.request_context.lifespan_context.service.search_details(
            session, entity_type, current_id, None, current_cursor, PAGE_SIZE
        )

@mcp.tool()
async def search_by_name(ctx: Context, entity_type: str, name: str, cursor: Optional[str] = None) -> re.Page[re.ProvinceDetails | re.DistrictDetails | re.MunicipalityDetails | re.LocalityDetails | re.StreetDetails]:
    """
    Search records by type and name part with pagination.

    entity_type: one of "provinces", "districts", "municipalities", "localities", "streets"
    id: entity database identifier
    cursor: pagination cursor
    """
    logg.info(f"search {entity_type} with name '{name}', cursor {cursor}")
    _, current_name, current_cursor = __details_input(None, name, cursor)
    async with ctx.request_context.lifespan_context.session_factory() as session:
        return await ctx.request_context.lifespan_context.service.search_details(
            session, entity_type, None, current_name, current_cursor, PAGE_SIZE
        )

def __details_input(id: str | None, name: str | None, cursor: Optional[str]) -> tuple[str | None, str | None, int]:
    current_cursor = __current_cursor(cursor)
    current_id = id if id and id.strip() else None
    current_name = name if name and name.strip() else None
    return current_id, current_name, current_cursor

def __current_cursor(cursor: str) -> int:
    return int(cursor) if cursor else 0

def main():
   """Entry point for the direct execution server."""
   mcp.run(transport="sse")

if __name__ == "__main__":
   main()

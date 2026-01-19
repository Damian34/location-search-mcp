from datetime import date
from pathlib import Path
from typing import TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

import mcp_lab.db.records as re

from mcp_lab.db.repository import LocationRepository
from mcp_lab.logger_cfg import logg
from mcp_lab.source_loader import SourceLoader
from mcp_lab.source_reader import SourceReader

T = TypeVar("T", bound=re.DataTable)


class LocationService:
    def __init__(self):
        self.__repository = LocationRepository()
        self.__source_loader = SourceLoader()
        self.__source_reader = SourceReader(self.__source_loader)

    def get_documents_folder(self) -> Path:
        return self.__source_loader.get_raw_data_folder()

    async def import_data(self, session: AsyncSession):
        logg.info("LocationService: async import_data start")
        registries = await self.__repository.find_all_async(session, re.AppRegistry)
        reg = registries[0] if registries else None
        today = date.today().isoformat()

        if reg and reg.gov_last_update == today:
            logg.info("LocationService: data already up-to-date")
            return

        provinces_gen, districts_gen, municipalities_gen = self.__source_reader.get_locations_terc()
        await self.__repository.save_async(session, provinces_gen)
        await self.__repository.save_async(session, districts_gen)
        await self.__repository.save_async(session, municipalities_gen)
        await self.__repository.save_async(session, self.__source_reader.get_locations_ulic())
        await self.__repository.save_async(session, self.__source_reader.get_locations_smic())

        if reg:
            reg.gov_last_update = today
            await self.__repository.save_async(session, [reg])
        else:
            await self.__repository.save_async(session, [re.AppRegistry("1", today)])
        logg.info("LocationService: data importing end")

    async def find_all_paginated(self, session: AsyncSession, entity_type: str, cursor: int, page_size: int = 10) -> re.Page[T]:
        logg.info(f"LocationService: find paginated '{entity_type}' recodes for cursor={cursor} and page_size={page_size}")
        clazz = self.__get_table_name(entity_type)
        return await self.__repository.find_all_paginated_async(session, clazz, cursor, page_size)

    async def search_details(self, session: AsyncSession, entity_type: str, _id: str | None, name: str | None, cursor: int, page_size: int = 10) -> re.Page[re.ProvinceDetails | re.DistrictDetails | re.MunicipalityDetails | re.LocalityDetails | re.StreetDetails]:
        if self.__tablename(re.Province) == entity_type:
            return await self.__repository.search_province_details_async(session, _id, name, cursor, page_size)
        elif self.__tablename(re.District) == entity_type:
            return await self.__repository.search_district_details_async(session, _id, name, cursor, page_size)
        elif self.__tablename(re.Municipality) == entity_type:
            return await self.__repository.search_municipality_details_async(session, _id, name, cursor, page_size)
        elif self.__tablename(re.Locality) == entity_type:
            return await self.__repository.search_locality_details_async(session, _id, name, cursor, page_size)
        elif self.__tablename(re.StreetDetails) == entity_type:
            return await self.__repository.search_street_details_async(session, _id, name, cursor, page_size)
        else:
            raise ValueError(f"Unknown resource name: {entity_type}")

    def __get_table_name(self, entity_type: str) -> type[re.Province | re.District | re.Municipality | re.Locality | re.Street]:
        for table in [re.Province, re.District, re.Municipality, re.Locality, re.Street]:
            if table.table().__tablename__ == entity_type:
                return table
        raise ValueError(f"Unknown resource name: {entity_type}")

    def __tablename(self, table: type[re.DataTable]) -> str:
        return table.table().__tablename__


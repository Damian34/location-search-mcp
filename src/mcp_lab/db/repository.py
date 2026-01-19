from dataclasses import asdict
from typing import Iterable, Type, TypeVar, Iterator

from sqlalchemy import insert, select, func, GenerativeSelect
from sqlalchemy.ext.asyncio import AsyncSession

import mcp_lab.db.records as re
from mcp_lab.db.migration.models import Base

from dataclasses import fields

T = TypeVar("T", bound=re.DataTable)


class LocationRepository:
    def __init__(self):
        pass

    async def save_async(self, session: AsyncSession, locations: Iterable[re.DataTable]):
        for batch in self.__batch_generator(locations, batch_size=1000):
            if not batch:
                continue
            table_model = type(batch[0]).table()
            stmt = insert(table_model)
            values = [asdict(item) for item in batch]
            await session.execute(stmt, values)
            await session.commit()

    def __batch_generator(self, locations: Iterable[re.DataTable], batch_size: int) -> Iterator[list[re.DataTable]]:
        batch = []
        for loc in locations:
            batch.append(loc)
            if len(batch) >= batch_size:
                yield batch
                batch = []
        if batch:
            yield batch

    async def find_all_async(self, session: AsyncSession, clazz: Type[T]) -> list[T]:
        table_model = clazz.table()
        statement = select(table_model)
        result = await session.execute(statement)
        rows = result.scalars().all()
        return self.__map_to_tables(rows, clazz)

    async def find_all_paginated_async(self, session: AsyncSession, clazz: Type[T], cursor: int, page_size: int = 10) -> re.Page[T]:
        table_model = clazz.table()
        statement = select(table_model).offset(cursor).limit(page_size)
        result = await session.execute(statement)
        rows = result.scalars().all()
        return self.__map_to_table_pages(rows, clazz, page_size, page_size)

    def __map_to_tables(self, rows: Iterable, clazz: Type[T]) -> list[T]:
        field_names = [f.name for f in fields(clazz)]
        mapped = []
        for row in rows:
            obj_dict = {field: getattr(row, field) for field in field_names}
            mapped.append(clazz(**obj_dict))
        return mapped

    def __map_to_table_pages(self, rows: Iterable, clazz: Type[T], cursor: int, page_size) -> re.Page[T]:
        records = self.__map_to_tables(rows, clazz)
        next_cursor = cursor + page_size if len(records) == page_size else None
        return re.Page(items=records, next_cursor=next_cursor)

    def __to_page(self, rows: list[T], cursor: int, page_size):
        next_cursor = cursor + page_size if len(rows) == page_size else None
        return re.Page(items=rows, next_cursor=next_cursor)

    async def search_province_details_async(self, session: AsyncSession, _id: str | None, name: str | None,
                                            cursor: int, page_size: int = 10) -> re.Page[re.ProvinceDetails]:
        province = re.Province.table()
        district = re.District.table()
        municipality = re.Municipality.table()
        locality = re.Locality.table()
        street = re.Street.table()

        statement = (
            select(
                province.id,
                province.name,
                func.count(func.distinct(district.id)),
                func.count(func.distinct(municipality.id)),
                func.count(func.distinct(locality.id)),
                func.count(func.distinct(street.id)),
            )
            .outerjoin(district, district.province_id == province.id)
            .outerjoin(municipality, municipality.district_id == district.id)
            .outerjoin(locality, locality.municipality_id == municipality.id)
            .outerjoin(street, street.locality_id == locality.id)
            .group_by(province.id, province.name)
            .offset(cursor)
            .limit(page_size)
        )
        statement = self.__append_where(statement, province, _id, name)
        result = await session.execute(statement)
        rows = result.all()

        return self.__to_page([
            re.ProvinceDetails(
                id=row[0],
                name=row[1],
                district_count=row[2],
                municipality_count=row[3],
                locality_count=row[4],
                street_count=row[5],
            )
            for row in rows
        ], page_size, page_size)

    async def search_district_details_async(
            self, session: AsyncSession, _id: str | None, name: str | None,
            cursor: int, page_size: int = 10
    ) -> re.Page[re.DistrictDetails]:
        district = re.District.table()
        province = re.Province.table()
        municipality = re.Municipality.table()
        locality = re.Locality.table()
        street = re.Street.table()

        statement = (
            select(
                district.id,
                district.name,
                province.id,
                province.name,
                func.count(func.distinct(municipality.id)),
                func.count(func.distinct(locality.id)),
                func.count(func.distinct(street.id)),
            )
            .outerjoin(province, district.province_id == province.id)
            .outerjoin(municipality, municipality.district_id == district.id)
            .outerjoin(locality, locality.municipality_id == municipality.id)
            .outerjoin(street, street.locality_id == locality.id)
            .group_by(district.id, district.name, province.id, province.name)
            .offset(cursor)
            .limit(page_size)
        )

        statement = self.__append_where(statement, district, _id, name)
        result = await session.execute(statement)
        rows = result.all()

        return self.__to_page([
            re.DistrictDetails(
                id=row[0],
                name=row[1],
                province=re.LocationShort(id=row[2], name=row[3]),
                municipality_count=row[4],
                locality_count=row[5],
                street_count=row[6],
            )
            for row in rows
        ], cursor, page_size)

    async def search_municipality_details_async(
            self, session: AsyncSession, _id: str | None, name: str | None,
            cursor: int, page_size: int = 10
    ) -> re.Page[re.MunicipalityDetails]:
        municipality = re.Municipality.table()
        district = re.District.table()
        province = re.Province.table()
        locality = re.Locality.table()
        street = re.Street.table()

        statement = (
            select(
                municipality.id,
                municipality.name,
                province.id,
                province.name,
                district.id,
                district.name,
                func.count(func.distinct(locality.id)),
                func.count(func.distinct(street.id)),
            )
            .outerjoin(district, municipality.district_id == district.id)
            .outerjoin(province, district.province_id == province.id)
            .outerjoin(locality, locality.municipality_id == municipality.id)
            .outerjoin(street, street.locality_id == locality.id)
            .group_by(municipality.id, municipality.name, district.id, district.name, province.id, province.name)
            .offset(cursor)
            .limit(page_size)
        )

        statement = self.__append_where(statement, municipality, _id, name)
        result = await session.execute(statement)
        rows = result.all()

        return self.__to_page([
            re.MunicipalityDetails(
                id=row[0],
                name=row[1],
                province=re.LocationShort(id=row[2], name=row[3]),
                district=re.LocationShort(id=row[4], name=row[5]),
                locality_count=row[6],
                street_count=row[7],
            )
            for row in rows
        ], cursor, page_size)

    async def search_locality_details_async(
            self, session: AsyncSession, _id: str | None, name: str | None,
            cursor: int, page_size: int = 10
    ) -> re.Page[re.LocalityDetails]:
        locality = re.Locality.table()
        municipality = re.Municipality.table()
        district = re.District.table()
        province = re.Province.table()
        street = re.Street.table()

        statement = (
            select(
                locality.id,
                locality.name,
                province.id,
                province.name,
                district.id,
                district.name,
                municipality.id,
                municipality.name,
                func.count(func.distinct(street.id)),
            )
            .outerjoin(municipality, locality.municipality_id == municipality.id)
            .outerjoin(district, municipality.district_id == district.id)
            .outerjoin(province, district.province_id == province.id)
            .outerjoin(street, street.locality_id == locality.id)
            .group_by(locality.id, locality.name, municipality.id, municipality.name,
                      district.id, district.name, province.id, province.name)
            .offset(cursor)
            .limit(page_size)
        )

        statement = self.__append_where(statement, locality, _id, name)
        result = await session.execute(statement)
        rows = result.all()

        return self.__to_page([
            re.LocalityDetails(
                id=row[0],
                name=row[1],
                province=re.LocationShort(id=row[2], name=row[3]),
                district=re.LocationShort(id=row[4], name=row[5]),
                municipality=re.LocationShort(id=row[6], name=row[7]),
                street_count=row[8],
            )
            for row in rows
        ], cursor, page_size)

    async def search_street_details_async(
            self, session: AsyncSession, _id: str | None, name: str | None,
            cursor: int, page_size: int = 10
    ) -> re.Page[re.StreetDetails]:
        street = re.Street.table()
        locality = re.Locality.table()
        municipality = re.Municipality.table()
        district = re.District.table()
        province = re.Province.table()

        statement = (
            select(
                street.id,
                street.name,
                province.id,
                province.name,
                district.id,
                district.name,
                municipality.id,
                municipality.name,
                locality.id,
                locality.name,
            )
            .outerjoin(locality, street.locality_id == locality.id)
            .outerjoin(municipality, locality.municipality_id == municipality.id)
            .outerjoin(district, municipality.district_id == district.id)
            .outerjoin(province, district.province_id == province.id)
            .offset(cursor)
            .limit(page_size)
        )

        statement = self.__append_where(statement, street, _id, name)
        result = await session.execute(statement)
        rows = result.all()

        return self.__to_page([
            re.StreetDetails(
                id=row[0],
                name=row[1],
                province=re.LocationShort(id=row[2], name=row[3]),
                district=re.LocationShort(id=row[4], name=row[5]),
                municipality=re.LocationShort(id=row[6], name=row[7]),
                locality=re.LocationShort(id=row[8], name=row[9]),
            )
            for row in rows
        ], cursor, page_size)

    def __append_where(self, statement: GenerativeSelect, table: type[Base], _id: str, name: str) -> GenerativeSelect:
        if _id:
            statement = statement.where(table.id == _id)
        elif name:
            statement = statement.where(func.lower(table.name).like(f"%{name.lower()}%"))
        return statement


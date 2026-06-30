from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypeVar, Generic, List

import search_mcp.db.migration.models as models


@dataclass
class DataTable(ABC):
    @classmethod
    @abstractmethod
    def table(cls) -> type[models.Base]: ...

T = TypeVar("T", bound=str | DataTable)

@dataclass
class Page(Generic[T]):
    items: List[T]
    next_cursor: int | None

@dataclass
class AppRegistry(DataTable):
    id: str
    gov_last_update: str

    @classmethod
    def table(cls) -> type[models.Base]:
        return models.AppRegistryTable


@dataclass
class Province(DataTable):
    id: str
    name: str

    @classmethod
    def table(cls) -> type[models.Base]:
        return models.ProvinceTable

@dataclass
class District(DataTable):
    id: str
    province_id: str
    name: str
    type: str

    @classmethod
    def table(cls) -> type[models.Base]:
        return models.DistrictTable

@dataclass
class Municipality(DataTable):
    id: str
    district_id: str
    name: str
    type: str

    @classmethod
    def table(cls) -> type[models.Base]:
        return models.MunicipalityTable

@dataclass
class Locality(DataTable):
    id: str
    municipality_id: str
    name: str

    @classmethod
    def table(cls) -> type[models.Base]:
        return models.LocalityTable

@dataclass
class Street(DataTable):
    id: str
    locality_id: str
    prefix: str
    name: str

    @classmethod
    def table(cls) -> type[models.Base]:
        return models.StreetTable

"""
Location details:
"""

@dataclass
class LocationShort:
    id: str
    name: str

@dataclass
class ProvinceDetails(DataTable):
    id: str
    name: str
    district_count: int
    municipality_count: int
    locality_count: int
    street_count: int

    @classmethod
    def table(cls) -> type[models.Base]:
        return Province.table()

@dataclass
class DistrictDetails(DataTable):
    id: str
    name: str
    province: LocationShort
    municipality_count: int
    locality_count: int
    street_count: int

    @classmethod
    def table(cls) -> type[models.Base]:
        return District.table()

@dataclass
class MunicipalityDetails(DataTable):
    id: str
    name: str
    province: LocationShort
    district: LocationShort
    locality_count: int
    street_count: int

    @classmethod
    def table(cls) -> type[models.Base]:
        return Municipality.table()

@dataclass
class LocalityDetails(DataTable):
    id: str
    name: str
    province: LocationShort
    district: LocationShort
    municipality: LocationShort
    street_count: int

    @classmethod
    def table(cls) -> type[models.Base]:
        return Locality.table()

@dataclass
class StreetDetails(DataTable):
    id: str
    name: str
    province: LocationShort
    district: LocationShort
    municipality: LocationShort
    locality: LocationShort

    @classmethod
    def table(cls) -> type[models.Base]:
        return Street.table()

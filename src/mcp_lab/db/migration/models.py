from __future__ import annotations

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class AppRegistryTable(Base):
    __tablename__ = "app_registry"
    id = Column(String, primary_key=True)
    gov_last_update = Column(String, nullable=False)

class ProvinceTable(Base):  # województwo z TERC
    __tablename__ = "provinces"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)

    districts = relationship("DistrictTable", back_populates="province", cascade="all, delete-orphan")

class DistrictTable(Base):  # powiat z TERC
    __tablename__ = "districts"
    id = Column(String, primary_key=True)
    province_id = Column(String, ForeignKey("provinces.id"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)

    province = relationship("ProvinceTable", back_populates="districts")
    municipalities = relationship("MunicipalityTable", back_populates="district", cascade="all, delete-orphan")

class MunicipalityTable(Base):  # gmina_terytorialnie z TERC
    __tablename__ = "municipalities"
    id = Column(String, primary_key=True)
    district_id = Column(String, ForeignKey("districts.id"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)

    district = relationship("DistrictTable", back_populates="municipalities")
    localities = relationship("LocalityTable", back_populates="municipality", cascade="all, delete-orphan")

class LocalityTable(Base):  # miejscowosc z SIMC
    __tablename__ = "localities"
    id = Column(String, primary_key=True)
    municipality_id = Column(String, ForeignKey("municipalities.id"), nullable=False)
    name = Column(String, nullable=False)

    municipality = relationship("MunicipalityTable", back_populates="localities")
    streets = relationship("StreetTable", back_populates="locality", cascade="all, delete-orphan")

class StreetTable(Base):  # ulica z ULIC
    __tablename__ = "streets"
    id = Column(String, primary_key=True)
    locality_id = Column(String, ForeignKey("localities.id"), nullable=False)
    prefix = Column(String, nullable=False)
    name = Column(String, nullable=False)

    locality = relationship("LocalityTable", back_populates="streets")


from sqlalchemy.orm import DeclarativeBase
from typing import List
from typing import Optional
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import String, ForeignKey, DateTime, Text, BigInteger

from datetime import datetime

from .engine import engine


class Base(DeclarativeBase):
     pass


class Sims(Base):
     __tablename__ = "sims"

     sims_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
     number_tel: Mapped[str] = mapped_column(String(11))
     iccid: Mapped[str] = mapped_column(String(20))
     apn: Mapped[Optional[str]] = mapped_column(Text())
     ip: Mapped[Optional[str]] = mapped_column(String(15))     
     state: Mapped[str] = mapped_column(String(100))
     activity: Mapped[Optional[datetime]] = mapped_column(DateTime())
     traffic: Mapped[Optional[str]] = mapped_column(String(15))
     operator: Mapped[str] = mapped_column(String(20))
     imei: Mapped[Optional[str]] = mapped_column(String(20))
     hash_data: Mapped[str] = mapped_column(String(100))
     state_in_lk: Mapped[str] = mapped_column(String(15))
     last_upload: Mapped[datetime] = mapped_column(DateTime())
     created_on: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now)
     update_on: Mapped[Optional[datetime]] = mapped_column(DateTime(), default=datetime.now, onupdate=datetime.now)

     updatesimlog: Mapped[List["UpdateSimLog"]] = relationship(back_populates="sims")

class ImportSimsLog(Base):
     __tablename__ = "importsimslog"

     importsimslog_id: Mapped[int] = mapped_column(primary_key=True)
     start_import: Mapped[str] = mapped_column(DateTime())
     name_file: Mapped[str] = mapped_column(Text())
     state: Mapped[Optional[str]] = mapped_column(String(20))
     count_import_sim: Mapped[Optional[int]]
     count_sim_file: Mapped[Optional[int]]
     description: Mapped[Optional[str]] = mapped_column(Text())
     error_import: Mapped[Optional[str]] = mapped_column(Text())
     created_on: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now)

     updatesimlog: Mapped[List["UpdateSimLog"]] = relationship(back_populates="importsimslog")


class UpdateSimLog(Base):
     __tablename__ = "updatesimlog"

     updatesimlog_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
     sims_id = mapped_column(ForeignKey("sims.sims_id"))
     importsimslog_id = mapped_column(ForeignKey("importsimslog.importsimslog_id"))
     number_tel: Mapped[Optional[str]] = mapped_column(String(11))
     iccid: Mapped[Optional[str]] = mapped_column(String(20))
     apn: Mapped[Optional[str]] = mapped_column(Text())
     ip: Mapped[Optional[str]] = mapped_column(String(15))
     state: Mapped[Optional[str]] = mapped_column(String(100))
     activity: Mapped[Optional[str]] = mapped_column(DateTime())
     traffic: Mapped[Optional[str]] = mapped_column(String(15))
     operator: Mapped[Optional[str]] = mapped_column(String(20))
     state_in_lk: Mapped[Optional[str]] = mapped_column(String(15))
     created_on: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now)


     sims: Mapped[List["Sims"]] = relationship(back_populates="updatesimlog")
     importsimslog: Mapped[List["ImportSimsLog"]] = relationship(back_populates="updatesimlog")


def create_db():
     Base.metadata.create_all(engine)     

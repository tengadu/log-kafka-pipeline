from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class LogEntry(Base):
    __tablename__ = "log_entries"

    log_id = Column(BigInteger, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False)
    log_type = Column(Enum("INFO", "WARN", "ERROR", "SUCCESS", "DEBUG"), nullable=False)
    source = Column(String(255), nullable=False)
    raw_message = Column(Text, nullable=False)
    ai_tag = Column(String(255))
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    details = relationship("LogEntryDetail", back_populates="log", cascade="all, delete")


class LogEntryDetail(Base):
    __tablename__ = "log_entry_details"

    detail_id = Column(BigInteger, primary_key=True, autoincrement=True)
    log_id = Column(BigInteger, ForeignKey("log_entries.log_id"), nullable=False)
    field_name = Column(String(255), nullable=False)
    field_value = Column(Text)

    log = relationship("LogEntry", back_populates="details")


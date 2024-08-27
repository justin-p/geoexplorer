import os
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/request_log.db")
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


class RequestLog(Base):
    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String, index=True)
    additional_info = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)


class RequestLogCreate(BaseModel):
    ip_address: str
    additional_info: str


class RequestLogResponse(BaseModel):
    id: int
    ip_address: str
    additional_info: str
    timestamp: datetime


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/")
async def root():
    return {"message": "Welcome to the request logging API"}


@app.get("/log")
@app.get("/log/{additional_info}")
async def log_request(request: Request, additional_info: str = ""):
    client_ip = request.client.host

    async with AsyncSessionLocal() as session:
        log_entry = RequestLog(ip_address=client_ip, additional_info=additional_info)
        session.add(log_entry)
        await session.commit()

    return {"message": "Request logged successfully"}


@app.get("/logged_ips", response_model=list[RequestLogResponse])
async def get_logs():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(RequestLog))
        logs = result.scalars().all()
        return [
            RequestLogResponse(
                id=log.id,
                ip_address=log.ip_address,
                additional_info=log.additional_info,
                timestamp=log.timestamp
            )
            for log in logs
        ]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

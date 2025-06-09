from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class HealthCheckResponse(BaseModel):
    status: str

class MongoHealthResponse(BaseModel):
    mongo: str
    status: str
    host: Optional[str] = None
    port: Optional[int] = None
    server_info: Optional[Dict[str, Any]] = None
    uptime: Optional[float] = None
    databases: Optional[List[Dict[str, Any]]] = None
    total_collections: Optional[int] = None
    total_storage_mb: Optional[float] = None
    error: Optional[str] = None


class RedisHealthResponse(BaseModel):
    redis: str
    status: str
    host: Optional[str] = None
    port: Optional[int] = None
    version: Optional[str] = None
    uptime: Optional[int] = None
    connected_clients: Optional[int] = None
    used_memory_mb: Optional[float] = None
    total_keys: Optional[int] = None
    info: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class DBHealthResponse(BaseModel):
    db: str
    status: str
    dialect: Optional[str] = None
    server_version: Optional[str] = None
    database_name: Optional[str] = None
    uptime: Optional[str] = None
    tables_count: Optional[int] = None
    error: Optional[str] = None

class DiskStatus(BaseModel):
    total_gb: float
    used_gb: float
    free_gb: float
    usage_percent: float

class MemoryStatus(BaseModel):
    total_gb: float
    used_gb: float
    free_gb: float
    usage_percent: float

class CPUStatus(BaseModel):
    usage_percent: float

class ProcessInfo(BaseModel):
    cpu_percent: float
    mem_mb: float
    name: str
    pid: int

class HealthStatusResponse(BaseModel):
    status: str
    app_uptime_seconds: int
    app_uptime: str
    server_uptime_seconds: int
    server_uptime: str
    disk: DiskStatus
    memory: MemoryStatus
    cpu: CPUStatus
    hostname: str
    top_processes : list[ProcessInfo]

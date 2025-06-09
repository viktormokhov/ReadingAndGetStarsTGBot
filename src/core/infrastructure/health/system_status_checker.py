import socket
import time
from typing import Any

import psutil

from src.core.application.interfaces.health_providers import SystemStatusChecker

START_TIME: float = time.time()


class DefaultSystemStatusChecker(SystemStatusChecker):
    """
    Стандартная реализация проверки состояния сервера и приложения.

    Позволяет получить информацию об аптайме приложения и сервера, диске, памяти, процессоре,
    топ-процессах, имени хоста.
    """
    async def get_status(self) -> dict[str, Any]:
        now: float = time.time()

        # Аптайм приложения
        app_uptime_seconds: int = int(now - START_TIME)
        app_uptime: str = self.format_uptime(app_uptime_seconds)

        # Аптайм cсервера
        boot_time: float = psutil.boot_time()
        server_uptime_seconds: int = int(now - boot_time)
        server_uptime: str = self.format_uptime(server_uptime_seconds)

        # Диск
        disk = psutil.disk_usage('/')
        disk_total_gb: float = round(disk.total / (1024 ** 3), 2)
        disk_used_gb: float = round(disk.used / (1024 ** 3), 2)
        disk_free_gb: float = round(disk.free / (1024 ** 3), 2)
        disk_percent: float = disk.percent

        # Память
        mem = psutil.virtual_memory()
        mem_total_gb: float = round(mem.total / (1024 ** 3), 2)
        mem_used_gb: float = round(mem.used / (1024 ** 3), 2)
        mem_free_gb: float = round(mem.available / (1024 ** 3), 2)
        mem_percent: float = mem.percent

        # CPU
        cpu_percent: float = psutil.cpu_percent(interval=0.1)
        cpu_per_core: list[float] = psutil.cpu_percent(percpu=True, interval=0.1)

        # Имя хоста и IP
        hostname: str = socket.gethostname()

        # Топ-5 процессов по памяти
        processes: list[dict[str, Any]] = []
        try:
            proc_iter = list(psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']))
            proc_iter.sort(key=lambda p: getattr(p.info['memory_info'], 'rss', 0), reverse=True)
            for proc in proc_iter[:5]:
                mem_mb = round(getattr(proc.info['memory_info'], 'rss', 0) / (1024 ** 2), 2)
                processes.append({
                    "pid": proc.info['pid'],
                    "name": proc.info['name'],
                    "mem_mb": mem_mb,
                    "cpu_percent": proc.info['cpu_percent']
                })
        except Exception:
            pass

        return {
            "status": "ok",
            "app_uptime_seconds": app_uptime_seconds,
            "app_uptime": app_uptime,
            "server_uptime_seconds": server_uptime_seconds,
            "server_uptime": server_uptime,
            "disk": {
                "total_gb": disk_total_gb,
                "used_gb": disk_used_gb,
                "free_gb": disk_free_gb,
                "usage_percent": disk_percent
            },
            "memory": {
                "total_gb": mem_total_gb,
                "used_gb": mem_used_gb,
                "free_gb": mem_free_gb,
                "usage_percent": mem_percent
            },
            "cpu": {
                "usage_percent": cpu_percent,
                "per_core_percent": cpu_per_core
            },
            "hostname": hostname,
            "top_processes": processes
        }

    def format_uptime(self, seconds: int) -> str:
        """
        Форматирует время в секундах в строку вида "Xd Xh Xm Xs".

        :param seconds: Количество секунд.
        :return: Форматированное время.
        """
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{days}d {hours}h {minutes}m {seconds}s"

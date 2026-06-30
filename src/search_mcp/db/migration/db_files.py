from pathlib import Path

from search_mcp.file_manager import FileManager

class DatabaseFiles:
    __file_manager = FileManager()
    __db_path: Path = __file_manager.create_data("db") / "app.db"

    @classmethod
    def get_db_path(cls) -> Path:
        return cls.__db_path

    @classmethod
    def get_db_path_sqlite(cls) -> str:
        return f"sqlite:///{cls.get_db_path()}"

    @classmethod
    def get_db_path_mcp(cls) -> str:
        return f"sqlite+aiosqlite:///{cls.get_db_path()}"

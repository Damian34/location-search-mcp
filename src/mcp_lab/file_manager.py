import os
import shutil
from pathlib import Path
from typing import AnyStr, List

class FileManager:
    __RESOURCES_DIR = "data"

    def create_data(self, folders: List[str] | str | None = None) -> Path:
        if folders is None:
            folder_list = []
        else:
            folder_list = folders if isinstance(folders, list) else [folders]

        project_dir = self.get_project_dir()
        self.create_folder(project_dir, [FileManager.__RESOURCES_DIR, *folder_list])
        return project_dir / self.__RESOURCES_DIR / Path(*folder_list)

    def create_folder(self, path: Path, folders: List[str] | str):
        folders = folders if isinstance(folders, list) else [folders]
        for folder in folders:
            path = path / folder
            path.mkdir(exist_ok=True)

    def get_project_dir(self) -> Path:
        path = self.get_path_dir(__file__)
        return path.parent.parent

    def get_path_dir(self, cls: os.PathLike[AnyStr]) -> Path:
        file = os.path.abspath(cls)
        folder = os.path.dirname(file)
        return Path(folder)

    def remove_path(self, path: str | Path):
        path = Path(path)
        project_dir = self.get_project_dir()
        if str(project_dir).startswith(str(path.resolve())):
            raise ValueError(f"Cannot remove project directory: {project_dir}")

        try:
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)
        except FileNotFoundError:
            pass

    def exist_file(self, folder: str | Path, prefix_file_name: str) -> Path | None:
        folder = Path(folder)
        if not folder.is_dir():
            return None

        for f in folder.iterdir():
            if f.is_file() and f.name.startswith(prefix_file_name):
                return f

        return None

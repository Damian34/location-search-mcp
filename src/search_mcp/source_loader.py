from datetime import date
from pathlib import Path
from zipfile import ZipFile

import requests
from bs4 import BeautifulSoup

from search_mcp.file_manager import FileManager


class SourceLoader:
    __DATA_FOLDER = "raw"
    __URL = "https://eteryt.stat.gov.pl/eTeryt/rejestr_teryt/udostepnianie_danych/baza_teryt/uzytkownicy_indywidualni/pobieranie/pliki_pelne.aspx"

    def __init__(self):
        self.__file_manger = FileManager()

    def download_terc(self) -> Path | None:
        return self.__download("TERC")

    def download_ulic(self) -> Path | None:
        return self.__download("ULIC")

    def download_simc(self) -> Path | None:
        return self.__download("SIMC")

    def __download(self, name: str) -> Path | None:
        event_target = f"ctl00$body$B{name}AdresowyPobierz"
        folder_path = self.__file_manger.create_data(SourceLoader.__DATA_FOLDER)

        exists_last_file = self.__file_manger.exist_file(folder_path, f"{name}_Ad")

        if exists_last_file and self.__is_today_file(exists_last_file):
            return exists_last_file

        file_path = folder_path / f"{name}_Address.zip"
        self.__download_resources(event_target, file_path)
        csv_file = self.__unpack(file_path)

        if exists_last_file and exists_last_file.name != csv_file.name:
            self.__file_manger.remove_path(exists_last_file)

        self.__file_manger.remove_path(file_path)
        return csv_file

    def __download_resources(self, event_target: str, file_path: str | Path):
        url = SourceLoader.__URL
        with requests.Session() as session:
            response = session.get(url)
            soup = BeautifulSoup(response.text, "html.parser")

            viewstate_input = soup.find("input", {"id": "__VIEWSTATE"})
            viewstate = viewstate_input["value"] if viewstate_input else ""
            payload = {
                "__EVENTTARGET": event_target,
                "__EVENTARGUMENT": "",
                "__VIEWSTATE": viewstate
            }
            download = session.post(url, data=payload)
            with open(file_path, "wb") as f:
                f.write(download.content)

    def __unpack(self, file_path: Path) -> Path:
        if not file_path.exists() or not file_path.suffix == ".zip":
            raise ValueError(f"Not found file {file_path} or it isn't a zip")

        extract_dir = file_path.parent

        with ZipFile(file_path, "r") as zip_ref:
            csv_files = [f for f in zip_ref.namelist() if f.lower().endswith(".csv")]
            if not csv_files:
                raise ValueError(f"Not found CSV in archive {file_path}")

            csv_file = csv_files[0]
            zip_ref.extract(csv_file, path=extract_dir)

        return extract_dir / csv_file

    def __is_today_file(self, file_path: Path) -> bool:
        today = date.today().isoformat()
        return today in file_path.name

    def get_raw_data_folder(self) -> Path:
        return self.__file_manger.create_data(SourceLoader.__DATA_FOLDER)


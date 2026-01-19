from typing import Iterable

from mcp_lab.source_loader import SourceLoader
from mcp_lab.db.records import Province, District, Municipality, Locality, Street


class SourceReader:
    def __init__(self, source_loader: SourceLoader):
        self.__source_loader = source_loader

    # TERC
    def get_locations_terc(self) -> tuple[Iterable[Province], Iterable[District], Iterable[Municipality]]:
        terc = self.__source_loader.download_terc()
        woj, pow, gmi, rodz, nazwa, typ = 0, 1, 2, 3, 4, 5

        def provinces_gen():
            with open(terc, "r") as f:
                next(f)
                for line in f:
                    if not line.strip():
                        continue
                    cels = line.split(";")
                    if cels[woj] and not cels[pow] and not cels[gmi] and not cels[rodz]:
                        yield Province(id=cels[woj], name=cels[nazwa].capitalize())

        def districts_gen():
            with open(terc, "r") as f:
                next(f)
                for line in f:
                    if not line.strip():
                        continue
                    cels = line.split(";")
                    if cels[woj] and cels[pow] and not cels[gmi] and not cels[rodz]:
                        yield District(
                            id=f"{cels[woj]}{cels[pow]}",
                            province_id=cels[woj],
                            name=cels[nazwa],
                            type=cels[typ]
                        )

        def municipalities_gen():
            with open(terc, "r") as f:
                next(f)
                for line in f:
                    if not line.strip():
                        continue
                    cels = line.split(";")
                    if cels[woj] and cels[pow] and cels[gmi] and cels[rodz]:
                        yield Municipality(
                            id=f"{cels[woj]}{cels[pow]}{cels[gmi]}{cels[rodz]}",
                            district_id=f"{cels[woj]}{cels[pow]}",
                            name=cels[nazwa],
                            type=cels[typ]
                        )

        return provinces_gen(), districts_gen(), municipalities_gen()

    # SMIC
    def get_locations_smic(self) -> Iterable[Locality]:
        simc = self.__source_loader.download_simc()
        woj, pow, gmi, rodz, nazwa, sym, sympod = 0, 1, 2, 3, 6, 7, 8

        with open(simc, "r") as f:
            next(f)
            for line in f:
                if not line.strip():
                    continue
                else:
                    cels = line.split(';')
                    yield Locality(
                        id=cels[sym],
                        municipality_id=f"{cels[woj]}{cels[pow]}{cels[gmi]}{cels[rodz]}",
                        name=cels[nazwa]
                    )

    # ULIC
    def get_locations_ulic(self) -> Iterable[Street]:
        ulic = self.__source_loader.download_ulic()
        woj, pow, gmi, rodz, sym, sym_ul, cecha, nazwa_1, nazwa_2 = 0, 1, 2, 3, 4, 5, 6, 7, 8

        with open(ulic, "r") as f:
            next(f)
            for line in f:
                if not line.strip():
                    continue
                else:
                    cels = line.split(';')
                    yield Street(
                        id=f"{cels[sym]}_{cels[sym_ul]}",
                        locality_id=cels[sym],
                        prefix=cels[cecha],
                        name=f"{cels[nazwa_2]} {cels[nazwa_1]}" if cels[nazwa_2] else cels[nazwa_1]
                    )

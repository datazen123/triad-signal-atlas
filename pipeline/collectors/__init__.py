"""Registry of collectors. To add one: write a module with NAME, TITLE, EVERY_DAYS,
SOURCE_URL, collect(prev) -> dict and validate(payload, prev) -> list[str], then list it here."""
from . import (celestrak_satcat, comtrade_mirror, federal_register, link_health,
               nobel_bridges, openalex_coauthor, portwatch, undesa_migrants)

ALL = [openalex_coauthor, nobel_bridges, federal_register, comtrade_mirror,
       portwatch, celestrak_satcat, undesa_migrants, link_health]

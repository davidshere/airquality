import dataclasses
from typing import Tuple

@dataclasses.dataclass
class AQILevel:
    level_name: str
    conc_low: float
    conc_high: float
    aqi_low: int
    aqi_high: int

LEVELS_25 = [
    AQILevel('Good', 0, 12, 0, 50),
    AQILevel('Moderate', 12.1, 35.4, 51, 100),
    AQILevel('USG', 35.5, 55.4, 101, 150),
    AQILevel('Unhealthy', 55.5, 150.4, 151, 200),
    AQILevel('Very Unhealthy', 150.5, 250.4, 201, 300),
    AQILevel('Hazardous', 250.5, 500.4, 301, 500)
]

LEVELS_25_MAP = {
    (level.conc_low, level.conc_high): level
    for level in LEVELS_25
}

def get_aqi(conc, level_map) -> Tuple[float, AQILevel]:
    for low, high in level_map:
        if conc > high:
            continue
        else:
            break
    level = level_map[(low, high)]
    aqi = ((level.aqi_high - level.aqi_low)/(level.conc_high-level.conc_low)) * (conc - level.conc_low) + level.aqi_low
    return aqi, level 

if __name__ == "__main__":

    print(get_aqi(20, LEVELS_25_MAP))
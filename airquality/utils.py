import dataclasses
from typing import Tuple

class Particle:
    TWO_POINT_FIVE = '2.5'
    TEN = '10'

@dataclasses.dataclass
class AQILevel:
    level_name: str
    conc_low: float
    conc_high: float
    aqi_low: int
    aqi_high: int

AQI_BREAKPOINTS = [
    ('Good', 0, 50),
    ('Moderate', 51, 100),
    ('USG', 101, 150),
    ('Unhealth', 151, 200),
    ('Very Unhealthy', 201, 300),
    ('Hazardous', 301, 500)
]

LEVELS_25 = [
    (0, 12),
    (12.1, 35.4),
    (35.5, 55.4),
    (55.5, 150.4),
    (150.5, 250.4),
    (250.5, 500.4)
]

LEVELS_10 = [
    (0, 54),
    (55, 154),
    (155, 254),
    (255, 354),
    (355, 424),
    (425, 604),
]

def get_aqi(conc: float, particle: Particle) -> float:
    if particle == Particle.TWO_POINT_FIVE:
        levels = LEVELS_25
        conc = round(conc, 1)
    else:
        levels = LEVELS_10
        conc = round(conc)

    aqi_levels = [
        AQILevel(breaks[0], lvl[0], lvl[1], breaks[1], breaks[2])
        for breaks, lvl in zip(AQI_BREAKPOINTS, LEVELS_25)
    ]

    for level in aqi_levels:
        if conc > level.conc_high:
            continue
        else:
            break
    aqi = ((level.aqi_high - level.aqi_low)/(level.conc_high-level.conc_low)) * (conc - level.conc_low) + level.aqi_low
    return round(aqi)

if __name__ == "__main__":

    print(get_aqi(20, LEVELS_25))
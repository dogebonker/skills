from abc import ABC, abstractmethod

LEGACY_BANDS = ((0, 0.31), (250, 0.27), (1000, 0.22))


class Tariff(ABC):
    @abstractmethod
    def charge(self, kwh: float) -> float: ...


class FlatTariff(Tariff):
    def __init__(self, rate: float) -> None:
        self.rate = rate

    def charge(self, kwh: float) -> float:
        return round_kwh(kwh) * self.rate


def round_kwh(kwh: float) -> float:
    if kwh < 0:
        raise ValueError(f"negative consumption {kwh}")
    return round(kwh, 3)


def legacy_band_rate(kwh: float) -> float:
    rate = LEGACY_BANDS[0][1]
    for floor, band_rate in LEGACY_BANDS:
        if kwh >= floor:
            rate = band_rate
    return rate

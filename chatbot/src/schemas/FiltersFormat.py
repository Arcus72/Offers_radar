from typing import Literal, List, Optional, TypeVar, Generic
from pydantic import BaseModel, Field, model_validator

Heating = Literal["miejskie", "gazowe", "elektryczne", "pompa ciepła", "piecowe", "inne"]
BuildingMaterial = Literal["cegła", "płyta", "pustak", "beton", "silikat", "mieszany", "drewno", "inne"]
KitchenType = Literal["aneks kuchenny", "osobna"]
Condition = Literal["do zamieszkania", "do remontu", "do odświeżenia", "do wykończenia"]
Parking = Literal["garaż podziemny", "garaż", "miejsce postojowe", "parking ogólnodostępny", "inne"]
BuildingType = Literal["blok", "apartamentowiec", "kamienica", "szeregowiec", "dom", "inne"]

T = TypeVar("T", int, float)


class RangeValue(BaseModel, Generic[T]):
    """Zakres wartości liczbowych (int/float)."""

    min_value: Optional[T] = Field(
        default=None,
        description="Dla wyrażeń typu 'od X', 'min X', 'co najmniej X'.",
    )
    exact_value: Optional[T] = Field(
        default=None,
        description="Dokładna liczba (np. '3 pokoje'->3, 'piętro 1'->1, 'parter'->0). 0 to poprawna liczba!",
    )
    max_value: Optional[T] = Field(
        default=None,
        description="Dla wyrażeń typu 'do X', 'max X', 'maksymalnie X'.",
    )

    @model_validator(mode="after")
    def normalize(self) -> "RangeValue[T]":
        """min bez max → exact."""
        if self.exact_value is None and self.min_value is not None:
            if self.max_value is None or self.min_value == self.max_value:
                self.exact_value = self.min_value
                self.min_value = None
                self.max_value = None
        return self


RangeInt = RangeValue[int]
RangeFloat = RangeValue[float]


class FiltersFormat(BaseModel):

    type: List[str] | None = Field(default=None, description="Rodzaj nieruchomości (np. mieszkanie, dom, działka, lokal).")
    city: List[str] | None = Field(default=None, description="Miasto / miasta.")
    district: List[str] | None = Field(default=None, description="Dzielnica / dzielnice.")
    street: List[str] | None = Field(default=None, description="Ulica / ulice.")
    price: RangeInt | None = Field(default=None, description="Cena w zł.")
    area: RangeFloat | None = Field(default=None, description="Powierzchnia w m².")
    rooms: RangeFloat | None = Field(default=None, description="Liczba pokoi.")
    bed_rooms: RangeFloat | None = Field(default=None, description="Liczba sypialni.")
    bathrooms: RangeFloat | None = Field(default=None, description="Liczba łazienek.")
    floor: RangeFloat | None = Field(default=None, description="Piętro (parter = exact_value: 0).")
    building_floors: RangeFloat | None = Field(default=None, description="Liczba pięter w budynku.")
    building_type: BuildingType | None = Field(default=None, description="Typ budynku.")
    building_material: BuildingMaterial | None = Field(default=None, description="Materiał budynku (wielka płyta -> płyta, żelbet -> beton).")
    build_year: RangeFloat | None = Field(default=None, description="Rok budowy.")
    interior_description: str | None = Field(default=None, description="Preferowany styl/stan wnętrza (np. jasne, nowoczesne).")
    lift: bool | None = Field(default=None, description="Winda w budynku.")
    kitchen_type: KitchenType | None = Field(default=None, description="Rodzaj kuchni.")
    condition: Condition | None = Field(default=None, description="Stan mieszkania.")
    has_balcony: bool | None = Field(default=None, description="Balkon, taras lub loggia.")
    balcony_area: RangeFloat | None = Field(default=None, description="Powierzchnia balkonu/tarasu w m².")
    storage_room: bool | None = Field(default=None, description="Piwnica lub komórka lokatorska.")
    parking: Parking | None = Field(default=None, description="Rodzaj miejsca parkingowego.")
    heating: Heating | None = Field(default=None, description="Rodzaj ogrzewania.")
    accessible: bool | None = Field(default=None, description="Udogodnienia dla niepełnosprawnych.")
    fenced: bool | None = Field(default=None, description="Ogrodzony teren.")
    monitoring: bool | None = Field(default=None, description="Monitoring / ochrona.")
    rent_fee: RangeInt | None = Field(default=None, description="Czynsz administracyjny w zł.")
    school: bool | None = Field(default=None, description="Bliskość szkoły.")
    school_dist: RangeInt | None = Field(default=None, description="Maksymalna odległość do szkoły (m).")
    kindergarten: bool | None = Field(default=None, description="Bliskość przedszkola/żłobka.")
    kindergarten_dist: RangeInt | None = Field(default=None, description="Maksymalna odległość do przedszkola (m).")
    university: bool | None = Field(default=None, description="Bliskość uczelni wyższej.")
    university_dist: RangeInt | None = Field(default=None, description="Maksymalna odległość do uczelni (m).")
    shop: bool | None = Field(default=None, description="Bliskość sklepu/supermarketu.")
    shop_dist: RangeInt | None = Field(default=None, description="Maksymalna odległość do sklepu (m).")
    public_transport: bool | None = Field(default=None, description="Bliskość przystanku zbiorkomu.")
    public_transport_dist: RangeInt | None = Field(default=None, description="Maksymalna odległość do przystanku (m).")
    park: bool | None = Field(default=None, description="Bliskość parku/terenów zielonych.")
    park_dist: RangeInt | None = Field(default=None, description="Maksymalna odległość do parku (m).")
    medical: bool | None = Field(default=None, description="Bliskość przychodni/szpitala.")
    medical_dist: RangeInt | None = Field(default=None, description="Maksymalna odległość do przychodni (m).")
    pharmacy: bool | None = Field(default=None, description="Bliskość apteki.")
    pharmacy_dist: RangeInt | None = Field(default=None, description="Maksymalna odległość do apteki (m).")
    city_center: bool | None = Field(default=None, description="Bliskość centrum miasta.")
    city_center_dist: RangeInt | None = Field(default=None, description="Maksymalna odległość do centrum (m).")

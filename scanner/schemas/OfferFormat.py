from pydantic import BaseModel, Field, field_validator
from typing import Literal
from datetime import date
import re

Heating = Literal["miejskie", "gazowe", "elektryczne", "pompa ciepła", "piecowe", "inne"]
BuildingMaterial = Literal["cegła", "płyta", "pustak", "beton", "silikat", "mieszany", "drewno", "inne"]
KitchenType = Literal["aneks kuchenny", "osobna"]
Condition = Literal["do zamieszkania", "do remontu", "do odświeżenia", "do wykończenia"]
Parking = Literal["garaż podziemny", "garaż", "miejsce postojowe", "parking ogólnodostępny", "inne"]
BuildingType = Literal["blok", "apartamentowiec", "kamienica", "szeregowiec", "dom", "inne"]

class ResponseFormat(BaseModel):
    added_date: date | None = Field(description="Wartość pola 'Data dodania' z parametrów szczegółowych, przepisana bez zmian w formacie RRRR-MM-DD")
    type: str | None = Field(description="Rodzaj nieruchomości z tytułu ogłoszenia: mieszkanie, dom, działka lub lokal")
    city: str | None = Field(description="Miasto: pierwszy element pola Localization")
    district: str | None = Field(description="Dzielnica: elementy pola Localization między miastem a ulicą. null, jeśli pole zawiera tylko miasto i ulicę")
    street: str | None = Field(description="Ulica: ostatni element pola Localization po ostatnim przecinku, np. 'Wrocław, Psie Pole, Bagienna' -> Bagienna")
    area: float | None = Field(description="Wartość pola 'Powierzchnia' w m² jako liczba z kropką dziesiętną, np. '44,00 m²' -> 44.0")
    rooms: int | None = Field(description="Wartość pola 'Liczba pokoi'")
    bed_rooms: int | None = Field(description="Liczba sypialni, tylko jeśli wynika z opisu")
    bathrooms: int | None = Field(description="Liczba łazienek, tylko jeśli wynika z opisu")
    floor: int | None = Field(description="Numer piętra z pola 'Piętro'. Słowo 'parter' to zawsze 0, '1 piętro' to 1, '2 piętro' to 2")
    building_floors: int | None = Field(description="Liczba pięter w budynku, np. 'czteropiętrowy budynek' -> 4")
    building_type: BuildingType | None = Field(description="Typ budynku z pola 'Typ budynku'. Wybierz najbliższą wartość z listy; 'inne' jeśli żadna nie pasuje, null jeśli brak informacji.")
    building_material: BuildingMaterial | None = Field(description="Materiał budynku, tylko jeśli podano w ogłoszeniu. Wybierz najbliższą wartość z listy (wielka płyta -> płyta, żelbet -> beton); 'inne' jeśli żadna nie pasuje, null jeśli brak informacji.")
    build_year: int | None = Field(description="Rok budowy")
    interior_description: str | None = Field(description="Krótki opis wyglądu wnętrza na podstawie ogłoszenia, np. jasne, przestronne, nowoczesne, ciemne, wymaga odświeżenia. Bez treści marketingowych.")
    lift: bool | None = Field(description="Czy w budynku jest winda: true, jeśli jest; false, jeśli napisano, że jej nie ma (np. 'bez windy')")
    kitchen_type: KitchenType | None = Field(description="Rodzaj kuchni: 'aneks kuchenny' (także kuchnia otwarta lub połączona z salonem) albo 'osobna'. null jeśli brak informacji.")
    condition: Condition | None = Field(description="Stan mieszkania, tylko jeśli wynika z ogłoszenia. Wybierz wartość z listy, w przeciwnym razie null.")
    has_balcony: bool | None = Field(description="Czy mieszkanie ma balkon, taras lub loggię: true, jeśli jest; false, jeśli napisano, że go nie ma. null, jeśli ogłoszenie o tym nie wspomina")
    balcony_area: float | None = Field(description="Powierzchnia balkonu lub tarasu w m², tylko jeśli podano ją liczbą. Sama wzmianka 'balkon' bez powierzchni -> null")
    storage_room: bool | None = Field(description="Czy do mieszkania przynależy komórka lokatorska lub piwnica")
    parking: Parking | None = Field(description="Miejsce parkingowe. Wybierz najbliższą wartość z listy ('miejsce postojowe' to przypisane miejsce naziemne); 'inne' jeśli żadna nie pasuje, null, jeśli ogłoszenie o nim nie wspomina")
    heating: Heating | None = Field(description="Rodzaj ogrzewania. Wybierz najbliższą wartość z listy; 'inne' jeśli żadna nie pasuje, null jeśli brak informacji.")
    accessible: bool | None = Field(description="Czy budynek jest przystosowany dla osób niepełnosprawnych (np. podjazd, brak barier). null, jeśli ogłoszenie o tym nie pisze")
    fenced: bool | None = Field(description="Czy teren jest ogrodzony")
    monitoring: bool | None = Field(description="Czy budynek jest monitorowany")
    rent_fee: int | None = Field(description="Miesięczny czynsz administracyjny (zł) jako liczba całkowita")
    school: bool | None = Field(description="Czy w okolicy jest szkoła podstawowa lub średnia")
    school_dist: int | None = Field(description="Odległość do najbliższej szkoły w metrach, tylko jeśli podano ją w ogłoszeniu; dla zakresu większa wartość, np. '100-200 m' -> 200")
    kindergarten: bool | None = Field(description="Czy w okolicy jest przedszkole lub żłobek")
    kindergarten_dist: int | None = Field(description="Odległość do najbliższego przedszkola lub żłobka w metrach, tylko jeśli podano ją w ogłoszeniu; dla zakresu większa wartość, np. '100-200 m' -> 200")
    university: bool | None = Field(description="Czy w okolicy jest uczelnia wyższa")
    university_dist: int | None = Field(description="Odległość do najbliższej uczelni wyższej w metrach, tylko jeśli podano ją w ogłoszeniu; dla zakresu większa wartość, np. '100-200 m' -> 200")
    shop: bool | None = Field(description="Czy w okolicy jest sklep spożywczy lub supermarket")
    shop_dist: int | None = Field(description="Odległość do najbliższego sklepu w metrach, tylko jeśli podano ją w ogłoszeniu; dla zakresu większa wartość, np. '100-200 m' -> 200")
    public_transport: bool | None = Field(description="Czy w okolicy jest przystanek komunikacji miejskiej")
    public_transport_dist: int | None = Field(description="Odległość do najbliższego przystanku w metrach, tylko jeśli podano ją w ogłoszeniu; dla zakresu większa wartość, np. '100-200 m' -> 200")
    park: bool | None = Field(description="Czy w okolicy jest park lub teren zielony")
    park_dist: int | None = Field(description="Odległość do najbliższego parku lub terenu zielonego w metrach, tylko jeśli podano ją w ogłoszeniu; dla zakresu większa wartość, np. '100-200 m' -> 200")
    medical: bool | None = Field(description="Czy w okolicy jest przychodnia lub szpital")
    medical_dist: int | None = Field(description="Odległość do najbliższej przychodni lub szpitala w metrach, tylko jeśli podano ją w ogłoszeniu; dla zakresu większa wartość, np. '100-200 m' -> 200")
    pharmacy: bool | None = Field(description="Czy w okolicy jest apteka")
    pharmacy_dist: int | None = Field(description="Odległość do najbliższej apteki w metrach, tylko jeśli podano ją w ogłoszeniu; dla zakresu większa wartość, np. '100-200 m' -> 200")
    city_center: bool | None = Field(description="Czy nieruchomość jest blisko centrum miasta, np. rynku lub głównej ulicy")
    city_center_dist: int | None = Field(description="Odległość do centrum miasta w metrach, tylko jeśli podano ją w ogłoszeniu; dla zakresu większa wartość, np. '100-200 m' -> 200")

class OfferFormat(ResponseFormat):
    title: str | None = Field(description="Tytuł ogłoszenia przepisany bez zmian")
    price: int | None = Field(description="Cena nieruchomości w zł jako liczba całkowita bez spacji, np. '359 000 zł' -> 359000")
    offer_id: int
    main_img_url: str | None = ""
    market_price: int | None = None

    @field_validator("price",  mode="before")
    @classmethod
    def parse_int(cls, v):
        if isinstance(v, str):
            digits = re.sub(r"\D", "", v.split(",")[0])
            return int(digits) if digits else None
        return v
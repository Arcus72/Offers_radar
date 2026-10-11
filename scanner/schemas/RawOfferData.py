from pydantic import BaseModel, field_validator
import re

class RawOfferData(BaseModel):
    offer_id: int
    title: str | None
    price: float| None
    main_img_url: str| None
    unstructured_desc: str| None

    @field_validator("price", mode="before")
    @classmethod
    def parse_price(cls, v):
        if isinstance(v, str):
            digits = re.sub(r"\D", "", v.split(",")[0])
            return float(digits) if digits else None
        return v

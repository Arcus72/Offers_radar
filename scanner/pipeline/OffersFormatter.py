from components.LlmFormatter import LlmFormatter
from schemas.OfferFormat import OfferFormat, ResponseFormat
from pipeline.PipelineTemplate import PipelineTemplate

class OffersFormatter(PipelineTemplate):
    TABLE = "offers"
    RAW_TABLE = "raw_offers"


    def __init__(self,db):
        self.db = db
        self.llm_formatter = LlmFormatter(ResponseFormat)
        self.raw_offers: list[dict] = []
        self.structured_offers: list[OfferFormat] = []

    def extract(self):
        self.raw_offers = self.db.get_all_data(self.RAW_TABLE)
     

    def transform(self, save_to_db: bool = True):
        for offer_i, offer in enumerate(self.raw_offers, start=1):
            print(f"Formatting: {offer_i}/{len(self.raw_offers)}")
            unstructured_desc = offer.get("unstructured_desc", "")

            try:
                if unstructured_desc:
                    formatted_desc = self.llm_formatter.format(unstructured_desc).model_dump()
                else:
                    formatted_desc = dict.fromkeys(ResponseFormat.model_fields)

                row = OfferFormat(
                    **formatted_desc,
                    offer_id=str(offer["offer_id"]),
                    main_img_url=offer["main_img_url"],
                    title=offer["title"],
                    price=offer["price"],
                )
            except Exception as e:
                # one bad LLM answer must not lose the whole batch; the offer is retried on the next run
                print(f"Formatting failed for offer {offer['offer_id']}. Skipping. {e}")
                continue

            if save_to_db:
                self.db.insert(row, table=self.TABLE)
            else:
                self.structured_offers.append(row)

    

    def load(self):
        return

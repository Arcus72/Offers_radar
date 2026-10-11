from __future__ import annotations
import time
import requests
from bs4 import BeautifulSoup
from schemas.RawOfferData import RawOfferData
from schemas.OfferFormat import OfferFormat

class OffersScraper:
	SELECTORS = {
	"title": ".t_o5gR4J",
	"price": ".t_yBEtHn",
	"description": ".t_1HMhyB",
	"basic_params": ".t_KgnU-a",
	"detailed_params": ".t_-deJfz",
	"localization": ".t_DfKH5W",
	"main_img": ".t_-nZCVz img"
	}

	def __init__(self, html: str | bytes, offer_id:str):
		self.soup = BeautifulSoup(html, "html.parser")
		self.offer_id = offer_id

	HEADERS = {
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
					  "(KHTML, like Gecko) Chrome/129.0 Safari/537.36",
		"Accept-Language": "pl-PL,pl;q=0.9,en;q=0.8",
	}

	@classmethod
	def _fetch(cls, url: str, attempts: int = 3) -> bytes | None:
		for attempt in range(1, attempts + 1):
			try:
				response = requests.get(url, headers=cls.HEADERS, timeout=15)
				response.raise_for_status()
				return response.content
			except requests.exceptions.RequestException as e:
				print(f"Request failed (attempt {attempt}/{attempts}): {e}")
				if attempt == attempts:
					return None
				time.sleep(2)

		return None

	@classmethod
	def from_offer_id(cls, offer_id: str | int, attempts: int = 3) -> OffersScraper | None:
		html = cls._fetch(f"https://tabelaofert.pl/oferta/x,{offer_id}", attempts)
		return cls(html, offer_id) if html is not None else None

	@classmethod
	def get_status_code(cls, offer_id: str | int) -> int | None:
		try:
			return requests.get(f"https://tabelaofert.pl/oferta/x,{offer_id}", headers=cls.HEADERS, timeout=15).status_code
		except requests.exceptions.RequestException:
			return None

	@classmethod
	def get_offers(cls, url:str, attempts: int = 3) -> list[str] | None:
		html = cls._fetch(url, attempts)
		if html is None:
			return None

		soup = BeautifulSoup(html, "html.parser")
		link_el = ".t_DFuFiS"
		links = soup.select(link_el)
		hrefs = ["https://tabelaofert.pl"+link.get("href") for link in links]
		return hrefs

	def _text(self, key: str) -> str | None:
		element = self.soup.select_one(self.SELECTORS[key])
		return element.get_text(strip=True) if element else None

	def _texts(self, key: str) -> list[str]:
		return [el.get_text(" - ", strip=True) for el in self.soup.select(self.SELECTORS[key])]

	def get_main_img_url(self) -> str:
		img = self.soup.select_one(self.SELECTORS["main_img"])
		if img:
			return img.get("src")
		return  ""

	def get_price(self) -> int | None:
		return OfferFormat.parse_int(self._text("price"))

	def get_all_data(self) -> RawOfferData:
		
		return {
			"offer_id": self.offer_id,
			"title": self._text("title"),
			"price": self._text("price"),
			"main_img_url": self.get_main_img_url(),
			"unstructured_desc": self.get_description()
		}

 
	def get_description(self) -> str:
		lines = [
			f"1. Localization: {self._text('localization')}",
			"2. Basic Parameters:",
			*self._texts('basic_params'),
			"",
			"3. Detailed Parameters:",
			*self._texts('detailed_params'),
			f"4. Description:\n {self._text('description')}\n"
		]

		return "\n".join(lines)


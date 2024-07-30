import asyncio
from collections import defaultdict
import json
from pathlib import Path
import re
from typing import List, Optional
from urllib.parse import urlencode
from scrapfly import ScrapflyClient, ScrapeConfig, ScrapeApiResponse
from parsel import Selector

scrapfly = ScrapflyClient(key=" scp-live-b0d3f03835104405bf5357abfb4c691a ")

async def request_hotels_page(
    query,
    checkin: str = "",
    checkout: str = "",
    number_of_rooms=1,
    offset: int = 0,
):
    """scrapes a single hotel search page of booking.com"""
    checkin_year, checking_month, checking_day = checkin.split("-") if checkin else "", "", ""
    checkout_year, checkout_month, checkout_day = checkout.split("-") if checkout else "", "", ""

    url = "https://www.booking.com/searchresults.html"
    url += "?" + urlencode(
        {
            "ss": query,
            "checkin_year": checkin_year,
            "checkin_month": checking_month,
            "checkin_monthday": checking_day,
            "checkout_year": checkout_year,
            "checkout_month": checkout_month,
            "checkout_monthday": checkout_day,
            "no_rooms": number_of_rooms,
            "offset": offset,
        }
    )
    return await scrapfly.async_scrape(ScrapeConfig(url, country="US"))


def parse_search_total_results(html: str):
    sel = Selector(text=html)
    # parse total amount of pages from heading1 text:
    # e.g. "London: 1,232 properties found"
    total_results = int(sel.css("h1").re("([\d,]+) properties found")[0].replace(",", ""))
    return total_results


def parse_search_hotels(html: str):
    sel = Selector(text=html)

    hotel_previews = {}
    for hotel_box in sel.xpath('//div[@data-testid="property-card"]'):
        url = hotel_box.xpath('.//h3/a[@data-testid="title-link"]/@href').get("").split("?")[0]
        hotel_previews[url] = {
            "name": hotel_box.xpath('.//h3/a[@data-testid="title-link"]/div/text()').get(""),
            "location": hotel_box.xpath('.//span[@data-testid="address"]/text()').get(""),
            "score": hotel_box.xpath('.//div[@data-testid="review-score"]/div/text()').get(""),
            "review_count": hotel_box.xpath('.//div[@data-testid="review-score"]/div[2]/div[2]/text()').get(""),
            "stars": len(hotel_box.xpath('.//div[@data-testid="rating-stars"]/span').getall()),
            "image": hotel_box.xpath('.//img[@data-testid="image"]/@src').get(),
        }
    return hotel_previews


async def scrape_search(
    query,
    checkin: str = "",
    checkout: str = "",
    number_of_rooms=1,
    max_results: Optional[int] = None,
):
    first_page = await request_hotels_page(
        query=query, checkin=checkin, checkout=checkout, number_of_rooms=number_of_rooms
    )
    hotel_previews = parse_search_hotels(first_page.content)
    total_results = parse_search_total_results(first_page.content)
    if max_results and total_results > max_results:
        total_results = max_results
    other_pages = await asyncio.gather(
        *[
            request_hotels_page(
                query=query,
                checkin=checkin,
                checkout=checkout,
                number_of_rooms=number_of_rooms,
                offset=offset,
            )
            for offset in range(25, total_results, 25)
        ]
    )
    for result in other_pages:
        hotel_previews.update(parse_search_hotels(result.content))
    return hotel_previews


def parse_hotel(html: str):
    sel = Selector(text=html)
    css = lambda selector, sep="": sep.join(sel.css(selector).getall()).strip()
    css_first = lambda selector: sel.css(selector).get("")
    lat, lng = css_first(".show_map_hp_link::attr(data-atlas-latlng)").split(",")
    features = defaultdict(list)
    for feat_box in sel.css("[data-capla-component*=FacilitiesBlock]>div>div>div"):
        type_ = feat_box.xpath('.//span[contains(@data-testid, "facility-group-icon")]/../text()').get()
        feats = [f.strip() for f in feat_box.css("li ::text").getall() if f.strip()]
        features[type_] = feats
    data = {
        "title": css("h2#hp_hotel_name::text"),
        "description": css("div#property_description_content ::text", "\n"),
        "address": css(".hp_address_subtitle::text"),
        "lat": lat,
        "lng": lng,
        "features": dict(features),
        "id": re.findall(r"b_hotel_id:\s*'(.+?)'", html)[0],
    }
    return data


async def scrape_hotels(urls: List[str], price_start_dt: str, price_n_days=30):
    async def scrape_hotel(url: str):
        result = await scrapfly.async_scrape(ScrapeConfig(
            url,
            session=url.split("/")[-1].split(".")[0],
            country="US",
        ))
        hotel = parse_hotel(result.content)
        hotel["url"] = result.context['url']
        csrf_token = re.findall(r"b_csrf_token:\s*'(.+?)'", result.content)[0]
        hotel["price"] = await scrape_prices(csrf_token=csrf_token, hotel_id=hotel["id"], hotel_url=url)
        return hotel

    async def scrape_prices(hotel_id, csrf_token, hotel_url):
        data = {
            "name": "hotel.availability_calendar",
            "result_format": "price_histogram",
            "hotel_id": hotel_id,
            "search_config": json.dumps(
                {
                    # we can adjust pricing configuration here but this is the default
                    "b_adults_total": 2,
                    "b_nr_rooms_needed": 1,
                    "b_children_total": 0,
                    "b_children_ages_total": [],
                    "b_is_group_search": 0,
                    "b_pets_total": 0,
                    "b_rooms": [{"b_adults": 2, "b_room_order": 1}],
                }
            ),
            "checkin": price_start_dt,
            "n_days": price_n_days,
            "respect_min_los_restriction": 1,
            "los": 1,
        }
        result = await scrapfly.async_scrape(
            ScrapeConfig(
                url="https://www.booking.com/fragment.json?cur_currency=usd",
                method="POST",
                data=data,
                headers={"X-Booking-CSRF": csrf_token},
                session=hotel_url.split("/")[-1].split(".")[0],
                country="US",
            )
        )
        return json.loads(result.content)["data"]

    hotels = await asyncio.gather(*[scrape_hotel(url) for url in urls])
    return hotels


async def run():
    out = Path(__file__).parent / "results"
    out.mkdir(exist_ok=True)

    result_hotels = await scrape_hotels(
        ["https://www.booking.com/hotel/gb/gardencourthotel.html"],
        price_start_dt="2023-04-20",
        price_n_days=7,
    )
    out.joinpath("hotels.json").write_text(json.dumps(result_hotels, indent=2, ensure_ascii=False))

    result_search = await scrape_search("London", checkin="2023-04-20", checkout="2023-04-27", max_results=100)
    out.joinpath("search.json").write_text(json.dumps(result_search, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(run())

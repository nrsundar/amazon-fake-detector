"""Amazon Product Advertising API helper."""

from typing import Optional, Dict, Any
import os

try:
    import requests
    from requests_aws4auth import AWS4Auth
except ImportError:  # pragma: no cover - library may not be installed
    requests = None
    AWS4Auth = None


def fetch_product_via_api(asin: str) -> Optional[Dict[str, Any]]:
    """Retrieve product details from Amazon's Product Advertising API.

    This function requires the following environment variables:
    - AMAZON_ACCESS_KEY
    - AMAZON_SECRET_KEY
    - AMAZON_PARTNER_TAG
    - AMAZON_REGION (optional, default ``us-east-1``)
    """
    if requests is None or AWS4Auth is None:
        print("Amazon API libraries are not installed.")
        return None

    access_key = os.getenv("AMAZON_ACCESS_KEY")
    secret_key = os.getenv("AMAZON_SECRET_KEY")
    partner_tag = os.getenv("AMAZON_PARTNER_TAG")
    region = os.getenv("AMAZON_REGION", "us-east-1")

    if not all([access_key, secret_key, partner_tag]):
        print("Amazon API credentials are missing.")
        return None

    endpoint = "https://webservices.amazon.com/paapi5/getitems"
    payload = {
        "ItemIds": [asin],
        "Resources": [
            "ItemInfo.Title",
            "ItemInfo.ByLineInfo",
            "ItemInfo.Features",
            "Offers.Listings.Price",
        ],
        "PartnerTag": partner_tag,
        "PartnerType": "Associates",
    }

    auth = AWS4Auth(access_key, secret_key, region, "ProductAdvertisingAPI")

    try:
        response = requests.post(endpoint, json=payload, auth=auth, timeout=10)
        if response.status_code != 200:
            print(f"Amazon API error: {response.status_code} - {response.text}")
            return None
        data = response.json()
        items = data.get("ItemsResult", {}).get("Items", [])
        if not items:
            return None
        item = items[0]
        info = item.get("ItemInfo", {})
        offers = item.get("Offers", {})
        price = (
            offers.get("Listings", [{}])[0]
            .get("Price", {})
            .get("Amount", 0.0)
        )
        title = info.get("Title", {}).get("DisplayValue", "Amazon Product")
        brand = info.get("ByLineInfo", {}).get("Brand", {}).get("DisplayValue", "Unknown Brand")
        features = info.get("Features", {}).get("DisplayValues", [])
        description = " ".join(features) if features else "No description available"
        return {
            "title": title,
            "description": description,
            "price": price,
            "brand": brand,
            "asin": asin,
            "url": f"https://www.amazon.com/dp/{asin}",
        }
    except Exception as exc:  # pragma: no cover - network call
        print(f"Error calling Amazon API: {exc}")
        return None


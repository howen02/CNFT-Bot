from dotenv import load_dotenv
import os
import requests

# Load environment variables
load_dotenv()

# Retrieve OpenCNFT API key from environment
OPENCNFT_KEY = os.getenv("OPENCNFT_KEY")

# Base URL for OpenCNFT API
BASE_URL = "https://api.opencnft.io/2/"

# Headers for API requests
HEADERS = {
    "X-Api-Key": OPENCNFT_KEY
}

def edit_percent(percentage: float) -> str:
    res = round(percentage * 100) if percentage else "0"

    if percentage > 0:
        return f"+{res}"
    else:
        return res

def to_ada(lovelace: int) -> str:
    return format(round(lovelace / 10**6), ',')

def fetch_data(ext: str) -> dict:
    url = f"{BASE_URL}" + ext
    response = requests.get(url=url, headers=HEADERS)

    return response.json()

def get_market(time_range: str) -> str:
    data = fetch_data(f"market/metrics?time_range={time_range}")
    
    # Unpack data values
    nfts, tx, volume, volume_change, nfts_change, tx_change = data.values()
    
    # Generate output string
    output = (
        f"NFTs sold: {nfts} [ {edit_percent(nfts_change)}% ]\n"
        f"Volume: {to_ada(volume)} ₳ [ {edit_percent(volume_change)}% ]\n"
        f"Transactions: {tx} [ {edit_percent(tx_change)}% ]"
    )
    
    return output

def get_collection_rankings() -> str:
    time_range = "24h"
    data = fetch_data(f"market/rank/collection?time_range={time_range}")['ranking']
    data = data[:5]
    output = ""

    for d in data:
        yesterday_volume = d.get('volume_ystd', 1)

        if yesterday_volume:
            vol_change = d['volume_today'] / d.get('volume_ystd', 1) - 1

        output += (
            f"{d['name']}\n"
            f"Floor: {d['floor_price']} ₳\n"
            "Volume\n"
            f"Today: {d['volume_today']} ₳ [ {edit_percent(vol_change)}% ]\n"
            f"Total: {d['volume']} ₳\n\n"
        )

    return output

def get_search_collection(input: str) -> str:
    projects = {"The Ape Society": "dac355946b4317530d9ec0cb142c63a4b624610786c2a32137d78e25", 
                "Clay Nation": "40fa2aa67258b4ce7b5782f74831d46a84c59a0ff0c28262fab21728", 
                "OREMOB": "062b1da3d344c1e6208ef908b2d308201e7ff6bcfddf0f606249817f", 
                "Toolheads": "285c0b8e91ba323da4ca083c9db837e111dafbf3143ece4d03eba8f4", 
                "Tappy by TapTools": "e3ff4ab89245ede61b3e2beab0443dbcc7ea8ca2c017478e4e8990e2",
                "The Hand by TGT Alpha": "311ce726255e36b230c6315fa89ab952f51e44afc46a458c6852e4ff",
                "Jellycubes - BIG": "3ee441f40fe395a2e98eea1df7cf8816b0fca3d5d164893596ce306d",
                 "Yummi Universe - Naru (main collection)": "b1814c6d3b0f7a42c9ee990c06c9d504a42bb22bf0e34e7908ae21b2",
                 "Tavern Squad": "2d01b3496fd22b1a61e6227c27250225b1186e5ebae7360b1fc5392c",
                 "Goombles": "158fd94afa7ee07055ccdee0ba68637fe0e700d0e58e8d12eca5be46",
                 "Berry": "b863bc7369f46136ac1048adb2fa7dae3af944c3bbb2be2f216a8d4f"
                }

    query = input.lower().replace(" ", "")
    policy = ""
    name = ""
    
    for p in projects:
        if query in p.lower().replace(" ", ""):
            policy = projects[p]
            name = p
    
    if policy:
        data = fetch_data(f"collection/{policy}")
        policy, thumbnail, total_volume, total_tx, total_nfts_sold, minted, holders, highest_sale, floor_price, floor_price_marketplace, marketcap = data.values()

        output = (
            f"{name}\n"
            f"Floor Price: {to_ada(floor_price)} ₳\n"
            f"Total Volume: {to_ada(total_volume)} ₳\n"
            f"Marketcap: {to_ada(marketcap)} ₳\n"
            f"Holders: {format(holders, ',')}\n"
        )
        
        return output
    else:
        return "Project not found"
    
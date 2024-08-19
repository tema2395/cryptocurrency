from pycoingecko import CoinGeckoAPI
import aiohttp
import asyncio


cg = CoinGeckoAPI()


async def get_crypto_price(crypto):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.coingecko.com/api/v3/simple/price?ids={crypto}&vs_currencies=usd"
            ) as response:
                data = await response.json()
                return data[crypto]["usd"]
    except Exception as e:
        print(f"Error fetching price for {crypto}: {e}")
        raise KeyError(f"Unable to fetch price for {crypto}")


async def search_crypto(query):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.coingecko.com/api/v3/search?query={query}"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    filtered_results = [
                        coin
                        for coin in data["coins"]
                        if query.lower() in coin["name"].lower()
                        or query.lower() in coin["symbol"].lower()
                        or query.lower() in coin["id"].lower()
                    ]
                    if not filtered_results:
                        async with session.get(
                            f"https://api.coingecko.com/api/v3/coins/{query.lower()}"
                        ) as direct_response:
                            if direct_response.status == 200:
                                coin_data = await direct_response.json()
                                filtered_results = [
                                    {
                                        "id": coin_data["id"],
                                        "name": coin_data["name"],
                                        "symbol": coin_data["symbol"],
                                    }
                                ]
                    return filtered_results[:5]
                else:
                    print(f"Error searching crypto: Status code {response.status}")
                    return []
    except Exception as e:
        print(f"Error searching crypto: {e}")
        return []

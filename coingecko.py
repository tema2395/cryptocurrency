from pycoingecko import CoinGeckoAPI
import aiohttp
import asyncio


cg = CoinGeckoAPI()


async def get_crypto_price(crypto):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.coingecko.com/api/v3/simple/price?ids={crypto}&vs_currencies=usd") as response:
                data = await response.json()
                return data[crypto]["usd"]
    except Exception as e:
        print(f"Error fetching price for {crypto}: {e}")
        raise KeyError(f"Unable to fetch price for {crypto}")
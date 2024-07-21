from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()


async def get_crypto_price(crypto):
    try:
        data = cg.get_price(ids=crypto, vs_currencies="usd")
        return data[crypto]["usd"]
    except Exception as e:
        print(f"Error fetching price for {crypto}: {e}")
        raise KeyError(f"Unable to fetch price for {crypto}")

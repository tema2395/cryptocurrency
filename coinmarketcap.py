import aiohttp
import json
import os 
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from dotenv import load_dotenv


load_dotenv()
api_key = os.getenv("X-CMC_PRO_API_KEY")



        
        
        
        

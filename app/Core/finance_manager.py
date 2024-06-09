
import aiohttp
from app.models.finance.dollar_enum import Bond, BondTime, DollarCategory
from app.models.finance.dollar_quotes import Exchange
from app.system.constants import URLS
from app.system.log import log
from app.system.utils import fetch
import textwrap

async def get_dollar_quote() -> str:
    url = URLS.CRIPTOYA_API.value + '/dolar'
    try:
        async with aiohttp.ClientSession() as session:
            json_response = await fetch(session, url)
            exchange_data = Exchange(json_response)
            
            official_price = exchange_data.get_price(DollarCategory.OFICIAL.value)
            credit_card_price = exchange_data.get_price(DollarCategory.TARJETA.value)
            blue_price = exchange_data.get_price(DollarCategory.BLUE.value, property='ask')
            crypto_price = exchange_data.get_price(DollarCategory.CRIPTO.value, 'usdt', property='ask')
            mep_gd30_day_price = exchange_data.get_price(DollarCategory.MEP.value, Bond.GD30.value, BondTime.DAY.value)
            ccl_gd30_day_price = exchange_data.get_price(DollarCategory.CCL.value, Bond.GD30.value, BondTime.DAY.value)
            
            result = f'''\
            Cotizaciones del dólar:

            Oficial: ${official_price}
            Tarjeta: ${credit_card_price} 
            Blue: ${blue_price} 
            Cripto (USDT): ${crypto_price} 
            MEP (GD30 24hs): ${mep_gd30_day_price} 
            CCL (GD30 24hs): ${ccl_gd30_day_price}'''

            return textwrap.dedent(result)
    except Exception:
        log('Error al obtener cotizaciones del dólar')
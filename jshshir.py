import re
import aiohttp
from datetime import datetime
from constants import DIDOX_URL


def calculate14(jshshir: str):
    """jshshirdagi 14-raqamni hisoblaydigan funksiya"""
    if not jshshir.isdigit():
        raise ValueError("Jshshir faqat raqamdanlar iborat bo'lishi kerak")
    if len(jshshir) != 13:
        raise ValueError("13 ta boshida raqamini kiriting oxirgisini hisoblayman")
    
    list_jshshir = list(map(int, list(jshshir)))
    list_731 = list([7, 3, 1]*5)[:13]
    x = sum([i*j for i, j in zip(list_jshshir, list_731)]) % 10
    return jshshir + str(x)


def check_date(date: str) -> str|None:
    if date is None:
        raise TypeError("Sana yuborilmagan yoki noto'g'ri formatda (matn kutilmoqda).")
    
    date_pattern = r"^[0-3][0-9]\.[01][0-9]\.[1-2][0-9]{3}$"
    if not re.match(date_pattern, date):
        raise TypeError("Tug'ilgan kun formati noto'g'ri")
    d, m, y = date.split(".")
    try:
        day = datetime.strptime(date, "%d.%m.%Y")
    except ValueError:
        raise ValueError("Noto'g'ri sana")
    if day > datetime.now():
        raise ValueError("Bugungi kundan katta sana")
    if day.year < 1900:
        raise ValueError("Yoshi katta bobomdan ham kattaku, bu odam tirikmi o'zi")
    return date


def first7digits(bday:str, is_women: bool):
  """boshidan 7 ta raqamini aniqlashtirib oladigan funksiya"""
  d, m, y = bday.split(".")
  x = [[3, 4], [5, 6]][int(y) >= 2000][is_women]
  return str(x) + d + m + y[2:]


async def check_api(jshshir: str):
    """JSHSHIR mavjudligi va ism, manzilini aniqlaydigan funksiya"""
    async with aiohttp.ClientSession() as ses:
        resp = await ses.get(DIDOX_URL + str(jshshir))
        if resp.status != 200:
            raise Exception("So'rov xatoligi")
        j = await resp.json()
        if not j["name"]:
            return False
        else:
            return j


async def check(bday: str, is_women: bool, region: str, i: int):
    """Umumiy jshshir aniqlab uni tekshiradigan funksiya"""
    if not 0 < i < 1000:
        raise ValueError("Reestr index qiymati chegaradan oshib ketti")
    if not region.isdigit() or len(region) != 3:
        raise ValueError("region kodi 3 ta raqam bo'lishi kerak")
        
    f7 = first7digits(bday, is_women)
    r_index = "0"*(3 - len(str(i))) + str(i)
    jshshir13 = f7 + region + r_index
    jshshir = calculate14(jshshir13)
    return await check_api(jshshir)


async def checkall_while_stop(bday: str, is_women: bool, region):
    """i = 1 dan tugaguncha hammasini tekshirish"""
    i = 1
    responses = []
    while i < 1000:
        r = await check(bday, is_women, region, i)
        if not r:
            break
        responses.append(r)
        i += 1
    return responses

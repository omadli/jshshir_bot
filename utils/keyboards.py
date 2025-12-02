import json
from sys import prefix
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


class CallbackRegion(CallbackData, prefix="region"):
    code: str
    

class CallbackDistrict(CallbackData, prefix="district"):
    code: str
    
    
class CallbackFilt(CallbackData, prefix="filter"):
    girls: bool
    boys: bool


regions_data: dict = {}
districts_data: dict = {}

with open("data/regions.json", encoding="utf8") as f:
    regions_data = json.loads(f.read())

with open("data/districts.json", encoding="utf8") as f:
    districts_data = json.loads(f.read())


regions_keyb = InlineKeyboardBuilder().add(
    *(types.inline_keyboard_button.InlineKeyboardButton(
            text=region["NAME_UZ_LATN"], 
            callback_data=CallbackRegion(code=code).pack()) 
         for code, region in regions_data.items())
    ).adjust(2).as_markup()


def districts_keyb(region_code: str) -> types.inline_keyboard_markup.InlineKeyboardMarkup: # type: ignore
    filtered_districts = filter(lambda x: x.startswith(region_code), districts_data)
    return InlineKeyboardBuilder().add(
        *(types.inline_keyboard_button.InlineKeyboardButton(
                text=districts_data[d_code]["NAME_UZ_LATN"], 
                callback_data=CallbackDistrict(code=d_code).pack())
             for d_code in filtered_districts)
    ).adjust(2).as_markup() # type: ignore


filter_keyb = InlineKeyboardBuilder().add(
    *(types.inline_keyboard_button.InlineKeyboardButton(
            text=x[0], 
            callback_data=CallbackFilt(girls=bool(x[1]), boys=bool(x[2])).pack()) 
         for x in [("Faqat erkaklar", 0, 1), ("Faqat ayollar", 1, 0), ("Hammasi", 1, 1)])
    ).adjust(1).as_markup()

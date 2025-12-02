from email import message
import re
import json
from datetime import datetime
from aiogram.filters import StateFilter
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext 
from aiogram import Dispatcher, html, types, F

from utils.states import Form
from jshshir import check_date, checkall_while_stop
from utils.keyboards import regions_keyb, districts_keyb, filter_keyb, CallbackRegion, CallbackDistrict, CallbackFilt

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await message.answer(
        f"Assalomu alaykum {html.bold(message.from_user.full_name)}!\n" # type: ignore
        f"Ushbu bot sizga kiritgan sanangizda tug'ilganlarni topib bera oladi.\n"
        f"Masalan siz bilan bir kunda tug'ilganlarni va hokazo...\n"
        f"Buning uchun pastdagi \"🚀Boshlash\" tugmasini bosing",
        reply_markup=types.reply_keyboard_markup.ReplyKeyboardMarkup(
            keyboard=[
                [types.keyboard_button.KeyboardButton(text="🚀Boshlash")]
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
            selective=True
        )
    )

@dp.message(F.text == "🚀Boshlash")
async def command_boshlash_handler(message: types.Message) -> None:
    await message.answer(
        text="Birinchi bo'lib viloyat tanlang. Qaysi viloyat bo'yicha qidiryapmiz...",
        reply_markup=regions_keyb
    )


@dp.callback_query(CallbackRegion.filter(F.code))
async def region_selecting_callback_handler(query: types.CallbackQuery, callback_data: CallbackRegion) -> None:
    await query.answer(text="Ok.")
    if query.message and hasattr(query.message, "edit_text"):
        await query.message.edit_text( # type: ignore
            text="Tumanni tanlang. Qaysi tuman bo'yicha qidiramiz...",
            reply_markup=districts_keyb(region_code=callback_data.code)
        )
    else:
        await query.bot.send_message( # type: ignore
            chat_id=query.chat_instance,
            text="Tumanni tanlang. Qaysi tuman bo'yicha qidiramiz...",
            reply_markup=districts_keyb(region_code=callback_data.code)
        )
        

@dp.callback_query(CallbackDistrict.filter(F.code))
async def district_selecting_callback_handler(query: types.CallbackQuery, callback_data: CallbackRegion, state: FSMContext) -> None:
    await query.answer(text="Ok.")
    data = []
    with open("data/data.json", encoding="utf8") as f:
        data = json.loads(f.read())
    filtered_data = list(filter(lambda x: x["d_code"]==callback_data.code, data))
    if len(filtered_data):
        codes = [x['code'] for x in filtered_data]
        await query.message.edit_text( # type: ignore
            text=f"Ushbu tuman bo'yicha aniqlangan kodlar: {' '.join(codes)}.\n"
                f"Endi sana kiriting kk.oo.yyyy ko'rinishida. Misol uchun 31.12.2025",
            reply_markup=None,
        )
        await state.set_state(Form.date)
        await state.set_data(data={
            "codes": codes,
            "d_code": callback_data.code
        })
    else:
        await query.message.edit_text( # type: ignore
            text="Ushbu hudud kodi topilmadi. Ehtimol siz bilsangiz adminga murojaat qiling.",
            reply_markup=None,
        )

@dp.message(Form.date)
async def form_date_handler(message: types.Message, state: FSMContext) -> None:
    date = message.text
    try:
        check_date(date) # type: ignore
        await state.update_data(data={
            "date": date
        })
        await state.set_state(Form.filter)
        await message.answer(
            text="Yaxshi endi shu sanada tug'ilgan kimlarni qidiramiz?",
            reply_markup=filter_keyb
        )
    except Exception as e:
        await message.answer(str(e) + "\nQayta to'g'rilab kiriting.")

    
@dp.callback_query(StateFilter(Form.filter) and CallbackFilt.filter(F.boys | F.girls))
async def final_callback_handler(query: types.CallbackQuery, callback_data: CallbackFilt, state: FSMContext) -> None:
    await query.answer(text="Ok.")
    m = await query.message.edit_text( # type: ignore
        text="Qidirilmoqda...",
        reply_markup=None
    )
    await query.bot.send_chat_action( # type: ignore
        chat_id=query.chat_instance,
        action="typing",
    )
    data = await state.get_data()
    await state.clear()
    responses = []
    if callback_data.boys:
        for code in data['codes']:
            responses += await checkall_while_stop(data['date'], False, code)
    if callback_data.girls:
        for code in data['codes']:
            responses += await checkall_while_stop(data['date'], True, code)
    if len(responses):
        text = ""
        for i, resp in enumerate(responses, start=1):
            text += f"{i}) {resp['name']} <code>{resp['personalNum']}</code>\n<i>{resp['address']}</i>\n\n"
        await m.edit_text(text) # type: ignore
    else:
        await m.edit_text( # type: ignore
            text="Hech nima topilmadi."
        )
        
    
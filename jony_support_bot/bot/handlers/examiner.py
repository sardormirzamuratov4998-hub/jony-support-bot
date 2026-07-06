from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from bot.states import ExaminerSearch
from bot.database import get_user_by_telegram_id, search_supports, get_user_by_id, get_groups_by_support
from bot.keyboards import support_results_kb
from bot.utils import examiner_support_card, build_full_excel_report

router = Router()


def is_approved_examiner(message: Message) -> bool:
    user = get_user_by_telegram_id(message.from_user.id)
    return bool(user and user["role"] == "examiner" and user["status"] == "approved")


router.message.filter(is_approved_examiner)


@router.message(F.text == "🔎 Support qidirish (guruhlar)")
async def ask_search(message: Message, state: FSMContext):
    await message.answer("Qidirilayotgan support ismi yoki familiyasini yozing:")
    await state.set_state(ExaminerSearch.query)


@router.message(StateFilter(ExaminerSearch.query))
async def do_search(message: Message, state: FSMContext):
    await state.clear()
    rows = search_supports(message.text)
    if not rows:
        await message.answer("Hech narsa topilmadi.")
        return
    if len(rows) == 1:
        user = rows[0]
        groups = get_groups_by_support(user["id"])
        await message.answer(examiner_support_card(user, groups))
        return
    await message.answer("Bir nechta natija topildi, birini tanlang:", reply_markup=support_results_kb(rows, prefix="ecard"))


@router.callback_query(F.data.startswith("ecard:"))
async def show_card(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[1])
    user = get_user_by_id(user_id)
    if not user:
        await callback.answer("Topilmadi", show_alert=True)
        return
    groups = get_groups_by_support(user_id)
    await callback.message.edit_text(examiner_support_card(user, groups))
    await callback.answer()


@router.message(F.text == "📊 Umumiy Excel hisobot")
async def send_excel(message: Message):
    buffer = build_full_excel_report()
    file = BufferedInputFile(buffer.read(), filename="support_hisobot.xlsx")
    await message.answer_document(file, caption="📊 Barcha supportlar bo'yicha umumiy hisobot")

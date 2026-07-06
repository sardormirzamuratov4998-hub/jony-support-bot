from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from bot.states import SupportAddGroup
from bot.database import get_user_by_telegram_id, get_groups_by_support, add_group
from bot.keyboards import branch_inline_kb_required, day_type_inline_kb, support_main_menu
from bot.utils import full_support_card, DAY_LABELS

router = Router()


def is_approved_support(message: Message) -> bool:
    user = get_user_by_telegram_id(message.from_user.id)
    return bool(user and user["role"] == "support" and user["status"] == "approved")


router.message.filter(is_approved_support)


@router.message(F.text == "➕ Guruh qo'shish")
async def add_group_start(message: Message, state: FSMContext):
    await message.answer("Guruh nomini kiriting:")
    await state.set_state(SupportAddGroup.name)


@router.message(StateFilter(SupportAddGroup.name))
async def add_group_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(SupportAddGroup.branch)
    await message.answer("Filialni tanlang:", reply_markup=branch_inline_kb_required(prefix="sgbranch"))


@router.callback_query(StateFilter(SupportAddGroup.branch), F.data.startswith("sgbranch:"))
async def add_group_branch(callback: CallbackQuery, state: FSMContext):
    branch = callback.data.split(":", 1)[1]
    await state.update_data(branch=branch)
    await state.set_state(SupportAddGroup.day_type)
    await callback.message.edit_text("Kun turini tanlang:", reply_markup=day_type_inline_kb(prefix="sgday"))
    await callback.answer()


@router.callback_query(StateFilter(SupportAddGroup.day_type), F.data.startswith("sgday:"))
async def add_group_day(callback: CallbackQuery, state: FSMContext):
    day_type = callback.data.split(":", 1)[1]
    await state.update_data(day_type=day_type)
    await state.set_state(SupportAddGroup.time)
    await callback.message.edit_text("Soatini kiriting (masalan 14:00):")
    await callback.answer()


@router.message(StateFilter(SupportAddGroup.time))
async def add_group_time(message: Message, state: FSMContext):
    data = await state.get_data()
    user = get_user_by_telegram_id(message.from_user.id)
    add_group(user["id"], data["name"], data["branch"], data["day_type"], message.text.strip())
    await state.clear()
    await message.answer("✅ Guruh muvaffaqiyatli qo'shildi!", reply_markup=support_main_menu())


@router.message(F.text == "📋 Mening guruhlarim")
async def my_groups(message: Message):
    user = get_user_by_telegram_id(message.from_user.id)
    groups = get_groups_by_support(user["id"])
    if not groups:
        await message.answer("Sizda hali guruhlar yo'q. \"➕ Guruh qo'shish\" tugmasi orqali qo'shishingiz mumkin.")
        return
    text = "📚 <b>Sizning guruhlaringiz:</b>\n\n"
    for g in groups:
        day = DAY_LABELS.get(g["day_type"], g["day_type"])
        text += f"• {g['name']} — {g['branch'] or '-'} — {day} — 🕒 {g['time']}\n"
    await message.answer(text)


@router.message(F.text == "👤 Profilim")
async def my_profile(message: Message):
    user = get_user_by_telegram_id(message.from_user.id)
    groups = get_groups_by_support(user["id"])
    await message.answer(full_support_card(user, groups))

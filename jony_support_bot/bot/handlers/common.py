from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext

from bot.config import ADMIN_IDS
from bot.states import Registration
from bot.database import get_user_by_telegram_id, create_pending_user, get_pending_users, get_user_by_id
from bot.keyboards import (
    phone_request_kb,
    remove_kb,
    branch_inline_kb,
    admin_main_menu,
    support_main_menu,
    examiner_main_menu,
    approve_request_kb,
)
from bot.utils import full_support_card
from bot.database import get_groups_by_support

router = Router()


def role_menu(role: str):
    if role == "admin":
        return admin_main_menu()
    if role == "support":
        return support_main_menu()
    if role == "examiner":
        return examiner_main_menu()
    return remove_kb()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    tg_id = message.from_user.id

    if tg_id in ADMIN_IDS:
        await message.answer(
            "Assalomu alaykum, Admin!\nJony Support Bot boshqaruv paneliga xush kelibsiz.",
            reply_markup=admin_main_menu(),
        )
        return

    user = get_user_by_telegram_id(tg_id)

    if user is None:
        await message.answer(
            "Assalomu alaykum! Jony Support botiga xush kelibsiz.\n\n"
            "Botdan foydalanish uchun ro'yxatdan o'tishingiz kerak.\n\n"
            "Ismingiz va familiyangizni kiriting (masalan: Aziz Karimov):"
        )
        await state.set_state(Registration.name)
        return

    if user["status"] == "pending":
        await message.answer("So'rovingiz ko'rib chiqilmoqda. Admin tasdiqlagach xabar beriladi.")
        return

    if user["status"] == "rejected":
        await message.answer(
            "Sizning so'rovingiz rad etilgan. Savol bo'lsa, admin bilan bog'laning.\n"
            "Qaytadan so'rov yubormoqchi bo'lsangiz /start ni bosing va ma'lumotlaringizni qayta kiriting."
        )
        return

    await message.answer(f"Xush kelibsiz, {user['first_name']}!", reply_markup=role_menu(user["role"]))


@router.message(StateFilter(Registration.name))
async def reg_name(message: Message, state: FSMContext):
    parts = message.text.strip().split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Iltimos, ism va familiyani birga kiriting. Masalan: Aziz Karimov")
        return
    first_name, last_name = parts[0], parts[1]
    await state.update_data(first_name=first_name, last_name=last_name)
    await message.answer(
        "Telefon raqamingizni yuboring (tugma orqali) yoki qo'lda yozing:",
        reply_markup=phone_request_kb(),
    )
    await state.set_state(Registration.phone)


@router.message(StateFilter(Registration.phone), F.contact)
async def reg_phone_contact(message: Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    await message.answer("Filialingizni tanlang:", reply_markup=branch_inline_kb(prefix="regbranch"))
    await state.set_state(Registration.branch)


@router.message(StateFilter(Registration.phone), F.text == "✍️ Qo'lda kiritish")
async def reg_phone_manual_prompt(message: Message, state: FSMContext):
    await message.answer("Telefon raqamingizni yozing (masalan: +998901234567):", reply_markup=remove_kb())


@router.message(StateFilter(Registration.phone), F.text)
async def reg_phone_text(message: Message, state: FSMContext):
    phone = message.text.strip()
    if len(phone) < 7:
        await message.answer("Telefon raqami noto'g'ri ko'rinmoqda. Qaytadan kiriting:")
        return
    await state.update_data(phone=phone)
    await message.answer("Filialingizni tanlang:", reply_markup=branch_inline_kb(prefix="regbranch"))
    await state.set_state(Registration.branch)


@router.callback_query(StateFilter(Registration.branch), F.data.startswith("regbranch:"))
async def reg_branch_chosen(callback, state: FSMContext, bot: Bot):
    value = callback.data.split(":", 1)[1]
    branch = None if value == "skip" else value
    data = await state.get_data()
    await state.clear()

    create_pending_user(
        telegram_id=callback.from_user.id,
        first_name=data["first_name"],
        last_name=data["last_name"],
        phone=data["phone"],
        branch=branch,
    )

    await callback.message.edit_text("So'rovingiz qabul qilindi ✅\nAdmin tasdiqlashini kuting.")

    user = get_user_by_telegram_id(callback.from_user.id)
    card = full_support_card(user, [])
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                f"🆕 Yangi so'rov!\n\n{card}",
                reply_markup=approve_request_kb(user["id"]),
            )
        except Exception:
            pass
    await callback.answer()

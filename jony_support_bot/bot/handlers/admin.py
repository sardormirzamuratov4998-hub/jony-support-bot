from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from bot.config import ADMIN_IDS
from bot.states import AdminSearch, AdminEditProfile, AdminGroupForm
from bot.database import (
    search_supports,
    get_user_by_id,
    get_groups_by_support,
    approve_user,
    reject_user,
    delete_user,
    update_user_field,
    get_pending_users,
    get_branch_stats,
    get_group_by_id,
    update_group,
    delete_group,
)
from bot.keyboards import (
    support_results_kb,
    admin_card_actions_kb,
    edit_field_kb,
    groups_menu_kb,
    confirm_kb,
    day_type_inline_kb,
    branch_inline_kb_required,
)
from bot.utils import full_support_card

router = Router()
router.message.filter(F.from_user.id.in_(ADMIN_IDS))
router.callback_query.filter(F.from_user.id.in_(ADMIN_IDS))


FIELD_LABELS = {
    "first_name": "Ism",
    "last_name": "Familiya",
    "phone": "Telefon",
    "branch": "Filial",
}


# ---------------- SEARCH ----------------

@router.message(F.text == "🔍 Support qidirish")
async def ask_search(message: Message, state: FSMContext):
    await message.answer("Qidirilayotgan support ismi yoki familiyasini yozing:")
    await state.set_state(AdminSearch.query)


@router.message(StateFilter(AdminSearch.query))
async def do_search(message: Message, state: FSMContext):
    await state.clear()
    rows = search_supports(message.text)
    if not rows:
        await message.answer("Hech narsa topilmadi.")
        return
    if len(rows) == 1:
        user = rows[0]
        groups = get_groups_by_support(user["id"])
        await message.answer(full_support_card(user, groups), reply_markup=admin_card_actions_kb(user["id"]))
        return
    await message.answer("Bir nechta natija topildi, birini tanlang:", reply_markup=support_results_kb(rows))


@router.callback_query(F.data.startswith("card:"))
async def show_card(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[1])
    user = get_user_by_id(user_id)
    if not user:
        await callback.answer("Topilmadi", show_alert=True)
        return
    groups = get_groups_by_support(user_id)
    await callback.message.edit_text(full_support_card(user, groups), reply_markup=admin_card_actions_kb(user_id))
    await callback.answer()


# ---------------- PENDING REQUESTS ----------------

@router.message(F.text == "📋 Kutilayotgan so'rovlar")
async def list_pending(message: Message):
    from bot.keyboards import approve_request_kb
    rows = get_pending_users()
    if not rows:
        await message.answer("Kutilayotgan so'rovlar yo'q.")
        return
    for user in rows:
        groups = get_groups_by_support(user["id"])
        await message.answer(full_support_card(user, groups), reply_markup=approve_request_kb(user["id"]))


@router.callback_query(F.data.startswith("approve:"))
async def approve_cb(callback: CallbackQuery, bot: Bot):
    _, user_id, role = callback.data.split(":")
    user_id = int(user_id)
    approve_user(user_id, role)
    user = get_user_by_id(user_id)

    from bot.keyboards import support_main_menu, examiner_main_menu
    menu = support_main_menu() if role == "support" else examiner_main_menu()
    role_uz = "Support" if role == "support" else "Examiner"

    try:
        await bot.send_message(
            user["telegram_id"],
            f"Tabriklaymiz! So'rovingiz tasdiqlandi ✅\nRolingiz: {role_uz}",
            reply_markup=menu,
        )
    except Exception:
        pass

    await callback.message.edit_text(f"✅ {user['first_name']} {user['last_name']} — {role_uz} sifatida qabul qilindi.")
    await callback.answer()


@router.callback_query(F.data.startswith("reject:"))
async def reject_cb(callback: CallbackQuery, bot: Bot):
    user_id = int(callback.data.split(":")[1])
    user = get_user_by_id(user_id)
    reject_user(user_id)
    try:
        await bot.send_message(user["telegram_id"], "Afsuski, so'rovingiz rad etildi.")
    except Exception:
        pass
    await callback.message.edit_text(f"❌ {user['first_name']} {user['last_name']} so'rovi rad etildi.")
    await callback.answer()


# ---------------- BRANCH STATS ----------------

@router.message(F.text == "📊 Filial statistikasi")
async def branch_stats(message: Message):
    support_rows, group_rows = get_branch_stats()
    support_map = {r["branch"] or "Noma'lum": r["support_count"] for r in support_rows}
    group_map = {r["branch"] or "Noma'lum": r["group_count"] for r in group_rows}

    branches = set(support_map) | set(group_map)
    if not branches:
        await message.answer("Hozircha statistika uchun ma'lumot yo'q.")
        return

    text = "📊 <b>Filiallar bo'yicha statistika</b>\n\n"
    for b in sorted(branches):
        text += f"🏢 <b>{b}</b>: {support_map.get(b, 0)} support, {group_map.get(b, 0)} guruh\n"
    await message.answer(text)


# ---------------- EDIT PROFILE ----------------

@router.callback_query(F.data.startswith("editmenu:"))
async def edit_menu(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[1])
    await callback.message.edit_text("Qaysi maydonni tahrirlaysiz?", reply_markup=edit_field_kb(user_id))
    await callback.answer()


@router.callback_query(F.data.startswith("editfield:"))
async def edit_field(callback: CallbackQuery, state: FSMContext):
    _, user_id, field = callback.data.split(":")
    await state.update_data(edit_user_id=int(user_id), edit_field=field)
    await state.set_state(AdminEditProfile.waiting_value)
    await callback.message.edit_text(f"{FIELD_LABELS[field]} uchun yangi qiymatni kiriting:")
    await callback.answer()


@router.message(StateFilter(AdminEditProfile.waiting_value))
async def save_field(message: Message, state: FSMContext):
    data = await state.get_data()
    update_user_field(data["edit_user_id"], data["edit_field"], message.text.strip())
    await state.clear()
    user = get_user_by_id(data["edit_user_id"])
    groups = get_groups_by_support(user["id"])
    await message.answer("✅ Yangilandi.")
    await message.answer(full_support_card(user, groups), reply_markup=admin_card_actions_kb(user["id"]))


# ---------------- GROUPS MANAGEMENT ----------------

@router.callback_query(F.data.startswith("groupsmenu:"))
async def groups_menu(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[1])
    groups = get_groups_by_support(user_id)
    if not groups:
        await callback.answer("Bu supportda guruhlar yo'q.", show_alert=True)
        return
    await callback.message.edit_text("Guruhni tanlang (tahrirlash ✏️ yoki o'chirish 🗑):", reply_markup=groups_menu_kb(user_id, groups))
    await callback.answer()


@router.callback_query(F.data.startswith("delgroup_confirm:"))
async def delgroup_confirm(callback: CallbackQuery):
    _, group_id, user_id = callback.data.split(":")
    await callback.message.edit_text(
        "Ushbu guruhni o'chirishni tasdiqlaysizmi?",
        reply_markup=confirm_kb("delgroup", int(group_id), user_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm:delgroup:"))
async def delgroup_do(callback: CallbackQuery):
    _, _, group_id, user_id = callback.data.split(":")
    delete_group(int(group_id))
    user = get_user_by_id(int(user_id))
    groups = get_groups_by_support(int(user_id))
    await callback.message.edit_text("✅ Guruh o'chirildi.\n\n" + full_support_card(user, groups), reply_markup=admin_card_actions_kb(int(user_id)))
    await callback.answer()


@router.callback_query(F.data.startswith("cancel:delgroup:"))
async def delgroup_cancel(callback: CallbackQuery):
    _, _, group_id, user_id = callback.data.split(":")
    groups = get_groups_by_support(int(user_id))
    await callback.message.edit_text("Bekor qilindi.", reply_markup=groups_menu_kb(int(user_id), groups))
    await callback.answer()


@router.callback_query(F.data.startswith("editgroup:"))
async def editgroup_start(callback: CallbackQuery, state: FSMContext):
    group_id = int(callback.data.split(":")[1])
    group = get_group_by_id(group_id)
    await state.update_data(edit_group_id=group_id, edit_support_id=group["support_id"])
    await state.set_state(AdminGroupForm.name)
    await callback.message.edit_text(f"Guruh nomi (hozirgi: {group['name']}). Yangi nomini yozing:")
    await callback.answer()


@router.message(StateFilter(AdminGroupForm.name))
async def editgroup_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(AdminGroupForm.branch)
    await message.answer("Filialni tanlang:", reply_markup=branch_inline_kb_required(prefix="agbranch"))


@router.callback_query(StateFilter(AdminGroupForm.branch), F.data.startswith("agbranch:"))
async def editgroup_branch(callback: CallbackQuery, state: FSMContext):
    branch = callback.data.split(":", 1)[1]
    await state.update_data(branch=branch)
    await state.set_state(AdminGroupForm.day_type)
    await callback.message.edit_text("Kun turini tanlang:", reply_markup=day_type_inline_kb(prefix="agday"))
    await callback.answer()


@router.callback_query(StateFilter(AdminGroupForm.day_type), F.data.startswith("agday:"))
async def editgroup_day(callback: CallbackQuery, state: FSMContext):
    day_type = callback.data.split(":", 1)[1]
    await state.update_data(day_type=day_type)
    await state.set_state(AdminGroupForm.time)
    await callback.message.edit_text("Soatini kiriting (masalan 14:00):")
    await callback.answer()


@router.message(StateFilter(AdminGroupForm.time))
async def editgroup_time(message: Message, state: FSMContext):
    data = await state.get_data()
    update_group(data["edit_group_id"], data["name"], data["branch"], data["day_type"], message.text.strip())
    await state.clear()
    user = get_user_by_id(data["edit_support_id"])
    groups = get_groups_by_support(data["edit_support_id"])
    await message.answer("✅ Guruh yangilandi.")
    await message.answer(full_support_card(user, groups), reply_markup=admin_card_actions_kb(user["id"]))


# ---------------- DELETE SUPPORT ----------------

@router.callback_query(F.data.startswith("delsupport_confirm:"))
async def delsupport_confirm(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[1])
    await callback.message.edit_text(
        "Ushbu supportni butunlay o'chirishni tasdiqlaysizmi? (Barcha guruhlari ham o'chadi)",
        reply_markup=confirm_kb("delsupport", user_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm:delsupport:"))
async def delsupport_do(callback: CallbackQuery):
    parts = callback.data.split(":")
    user_id = int(parts[2])
    user = get_user_by_id(user_id)
    delete_user(user_id)
    await callback.message.edit_text(f"🗑 {user['first_name']} {user['last_name']} tizimdan o'chirildi.")
    await callback.answer()


@router.callback_query(F.data.startswith("cancel:delsupport:"))
async def delsupport_cancel(callback: CallbackQuery):
    parts = callback.data.split(":")
    user_id = int(parts[2])
    user = get_user_by_id(user_id)
    groups = get_groups_by_support(user_id)
    await callback.message.edit_text("Bekor qilindi.\n\n" + full_support_card(user, groups), reply_markup=admin_card_actions_kb(user_id))
    await callback.answer()

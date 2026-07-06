from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from bot.config import BRANCHES


def phone_request_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Raqamni yuborish", request_contact=True)],
            [KeyboardButton(text="✍️ Qo'lda kiritish")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def remove_kb():
    from aiogram.types import ReplyKeyboardRemove
    return ReplyKeyboardRemove()


def branch_inline_kb(prefix="branch"):
    buttons = [
        [InlineKeyboardButton(text=b, callback_data=f"{prefix}:{b}")] for b in BRANCHES
    ]
    buttons.append([InlineKeyboardButton(text="O'tkazib yuborish", callback_data=f"{prefix}:skip")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def branch_inline_kb_required(prefix="sgbranch"):
    buttons = [
        [InlineKeyboardButton(text=b, callback_data=f"{prefix}:{b}")] for b in BRANCHES
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def day_type_inline_kb(prefix="day"):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Toq kun", callback_data=f"{prefix}:toq"),
                InlineKeyboardButton(text="Juft kun", callback_data=f"{prefix}:juft"),
            ]
        ]
    )


def admin_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔍 Support qidirish")],
            [KeyboardButton(text="➕ Yangi guruh qo'shish")],
            [KeyboardButton(text="📋 Kutilayotgan so'rovlar")],
            [KeyboardButton(text="📊 Filial statistikasi"), KeyboardButton(text="📈 Ish yuki statistikasi")],
            [KeyboardButton(text="👑 Adminlar ro'yxati")],
        ],
        resize_keyboard=True,
    )


def support_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Guruh qo'shish")],
            [KeyboardButton(text="📋 Mening guruhlarim")],
            [KeyboardButton(text="👤 Profilim")],
        ],
        resize_keyboard=True,
    )


def examiner_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔎 Support qidirish (guruhlar)")],
            [KeyboardButton(text="📊 Umumiy Excel hisobot")],
        ],
        resize_keyboard=True,
    )


def approve_request_kb(user_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Support", callback_data=f"approve:{user_id}:support"),
                InlineKeyboardButton(text="✅ Examiner", callback_data=f"approve:{user_id}:examiner"),
            ],
            [InlineKeyboardButton(text="👑 Admin qilib tayinlash", callback_data=f"approve:{user_id}:admin")],
            [InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject:{user_id}")],
        ]
    )


def admins_list_kb(rows):
    buttons = []
    for r in rows:
        label = f"❌ {r['first_name']} {r['last_name']} — adminlikni bekor qilish"
        buttons.append([InlineKeyboardButton(text=label, callback_data=f"revoke_admin_confirm:{r['id']}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def support_results_kb(rows, prefix="card"):
    buttons = []
    for r in rows:
        label = f"{r['first_name']} {r['last_name']} ({r['branch'] or '-'})"
        buttons.append([InlineKeyboardButton(text=label, callback_data=f"{prefix}:{r['id']}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_card_actions_kb(user_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Tahrirlash", callback_data=f"editmenu:{user_id}")],
            [InlineKeyboardButton(text="➕ Guruh qo'shish", callback_data=f"addgroup:{user_id}")],
            [InlineKeyboardButton(text="🔁 Guruhlarni boshqarish", callback_data=f"groupsmenu:{user_id}")],
            [InlineKeyboardButton(text="🗑 Supportni o'chirish", callback_data=f"delsupport_confirm:{user_id}")],
        ]
    )


def workload_recommend_kb(rows):
    buttons = []
    for i, r in enumerate(rows):
        mark = "🧠 " if i == 0 else ""
        label = f"{mark}{r['first_name']} {r['last_name']} — {r['group_count']} ta guruh"
        buttons.append([InlineKeyboardButton(text=label, callback_data=f"newgroup_pick:{r['id']}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def edit_field_kb(user_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Ism", callback_data=f"editfield:{user_id}:first_name")],
            [InlineKeyboardButton(text="Familiya", callback_data=f"editfield:{user_id}:last_name")],
            [InlineKeyboardButton(text="Telefon", callback_data=f"editfield:{user_id}:phone")],
            [InlineKeyboardButton(text="Filial", callback_data=f"editfield:{user_id}:branch")],
            [InlineKeyboardButton(text="⬅️ Orqaga", callback_data=f"card:{user_id}")],
        ]
    )


def groups_menu_kb(user_id: int, groups):
    buttons = []
    for g in groups:
        label = f"{g['name']} ({g['day_type']}, {g['time']})"
        buttons.append([
            InlineKeyboardButton(text=f"✏️ {label}", callback_data=f"editgroup:{g['id']}"),
            InlineKeyboardButton(text="🗑", callback_data=f"delgroup_confirm:{g['id']}:{user_id}"),
        ])
    buttons.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data=f"card:{user_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def confirm_kb(action: str, obj_id: int, extra: str = ""):
    yes_data = f"confirm:{action}:{obj_id}:{extra}"
    no_data = f"cancel:{action}:{obj_id}:{extra}"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Ha", callback_data=yes_data),
                InlineKeyboardButton(text="❌ Yo'q", callback_data=no_data),
            ]
        ]
    )

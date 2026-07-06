import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Bir nechta admin bo'lishi mumkin, vergul bilan ajratilgan telegram ID lar
ADMIN_IDS = [
    int(x.strip())
    for x in os.getenv("ADMIN_IDS", "").split(",")
    if x.strip().isdigit()
]

DB_PATH = os.getenv("DB_PATH", "support_bot.db")

BRANCHES = ["Zafar", "Bekobod", "Stretinka"]

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable topilmadi! Railway Variables bo'limiga qo'shing.")

if not ADMIN_IDS:
    raise RuntimeError("ADMIN_IDS environment variable topilmadi! Kamida bitta admin telegram ID kerak.")

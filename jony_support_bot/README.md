# Jony Support Bot

Support xodimlarini boshqarish uchun Telegram bot. 3 ta rol: **Admin**, **Support**, **Examiner**.

## Imkoniyatlari

**Admin**
- Support ismi/familiyasi bo'yicha qidirish → to'liq karta (ism, familiya, telefon, filial, guruhlari, kun turi, soati) — faqat adminga ko'rinadi
- Filial bo'yicha statistika
- Kutilayotgan so'rovlarni ko'rish va tasdiqlash (Support yoki Examiner rolini berish) yoki rad etish
- Support profilini tahrirlash (ism, familiya, telefon, filial)
- Support guruhlarini almashtirish (tahrirlash) va o'chirish
- Supportni butunlay o'chirish

**Support**
- Bot orqali ro'yxatdan o'tish so'rovi (ism, familiya majburiy, telefon majburiy — tugma orqali yoki qo'lda)
- Admin tasdiqlagach botdan foydalanish
- O'zi guruh qo'shishi (guruh nomi, filial, toq/juft kun, soat so'raladi)
- O'z guruhlari ro'yxatini va profilini ko'rish

**Examiner**
- Support ismi/familiyasi bo'yicha qidirish → guruhlari ko'rinadi, lekin telefon raqami **ko'rinmaydi**
- Barcha supportlar bo'yicha filial/guruh tartibida umumiy Excel hisobot yuklab olish

## O'rnatish (lokal test uchun)

```bash
python -m venv .venv
source .venv/bin/activate   # Windowsda: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# .env faylini oching va BOT_TOKEN, ADMIN_IDS ni to'ldiring
python main.py
```

`ADMIN_IDS` — sizning shaxsiy Telegram ID raqamingiz (bir nechta bo'lsa vergul bilan ajrating). ID ni bilish uchun @userinfobot ga yozing.

## Railway'ga joylashtirish (GitHub orqali)

1. Ushbu papkani GitHub repositoriyasiga yuklang (push qiling).
2. Railway.app → **New Project** → **Deploy from GitHub repo** → repozitoriyani tanlang.
3. Railway avtomatik `requirements.txt`ni topib, Python muhitini o'rnatadi.
4. **Variables** bo'limiga o'ting va qo'shing:
   - `BOT_TOKEN` = bot tokeningiz (BotFather'dan)
   - `ADMIN_IDS` = sizning telegram ID raqamingiz
   - `DB_PATH` = `/data/support_bot.db` (quyidagi Volume bilan birga)
5. **Settings → Deploy** bo'limida Start Command sifatida `python main.py` ni kiriting (Procfile avtomatik o'qiladi, lekin agar Railway "web" turi sifatida aniqlasa, buni qo'lda ko'rsating).
6. Ma'lumotlar bazasi deploy qilinganda o'chib ketmasligi uchun **Volume** qo'shing:
   - Settings → Volumes → **New Volume** → Mount path: `/data`
   - `DB_PATH` ni `/data/support_bot.db` qilib qo'yganingizga ishonch hosil qiling.
7. Deploy tugagach, botga Telegram'da `/start` yozib tekshiring.

⚠️ **Muhim:** Agar avval boshqa loyihada shu bot tokenini ishlatgan bo'lsangiz yoki token biror joyda oshkor bo'lgan bo'lsa, BotFather orqali `/revoke` qilib yangi token oling.

## Papka strukturasi

```
jony_support_bot/
├── main.py                 # Bot ishga tushirish nuqtasi
├── requirements.txt
├── Procfile
├── .env.example
└── bot/
    ├── config.py           # Sozlamalar (token, admin ID, filiallar)
    ├── database.py         # SQLite bilan ishlash
    ├── states.py           # FSM holatlari
    ├── keyboards.py        # Klaviaturalar
    ├── utils.py            # Karta formatlash, Excel hisobot
    └── handlers/
        ├── common.py       # /start, ro'yxatdan o'tish so'rovi
        ├── admin.py        # Admin funksiyalari
        ├── support.py      # Support funksiyalari
        └── examiner.py     # Examiner funksiyalari
```

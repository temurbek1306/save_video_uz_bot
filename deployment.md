# Render.com orqali deploy qilish (Qadamba-qadam)

Render'da botingizni 24/7 ishlatish uchun quyidagi qadamlarni bajaring:

### 1. GitHub'ga yuklash
Kodingizni GitHub-da yangi (private bo'lishi tavsiya etiladi) repozitoriyaga yuklang.

### 2. Render-da yangi xizmat ochish
1. [Render Dashboard](https://dashboard.render.com/)-ga kiring.
2. **New +** tugmasini bosing va **Background Worker**-ni tanlang.
3. GitHub repozitoriyangizni ulang.

### 3. Sozlamalar
- **Name**: `save-video-uz-bot`
- **Region**: O'zingizga yaqinini tanlang (masalan, Frankfurt).
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python main.py`

### 4. Muhit o'zgaruvchilari (Environment Variables)
"Advanced" tugmasini bosing va quyidagilarni qo'shing:
- `BOT_TOKEN`: `8507784193:AAEj2tMBQniB9wJ5cjOY-Sq6bKLZs-PLEy4`

### 5. Muhim eslatma
Render-ning bepul versiyasida `ffmpeg` o'rnatilmagan bo'lishi mumkin. Lekin biz botni `ffmpeg`siz ham ishlaydigan qilib sozlanganmiz, shuning uchun muammo bo'lmaydi.

### 6. Video yuklash limiti
Render-ning bepul versiyasida disk xotirasi vaqtinchalik bo'ladi. Bot fayllarni yuklab bo'lgach o'chirib yuboradi, bu bepul xosting uchun juda mos.
鼓

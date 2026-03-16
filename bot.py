from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

TOKEN = "8623473038:AAGdp-dDTBO-yx3hW-QflEjEkeVHMMsFjKY"

ADMIN_ID = 2056540476

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Заказать монтаж", callback_data="order")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Привет 👋\nЯ бот для заказа монтажа видео 🎬\nНажми кнопку ниже, чтобы оставить заявку.",
        reply_markup=reply_markup
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    # кнопка заказа
    if query.data == "order":
        user_data[user_id] = {"stage": 0}
        await query.message.reply_text(
            "Отлично! Давай соберём заявку.\n\n1️⃣ Тип видео (YouTube, TikTok, Shorts):"
        )

    # принятие заявки
    elif query.data.startswith("accept_"):
        client_id = int(query.data.split("_")[1])

        await context.bot.send_message(
            chat_id=client_id,
            text="✅ Ваша заявка на монтаж одобрена!\nСкоро вам напишут."
        )

        await query.edit_message_text("✅ Заявка принята")

    # отклонение заявки
    elif query.data.startswith("reject_"):
        client_id = int(query.data.split("_")[1])

        await context.bot.send_message(
            chat_id=client_id,
            text="❌ К сожалению, сейчас мы не можем взять вашу заявку.\nСпасибо за обращение."
        )

        await query.edit_message_text("❌ Заявка отклонена")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if user_id not in user_data:
        await update.message.reply_text("Нажми /start чтобы начать заказ.")
        return

    stage = user_data[user_id]["stage"]

    if stage == 0:
        user_data[user_id]["video_type"] = text
        user_data[user_id]["stage"] = 1
        await update.message.reply_text("2️⃣ Пример монтажа (можно ссылку на ютубера или описание стиля):")

    elif stage == 1:
        user_data[user_id]["style"] = text
        user_data[user_id]["stage"] = 2
        await update.message.reply_text("3️⃣ Длительность исходного видео (в минутах):")

    elif stage == 2:
        user_data[user_id]["duration"] = text
        user_data[user_id]["stage"] = 3
        await update.message.reply_text("4️⃣ Когда нужен готовый ролик (дата/срок):")

    elif stage == 3:
        user_data[user_id]["deadline"] = text
        user_data[user_id]["stage"] = 4
        await update.message.reply_text("5️⃣ Бюджет (₽):")

    elif stage == 4:
        user_data[user_id]["budget"] = text
        user_data[user_id]["stage"] = 5
        await update.message.reply_text("6️⃣ Способ оплаты (название банка):")

    elif stage == 5:
        user_data[user_id]["payment"] = text
        user_data[user_id]["stage"] = 6
        await update.message.reply_text("7️⃣ Твой Telegram для связи (например @username):")

    elif stage == 6:
        user_data[user_id]["tg_username"] = text

        data = user_data[user_id]

        message = (
            f"Новая заявка на монтаж 🎬\n\n"
            f"Тип видео: {data['video_type']}\n"
            f"Стиль: {data['style']}\n"
            f"Длительность: {data['duration']}\n"
            f"Срок: {data['deadline']}\n"
            f"Бюджет: {data['budget']}\n"
            f"Оплата: {data['payment']}\n"
            f"Telegram: {data['tg_username']}"
        )

        keyboard = [[
            InlineKeyboardButton("👍 Принять", callback_data=f"accept_{user_id}"),
            InlineKeyboardButton("👎 Отклонить", callback_data=f"reject_{user_id}")
        ]]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=message,
            reply_markup=reply_markup
        )

        await update.message.reply_text(
            "✅ Заявка отправлена! Ожидайте ответа."
        )

        user_data.pop(user_id)


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()

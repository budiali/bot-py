import os
from dotenv import load_dotenv
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ContextTypes, ConversationHandler, CallbackQueryHandler

import pd_generate as gen

load_dotenv()

# Mengonfigurasi logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    # handlers=[logging.FileHandler("bot_log.txt"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)
END = ConversationHandler.END

TOKEN=os.getenv('TELEGRAM_BOT_TOKEN')

(
ECHO,
END_CONV,
LIST_TICKET,
BACK_BUTTON,
) = map(chr, range(4))

SELECTING_ACTION = map(chr, range(4,5))

async def initialize_user_data(update: Update, context: CallbackContext) -> str:
    if update.message:
        user = update.message.from_user
    else:
        user = update.callback_query.from_user

    firstname = user.first_name
    lastname = user.last_name
    chat_id = user.id
    fullname = f"{firstname} {lastname}"

    context.user_data['user_dict'] = {
        'firstname': firstname,
        'lastname': lastname,
        'chat_id': chat_id,
        'fullname': fullname
    }

    # logger.info(f"{context.user_data}")

# Fungsi untuk menangani perintah /start
async def start(update: Update, context: CallbackContext) -> None:
    await initialize_user_data(update, context)
    user_dict = context.user_data['user_dict']

    # logger.info(f"User {update.effective_message.from_user.username} started the bot")
    await update.effective_message.reply_text(f"Halo {user_dict['fullname']} ! Saya adalah bot sederhana.")
    return await main_button(update,context)

# Fungsi untuk menangani pesan teks umum
async def echo(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    await update.message.reply_text(f'Anda mengirim: {user_message}')

async def main_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"User {update.effective_message.from_user.username} choose main button")
    button = [
        [InlineKeyboardButton("Approval Troubleshoot Ticket", callback_data=str(LIST_TICKET))],
        [InlineKeyboardButton("Done", callback_data=str(END_CONV))]
    ]
    keyboard=InlineKeyboardMarkup(button)
    text="Pilih tombol berikut:"
    await update.effective_message.reply_text(text=text, reply_markup=keyboard)

    return SELECTING_ACTION

async def list_ticket(update: Update, context: CallbackContext) -> str:
    query = update.callback_query
    await query.answer()
    text_option=f"Anda memilih kategori: *Approval Troubleshoot Ticket*"
    await query.edit_message_text(text=text_option, parse_mode='Markdown')
    
    button = [
        [InlineKeyboardButton("Back", callback_data=str(BACK_BUTTON))]
    ]
    keyboard=InlineKeyboardMarkup(button)

    # tickets = "\n".join(create_random_ticket(update,context))
    tickets = create_random_ticket(update, context)
    await query.message.reply_text(text=f"Berikut Daftar Tiket Anda : \n\n{tickets}", reply_markup=keyboard)

    return SELECTING_ACTION

async def back_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    # menghapus text sebelumnya
    await context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
    # menghapus tombol sebelumnya
    # await query.edit_message_reply_markup(reply_markup=None)
    await start(update,context)

async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Percakapan dibatalkan.")
    return END

async def end_conv(update: Update, context:ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Percakapan dibatalkan.")
    await send_animation(update, context)
    # return END

def create_random_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    ticket_numbers = gen.data_tickets()
    # logger.info(f"Data gen.ticket >> {ticket_numbers}")
    all_tickets = "\n".join(ticket_numbers)
    
    return all_tickets

async def send_animation(update: Update, context:ContextTypes.DEFAULT_TYPE) -> str:
    await initialize_user_data(update, context)
    user_dict = context.user_data['user_dict']
    # logger.info(f"Context Data  Send Anim >>> {user_dict['chat_id']}")

    chat_id = user_dict['chat_id']
    
    await context.bot.send_animation(chat_id=chat_id, animation='https://cdnl.iconscout.com/lottie/premium/preview-watermark/website-repair-animation-download-in-lottie-json-gif-static-svg-file-formats--under-logo-web-configuration-maintenance-development-construction-pack-design-animations-6516026.mp4')


def error(update, context):
    logger.warning(f'Update {update} caused error {context.error}')

# Fungsi utama untuk menjalankan bot
def main():
    # Ganti 'YOUR_API_TOKEN' dengan token API yang Anda dapatkan dari BotFather
    application = Application.builder().token(TOKEN).build()

    selection_handler=[
        CallbackQueryHandler(end_conv, pattern="^"+END_CONV+"$"),
        CallbackQueryHandler(list_ticket, pattern="^"+LIST_TICKET+"$"),
        CallbackQueryHandler(back_button, pattern="^"+BACK_BUTTON+"$"),
    ]

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECTING_ACTION: selection_handler,
            ECHO:[MessageHandler(filters.TEXT & ~filters.COMMAND, echo)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Daftarkan handler untuk perintah /start
    application.add_handler(conversation_handler)
    application.add_error_handler(error)
    # Mulai polling untuk menerima update
    application.run_polling()

if __name__ == '__main__':
    main()

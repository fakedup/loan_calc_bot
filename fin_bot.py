from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import logging
import settings  # тут токен
from textwrap import dedent
import loan_calc
import datetime

# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO,
#     filename='bot.log')

token = settings.TELEGRAM_API_KEY

START_CALC, SUM, PAYMENT, RATE, TERM = range(5)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

fh = logging.FileHandler('bot_debug.log')
fh.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

fh = logging.FileHandler('bot_info.log')
fh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

user_calculations_log_file = 'logs/user_calculations.log'

def main():
    updater = Updater(token)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', bot_start))

    conv_handler = ConversationHandler(
        entry_points = [RegexHandler('^(Payment|Credit Sum|Rate|Term)$', calc_start, pass_chat_data = True)],

        states = {
        SUM: [MessageHandler(Filters.text, get_sum, pass_chat_data = True)],
        PAYMENT: [MessageHandler(Filters.text, get_payment, pass_chat_data = True)],
        RATE: [MessageHandler(Filters.text, get_rate, pass_chat_data = True)],
        TERM: [MessageHandler(Filters.text, get_term, pass_chat_data = True)]
        },

        fallbacks = [CommandHandler('cancel', cancel, pass_chat_data = True)],

        allow_reentry = True

        )
    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()

def bot_start(bot, update):
    text = dedent('''\
    This is financial bot.

    Enter command to start calculation.''')
    reply_keyboard = [['Payment', 'Credit Sum'], ['Rate', 'Term']]
    update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

def calc_start(bot, update, chat_data):
    func_choice = update.message.text 
    chat_data['loan'] = loan_calc.Loan()
    chat_data['choice'] = func_choice
    update.message.reply_text('You chose to calc {}. Now enter sum or /cancel.'.format(func_choice))
    if func_choice == 'Payment' or func_choice == 'Rate':
        return SUM
    elif func_choice == 'Credit Sum':
        return PAYMENT

def get_sum (bot, update, chat_data):
    # update.message.reply_text(chat_data['loan'].get_loan_parameters())
    choice = chat_data['choice']
    try:
        summ = float(update.message.text)
    except:
        update.message.reply_text('Invalid data. You chose to calc {}. Now enter sum or /cancel.'.format(chat_data['choice']))
        return SUM
    chat_data['loan'].set_summ(summ)
    if choice == 'Payment':
        update.message.reply_text('Now enter rate.')
        return RATE
    elif choice == 'Rate':
        update.message.reply_text('Now enter payment.')
        return PAYMENT

def get_payment(bot, update, chat_data):
    # update.message.reply_text(chat_data['loan'].get_loan_parameters())
    choice = chat_data['choice']
    try:
        payment = float(update.message.text)
    except:
        update.message.reply_text('Invalid data. You chose to calc {}. Now enter sum or /cancel.'.format(chat_data['choice']))
        return PAYMENT
    chat_data['loan'].set_payment(payment)
    if choice == 'Credit Sum':
        update.message.reply_text('Now enter rate.')
        return RATE
    elif choice == 'Rate':
        update.message.reply_text('Now enter term.')
        return TERM

    return ConversationHandler.END

def get_rate(bot, update, chat_data):
    # update.message.reply_text(chat_data['loan'].get_loan_parameters())
    choice = chat_data['choice']
    try:
        rate = float(update.message.text)
    except:
        update.message.reply_text('Invalid data. You chose to calc {}. Now enter sum or /cancel.'.format(chat_data['choice']))
        return RATE
    chat_data['loan'].set_rate(rate)
    if choice == 'Payment' or choice == 'Credit Sum':
        update.message.reply_text('Now enter term (number of months).')
        return TERM

def get_term(bot, update, chat_data):
    choice = chat_data['choice']
    loan = chat_data['loan']
    try:
        term = int(update.message.text)
    except:
        update.message.reply_text('Invalid data. You chose to calc {}. Now enter sum or /cancel.'.format(chat_data['choice']))
        return RATE
    loan.set_term(term)
    if choice == 'Payment':
        loan.calc_payment()
    elif choice == 'Credit Sum':
        loan.calc_summ()
    elif choice == 'Rate':
        loan.calc_rate()
    update.message.reply_text(loan.get_loan_parameters())
    user = update.message.from_user
    user_name = str(user.id) + ' ' + user.first_name + ' ' + user.last_name
    write_user_action_log (user_calculations_log_file, user_name, loan.get_log_string())
    clear_chat_data (chat_data)       
    return ConversationHandler.END

def cancel(bot, update):
    update.message.reply_text('Maybe next time.')
    return ConversationHandler.END

def clear_chat_data(chat_data):
    del chat_data['loan']
    del chat_data['choice']

def write_user_action_log(file, user_name, string):
    with open(file, 'a') as f:
        f.write (user_name + ';'+datetime.datetime.now().strftime('%d/%m/%Y %H:%M') +';'+ string + '\n')


if __name__ == '__main__':

    main()
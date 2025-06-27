from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, ContentType
import os
from dotenv import load_dotenv


load_dotenv('vars.env') #Получение пути ключей бота
dotenv_path = os.getenv('BOT_KEYS_PLACE')
load_dotenv(dotenv_path)
bot_token = os.getenv('WARSHIPS_BOT')
if bot_token is not None:
    print('Key was found')
else:
    print('Key not found')
    exit()

bot  = Bot(token=bot_token)
dp = Dispatcher()

@dp.message(Command(commands=["start"]))
async def process_start_command(message: Message):
    await message.answer('Свага здесь?')

@dp.message(Command(commands=["help"]))
async def process_help_command(message: Message):
    await message.answer('Ты глупый или что-то?')

@dp.message()
async def send_echo(message: Message):
    await message.reply(text=message.text)
if __name__ == "__main__":
    dp.run_polling(bot)
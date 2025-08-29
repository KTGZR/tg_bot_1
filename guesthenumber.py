#Python 3.8
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command,CommandStart, BaseFilter
from aiogram.types import Message, ContentType, PhotoSize
import os
from datetime import datetime
from dotenv import load_dotenv
import random
import time
from typing import List,Union,Dict,Any

# pyright: reportOptionalMemberAccess=false
# pyright: reportArgumentType=false
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

admins_id = [790161259]

users = {}

user = {
    'in_game' : False,
    'secret_number': None,
    'attempts':None,
    'total_games':0,
    'wins':0
}

ATTEMPTS = 5

class IsAdmin(BaseFilter):
    def __init__(self,adm_ids: List[int]) -> None:
       self.adm_lst = adm_ids
    async def __call__(self,message: Message) -> Union[bool ,Dict[str,int]]:
        return {'status' : 1 if message.from_user.id in self.adm_lst else 0}

class FindDigits(BaseFilter):
    async def __call__(self, message: Message) -> Union[bool ,Dict[str,List[int]]]:
        numbers = []
        for word in message.text.replace(',',' ').split(' '):
            correct_word = word.strip(' ').replace('.','')
            if correct_word.isdigit():
                numbers.append(int(correct_word))
        if numbers:
            return {'numbers' : numbers}
        else:
            return False

def random_nimber() -> int:
    return random.randint(1,100)

@dp.message(IsAdmin(admins_id),Command(commands=["botstat"]))
async def answer_admin_message(message: Message, status: int):
    if status == 1:
        await message.answer(f'Статистика бота(Доступна только админам):\n{users}\nКоличество пользователей: {len(users)}')
    else:
        await message.answer(f'Вы не администратор.')


@dp.message(lambda msg: msg.text and msg.text == '/start')
async def process_start_command(message: Message):
    await message.answer('Привет!\nДавайте сыграем в игру "Угадай число"?\n\n'
        'Чтобы получить правила игры и список доступных '
        'команд - отправьте команду /help.\n'
        'Также ты можешь отправить фото и получить её характеристики.\n'
        'Я могу искать числа в строке.\nНапиши "найди число" и я найду число в тексте')
    await bot.send_animation(message.chat.id,'CgACAgQAAxkBAAIGsGiuhhXWenc9PERVPZmQGiUY2xX6AAI7CQAC9tN1UV7GrXr_nOnyNgQ')
    if message.from_user.id not in users:
        users[message.from_user.id] = user
    print(users)

@dp.message(Command(commands=["help"]))
async def process_help_command(message: Message):
    await message.answer( 'Правила игры:\n\nЯ загадываю число от 1 до 100, '
        f'а вам нужно его угадать\nУ вас есть {ATTEMPTS} '
        'попыток\n\nДоступные команды:\n/help - правила '
        'игры и список команд\n/cancel - выйти из игры\n'
        '/stat - посмотреть статистику\n/botstat - информация о боте(администратор)\n/off - выключение бота(администратор)\n\nДавай сыграем?')


@dp.message(Command(commands=["stat"]))
async def process_stat_command(message: Message):
    await message.answer( f'Всего игр сыграно: {user["total_games"]}\n'
        f'Игр выиграно: {user["wins"]}')

@dp.message(Command(commands=["cancel"]))
async def process_cancel_command(message: Message):
    if users[message.from_user.id]['in_game']:
        users[message.from_user.id]['in_game'] = False
        await message.answer(
        'Вы вышли из игры. Если захотите сыграть '
        'снова - напишите об этом'
        )
    else:
        await message.answer(
        'А мы и так с вами не играем. '
        'Может, сыграем разок?'
        )

@dp.message(F.photo[-1].as_('photo_max'),F.photo[0].as_('photo_min'))
async def process_photo_send(message: Message, photo_max: PhotoSize, photo_min: PhotoSize):
    print(photo_max)
    print(photo_min)
    await message.answer(f'Photo low quality info:\nfile_id={photo_min.file_id}\nfile_unique_id={photo_min.file_unique_id}\nfile_size={photo_min.file_size}\nresolution= {photo_min.width}x{photo_min.height}\nPhoto high quality info:\nfile_id={photo_max.file_id}\nfile_unique_id={photo_max.file_unique_id}\nfile_size={photo_max.file_size}\nresolution= {photo_max.width}x{photo_max.height}')

@dp.message(F.text.lower().startswith('найди числа'), FindDigits())
async def search_digits_was_find(message: Message, numbers: List[int]):
    await message.answer(f'Числа найдены!\nИх список: {numbers}.\nОбщее количество чисел: {len(numbers)}.')

@dp.message(F.text.lower().startswith('найди числа'))
async def search_digits_wasnt_find(message: Message):
    await message.answer(f'Чисел не найдено 👍') #Тут должен быть эмодзи лайк

@dp.message(F.text.lower().in_(['да', 'давай', 'сыграем', 'игра',
                                'играть', 'хочу играть']))
async def process_positive_answer(message: Message):
    if not users[message.from_user.id]['in_game']:
        users[message.from_user.id]['in_game'] = True
        users[message.from_user.id]['secret_number'] = random_nimber()
        users[message.from_user.id]['attempts'] = ATTEMPTS
        await message.answer(
            'Ура!\n\nЯ загадал число от 1 до 100, '
            'попробуй угадать!'
        )
    else:
        await message.answer(
            'Пока мы играем в игру я могу '
            'реагировать только на числа от 1 до 100 '
            'и команды /cancel и /stat'
        )

@dp.message(F.text.lower().in_(['нет', 'не', 'не хочу', 'не буду']))
async def process_negative_answer(message: Message):
    if not users[message.from_user.id]['in_game']:
        await message.answer(
            'Жаль :(\n\nЕсли захотите поиграть - просто '
            'напишите об этом'
        )
    else:
        await message.answer(
            'Мы же сейчас с вами играем. Присылайте, '
            'пожалуйста, числа от 1 до 100'
        )

@dp.message(lambda x: x.text and x.text.isdigit() and 1 <= int(x.text) <= 100)
async def process_numbers_answer(message: Message):
    if users[message.from_user.id]['in_game']:
        if int(message.text) == users[message.from_user.id]['secret_number']:
            users[message.from_user.id]['in_game'] = False
            users[message.from_user.id]['total_games'] += 1
            users[message.from_user.id]['wins'] += 1
            await message.answer(
                'Ура!!! Вы угадали число!\n\n'
                'Может, сыграем еще?'
            )
        elif int(message.text) > users[message.from_user.id]['secret_number']:
            users[message.from_user.id]['attempts'] -= 1
            await message.answer('Мое число меньше')
        elif int(message.text) < users[message.from_user.id]['secret_number']:
            users[message.from_user.id]['attempts'] -= 1
            await message.answer('Мое число больше')

        if users[message.from_user.id]['attempts'] == 0:
            users[message.from_user.id]['in_game'] = False
            users[message.from_user.id]['total_games'] += 1
            await message.answer(
                'К сожалению, у вас больше не осталось '
                'попыток. Вы проиграли :(\n\nМое число '
                f'было {user["secret_number"]}\n\nДавайте '
                'сыграем еще?'
            )
    else:
        await message.answer('Мы еще не играем. Хотите сыграть?')

@dp.message(IsAdmin(admins_id),Command(commands=['off']))
async def off_bot(message: Message, status: int):
    if status == 1:
        print('Exiting by admins request from telegram')
        exit()
    else:
        await message.answer('Вы не можете выключить бота, вы не администратор.')

@dp.message(Command(commands=['test']))
async def test_us(message: Message):
     print(users)

@dp.message(Command(commands=['exit']))
async def user_exit(message: Message):
    if message.from_user.id not in users:
        await message.answer('Ты еще начал играть чтобы выходить(')
    else:
        del users[message.from_user.id]
        await message.answer('Увидимся в следующий раз ✋')

@dp.message()
async def process_other_answers(message: Message):
    if users[message.from_user.id]['in_game']:
        await message.answer(
            'Мы же сейчас с вами играем. '
            'Присылайте, пожалуйста, числа от 1 до 100'
        )
    else:
        await message.answer(
            'Я довольно ограниченный бот, давайте '
            'просто сыграем в игру?'
        )

if __name__ == "__main__":
    dp.run_polling(bot)

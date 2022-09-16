from aiogram import executor, Bot, types, Dispatcher
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from settings import *
from table import DB
from datetime import datetime
from random import randint


class Feedback(StatesGroup):
    Direction = State()
    Category = State()
    Problem = State()
    Fin = State()
    Pre_ans = State()
    Ans = State()


id_feedback = []

markup0 = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
markup0_1 = InlineKeyboardMarkup()
markup1 = InlineKeyboardMarkup(row_width=2)
markup2 = InlineKeyboardMarkup(row_width=3)

markup0_1.add(InlineKeyboardButton(text='Передать отзыв', callback_data="Передать отзыв"))

for direct in range(0, len(Direction), 2):
    btn1 = InlineKeyboardButton(text=Direction[direct], callback_data=Direction[direct])
    btn2 = InlineKeyboardButton(text=Direction[direct + 1], callback_data=Direction[direct + 1])
    markup1.row(btn1, btn2)

for categ in range(0, len(Category) - 1, 3):
    btn1 = InlineKeyboardButton(text=Category[categ], callback_data=Category[categ])
    btn2 = InlineKeyboardButton(text=Category[categ + 1], callback_data=Category[categ + 1])
    btn3 = InlineKeyboardButton(text=Category[categ + 2], callback_data=Category[categ + 2])
    markup2.row(btn1, btn2, btn3)
markup2.add(InlineKeyboardButton(text=Category[-1], callback_data=Category[-1]))

bot = Bot(token=Token_Bot)
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(commands=['start'], state="*")
async def welcome(message: types.Message):
    await message.answer('Выберите что вы хотите сделать', reply_markup=markup0_1)
    await Feedback.Direction.set()


# Это продолжение для инлайн клавиатуры
@dp.callback_query_handler(state=Feedback.Direction)
async def Choose_Direction(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text('Выберите направление подготовки', reply_markup=markup1)
    await Feedback.next()


# Это продолжение для кнопок, которые открываются вместо клавиатуры
@dp.message_handler(state=Feedback.Direction)
async def Choose_Direction(message: types.Message, state: FSMContext):
    await message.answer('Выберите категорию отзыва', reply_markup=markup1)
    await Feedback.next()


@dp.callback_query_handler(state=Feedback.Category)
async def Choose_Category(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(direction=call.data)
    await call.message.edit_text('Выберите категорию подготовки', reply_markup=markup2)
    await Feedback.next()


@dp.callback_query_handler(state=Feedback.Problem)
async def Problem(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(category=call.data)
    await call.message.edit_text(
        'Очень важно любой отзыв конкретизировать так, чтобы люди, которые реагируют на ваши отзывы сразу понимали, в чем дело. Важно указывать: \n- кратко суть проблемы\n- с чем связана проблема (сайт/материалы/ДЗ/кураторы и т.д.)\n- предмет\n- преподаватель\nЧем четче вы сформулируете свой запрос, чем четче ответ на него последует!')
    await Feedback.next()


def Save_data(data):
    FB_table = DB('feedback_sng_db', 'feedback_sng')
    return FB_table.save_data(data)


def create_id():
    return randint(100000, 1000000)


@dp.message_handler(state=Feedback.Fin)
async def End(message: types.Message, state: FSMContext):
    await state.update_data(problem=message.text)
    await message.answer('Ваш запрос принят',
                         reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
                             KeyboardButton('/start')))
    data = await state.get_data()
    f_b = {'_id': str(create_id()),
           'user name': message.from_user.full_name,
           'От кого': message.from_user.id,
           'Дата и время отправки запроса': datetime.now().strftime('%d.%m.%y\n%H:%M:%S'),
           'Направление': data.get('direction'),
           'Категория': data.get('category'),
           'Отзыв': data.get('problem'),
           'Дата и время ответа сотрудника': '',
           'Ответ сотрудника': ''}
    id = str(Save_data(f_b))

    fin_markup = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton(text='Ответить на отзыв', callback_data=id))

    await bot.send_message(chat_id, "id запроса:" + id + '\n' +
                           'user name:' + f_b['user name'] + '\n' +
                           'Направление:' + f_b['Направление'] + '\n' +
                           'Категория:' + f_b['Категория'] + '\n' +
                           'Отзыв:' + f_b['Отзыв'], reply_markup=fin_markup)
    await state.finish()


@dp.callback_query_handler(chat_id=chat_id)
async def answer(call: CallbackQuery, state: FSMContext):
    global id_feedback
    # Получаем id отзыва из сообщения из беседы с руководителями
    id = call.message.text.split('user name')[0].split(':')[1][:-1]
    id_feedback.append(id)
    await call.message.edit_text(call.message.text + '\n' + f'На отзыв отвечает {call.from_user.first_name}')
    await state.update_data(_id=id)
    Inline_markup = InlineKeyboardMarkup(row_width=3)
    Inline_markup.add(InlineKeyboardButton(text='Написать ответ на отзыв', callback_data='Write_ans'))
    await bot.send_message(call.from_user.id, ' Нажмите кнопку ниже напишите ответ на отзыв',
                           reply_markup=Inline_markup)


@dp.callback_query_handler(text='Write_ans')
async def check(call: CallbackQuery):
    await Feedback.Ans.set()
    await call.message.edit_text('Ниже напишите ответ на отзыв')


@dp.message_handler(state=Feedback.Ans)
async def save_answer(message: types.Message):
    global id_feedback
    FB_table = DB('feedback_sng_db', 'feedback_sng')
    f_b = FB_table.collection.find_one({'_id': str(id_feedback[0])})
    f_b['Ответ сотрудника'] = message.text
    f_b['Дата и время ответа сотрудника'] = datetime.now().strftime('%d.%m.%y\n%H:%M:%S')
    FB_table.update_item(id_feedback[0], f_b)
    id_feedback.pop()
    await message.answer(f'Ответ успешно принят!\nХорошая работа,{message.from_user.first_name}')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

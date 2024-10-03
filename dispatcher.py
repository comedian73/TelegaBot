from aiogram import Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import F
from questions import quiz_data
from logic import new_quiz, get_quiz_index, update_quiz_index, get_question

# Диспетчер
dp = Dispatcher()

# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Логика обработки команды /start
    # Создаем сборщика клавиатур типа Reply
    builder = ReplyKeyboardBuilder()
    # Добавляем в сборщик одну кнопку
    builder.add(types.KeyboardButton(text="Начать игру"))
    await message.answer("Привет! Я бот для проведения квиза.", reply_markup=builder.as_markup(resize_keyboard=True))

# Хэндлер на команды /quiz
@dp.message(F.text=="Начать игру")
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    # Отправляем новое сообщение без кнопок
    await message.answer(f"Давайте начнем квиз!")
    # Запускаем новый квиз
    await new_quiz(message)


@dp.callback_query(F.data)
async def right_answer(callback: types.CallbackQuery):
    # редактируем текущее сообщение с целью убрать кнопки (reply_markup=None)
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    # Получение текущего вопроса для данного пользователя
    current_question_index = await get_quiz_index(callback.from_user.id)
    correct_option = quiz_data[current_question_index]['correct_option']
    if F.data == "right_answer":
        # Отправляем в чат сообщение, что ответ верный
        await callback.message.answer("Верно!")
    else:
        # Отправляем в чат сообщение об ошибке с указанием верного ответа
        await callback.message.answer(f"Неправильно. Правильный ответ: {quiz_data[current_question_index]['options'][correct_option]}")
        
    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)

    # Проверяем достигнут ли конец квиза
    if current_question_index < len(quiz_data):
        # Следующий вопрос
        await get_question(callback.message, callback.from_user.id)
    else:
        # Уведомление об окончании квиза
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")


# @dp.callback_query(F.data == "wrong_answer")
# async def wrong_answer(callback: types.CallbackQuery):
#     # редактируем текущее сообщение с целью убрать кнопки (reply_markup=None)
#     await callback.bot.edit_message_reply_markup(
#         chat_id=callback.from_user.id,
#         message_id=callback.message.message_id,
#         reply_markup=None
#     )

#     # Получение текущего вопроса для данного пользователя
#     current_question_index = await get_quiz_index(callback.from_user.id)

#     correct_option = quiz_data[current_question_index]['correct_option']

#     # Отправляем в чат сообщение об ошибке с указанием верного ответа
#     await callback.message.answer(f"Неправильно. Правильный ответ: {quiz_data[current_question_index]['options'][correct_option]}")

#     # Обновление номера текущего вопроса в базе данных
#     current_question_index += 1
#     await update_quiz_index(callback.from_user.id, current_question_index)

#     # Проверяем достигнут ли конец квиза
#     if current_question_index < len(quiz_data):
#         # Следующий вопрос
#         await get_question(callback.message, callback.from_user.id)
#     else:
#         # Уведомление об окончании квиза
#         await callback.message.answer("Это был последний вопрос. Квиз завершен!")

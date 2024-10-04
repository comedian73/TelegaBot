from aiogram import Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram import F
from questions import quiz_data
from logic import (new_quiz, get_quiz_index, update_quiz_index, 
                   get_question, get_correct_answers, update_correct_answers)

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

@dp.message(F.text=="Результат")
@dp.message(Command("result"))
async def cmd_result(message: types.Message):
    # Логика обработки команды /result
    builder = InlineKeyboardBuilder()
    # Добавляем в сборщик кнопки
    builder.add(types.InlineKeyboardButton(text="Играть", callback_data="game"),
                types.InlineKeyboardButton(text="Отмена", callback_data="cancel"))
    
    result = await get_correct_answers(message.from_user.id)
    current_question_index = await get_quiz_index(message.from_user.id)

    await message.answer(f"Твой последний результат {result} из {current_question_index}.\n"
                         "Хотите улучшить результат?", reply_markup=builder.as_markup(resize_keyboard=True))

@dp.callback_query(F.data!="game")
async def callback(callback: types.CallbackQuery):
    # редактируем текущее сообщение с целью убрать кнопки (reply_markup=None)
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    if callback.data != "cancel":
    
        # Получение текущего вопроса для данного пользователя
        current_question_index = await get_quiz_index(callback.from_user.id)
        #Получение номера правильного ответа
        correct_option = quiz_data[current_question_index]['correct_option']
        #Получение правильного ответа в виде текста
        opt = quiz_data[current_question_index]['options'][correct_option]
        #Получение количества правильных ответов
        correct_answers = await get_correct_answers(callback.from_user.id)
        #Меняем кнопки на выбранный ответ
        await callback.message.answer(f'Ваш ответ: {callback.data}')

        #Проверяем ответ на правильность и если верно обновляем количество ответов
        if opt == str(callback.data):
            correct_answers +=1
            await update_correct_answers(callback.from_user.id, correct_answers)

        # Обновление номера текущего вопроса в базе данных
        current_question_index += 1
        await update_quiz_index(callback.from_user.id, current_question_index)

        # Проверяем достигнут ли конец квиза
        if current_question_index < len(quiz_data):
            # Следующий вопрос
            await get_question(callback.message, callback.from_user.id)
        else:
            # Уведомление об окончании квиза
            await callback.message.answer("Это был последний вопрос. Квиз завершен! \n"
                                        f"Вы ответили верно на {correct_answers} вопросов из {current_question_index}")
        
@dp.callback_query(F.data=="game")
async def callback(callback: types.CallbackQuery):
    # редактируем текущее сообщение с целью убрать кнопки (reply_markup=None)
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    
    await new_quiz(callback.message)
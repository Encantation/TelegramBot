from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram import Dispatcher, types
import googleapiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
import httplib2


class SaveExpenses(StatesGroup):
    waiting_for_expense_name = State()
    waiting_for_expense_value = State()

def register_handlers_expense(dp: Dispatcher):
    dp.register_message_handler(start_save_expenses, Text(equals="записать расходы", ignore_case=True), state="*")
    dp.register_message_handler(start_save_expenses, commands="save", state="*")
    dp.register_message_handler(expense_name, state=SaveExpenses.waiting_for_expense_name)
    dp.register_message_handler(expense_value, state=SaveExpenses.waiting_for_expense_value)


async def start_save_expenses(message: types.Message):
    await message.answer("Введите имя расхода", reply_markup=types.ReplyKeyboardRemove())
    await SaveExpenses.waiting_for_expense_name.set()


async def expense_name(message: types.Message, state: FSMContext):
    await state.update_data(expense=message.text)
    await message.answer("Введите сумму:")
    await SaveExpenses.waiting_for_expense_value.set()


async def expense_value(message: types.Message, state: FSMContext):
    await state.update_data(value=message.text)
    # Добавить строку в конец таблицы GoogleSheets
    user_data = await state.get_data()
    # берем данные по Google API аккаунту из файла, задаем ID гугл-таблицы
    CREDENTIALS_FILE = 'credentials.json'
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIALS_FILE,
        ['https://www.googleapis.com/auth/spreadsheets']
    )
    httpAuth = credentials.authorize(httplib2.Http())
    spreadsheet_id = '16_Gx7RB9Q5cUFD09_3E0LbnLjNRgSBS5SV0FD2yhDM8'
    service = googleapiclient.discovery.build('sheets', 'v4', http=httpAuth)
    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range="Sheet1!A:A",
        valueInputOption="USER_ENTERED",
        body={
                 "majorDimension": 'COLUMNS',
                 "values": [[user_data['expense']], [user_data['value']]],
        }
    ).execute()
    await message.answer("Расход успешно добавлен")
    await state.finish()



# values = service.spreadsheets().values().get(
#     spreadsheetId=spreadsheet_id,
#     range='A1:E10',
#     majorDimension='ROWS'
# ).execute()
import gspread
from google.oauth2.gdch_credentials import ServiceAccountCredentials
from settings import *

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('Umschool.json', scope)
gc = gspread.authorize(credentials)
table = gc.open_by_key(KEY_TABLE)
table_for_umschool = gc.open('<LIST NAME>')
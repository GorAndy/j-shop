import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = str(os.getenv("BOT_TOKEN"))

admins = [admin.strip() for admin in os.getenv('ADMINS_ID').split(',')]

host = os.getenv('PGHOST')
PGUSER = os.getenv('PGUSER')
PGPASS = os.getenv('PGPASS')
DBNAME = os.getenv('DBNAME')
LIQPAY_TOKEN = os.getenv('LIQPAY_TOKEN')

I18N_DOMAIN = 'testbot'
BASE_DIR = Path(__file__).parent
LOCALES_DIR = BASE_DIR / 'locales'


ip = os.getenv("ip")

aiogram_redis = {
    'host': ip,
}

redis = {
    'address': (ip, 6379),
    'encoding': 'utf8'
}

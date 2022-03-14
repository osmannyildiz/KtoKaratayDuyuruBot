from dotenv import load_dotenv
load_dotenv()
from os import environ as env
from datetime import date, timedelta


BOT_CONFIG = {
    "token": env.get("BOT_TOKEN")
}

OLDEST_ANNOUNCEMENT_DATE = date.today() - timedelta(days=45)
MESSAGE_FORMAT = "📣 {channel_name} — {announcement_date}\n*{announcement_title}*\n[Duyuruya git]({announcement_url})"

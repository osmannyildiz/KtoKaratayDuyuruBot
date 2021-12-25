from dotenv import load_dotenv
load_dotenv()
from os import environ as env


BOT_CONFIG = {
    "token": env.get("BOT_TOKEN")
}

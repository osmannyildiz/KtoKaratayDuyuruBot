from tgbots.kto_karatay_duyuru_bot.bot import Bot
from tgbots.kto_karatay_duyuru_bot.config import bot_config
from db.mysql import create_dbconn


dbconn = create_dbconn("kkdb")
bot = Bot(bot_config, dbconn)


if __name__ == "__main__":
    bot.run_dev()

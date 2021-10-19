# DEV CONFIG
bot_config = {
    "TOKEN": ""
}


# OVERRIDE WITH PROD CONFIG IF AVAILABLE
try:
    from tgbots.kto_karatay_duyuru_bot.config_prod import *
except ImportError:
    pass

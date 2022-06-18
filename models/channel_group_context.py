from tgbots.kto_karatay_duyuru_bot.db import dbsvc


class ChannelGroupContext:
    def __init__(self, name, service_class, *args):
        self.dbsvc_channels = dbsvc[name + "_channels"]
        self.dbsvc_subscriptions = dbsvc[name + "_channels_subscriptions"]
        self.service = service_class(self.dbsvc_channels, *args)

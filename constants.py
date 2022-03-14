class StaticClassBase:
    @classmethod
    def as_list(cls):
        return [val for key, val in cls.__dict__.items() if not key.startswith("_") and key != "as_list"]


class Commands(StaticClassBase):
    START = "/start"                                    # Tanış
    TOGGLE_KKDB_SPECIAL_CHANNELS = "/kkdb_ozel"         # KKDB'ye özel duyuru kanallarını ayarla
    TOGGLE_WEBSITE_FACULTY_CHANNELS = "/fakulteler"     # Fakülte duyuru kanallarını ayarla
    TOGGLE_WEBSITE_DEPARTMENT_CHANNELS = "/bolumler"    # Bölüm duyuru kanallarını ayarla
    TOGGLE_WEBSITE_MISC_CHANNELS = "/diger"             # Diğer duyuru kanallarını ayarla
    FORGET_ME = "/beni_unut"                            # Bilgilenmekten sıkıldın mı?


class ChannelTypes(StaticClassBase):
    KKDB_SPECIAL = "kkdb_special"
    WEBSITE_FACULTY = "website_faculty"
    WEBSITE_DEPARTMENT = "website_department"
    WEBSITE_MISC = "website_misc"


class UserStates(StaticClassBase):
    MEETING_EXPECTING_FACULTY = "meeting_expecting_faculty"
    MEETING_EXPECTING_DEPARTMENT = "meeting_expecting_department"
    IDLE = "idle"
    TOGGLE_EXPECTING_KKDB_SPECIAL_CHANNEL = "toggle_expecting_kkdb_special_channel"
    TOGGLE_EXPECTING_WEBSITE_FACULTY_CHANNEL = "toggle_expecting_website_faculty_channel"
    TOGGLE_EXPECTING_WEBSITE_DEPARTMENT_CHANNEL = "toggle_expecting_website_department_channel"
    TOGGLE_EXPECTING_WEBSITE_MISC_CHANNEL = "toggle_expecting_website_misc_channel"

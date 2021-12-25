from tgbots.kto_karatay_duyuru_bot.message_texts import MessageTexts as MT
from tgbots.kto_karatay_duyuru_bot.db import dbsvc
from datetime import date


def build_custom_kb_of_faculties(bot):
    faculty_list = [faculty["name"] for faculty in dbsvc["faculties"].get()]
    faculty_list.sort()
    custom_kb = bot.api.build_vertical_custom_keyboard(faculty_list)
    return custom_kb

def build_custom_kb_of_departments(bot, faculty_id):
    department_list = [department["name"] for department in dbsvc["departments"].get("faculty_id=%s", [faculty_id])]
    department_list.sort()
    custom_kb = bot.api.build_vertical_custom_keyboard(department_list)
    return custom_kb

def build_custom_kb_for_ayarla(bot, user_id):
    subscribed_channels_of_user = [subscription["channel_id"] for subscription in dbsvc["subscriptions"].get("user_id=%s", [user_id])]
    list_for_custom_kb = []
    list_for_custom_kb.append(MT.ayarla_done_button())
    for channel in dbsvc["channels"].get():
        if channel["id"] in subscribed_channels_of_user:
            list_for_custom_kb.append(channel["name"] + " ✅")
        else:
            list_for_custom_kb.append(channel["name"] + " ❌")
    custom_kb = bot.api.build_vertical_custom_keyboard(list_for_custom_kb)
    return custom_kb

def build_custom_kb_for_curr_state(bot, user_id, user_state=None):
    user = dbsvc["users"].getone("id=%s", [user_id])

    if user_state is None:
        user_state = user["state"]

    if user_state == 2:
        return build_custom_kb_of_faculties(bot)
    elif user_state == 3:
        faculty_id = user["faculty_id"]
        return build_custom_kb_of_departments(bot, faculty_id)
    elif user_state == 5:
        return build_custom_kb_for_ayarla(bot, user_id)
    else:
        return bot.api.build_remove_keyboard()


def sanitize_and_validate_user_name(user_name):
    # sadece alfanümerik + bazı diğer karakterler
    new_user_name = ""
    allowed_chars = list(" -_")
    for char in user_name:
        if (
            char.isalnum() or
            char in allowed_chars
        ):
            new_user_name += char
    user_name = new_user_name

    # birden fazla boşluk yerine tek boşluk
    user_name = " ".join(user_name.split())

    # baş ve sondaki boşlukları sil
    user_name = user_name.strip()

    # yeni satır veya tab yerine tek boşluk
    user_name = user_name.replace("\n", " ").replace("\t", " ")

    # min. uzunluk 2
    if len(user_name) < 2:
        return None

    # max. uzunluk 32
    user_name = user_name[:32].strip()

    return user_name
    # isim hiçbir şekilde uygun değilse None döndürür


def parse_string_to_date(str_obj):
    turkish_month_names = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
    d, m, y = str_obj.split()
    y = int(y)
    m = turkish_month_names.index(m) + 1
    d = int(d)
    return date(y, m, d)


def create_subscriptions_to_special_channels(dbsvc, user_id):
    for channel in dbsvc["channels"].getall("item_type=%s", [3]):  # dbsvc.get kullanınca "Unread results" oluyor
        dbsvc["subscriptions"].insert(user_id, channel["id"])


def get_subscribed_users_ids(dbsvc, channel_id):
    return [subscription["user_id"] for subscription in dbsvc["subscriptions"].get("channel_id=%s", [channel_id])]


def get_or_create_stat(dbsvc, name, item_id, default_value=0):
    stat = dbsvc["stats"].getone("name=%s AND item_id=%s", [name, item_id])
    if stat:
        return stat
    else:
        dbsvc["stats"].insert(name, item_id, default_value)
        return dbsvc["stats"].getone("name=%s AND item_id=%s", [name, item_id])


def increment_or_create_stat(dbsvc, name, item_id, default_value=0):
    stat = dbsvc["stats"].getone("name=%s AND item_id=%s", [name, item_id])
    if stat:
        dbsvc["stats"].increaseColumn("value", 1, "id=%s", [stat["id"]])
    else:
        dbsvc["stats"].insert(name, item_id, default_value + 1)


def toggle_subscription(dbsvc, user_id, channel_id):
    if subscription := dbsvc["subscriptions"].getone("user_id=%s AND channel_id=%s", [user_id, channel_id]):
        dbsvc["subscriptions"].delete("id=%s", [subscription["id"]])
        new_state = False
    else:
        dbsvc["subscriptions"].insert(user_id, channel_id)
        new_state = True
    return new_state

from datetime import date
from tgbots.kto_karatay_duyuru_bot.message_texts import message_texts as mt
from tgbots.kto_karatay_duyuru_bot.db_helpers import (
    delete_user,
    get_channels_by_item_type, create_subscription,
    get_departments_by_faculty_id, get_user,
    get_channels, get_subscriptions_by_user_id,
    get_users, get_faculties, get_departments, get_channels_by_item_type,
    get_subscriptions_by_channel_id,
    get_stat_by_name_and_item_id, create_stat, set_stat_by_name_and_item_id
)


def build_custom_kb_of_faculties(bot):
    faculty_list = [row[0] for row in get_faculties(bot, "name")]
    faculty_list.sort()
    custom_kb = bot.api.build_vertical_custom_keyboard(faculty_list)
    return custom_kb

def build_custom_kb_of_departments(bot, faculty_id):
    department_list = [row[0] for row in get_departments_by_faculty_id(bot, faculty_id, "name")]
    department_list.sort()
    custom_kb = bot.api.build_vertical_custom_keyboard(department_list)
    return custom_kb

def build_custom_kb_for_ayarla(bot, user_id):
    channels = get_channels(bot, "id, name")
    subscribed_channels_of_user = [row[0] for row in get_subscriptions_by_user_id(bot, user_id, "channel_id")]
    list_for_custom_kb = []
    list_for_custom_kb.append(mt.ayarla_done_button())
    for channel_id, channel_name in channels:
        if channel_id in subscribed_channels_of_user:
            list_for_custom_kb.append(channel_name + " ✅")
        else:
            list_for_custom_kb.append(channel_name + " ❌")
    custom_kb = bot.api.build_vertical_custom_keyboard(list_for_custom_kb)
    return custom_kb

def build_custom_kb_for_curr_state(bot, user_id, user_state=None):
    if user_state == None:
        user_state = get_user(bot, user_id, "state")[0]

    if user_state == 2:
        return build_custom_kb_of_faculties(bot)
    elif user_state == 3:
        faculty_id = get_user(bot, user_id, "faculty_id")[0]
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

    # baş ve sondaki boşlukları sil
    user_name = user_name.strip()

    # yeni satır veya tab yerine tek boşluk
    user_name = user_name.replace("\n", " ").replace("\t", " ")

    # birden fazla boşluk yerine tek boşluk
    user_name = " ".join(user_name.split())

    # min. uzunluk 5
    if len(user_name) < 5:
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


def create_subscriptions_to_special_channels(bot, user_id):
    rows = get_channels_by_item_type(bot, 3, "id")
    for row in rows:
        create_subscription(bot, user_id, row[0])


def get_subscribed_users_ids(bot, channel_id):
    return [row[0] for row in get_subscriptions_by_channel_id(bot, channel_id, "user_id")]


def get_or_create_stat(bot, stat_name, stat_item_id, cols, default_value=0):
    row = get_stat_by_name_and_item_id(bot, stat_name, stat_item_id, cols)
    if row:
        return row
    else:
        create_stat(bot, stat_name, stat_item_id, default_value)
        return get_stat_by_name_and_item_id(bot, stat_name, stat_item_id, cols)

def increment_or_create_stat(bot, stat_name, stat_item_id, default_value=0):
    row = get_stat_by_name_and_item_id(bot, stat_name, stat_item_id, "value")
    if row:
        set_stat_by_name_and_item_id(bot, stat_name, stat_item_id, "value", row[0] + 1)
    else:
        create_stat(bot, stat_name, stat_item_id, default_value + 1)

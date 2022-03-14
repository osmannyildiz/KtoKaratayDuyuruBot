from tgbots.kto_karatay_duyuru_bot.db import dbsvc
from tgbots.kto_karatay_duyuru_bot.constants import Commands, ChannelTypes, UserStates
from tgbots.kto_karatay_duyuru_bot.message_texts import MessageTexts as MT
from datetime import date


def build_custom_kb_of_faculties(bot):
    faculty_list = [faculty["name"] for faculty in dbsvc["faculties"].get()]
    faculty_list.sort()
    custom_kb = bot.api.build_vertical_custom_keyboard(faculty_list, one_time=True)
    return custom_kb


def build_custom_kb_of_departments(bot, faculty_id):
    department_list = [department["name"] for department in dbsvc["departments"].get("faculty_id=%s", [faculty_id])]
    department_list.sort()
    custom_kb = bot.api.build_vertical_custom_keyboard(department_list, one_time=True)
    return custom_kb


def build_custom_kb_for_toggle_channels(bot, user_id, channel_type):
    dbsvc_channels = dbsvc[channel_type + "_channels"]
    dbsvc_subscriptions = dbsvc[channel_type + "_channels_subscriptions"]
    subscribed_channel_ids_of_user = [subscription["channel_id"] for subscription in dbsvc_subscriptions.get("user_id=%s", [user_id])]
    list_for_custom_kb = []
    list_for_custom_kb.append(MT.toggle_done_button())
    for channel in dbsvc_channels.get():
        if channel["id"] in subscribed_channel_ids_of_user:
            list_for_custom_kb.append(channel["name"] + " ✅")
        else:
            list_for_custom_kb.append(channel["name"] + " ❌")
    custom_kb = bot.api.build_vertical_custom_keyboard(list_for_custom_kb, one_time=True)
    return custom_kb


def build_custom_kb_for_curr_state(bot, user):
    state = user["state"]

    if state == UserStates.MEETING_EXPECTING_FACULTY:
        return build_custom_kb_of_faculties(bot)
    elif state == UserStates.MEETING_EXPECTING_DEPARTMENT:
        return build_custom_kb_of_departments(bot, user["faculty_id"])
    elif state in [
        UserStates.TOGGLE_EXPECTING_KKDB_SPECIAL_CHANNEL,
        UserStates.TOGGLE_EXPECTING_WEBSITE_FACULTY_CHANNEL,
        UserStates.TOGGLE_EXPECTING_WEBSITE_DEPARTMENT_CHANNEL,
        UserStates.TOGGLE_EXPECTING_WEBSITE_MISC_CHANNEL
    ]:
        channel_type = user_state_to_channel_type(state)
        return build_custom_kb_for_toggle_channels(bot, user["id"], channel_type)
    else:
        return bot.api.build_remove_keyboard()


def parse_string_to_date(str_obj):
    turkish_month_names = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
    d, m, y = str_obj.split()
    y = int(y)
    m = turkish_month_names.index(m) + 1
    d = int(d)
    return date(y, m, d)


def create_subscription_to_faculty_channel(user_id, faculty_id):
    faculty_channel = dbsvc["website_faculty_channels"].getone("faculty_id=%s", [faculty_id])
    dbsvc["website_faculty_channels_subscriptions"].insert(user_id, faculty_channel["id"])


def create_subscription_to_department_channel(user_id, department_id):
    department_channel = dbsvc["website_department_channels"].getone("department_id=%s", [department_id])
    dbsvc["website_department_channels_subscriptions"].insert(user_id, department_channel["id"])


def create_subscriptions_to_default_channels(user_id):
    for channel_type in [ChannelTypes.KKDB_SPECIAL, ChannelTypes.WEBSITE_MISC]:
        dbsvc_channels = dbsvc[channel_type + "_channels"]
        dbsvc_subscriptions = dbsvc[channel_type + "_channels_subscriptions"]
        for channel in dbsvc_channels.getall("subscribe_by_default=%s", [True]):
            dbsvc_subscriptions.insert(user_id, channel["id"])


def get_or_create_stat(name, item_id, default_value=0):
    stat = dbsvc["stats"].getone("name=%s AND item_id=%s", [name, item_id])
    if stat:
        return stat
    else:
        dbsvc["stats"].insert(name, item_id, default_value)
        return default_value


def increment_or_create_stat(name, item_id, default_value=0):
    stat = dbsvc["stats"].getone("name=%s AND item_id=%s", [name, item_id])
    if stat:
        dbsvc["stats"].increaseColumn("value", 1, "id=%s", [stat["id"]])
    else:
        dbsvc["stats"].insert(name, item_id, default_value + 1)


def toggle_subscription(user_id, channel_type, channel_id):
    dbsvc_subscriptions = dbsvc[channel_type + "_channels_subscriptions"]
    if subscription := dbsvc_subscriptions.getone("user_id=%s AND channel_id=%s", [user_id, channel_id]):
        dbsvc_subscriptions.deletebyid(subscription["id"])
        new_state = False
    else:
        dbsvc_subscriptions.insert(user_id, channel_id)
        new_state = True
    return new_state


def find_type_of_channel_with_name(channel_name):
    for channel_type in ChannelTypes.as_list():
        channel = dbsvc[channel_type + "_channels"].getone("name=%s", [channel_name])
        if channel:
            return channel_type, channel
    return None, None


def command_to_user_state(cmd):
    if cmd == Commands.TOGGLE_KKDB_SPECIAL_CHANNELS:
        return UserStates.TOGGLE_EXPECTING_KKDB_SPECIAL_CHANNEL
    elif cmd == Commands.TOGGLE_WEBSITE_FACULTY_CHANNELS:
        return UserStates.TOGGLE_EXPECTING_WEBSITE_FACULTY_CHANNEL
    elif cmd == Commands.TOGGLE_WEBSITE_DEPARTMENT_CHANNELS:
        return UserStates.TOGGLE_EXPECTING_WEBSITE_DEPARTMENT_CHANNEL
    elif cmd == Commands.TOGGLE_WEBSITE_MISC_CHANNELS:
        return UserStates.TOGGLE_EXPECTING_WEBSITE_MISC_CHANNEL
    else:
        raise Exception(f"Given command '{cmd}' isn't related to any user state.")


def command_to_channel_type(cmd):
    if cmd == Commands.TOGGLE_KKDB_SPECIAL_CHANNELS:
        return ChannelTypes.KKDB_SPECIAL
    elif cmd == Commands.TOGGLE_WEBSITE_FACULTY_CHANNELS:
        return ChannelTypes.WEBSITE_FACULTY
    elif cmd == Commands.TOGGLE_WEBSITE_DEPARTMENT_CHANNELS:
        return ChannelTypes.WEBSITE_DEPARTMENT
    elif cmd == Commands.TOGGLE_WEBSITE_MISC_CHANNELS:
        return ChannelTypes.WEBSITE_MISC
    else:
        raise Exception(f"Given command '{cmd}' isn't related to any channel type.")


def user_state_to_channel_type(state):
    if state == UserStates.TOGGLE_EXPECTING_KKDB_SPECIAL_CHANNEL:
        return ChannelTypes.KKDB_SPECIAL
    elif state == UserStates.TOGGLE_EXPECTING_WEBSITE_FACULTY_CHANNEL:
        return ChannelTypes.WEBSITE_FACULTY
    elif state == UserStates.TOGGLE_EXPECTING_WEBSITE_DEPARTMENT_CHANNEL:
        return ChannelTypes.WEBSITE_DEPARTMENT
    elif state == UserStates.TOGGLE_EXPECTING_WEBSITE_MISC_CHANNEL:
        return ChannelTypes.WEBSITE_MISC
    else:
        raise Exception(f"Given user state '{state}' isn't related to any channel type.")


def user_state_to_message_text(state):
    if state == UserStates.MEETING_EXPECTING_FACULTY:
        return MT.ask_faculty()
    elif state == UserStates.MEETING_EXPECTING_DEPARTMENT:
        return MT.ask_department()
    else:
        raise Exception(f"Given user state '{state}' isn't related to any message text.")

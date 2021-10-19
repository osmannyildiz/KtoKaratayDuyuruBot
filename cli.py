import sys
from tgbots.kto_karatay_duyuru_bot.main import bot
from pprint import pprint


def add_to_faculties():
    with bot.dbconn.cursor() as cur:
        print("start")
        i = 0
        with open("_meta/faculties.txt") as f:
            for line in f:
                print("add")
                cur.execute("INSERT INTO faculties (name, code) VALUES (%s,%s);", line[:-1].split("\t"))
                i += 1
        print(f"added {i} records")
        print("end")


def add_to_departments():
    with bot.dbconn.cursor() as cur:
        print("start")
        i = 0
        with open("_meta/departments.txt") as f:
            for line in f:
                print("add")
                cur.execute("INSERT INTO departments (faculty_id, name, code) VALUES (%s,%s,%s);", line[:-1].split("\t"))
                i += 1
        print(f"added {i} records")
        print("end")


def add_to_channels():
    with bot.dbconn.cursor() as cur:
        print("start")
        i = 0
        with open("_meta/channels.txt") as f:
            for line in f:
                print("add")
                cur.execute("INSERT INTO channels (name, item_type) VALUES (%s,%s);", [line[:-1], 3])
                i += 1
        print(f"added {i} records")
        print("end")


def generate_channels():
    faculties = []
    with open("_meta/faculties.txt") as f:
        for line in f:
            faculties.append(line[:-1].split("\t")[0])

    departments = []
    with open("_meta/departments.txt") as f:
        for line in f:
            departments.append(line[:-1].split("\t")[1])

    if len(faculties) != len(set(faculties)):
        pprint(faculties)
        pprint(set(faculties))
        raise Exception("Faculty names aren't unique")
    if len(departments) != len(set(departments)):
        pprint(departments)
        pprint(set(departments))
        raise Exception("Department names aren't unique")

    with bot.dbconn.cursor() as cur:
        print("start")
        i = 0

        cur.execute("SELECT id, name FROM faculties;")
        rows = cur.fetchall()
        for faculty_id, faculty_name in rows:
            if faculty_name in departments:
                faculty_name += " (Fakülte)"
            print("add")
            cur.execute("INSERT INTO channels (name, item_type, item_id) VALUES (%s,%s,%s);", [faculty_name, 1, faculty_id])
            i += 1

        cur.execute("SELECT id, name FROM departments;")
        rows = cur.fetchall()
        for department_id, department_name in rows:
            if department_name in faculties:
                department_name += " (Bölüm)"
            print("add")
            cur.execute("INSERT INTO channels (name, item_type, item_id) VALUES (%s,%s,%s);", [department_name, 2, department_id])
            i += 1

        print(f"added {i} records")
        print("end")


def reset_last_announcement_ids():
    with bot.dbconn.cursor() as cur:
        print("start")
        cur.execute("UPDATE channels SET last_announcement_id = NULL;")
        print("end")


def check_and_handle_new_faculties_announcements(bot):
    from tgbots.kto_karatay_duyuru_bot.scraping import get_new_faculties_announcements, MSG_FORMAT
    from tgbots.kto_karatay_duyuru_bot.db_helpers import (
        get_channel_by_faculty_id, get_subscriptions_by_channel_id
    )
    from tgbots.kto_karatay_duyuru_bot.helpers import get_subscribed_users_ids

    new_faculties_announcements = get_new_faculties_announcements(bot)
    for faculty_id, faculty_announcements in new_faculties_announcements.items():
        channel_id, channel_name = get_channel_by_faculty_id(bot, faculty_id, "id, name")
        subscribed_users_ids = get_subscribed_users_ids(bot, channel_id)
        for user_id in subscribed_users_ids:
            for announcement in faculty_announcements:
                bot.api.send_message(
                    user_id,
                    MSG_FORMAT.format(
                        channel_name=bot.api.escape_mdv2(channel_name),
                        announcement_date=bot.api.escape_mdv2(announcement['date'].strftime('%d.%m.%Y')),
                        announcement_title=bot.api.escape_mdv2(announcement['title']),
                        announcement_url=announcement['url']
                    ),
                    parse_mode="MarkdownV2",
                    disable_preview=True
                )


def check_and_handle_new_departments_announcements(bot):
    from tgbots.kto_karatay_duyuru_bot.scraping import get_new_departments_announcements, MSG_FORMAT
    from tgbots.kto_karatay_duyuru_bot.db_helpers import (
        get_channel_by_department_id, get_subscriptions_by_channel_id
    )
    from tgbots.kto_karatay_duyuru_bot.helpers import get_subscribed_users_ids

    new_departments_announcements = get_new_departments_announcements(bot)
    for department_id, department_announcements in new_departments_announcements.items():
        channel_id, channel_name = get_channel_by_department_id(bot, department_id, "id, name")
        subscribed_users_ids = get_subscribed_users_ids(bot, channel_id)
        for user_id in subscribed_users_ids:
            for announcement in department_announcements:
                bot.api.send_message(
                    user_id,
                    MSG_FORMAT.format(
                        channel_name=bot.api.escape_mdv2(channel_name),
                        announcement_date=bot.api.escape_mdv2(announcement['date'].strftime('%d.%m.%Y')),
                        announcement_title=bot.api.escape_mdv2(announcement['title']),
                        announcement_url=announcement['url']
                    ),
                    parse_mode="MarkdownV2",
                    disable_preview=True
                )


def main(argv):
    arg1 = argv[1]
    if arg1 == "add_to_faculties":
        add_to_faculties()
    elif arg1 == "add_to_departments":
        add_to_departments()
    elif arg1 == "add_to_channels":
        add_to_channels()
    elif arg1 == "generate_channels":
        generate_channels()
    elif arg1 == "db_setup":
        print("- enter mysql shell: mysql -p")
        print("- dump database (if exists): DROP DATABASE kkdb;")
        print("- create database: CREATE DATABASE kkdb;")
        print("- exit mysql shell: exit")
        print('- import sql: mysql -p kkdb < "independent study.sql"')
        print("if you haven't done these, press 'ctrl+c'. else, press 'enter'")
        input()
        add_to_faculties()
        add_to_departments()
        generate_channels()
        add_to_channels()
    elif arg1 == "reset_last_announcement_ids":
        reset_last_announcement_ids()
    elif arg1 == "cron_tasks":
        check_and_handle_new_faculties_announcements(bot)
        check_and_handle_new_departments_announcements(bot)
    else:
        print("error: arg1")



if __name__ == "__main__":
    main(sys.argv)

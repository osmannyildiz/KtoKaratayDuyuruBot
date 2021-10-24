import sys
import csv
from tgbots.kto_karatay_duyuru_bot.main import bot
from tgbots.kto_karatay_duyuru_bot.db import dbsvc
from pprint import pprint


def import_faculties():
    print("start")
    i = 0
    with open("data/faculties.csv") as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            print("add")
            dbsvc["faculties"].insert(*row)
            i += 1
    print(f"added {i} records")
    print("end")


def import_departments():
    print("start")
    i = 0
    with open("data/departments.csv") as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            print("add")
            dbsvc["departments"].insert(*row)
            i += 1
    print(f"added {i} records")
    print("end")


def import_special_channels():
    print("start")
    i = 0
    with open("data/special_channels.csv") as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            print("add")
            dbsvc["channels"].insert(row[0], 3, None)
            i += 1
    print(f"added {i} records")
    print("end")


def generate_channels():
    faculties = []
    with open("data/faculties.csv") as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            faculties.append(row[0])

    departments = []
    with open("data/departments.csv") as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            departments.append(row[1])

    if len(faculties) != len(set(faculties)):
        pprint(faculties)
        pprint(set(faculties))
        raise Exception("Faculty names aren't unique")
    if len(departments) != len(set(departments)):
        pprint(departments)
        pprint(set(departments))
        raise Exception("Department names aren't unique")

    print("start")
    i = 0

    for faculty in dbsvc["faculties"].get():
        if faculty["name"] in departments:
            faculty["name"] += " (Fakülte)"
        print("add")
        dbsvc["channels"].insert(faculty["name"], 1, faculty["id"])
        i += 1

    for department in dbsvc["departments"].get():
        if department["name"] in faculties:
            department["name"] += " (Bölüm)"
        print("add")
        dbsvc["channels"].insert(department["name"], 2, department["id"])
        i += 1

    print(f"added {i} records")
    print("end")


def reset_last_announcement_ids():
    print("start")
    dbsvc["channels"].update("last_announcement_id=NULL", None, "true", None)
    print("end")


def check_and_handle_new_announcements(bot, dbsvc, item_type):
    from tgbots.kto_karatay_duyuru_bot.scraping import get_new_announcements, MSG_FORMAT
    from tgbots.kto_karatay_duyuru_bot.helpers import get_subscribed_users_ids

    new_announcements = get_new_announcements(dbsvc, item_type)
    for item_id, item_announcements in new_announcements.items():
        if item_type == "faculty":
            item_channel = dbsvc["channels"].getone("item_type=%s AND item_id=%s", [1, item_id])
        elif item_type == "department":
            item_channel = dbsvc["channels"].getone("item_type=%s AND item_id=%s", [2, item_id])
        subscribed_users_ids = get_subscribed_users_ids(bot, item_channel["id"])
        for user_id in subscribed_users_ids:
            for announcement in item_announcements:
                bot.api.send_message(
                    user_id,
                    MSG_FORMAT.format(
                        channel_name=bot.api.escape_mdv2(item_channel["name"]),
                        announcement_date=bot.api.escape_mdv2(announcement['date'].strftime('%d.%m.%Y')),
                        announcement_title=bot.api.escape_mdv2(announcement['title']),
                        announcement_url=announcement['url']
                    ),
                    parse_mode="MarkdownV2",
                    disable_preview=True
                )


def main(argv):
    arg1 = argv[1]
    if arg1 == "import_faculties":
        import_faculties()
    elif arg1 == "import_departments":
        import_departments()
    elif arg1 == "import_special_channels":
        import_special_channels()
    elif arg1 == "generate_channels":
        generate_channels()
    elif arg1 == "init_db":
        # print("- enter mysql shell: mysql -p")
        # print("- drop database (if exists): DROP DATABASE kkdb;")
        # print("- create database: CREATE DATABASE kkdb;")
        # print("- exit mysql shell: exit")
        print('- import sql: mysql -p kkdb < "independent study.sql"')
        print("if you haven't done these, press 'ctrl+c'. else, press 'enter'")
        input()
        import_faculties()
        import_departments()
        generate_channels()
        import_special_channels()
    elif arg1 == "reset_last_announcement_ids":
        reset_last_announcement_ids()
    elif arg1 == "cron_tasks":
        check_and_handle_new_announcements(bot, dbsvc, "faculty")
        check_and_handle_new_announcements(bot, dbsvc, "department")
    else:
        print("error: arg1")


if __name__ == "__main__":
    main(sys.argv)

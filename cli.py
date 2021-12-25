import sys
import csv
from tgbots.kto_karatay_duyuru_bot.bot import bot
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
            dbsvc["channels"].insert(row[0], 3, [])
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
    dbsvc["channels"].update("last_announcement_id=NULL", [], "true", [])
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
        subscribed_users_ids = get_subscribed_users_ids(dbsvc, item_channel["id"])
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
    cmd = argv[1]
    if cmd == "set_webhook":
        ok, r = bot.api.set_webhook(argv[2])
        if ok:
            print("OK")
        else:
            print("ERROR:")
            pprint(r)
    elif cmd == "delete_webhook":
        ok, r = bot.api.delete_webhook()
        if ok:
            print("OK")
        else:
            print("ERROR:")
            pprint(r)
    elif cmd == "init_db":
        print("- import sql: mysql -p < misc/mysql_schema.sql")
        print("do this, then press 'enter'")
        input()
        import_faculties()
        import_departments()
        generate_channels()
        import_special_channels()
    elif cmd == "reset_last_announcement_ids":
        reset_last_announcement_ids()
    elif cmd == "cron_tasks":
        check_and_handle_new_announcements(bot, dbsvc, "faculty")
        check_and_handle_new_announcements(bot, dbsvc, "department")
    else:
        print("ERROR: Given command doesn't exist.")


if __name__ == "__main__":
    main(sys.argv)

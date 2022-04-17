import sys
import csv
from tgbots.kto_karatay_duyuru_bot.bot import bot
from tgbots.kto_karatay_duyuru_bot.db import dbsvc
from tgbots.kto_karatay_duyuru_bot.config import MESSAGE_FORMAT
from tgbots.kto_karatay_duyuru_bot.constants import ChannelTypes
from tgbots.kto_karatay_duyuru_bot.models.channel_context import ChannelContext
from tgbots.kto_karatay_duyuru_bot.announcements_services import WebsiteAnnouncementsService, WebsiteFacultyAnnouncementsService, WebsiteDepartmentAnnouncementsService
from pprint import pprint


channel_ctxs = [
    ChannelContext(ChannelTypes.WEBSITE_FACULTY, WebsiteFacultyAnnouncementsService, dbsvc["faculties"]),
    ChannelContext(ChannelTypes.WEBSITE_DEPARTMENT, WebsiteDepartmentAnnouncementsService, dbsvc["departments"]),
    ChannelContext(ChannelTypes.WEBSITE_MISC, WebsiteAnnouncementsService)
]


def import_faculties():
    print("Importing faculties...\t", end="")
    i = 0
    with open("data/faculties.csv") as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            dbsvc["faculties"].insert(row["name"], row["code"])
            i += 1
    print(f"Done. Added {i} faculties.")


def import_departments():
    print("Importing departments...\t", end="")
    i = 0
    with open("data/departments.csv") as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            code = row["code"] if row["code"] else None
            dbsvc["departments"].insert(row["faculty_id"], row["name"], code)
            i += 1
    print(f"Done. Added {i} departments.")


def import_website_misc_channels():
    print("Importing website misc channels...\t", end="")
    i = 0
    with open("data/website_misc_channels.csv") as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            subscribe_by_default = True if row["subscribe_by_default"] == "true" else False
            dbsvc["website_misc_channels"].insert(row["name"], row["url"], subscribe_by_default)
            i += 1
    print(f"Done. Added {i} website misc channels.")


def import_kkdb_special_channels():
    print("Importing KKDB special channels...\t", end="")
    i = 0
    with open("data/kkdb_special_channels.csv") as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            subscribe_by_default = True if row["subscribe_by_default"] == "true" else False
            dbsvc["kkdb_special_channels"].insert(row["name"], subscribe_by_default)
            i += 1
    print(f"Done. Added {i} KKDB special channels.")


def generate_channels_for_faculties_and_departments():
    faculties = []
    with open("data/faculties.csv") as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            faculties.append(row["name"])

    departments = []
    with open("data/departments.csv") as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            departments.append(row["name"])

    if len(faculties) != len(set(faculties)):
        raise Exception("Faculty names aren't unique!")
    if len(departments) != len(set(departments)):
        raise Exception("Department names aren't unique!")

    print("Generating channels for faculties...\t", end="")
    i = 0
    for faculty in dbsvc["faculties"].getall():
        if faculty["name"] in departments:
            faculty["name"] += " (Fakülte)"
        dbsvc["website_faculty_channels"].insert(faculty["name"], faculty["id"])
        i += 1
    print(f"Done. Added {i} faculty channels.")

    print("Generating channels for departments...\t", end="")
    i = 0
    for department in dbsvc["departments"].getall():
        if department["name"] in faculties:
            department["name"] += " (Bölüm)"
        dbsvc["website_department_channels"].insert(department["name"], department["id"])
        i += 1
    print(f"Done. Added {i} department channels.")


def reset_last_announcement_ids():
    print("Resetting last announcement ids of relevant channels...\t", end="")
    for channel_ctx in channel_ctxs:
        channel_ctx.service.reset_last_announcement_ids()
    print("Done.")


def check_and_handle_new_announcements():
    for channel_ctx in channel_ctxs:
        new_announcements = channel_ctx.service.get_new_announcements_of_all_channels()
        for channel_id, channel_announcements in new_announcements.items():
            channel = channel_ctx.dbsvc_channels.getbyid(channel_id)
            subscribed_users_ids = (
                subscription["user_id"]
                for subscription in channel_ctx.dbsvc_subscriptions.get("channel_id=%s", [channel["id"]])
            )
            for user_id in subscribed_users_ids:
                for announcement in channel_announcements:
                    user = dbsvc["users"].getbyid(user_id)
                    if not user:
                        # Muhtemelen önceki mesajı gönderirken bu kullanıcının botu sildiğini fark ettik
                        break
                    chat_id = user["chat_id"]
                    print(f"sending message to {chat_id}")
                    bot.send_message(
                        chat_id,
                        MESSAGE_FORMAT.format(
                            channel_name=bot.api.escape_mdv2(channel["name"]),
                            announcement_date=bot.api.escape_mdv2(announcement.date.strftime('%d.%m.%Y')),
                            announcement_title=bot.api.escape_mdv2(announcement.title),
                            announcement_url=announcement.url
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
        print("$ mysql -u mydbuser -p < misc/mysql_schema.sql")
        input("Do this, then press 'Enter': ")
        import_faculties()
        import_departments()
        generate_channels_for_faculties_and_departments()
        import_website_misc_channels()
        import_kkdb_special_channels()
    elif cmd == "reset_last_announcement_ids":
        reset_last_announcement_ids()
    elif cmd == "cron_tasks":
        check_and_handle_new_announcements()
    else:
        print("ERROR: Given command doesn't exist.")


if __name__ == "__main__":
    main(sys.argv)

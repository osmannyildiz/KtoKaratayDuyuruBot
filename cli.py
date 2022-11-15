import sys
import csv
from tgbots.kto_karatay_duyuru_bot.bot import bot
from tgbots.kto_karatay_duyuru_bot.db import dbsvc
from tgbots.kto_karatay_duyuru_bot.config import MESSAGE_FORMAT
from tgbots.kto_karatay_duyuru_bot.constants import ChannelTypes
from tgbots.kto_karatay_duyuru_bot.models.channel_group_context import ChannelGroupContext
from tgbots.kto_karatay_duyuru_bot.announcements_services import WebsiteAnnouncementsService, WebsiteFacultyAnnouncementsService, WebsiteDepartmentAnnouncementsService
from datetime import datetime
from pprint import pprint


website_channel_group_ctxs = [
    ChannelGroupContext(ChannelTypes.WEBSITE_FACULTY, WebsiteFacultyAnnouncementsService, dbsvc["faculties"]),
    ChannelGroupContext(ChannelTypes.WEBSITE_DEPARTMENT, WebsiteDepartmentAnnouncementsService, dbsvc["departments"]),
    ChannelGroupContext(ChannelTypes.WEBSITE_MISC, WebsiteAnnouncementsService)
]


def print_with_time(msg, **kwargs):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H-%M-%S')}]\t{msg}", **kwargs)


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


def reset_last_announcement_ids_of_website_channels():
    print("Resetting last announcement ids of website channels...\t", end="")
    for channel_ctx in website_channel_group_ctxs:
        channel_ctx.service.reset_last_announcement_ids()
    print("Done.")


def check_and_handle_new_website_announcements():
    print_with_time("== Starting to check and handle new announcements.")

    for channel_group_ctx in website_channel_group_ctxs:
        for channel in channel_group_ctx.dbsvc_channels.getall():
            if channel["disable_website_check"]:
                # print_with_time(f"Skipping channel {channel['name']}.")
                continue

            channel_announcements = channel_group_ctx.service.get_new_announcements_of_channel(channel)
            num_announcements = len(channel_announcements)
            print_with_time(f"{num_announcements} new announcements for channel {channel['name']}.")

            if not num_announcements:
                continue

            subscribed_users_ids = (
                subscription["user_id"]
                for subscription in channel_group_ctx.dbsvc_subscriptions.get("channel_id=%s", [channel["id"]])
            )

            i = 0
            for user_id in subscribed_users_ids:
                for announcement in channel_announcements:
                    user = dbsvc["users"].getbyid(user_id)
                    if not user:
                        # Muhtemelen önceki mesajı gönderirken bu kullanıcının botu sildiğini fark ettik
                        break
                    chat_id = user["chat_id"]
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
                    i += 1
            print_with_time(f"Sent {i} messages.")

    print_with_time("== Finished.")


def disable_website_check_for_website_channels_with_no_subscribers():  # haha ;D
    print("Disabling website check for website channels with no subscribers...\t", end="")

    i = 0
    for channel_group_ctx in website_channel_group_ctxs:
        for channel in channel_group_ctx.dbsvc_channels.getall("disable_website_check=false", []):
            # if channel["disable_website_check"]:
            #     continue
            any_subscription = channel_group_ctx.dbsvc_subscriptions.getone("channel_id=%s", [channel["id"]])
            if not any_subscription:
                channel_group_ctx.dbsvc_channels.update_column_with_value("disable_website_check", True, "id=%s", [channel["id"]])
                i += 1

    print(f"Done. Disabled website check for {i} channels.")


def main(argv):
    cmd = argv[1]
    if cmd == "get_webhook":
        ok, r = bot.api.get_webhook_info()
        if ok:
            print("OK")
            pprint(r["result"])
        else:
            print("ERROR:")
            pprint(r)
    elif cmd == "set_webhook":
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
        reset_last_announcement_ids_of_website_channels()
    elif cmd == "disable_website_check":
        disable_website_check_for_website_channels_with_no_subscribers()
    elif cmd == "cron_tasks":
        check_and_handle_new_website_announcements()
    else:
        print("ERROR: Given command doesn't exist.")


if __name__ == "__main__":
    main(sys.argv)

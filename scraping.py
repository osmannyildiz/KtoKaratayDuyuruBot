from tgbots.kto_karatay_duyuru_bot.helpers import parse_string_to_date
import requests
from bs4 import BeautifulSoup
from datetime import date, timedelta


BASE_URL = "https://www.karatay.edu.tr/"
FACULTY_ANNOUNCEMENTS_URL_FORMAT = BASE_URL + "FakulteDuyurular/{}.html"
DEPARTMENT_ANNOUNCEMENTS_URL_FORMAT = BASE_URL + "BolumDuyurular/{}.html"
OLDEST_DATE = date.today() - timedelta(days=45)
MSG_FORMAT = "\\[{channel_name} \\- `{announcement_date}`\\]\n*{announcement_title}*\n[Duyuruya git]({announcement_url})"


def get_announcements(item_type, item_code):
    if item_type == "faculty":
        print(FACULTY_ANNOUNCEMENTS_URL_FORMAT.format(item_code))
        resp = requests.get(FACULTY_ANNOUNCEMENTS_URL_FORMAT.format(item_code))
    elif item_type == "department":
        print(DEPARTMENT_ANNOUNCEMENTS_URL_FORMAT.format(item_code))
        resp = requests.get(DEPARTMENT_ANNOUNCEMENTS_URL_FORMAT.format(item_code))
    soup = BeautifulSoup(resp.text, "html.parser")
    els_announcement = soup.select(".postcontent tr")
    els_announcement.pop(0)  # table header
    r = []
    for el_announcement in els_announcement:
        announcement_date = el_announcement.select("td:nth-child(1) a")[0].string.strip()
        el_announcement_link = el_announcement.select("td:nth-child(2) a")[0]
        announcement_id = int(el_announcement_link["href"].split("/")[-1][:-5])
        announcement_title = el_announcement_link.string.strip()
        announcement_url = BASE_URL + el_announcement_link["href"]
        r.append({
            "id": announcement_id,
            "date": parse_string_to_date(announcement_date),
            "title": announcement_title,
            "url": announcement_url
        })
    print(f"{len(r)} unfiltered")
    return r


def get_new_announcements(dbsvc, item_type):
    if item_type == "faculty":
        items = dbsvc["faculties"].getall()
    elif item_type == "department":
        items = dbsvc["departments"].getall()
    r = {}
    for item in items:
        if item_type == "faculty":
            item_channel = dbsvc["channels"].getone("item_type=%s AND item_id=%s", [1, item["id"]])
        elif item_type == "department":
            if not item["code"]:
                continue
            item_channel = dbsvc["channels"].getone("item_type=%s AND item_id=%s", [2, item["id"]])
        item_announcements = get_announcements(item_type, item["code"])
        item_announcements = [announcement for announcement in item_announcements if announcement["date"] > OLDEST_DATE]
        if item_channel["last_announcement_id"]:
            item_announcements = [announcement for announcement in item_announcements if announcement["id"] > item_channel["last_announcement_id"]]  # type(item_channel["last_announcement_id"]) == int
        if item_announcements:
            r[item["id"]] = item_announcements
            new_item_channel_last_announcement_id = max([announcement["id"] for announcement in item_announcements])
            dbsvc["channels"].update_column_with_value("last_announcement_id", new_item_channel_last_announcement_id, "id=%s", [item_channel["id"]])
    return r

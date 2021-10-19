import requests
from bs4 import BeautifulSoup
from datetime import date, timedelta
from tgbots.kto_karatay_duyuru_bot.db_helpers import (
    get_faculties,
    get_departments,
    get_channel_by_faculty_id, get_channel_by_department_id, set_channel
)
from tgbots.kto_karatay_duyuru_bot.helpers import parse_string_to_date


BASE_URL = "https://www.karatay.edu.tr/"
FACULTY_ANNOUNCEMENTS_URL_FORMAT = BASE_URL + "FakulteDuyurular/{}.html"
DEPARTMENT_ANNOUNCEMENTS_URL_FORMAT = BASE_URL + "BolumDuyurular/{}.html"
OLDEST_DATE = date.today() - timedelta(days=45)
MSG_FORMAT = "\\[{channel_name} \\- `{announcement_date}`\\]\n*{announcement_title}*\n[Duyuruya git]({announcement_url})"


def get_faculty_announcements(faculty_code):
    print(FACULTY_ANNOUNCEMENTS_URL_FORMAT.format(faculty_code))
    resp = requests.get(FACULTY_ANNOUNCEMENTS_URL_FORMAT.format(faculty_code))
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
    print(len(r), "unfiltered")
    return r


def get_new_faculties_announcements(bot):
    faculty_rows = get_faculties(bot, "id, code")
    r = {}
    for faculty_row in faculty_rows:
        faculty_id, faculty_code = faculty_row
        channel_id, channel_last_announcement_id = get_channel_by_faculty_id(bot, faculty_id, "id, last_announcement_id")  # type(channel_last_announcement_id) == int
        faculty_announcements = get_faculty_announcements(faculty_code)
        faculty_announcements = [announcement for announcement in faculty_announcements if announcement["date"] > OLDEST_DATE]
        if channel_last_announcement_id:
            faculty_announcements = [announcement for announcement in faculty_announcements if announcement["id"] > channel_last_announcement_id]
        if faculty_announcements:
            r[faculty_id] = faculty_announcements
            new_channel_last_announcement_id = max([announcement["id"] for announcement in faculty_announcements])
            set_channel(bot, channel_id, "last_announcement_id", new_channel_last_announcement_id)
    return r


def get_department_announcements(department_code):
    print(DEPARTMENT_ANNOUNCEMENTS_URL_FORMAT.format(department_code))
    resp = requests.get(DEPARTMENT_ANNOUNCEMENTS_URL_FORMAT.format(department_code))
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
    print(len(r), "unfiltered")
    return r


def get_new_departments_announcements(bot):
    department_rows = get_departments(bot, "id, code")
    r = {}
    for department_row in department_rows:
        department_id, department_code = department_row
        if not department_code:
            continue
        channel_id, channel_last_announcement_id = get_channel_by_department_id(bot, department_id, "id, last_announcement_id")  # type(channel_last_announcement_id) == int
        department_announcements = get_department_announcements(department_code)
        department_announcements = [announcement for announcement in department_announcements if announcement["date"] > OLDEST_DATE]
        if channel_last_announcement_id:
            department_announcements = [announcement for announcement in department_announcements if announcement["id"] > channel_last_announcement_id]
        if department_announcements:
            r[department_id] = department_announcements
            new_channel_last_announcement_id = max([announcement["id"] for announcement in department_announcements])
            set_channel(bot, channel_id, "last_announcement_id", new_channel_last_announcement_id)
    return r

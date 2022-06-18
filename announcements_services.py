import requests
from bs4 import BeautifulSoup
from tgbots.kto_karatay_duyuru_bot.config import OLDEST_ANNOUNCEMENT_DATE
from tgbots.kto_karatay_duyuru_bot.models.website_announcement import WebsiteAnnouncement
from tgbots.kto_karatay_duyuru_bot.helpers import parse_string_to_date


class WebsiteAnnouncementsService:
    base_url = "https://www.karatay.edu.tr/"

    def __init__(self, dbsvc_channels):
        self.dbsvc_channels = dbsvc_channels

    def get_source_url_of_channel(self, channel):
        return self.base_url + channel["url"]

    def reset_last_announcement_ids(self):
        self.dbsvc_channels.update_column_with_value("last_announcement_id", None, "true", [])

    def get_announcements_of_channel(self, channel):
        if channel.get("disable_website_check"):
            return []

        announcements = []

        source_url = self.get_source_url_of_channel(channel)
        if source_url:
            resp = requests.get(source_url)
            soup = BeautifulSoup(resp.text, "html.parser")
            els_announcement = soup.select(".postcontent tr")
            els_announcement.pop(0)  # Table header
            for el_announcement in els_announcement:
                announcement_date = el_announcement.select("td:nth-child(1) a")[0].string.strip()
                el_announcement_link = el_announcement.select("td:nth-child(2) a")[0]
                announcement_id = int(el_announcement_link["href"].split("/")[-1][:-5])
                announcement_title = el_announcement_link.string.strip()
                announcement_url = self.base_url + el_announcement_link["href"]
                announcements.append(WebsiteAnnouncement(
                    announcement_id,
                    parse_string_to_date(announcement_date),
                    announcement_title,
                    announcement_url
                ))

        return announcements

    def get_new_announcements_of_channel(self, channel):
        announcements = self.get_announcements_of_channel(channel)

        # Filter for oldest announcement date
        announcements = [
            announcement
            for announcement in announcements
            if announcement.date > OLDEST_ANNOUNCEMENT_DATE
        ]

        # Filter for last announcement id
        if channel["last_announcement_id"]:
            announcements = [
                announcement
                for announcement in announcements
                if announcement.id > channel["last_announcement_id"]
            ]

        # Update last announcement id
        if announcements:
            last_announcement_id = max([announcement.id for announcement in announcements], default=None)
            if last_announcement_id:
                self.dbsvc_channels.update_column_with_value("last_announcement_id", last_announcement_id, "id=%s", [channel["id"]])

        return announcements


class WebsiteFacultyAnnouncementsService(WebsiteAnnouncementsService):
    def __init__(self, dbsvc_channels, dbsvc_faculties):
        super().__init__(dbsvc_channels)
        self.dbsvc_faculties = dbsvc_faculties

    def get_source_url_of_channel(self, channel):
        faculty = self.dbsvc_faculties.getbyid(channel["faculty_id"])
        return self.base_url + "FakulteDuyurular/{}.html".format(faculty["code"])


class WebsiteDepartmentAnnouncementsService(WebsiteAnnouncementsService):
    def __init__(self, dbsvc_channels, dbsvc_departments):
        super().__init__(dbsvc_channels)
        self.dbsvc_departments = dbsvc_departments

    def get_source_url_of_channel(self, channel):
        department = self.dbsvc_departments.getbyid(channel["department_id"])
        if department["code"]:
            return self.base_url + "BolumDuyurular/{}.html".format(department["code"])

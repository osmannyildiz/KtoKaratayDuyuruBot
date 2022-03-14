from dataclasses import dataclass
from datetime import date


@dataclass
class WebsiteAnnouncement:
    id : int
    date : date
    title : str
    url : str

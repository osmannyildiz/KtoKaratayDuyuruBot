from dbpkg.databases.mysql import create_dbconn
from dbpkg.service import DbTableServiceBase
from dbpkg.utils import DbconnManager


class DbFacultiesService(DbTableServiceBase):
    def __init__(self, get_dbconn):
        super().__init__("faculties", get_dbconn)

    def insert(self, name, code):
        return self._insert("name, code", "%s, %s", [name, code])


class DbDepartmentsService(DbTableServiceBase):
    def __init__(self, get_dbconn):
        super().__init__("departments", get_dbconn)

    def insert(self, faculty_id, name, code):
        return self._insert("faculty_id, name, code", "%s, %s, %s", [faculty_id, name, code])


class DbUsersService(DbTableServiceBase):
    def __init__(self, get_dbconn):
        super().__init__("users", get_dbconn)

    def insert(self, chat_id, state):
        return self._insert("chat_id, state", "%s, %s", [chat_id, state])

    def set_state(self, user_id, new_state):
        return self.update_column_with_value("state", new_state, "id=%s", [user_id])


class DbKkdbSpecialChannelsService(DbTableServiceBase):
    def __init__(self, get_dbconn):
        super().__init__("kkdb_special_channels", get_dbconn)

    def insert(self, name, subscribe_by_default=False):
        return self._insert("name, subscribe_by_default", "%s, %s", [name, subscribe_by_default])


class DbWebsiteFacultyChannelsService(DbTableServiceBase):
    def __init__(self, get_dbconn):
        super().__init__("website_faculty_channels", get_dbconn)

    def insert(self, name, faculty_id):
        return self._insert("name, faculty_id", "%s, %s", [name, faculty_id])


class DbWebsiteDepartmentChannelsService(DbTableServiceBase):
    def __init__(self, get_dbconn):
        super().__init__("website_department_channels", get_dbconn)

    def insert(self, name, department_id):
        return self._insert("name, department_id", "%s, %s", [name, department_id])


class DbWebsiteMiscChannelsService(DbTableServiceBase):
    def __init__(self, get_dbconn):
        super().__init__("website_misc_channels", get_dbconn)

    def insert(self, name, url, subscribe_by_default=False):
        return self._insert("name, url, subscribe_by_default", "%s, %s, %s", [name, url, subscribe_by_default])


class DbChannelsSubscriptionsServiceBase(DbTableServiceBase):
    def insert(self, user_id, channel_id):
        return self._insert("user_id, channel_id", "%s, %s", [user_id, channel_id])


class DbKkdbSpecialChannelsSubscriptionsService(DbChannelsSubscriptionsServiceBase):
    def __init__(self, get_dbconn):
        super().__init__("kkdb_special_channels_subscriptions", get_dbconn)


class DbWebsiteFacultyChannelsSubscriptionsService(DbChannelsSubscriptionsServiceBase):
    def __init__(self, get_dbconn):
        super().__init__("website_faculty_channels_subscriptions", get_dbconn)


class DbWebsiteDepartmentChannelsSubscriptionsService(DbChannelsSubscriptionsServiceBase):
    def __init__(self, get_dbconn):
        super().__init__("website_department_channels_subscriptions", get_dbconn)


class DbWebsiteMiscChannelsSubscriptionsService(DbChannelsSubscriptionsServiceBase):
    def __init__(self, get_dbconn):
        super().__init__("website_misc_channels_subscriptions", get_dbconn)


class DbStatsService(DbTableServiceBase):
    def __init__(self, get_dbconn):
        super().__init__("stats", get_dbconn)

    def insert(self, name, item_id, value):
        return self._insert("name, item_id, value", "%s, %s, %s", [name, item_id, value])


get_dbconn = DbconnManager(create_dbconn("kkdb")).get_dbconn
dbsvc = {
    svc.table_name: svc
    for svc in [
        DbFacultiesService(get_dbconn),
        DbDepartmentsService(get_dbconn),
        DbUsersService(get_dbconn),
        DbKkdbSpecialChannelsService(get_dbconn),
        DbWebsiteFacultyChannelsService(get_dbconn),
        DbWebsiteDepartmentChannelsService(get_dbconn),
        DbWebsiteMiscChannelsService(get_dbconn),
        DbKkdbSpecialChannelsSubscriptionsService(get_dbconn),
        DbWebsiteFacultyChannelsSubscriptionsService(get_dbconn),
        DbWebsiteDepartmentChannelsSubscriptionsService(get_dbconn),
        DbWebsiteMiscChannelsSubscriptionsService(get_dbconn),
        DbStatsService(get_dbconn),
    ]
}

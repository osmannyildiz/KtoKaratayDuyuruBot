from dbpkg.service import DbTableServiceBase
from dbpkg.mysql import create_dbconn


class DbFacultiesService(DbTableServiceBase):
    def __init__(self, dbconn):
        super().__init__(dbconn, "faculties")

    def insert(self, name, code):
        return self._insert("name, code", "%s, %s", [name, code])


class DbDepartmentsService(DbTableServiceBase):
    def __init__(self, dbconn):
        super().__init__(dbconn, "departments")

    def insert(self, faculty_id, name, code):
        return self._insert("faculty_id, name, code", "%s, %s, %s", [faculty_id, name, code])


class DbUsersService(DbTableServiceBase):
    def __init__(self, dbconn):
        super().__init__(dbconn, "users")

    def insert(self, chat_id, state):
        return self._insert("chat_id, state", "%s, %s", [chat_id, state])

    def set_state(self, user_id, new_state):
        return self.update_column_with_value("state", new_state, "id=%s", [user_id])


class DbKkdbSpecialChannelsService(DbTableServiceBase):
    def __init__(self, dbconn):
        super().__init__(dbconn, "kkdb_special_channels")

    def insert(self, name, subscribe_by_default=False):
        return self._insert("name, subscribe_by_default", "%s, %s", [name, subscribe_by_default])


class DbWebsiteFacultyChannelsService(DbTableServiceBase):
    def __init__(self, dbconn):
        super().__init__(dbconn, "website_faculty_channels")

    def insert(self, name, faculty_id):
        return self._insert("name, faculty_id", "%s, %s", [name, faculty_id])


class DbWebsiteDepartmentChannelsService(DbTableServiceBase):
    def __init__(self, dbconn):
        super().__init__(dbconn, "website_department_channels")

    def insert(self, name, department_id):
        return self._insert("name, department_id", "%s, %s", [name, department_id])


class DbWebsiteMiscChannelsService(DbTableServiceBase):
    def __init__(self, dbconn):
        super().__init__(dbconn, "website_misc_channels")

    def insert(self, name, url, subscribe_by_default=False):
        return self._insert("name, url, subscribe_by_default", "%s, %s, %s", [name, url, subscribe_by_default])


class DbChannelsSubscriptionsServiceBase(DbTableServiceBase):
    def insert(self, user_id, channel_id):
        return self._insert("user_id, channel_id", "%s, %s", [user_id, channel_id])


class DbKkdbSpecialChannelsSubscriptionsService(DbChannelsSubscriptionsServiceBase):
    def __init__(self, dbconn):
        super().__init__(dbconn, "kkdb_special_channels_subscriptions")


class DbWebsiteFacultyChannelsSubscriptionsService(DbChannelsSubscriptionsServiceBase):
    def __init__(self, dbconn):
        super().__init__(dbconn, "website_faculty_channels_subscriptions")


class DbWebsiteDepartmentChannelsSubscriptionsService(DbChannelsSubscriptionsServiceBase):
    def __init__(self, dbconn):
        super().__init__(dbconn, "website_department_channels_subscriptions")


class DbWebsiteMiscChannelsSubscriptionsService(DbChannelsSubscriptionsServiceBase):
    def __init__(self, dbconn):
        super().__init__(dbconn, "website_misc_channels_subscriptions")


class DbStatsService(DbTableServiceBase):
    def __init__(self, dbconn):
        super().__init__(dbconn, "stats")

    def insert(self, name, item_id, value):
        return self._insert("name, item_id, value", "%s, %s, %s", [name, item_id, value])


dbconn = create_dbconn("kkdb")
dbsvc = {
    svc.tablename: svc
    for svc in [
        DbFacultiesService(dbconn),
        DbDepartmentsService(dbconn),
        DbUsersService(dbconn),
        DbKkdbSpecialChannelsService(dbconn),
        DbWebsiteFacultyChannelsService(dbconn),
        DbWebsiteDepartmentChannelsService(dbconn),
        DbWebsiteMiscChannelsService(dbconn),
        DbKkdbSpecialChannelsSubscriptionsService(dbconn),
        DbWebsiteFacultyChannelsSubscriptionsService(dbconn),
        DbWebsiteDepartmentChannelsSubscriptionsService(dbconn),
        DbWebsiteMiscChannelsSubscriptionsService(dbconn),
        DbStatsService(dbconn),
    ]
}

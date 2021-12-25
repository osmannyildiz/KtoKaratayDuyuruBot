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


class DbChannelsService(DbTableServiceBase):
    def __init__(self, dbconn):
        super().__init__(dbconn, "channels")

    def insert(self, name, item_type, item_id):
        return self._insert("name, item_type, item_id", "%s, %s, %s", [name, item_type, item_id])


class DbUsersService(DbTableServiceBase):
    def __init__(self, dbconn):
        super().__init__(dbconn, "users")

    def insert(self, chat_id):
        return self._insert("chat_id", "%s", [chat_id])


class DbSubscriptionsService(DbTableServiceBase):
    def __init__(self, dbconn):
        super().__init__(dbconn, "subscriptions")

    def insert(self, user_id, channel_id):
        return self._insert("user_id, channel_id", "%s, %s", [user_id, channel_id])


class DbStatsService(DbTableServiceBase):
    def __init__(self, dbconn):
        super().__init__(dbconn, "stats")

    def insert(self, name, item_id, value):
        return self._insert("name, item_id, value", "%s, %s, %s", [name, item_id, value])


dbconn = create_dbconn("kkdb")
dbsvc = {
    "faculties": DbFacultiesService(dbconn),
    "departments": DbDepartmentsService(dbconn),
    "channels": DbChannelsService(dbconn),
    "users": DbUsersService(dbconn),
    "subscriptions": DbSubscriptionsService(dbconn),
    "stats": DbStatsService(dbconn),
}

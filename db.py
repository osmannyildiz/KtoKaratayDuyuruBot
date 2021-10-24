from dbpkg.service import DbTableServiceBase
from dbpkg.mysql import create_dbconn


class DbSubscriptionsService(DbTableServiceBase):
    def __init__(self, dbconn):
        super().__init__(dbconn, "subscriptions")

    def insert(self, user_id, channel_id):
        return self._insert("user_id, channel_id", "%s, %s", [user_id, channel_id])


class DbUsersService(DbTableServiceBase):
    def __init__(self, dbconn, dbsvc_subscriptions):
        super().__init__(dbconn, "users")
        self.dbsvc_subscriptions = dbsvc_subscriptions

    def insert(self, id):
        return self._insert("id", "%s", [id])

    def delete(self, where_clause, where_values):
        user = self.getone(where_clause, where_values)
        self.dbsvc_subscriptions.delete("user_id=%s", [user["id"]])
        super().delete(where_clause, where_values)


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


class DbStatsService(DbTableServiceBase):
    def __init__(self, dbconn):
        super().__init__(dbconn, "stats")

    def insert(self, name, item_id, value):
        return self._insert("name, item_id, value", "%s, %s, %s", [name, item_id, value])


dbconn = create_dbconn("kkdb")
dbsvc_subscriptions = DbSubscriptionsService(dbconn)
dbsvc_users = DbUsersService(dbconn, dbsvc_subscriptions)
dbsvc_faculties = DbFacultiesService(dbconn)
dbsvc_departments = DbDepartmentsService(dbconn)
dbsvc_channels = DbChannelsService(dbconn)
dbsvc_stats = DbStatsService(dbconn)
dbsvc = {
    "subscriptions": dbsvc_subscriptions,
    "users": dbsvc_users,
    "faculties": dbsvc_faculties,
    "departments": dbsvc_departments,
    "channels": dbsvc_channels,
    "stats": dbsvc_stats,
}

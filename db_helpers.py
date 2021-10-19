##### USERS #####

def get_users(bot, cols):
    cur = bot.dbconn.cursor()
    cur.execute(f"SELECT {cols} FROM users;")
    rows = cur.fetchall()
    cur.close()
    return rows

def get_user(bot, user_id, cols):
    cur = bot.dbconn.cursor()
    cur.execute(f"SELECT {cols} FROM users WHERE id = %s;", [user_id])
    row = cur.fetchone()
    cur.close()
    return row

def set_user(bot, user_id, col, new_val):
    cur = bot.dbconn.cursor()
    cur.execute(f"UPDATE users SET {col} = %s WHERE id = %s;", [new_val, user_id])
    cur.close()

def create_user(bot, user_id):
    cur = bot.dbconn.cursor()
    cur.execute("INSERT INTO users (id) VALUES (%s);", [user_id])
    cur.close()

def delete_user(bot, user_id):
    cur = bot.dbconn.cursor()
    cur.execute("DELETE FROM subscriptions WHERE user_id = %s;", [user_id])
    cur.execute("DELETE FROM users WHERE id = %s;", [user_id])
    cur.close()

def user_exists(bot, user_id):
    return get_user(bot, user_id, "id")


##### FACULTIES #####

def get_faculties(bot, cols):
    cur = bot.dbconn.cursor()
    cur.execute(f"SELECT {cols} FROM faculties;")
    rows = cur.fetchall()
    cur.close()
    return rows

def get_faculty(bot, faculty_id, cols):
    cur = bot.dbconn.cursor()
    cur.execute(f"SELECT {cols} FROM faculties WHERE id = %s;", [faculty_id])
    row = cur.fetchone()
    cur.close()
    return row

def get_faculty_by_name(bot, faculty_name, cols):
    cur = bot.dbconn.cursor()
    cur.execute(f"SELECT {cols} FROM faculties WHERE name = %s;", [faculty_name])
    row = cur.fetchone()
    cur.close()
    return row


##### DEPARTMENTS #####

def get_departments(bot, cols):
    cur = bot.dbconn.cursor()
    cur.execute(f"SELECT {cols} FROM departments;")
    rows = cur.fetchall()
    cur.close()
    return rows

def get_departments_by_faculty_id(bot, faculty_id, cols):
    cur = bot.dbconn.cursor()
    cur.execute(f"SELECT {cols} FROM departments WHERE faculty_id = %s;", [faculty_id])
    rows = cur.fetchall()
    cur.close()
    return rows

def get_department_by_name(bot, department_name, cols):
    cur = bot.dbconn.cursor()
    cur.execute(f"SELECT {cols} FROM departments WHERE name = %s;", [department_name])
    row = cur.fetchone()
    cur.close()
    return row


##### CHANNELS #####

def get_channels(bot, cols, order=True):
    sql = f"SELECT {cols} FROM channels"
    if order:
        sql += " ORDER BY item_type DESC, name ASC"
    sql += ";"

    cur = bot.dbconn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()
    return rows

def get_channels_by_item_type(bot, item_type, cols):
    cur = bot.dbconn.cursor()
    cur.execute(f"SELECT {cols} FROM channels WHERE item_type = %s;", [item_type])
    rows = cur.fetchall()
    cur.close()
    return rows

def get_channel(bot, channel_id, cols):
    cur = bot.dbconn.cursor()
    cur.execute(f"SELECT {cols} FROM channels WHERE id = %s;", [channel_id])
    row = cur.fetchone()
    cur.close()
    return row

def get_channel_by_name(bot, channel_name, cols):
    cur = bot.dbconn.cursor()
    cur.execute(f"SELECT {cols} FROM channels WHERE name = %s;", [channel_name])
    row = cur.fetchone()
    cur.close()
    return row

def get_channel_by_faculty_id(bot, faculty_id, cols):
    cur = bot.dbconn.cursor()
    cur.execute(f"SELECT {cols} FROM channels WHERE item_type = 1 AND item_id = %s;", [faculty_id])
    row = cur.fetchone()
    cur.close()
    return row

def get_channel_by_department_id(bot, department_id, cols):
    cur = bot.dbconn.cursor()
    cur.execute(f"SELECT {cols} FROM channels WHERE item_type = 2 AND item_id = %s;", [department_id])
    row = cur.fetchone()
    cur.close()
    return row

def set_channel(bot, channel_id, col, new_val):
    cur = bot.dbconn.cursor()
    cur.execute(f"UPDATE channels SET {col} = %s WHERE id = %s;", [new_val, channel_id])
    cur.close()

def create_special_channel(bot, channel_name):
    cur = bot.dbconn.cursor()
    cur.execute("INSERT INTO channels (name, item_type) VALUES (%s,%s);", [channel_name, 3])
    cur.close()

def delete_channel(bot, channel_id):
    cur = bot.dbconn.cursor()
    cur.execute("DELETE FROM subscriptions WHERE channel_id = %s;", [channel_id])
    cur.execute("DELETE FROM stats WHERE name = 'channel_msg_count' AND item_id = %s;", [channel_id])
    cur.execute("DELETE FROM channels WHERE id = %s;", [channel_id])
    cur.close()


##### SUBSCRIPTIONS #####

def get_subscriptions_by_user_id(bot, user_id, cols):
    cur = bot.dbconn.cursor()
    cur.execute(f"SELECT {cols} FROM subscriptions WHERE user_id = %s;", [user_id])
    rows = cur.fetchall()
    cur.close()
    return rows

def get_subscriptions_by_channel_id(bot, channel_id, cols):
    cur = bot.dbconn.cursor()
    cur.execute(f"SELECT {cols} FROM subscriptions WHERE channel_id = %s;", [channel_id])
    rows = cur.fetchall()
    cur.close()
    return rows

def get_subscription_alt(bot, user_id, channel_id, cols):
    cur = bot.dbconn.cursor()
    cur.execute(f"SELECT {cols} FROM subscriptions WHERE user_id = %s AND channel_id = %s;", [user_id, channel_id])
    row = cur.fetchone()
    cur.close()
    return row

def create_subscription(bot, user_id, channel_id):
    cur = bot.dbconn.cursor()
    cur.execute("INSERT INTO subscriptions (user_id, channel_id) VALUES (%s,%s);", [user_id, channel_id])
    cur.close()

def delete_subscription(bot, subscription_id):
    cur = bot.dbconn.cursor()
    cur.execute("DELETE FROM subscriptions WHERE id = %s;", [subscription_id])
    cur.close()

def toggle_subscription_alt(bot, user_id, channel_id):
    row = get_subscription_alt(bot, user_id, channel_id, "id")
    if row:
        subscription_id = row[0]
        delete_subscription(bot, subscription_id)
        new_state = False
    else:
        create_subscription(bot, user_id, channel_id)
        new_state = True
    return new_state


##### STATS #####

# def get_stat_by_name(bot, stat_name, cols):
#     cur = bot.dbconn.cursor()
#     cur.execute(f"SELECT {cols} FROM stats WHERE name = %s;", [stat_name])
#     row = cur.fetchone()
#     cur.close()
#     return row

def get_stat_by_name_and_item_id(bot, stat_name, stat_item_id, cols):
    cur = bot.dbconn.cursor()
    cur.execute(f"SELECT {cols} FROM stats WHERE name = %s AND item_id = %s;", [stat_name, stat_item_id])
    row = cur.fetchone()
    cur.close()
    return row

# def set_stat_by_name(bot, stat_name, col, new_val):
#     cur = bot.dbconn.cursor()
#     cur.execute(f"UPDATE stats SET {col} = %s WHERE name = %s;", [new_val, stat_name])
#     cur.close()

def set_stat_by_name_and_item_id(bot, stat_name, stat_item_id, col, new_val):
    cur = bot.dbconn.cursor()
    cur.execute(f"UPDATE stats SET {col} = %s WHERE name = %s AND item_id = %s;", [new_val, stat_name, stat_item_id])
    cur.close()

def create_stat(bot, stat_name, stat_item_id, stat_value):
    cur = bot.dbconn.cursor()
    cur.execute("INSERT INTO stats (name, item_id, value) VALUES (%s,%s,%s);", [stat_name, stat_item_id, stat_value])
    cur.close()

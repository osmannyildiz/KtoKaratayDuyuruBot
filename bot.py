from tgbot import BaseBot
from tgbots.kto_karatay_duyuru_bot.db import dbsvc
from tgbots.kto_karatay_duyuru_bot.config import BOT_CONFIG
from tgbots.kto_karatay_duyuru_bot.constants import Commands, UserStates
from tgbots.kto_karatay_duyuru_bot.message_texts import MessageTexts as MT
from tgbots.kto_karatay_duyuru_bot.helpers import (
    create_subscription_to_faculty_channel,
    create_subscription_to_department_channel,
    create_subscriptions_to_default_channels,
    build_custom_kb_of_faculties,
    build_custom_kb_of_departments,
    build_custom_kb_for_toggle_channels,
    build_custom_kb_for_curr_state,
    toggle_subscription,
    find_type_of_channel_with_name,
    command_to_user_state,
    command_to_channel_type,
    user_state_to_channel_type,
    user_state_to_message_text
)
from pprint import pprint


class Bot(BaseBot):
    def send_message(self, chat_id, text, **kwargs):
        ok, r = self.api.send_message(chat_id, text, **kwargs)
        if not ok:
            description = r["description"]
            if description == "Forbidden: bot was blocked by the user":
                # Kullanıcı botu silmişse sen de kullanıcıyı sil
                dbsvc["users"].delete("chat_id=%s", [chat_id])
            else:
                raise Exception(r)
        return ok, r

    def handle_update(self, update):
        if msg := update.get("message"):
            self.handle_message(msg)
        elif update.get("my_chat_member", dict()).get("new_chat_member", dict()).get("status") == "kicked":
            # Kullanıcı botu sildi, sen de kullanıcıyı sil
            chat_id = update["my_chat_member"]["chat"]["id"]
            dbsvc["users"].delete("chat_id=%s", [chat_id])
        else:
            # FIXME Beklenmedik durum: Gelen olay mesaj değil
            pprint(update)

    def handle_message(self, msg):
        msg_id = msg["message_id"]
        chat_id = msg["chat"]["id"]
        text = msg.get("text")
        print(f"{chat_id}:\n{text}\n")
        if text:

            if text.startswith("/"):
                self.handle_command(msg_id, chat_id, text)
                return
            else:
                if user := dbsvc["users"].getone("chat_id=%s", [chat_id]):

                    if user["state"] == UserStates.MEETING_EXPECTING_FACULTY:
                        # Kullanıcı fakülte seçti
                        if faculty := dbsvc["faculties"].getone("name=%s", [text]):
                            dbsvc["users"].update_column_with_value("faculty_id", faculty["id"], "id=%s", [user["id"]])
                            custom_kb = build_custom_kb_of_departments(self, faculty["id"])
                            dbsvc["users"].set_state(user["id"], UserStates.MEETING_EXPECTING_DEPARTMENT)
                            self.send_message(chat_id, MT.ask_department(), reply_markup=custom_kb)
                            return
                        else:
                            # Özel klavyeden seçmedi (böyle bir fakülte yok)
                            custom_kb = build_custom_kb_of_faculties(self)
                            self.send_message(chat_id, MT.invalid_response_use_keyboard(), reply_markup=custom_kb)
                            return

                    elif user["state"] == UserStates.MEETING_EXPECTING_DEPARTMENT:
                        # Kullanıcı bölüm seçti
                        if department := dbsvc["departments"].getone("name=%s", [text]):
                            dbsvc["users"].update_column_with_value("department_id", department["id"], "id=%s", [user["id"]])
                            create_subscription_to_faculty_channel(user["id"], user["faculty_id"])
                            if department["code"]:
                                create_subscription_to_department_channel(user["id"], department["id"])
                            create_subscriptions_to_default_channels(user["id"])
                            dbsvc["users"].set_state(user["id"], UserStates.IDLE)
                            self.send_message(chat_id, MT.meeting_done(), reply_markup=self.api.build_remove_keyboard())
                            return
                        else:
                            # Özel klavyeden seçmedi (böyle bir bölüm yok)
                            custom_kb = build_custom_kb_of_departments(self, user["faculty_id"])
                            self.send_message(chat_id, MT.invalid_response_use_keyboard(), reply_markup=custom_kb)
                            return

                    elif user["state"] in [
                        UserStates.TOGGLE_EXPECTING_KKDB_SPECIAL_CHANNEL,
                        UserStates.TOGGLE_EXPECTING_WEBSITE_FACULTY_CHANNEL,
                        UserStates.TOGGLE_EXPECTING_WEBSITE_DEPARTMENT_CHANNEL,
                        UserStates.TOGGLE_EXPECTING_WEBSITE_MISC_CHANNEL
                    ]:
                        # Kullanıcı ayarlamalar yapıyor
                        if text.strip().lower() in [MT.toggle_done_button().lower(), "tamamla"]:
                            # Tamamla
                            dbsvc["users"].set_state(user["id"], UserStates.IDLE)
                            self.api.delete_message(chat_id, user["bot_last_msg_id"])
                            self.send_message(chat_id, MT.toggle_done(), reply_markup=self.api.build_remove_keyboard())
                            return
                        else:
                            # Kanal aboneliğini aç/kapat
                            channel_type = user_state_to_channel_type(user["state"])
                            dbsvc_channels = dbsvc[channel_type + "_channels"]
                            channel_name = text[:-2]
                            channel = dbsvc_channels.getone("name=%s", [channel_name])
                            if channel:
                                toggle_subscription(user["id"], channel_type, channel["id"])
                                message_text = MT.toggle_waiting()
                            else:
                                # Özel klavyeden seçmedi (böyle bir kanal yok)
                                message_text = MT.invalid_response_use_keyboard()
                            custom_kb = build_custom_kb_for_toggle_channels(self, user["id"], channel_type)
                            self.api.delete_message(chat_id, msg_id)  # Kullanıcının mesajını (mesela "Genel Duyurular ❌" veya "hjkhjkhjk") sil
                            self.api.delete_message(chat_id, user["bot_last_msg_id"])  # Botun mesajını (mesela "...") sil
                            ok, sent_msg = self.send_message(chat_id, message_text, reply_markup=custom_kb)
                            if ok:
                                dbsvc["users"].update_column_with_value("bot_last_msg_id", sent_msg["result"]["message_id"], "id=%s", [user["id"]])
                            return

                    else:
                        # Kullanıcıdan mesaj beklemiyorduk
                        if user["state"] != UserStates.IDLE:
                            raise Exception(f"Unexpected situation. Probably there is an unhandled user state. User's state is: {user['state']}")
                        self.send_message(chat_id, MT.could_not_understand())
                        return

                else:
                    # Kullanıcı veritabanında kayıtlı değil
                    self.send_message(chat_id, MT.not_met())
                    return

        else:
            # FIXME Beklenmedik durum: Gelen mesajda text yok
            pprint(msg)
            self.send_message(chat_id, MT.oops())
            return

    def handle_command(self, msg_id, chat_id, cmd):
        if cmd == Commands.START:
            if user := dbsvc["users"].getone("chat_id=%s", [chat_id]):
                # Kullanıcı zaten varsa
                if user["state"] == UserStates.IDLE:
                    # Zaten tanışmıştık
                    self.send_message(chat_id, MT.already_met())
                    return
                elif user["state"] in [
                    UserStates.MEETING_EXPECTING_FACULTY,
                    UserStates.MEETING_EXPECTING_DEPARTMENT
                ]:
                    # Tanışma zaten devam ediyor
                    message_text = MT.meeting_already_ongoing()
                    message_text += "\n👉 " + user_state_to_message_text(user["state"])
                    custom_kb = build_custom_kb_for_curr_state(self, user)
                    self.send_message(chat_id, message_text, reply_markup=custom_kb)
                    return
                else:
                    # Zaten tanışmıştık, mevcut komutu işlemeye devam et
                    custom_kb = build_custom_kb_for_curr_state(self, user)
                    self.send_message(chat_id, MT.already_met(), reply_markup=custom_kb)
                    return
            else:
                dbsvc["users"].insert(chat_id, UserStates.MEETING_EXPECTING_FACULTY)
                user = dbsvc["users"].getone("chat_id=%s", [chat_id])
                self.send_message(chat_id, MT.hello())
                custom_kb = build_custom_kb_of_faculties(self)
                self.send_message(chat_id, MT.ask_faculty(), reply_markup=custom_kb)
                return
        else:
            if user := dbsvc["users"].getone("chat_id=%s", [chat_id]):
                if user["state"] != UserStates.IDLE:
                    # Diğer komutları işleme!, önce mevcut olanı tamamla
                    message_text = MT.finish_cmd_first()
                    try:
                        message_text += "\n👉 " + user_state_to_message_text(user["state"])
                    except:
                        pass
                    custom_kb = build_custom_kb_for_curr_state(self, user)
                    self.send_message(chat_id, message_text, reply_markup=custom_kb)
                    return
                else:

                    if cmd in [
                        Commands.TOGGLE_KKDB_SPECIAL_CHANNELS,
                        Commands.TOGGLE_WEBSITE_FACULTY_CHANNELS,
                        Commands.TOGGLE_WEBSITE_DEPARTMENT_CHANNELS,
                        Commands.TOGGLE_WEBSITE_MISC_CHANNELS
                    ]:
                        user_state = command_to_user_state(cmd)
                        channel_type = command_to_channel_type(cmd)
                        dbsvc["users"].set_state(user["id"], user_state)
                        self.send_message(chat_id, MT.toggle_start())
                        custom_kb = build_custom_kb_for_toggle_channels(self, user["id"], channel_type)
                        ok, sent_msg = self.send_message(chat_id, MT.toggle_waiting(), reply_markup=custom_kb)
                        if ok:
                            dbsvc["users"].update_column_with_value("bot_last_msg_id", sent_msg["result"]["message_id"], "id=%s", [user["id"]])
                        return

                    elif cmd == Commands.FORGET_ME:
                        self.send_message(chat_id, MT.forget())
                        return

                    else:
                        # Böyle bir komut yok
                        self.send_message(chat_id, MT.could_not_understand())
                        return

            else:
                # Kullanıcı veritabanında kayıtlı değil
                self.send_message(chat_id, MT.not_met())
                return


bot = Bot(BOT_CONFIG)

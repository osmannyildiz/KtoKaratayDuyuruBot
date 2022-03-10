from tgbot import BaseBot
from tgbots.kto_karatay_duyuru_bot.config import BOT_CONFIG
from tgbots.kto_karatay_duyuru_bot.message_texts import MessageTexts as MT
from tgbots.kto_karatay_duyuru_bot.db import dbsvc
from tgbots.kto_karatay_duyuru_bot.helpers import (
    create_subscriptions_to_special_channels,
    build_custom_kb_of_faculties, build_custom_kb_of_departments, build_custom_kb_for_ayarla,
    build_custom_kb_for_curr_state,
    toggle_subscription
)
from datetime import datetime
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
            else:
                if user := dbsvc["users"].getone("chat_id=%s", [chat_id]):
                    if user["state"] == 1:
                        # Kullanıcı fakülte seçti
                        if faculty := dbsvc["faculties"].getone("name=%s", [text]):
                            dbsvc["users"].update_column_with_value("faculty_id", faculty["id"], "id=%s", [user["id"]])
                            custom_kb = build_custom_kb_of_departments(self, faculty["id"])
                            self.send_message(chat_id, MT.ask_department(), reply_markup=custom_kb)
                            dbsvc["users"].update_column_with_value("state", 2, "id=%s", [user["id"]])
                        else:
                            # Özel klavyeden seçmedi (böyle bir fakülte yok)
                            custom_kb = build_custom_kb_of_faculties(self)
                            self.send_message(chat_id, MT.invalid_response_use_keyboard(), reply_markup=custom_kb)

                    elif user["state"] == 2:
                        # Kullanıcı bölüm seçti
                        if department := dbsvc["departments"].getone("name=%s", [text]):
                            dbsvc["users"].update_column_with_value("department_id", department["id"], "id=%s", [user["id"]])
                            faculty_channel = dbsvc["channels"].getone("item_type=%s AND item_id=%s", [1, user["faculty_id"]])
                            department_channel = dbsvc["channels"].getone("item_type=%s AND item_id=%s", [2, department["id"]])
                            dbsvc["subscriptions"].insert(user["id"], faculty_channel["id"])
                            dbsvc["subscriptions"].insert(user["id"], department_channel["id"])
                            create_subscriptions_to_special_channels(dbsvc, user["id"])
                            self.send_message(chat_id, MT.meeting_done(), reply_markup=self.api.build_remove_keyboard())
                            dbsvc["users"].update_column_with_value("state", 3, "id=%s", [user["id"]])
                        else:
                            # Özel klavyeden seçmedi (böyle bir bölüm yok)
                            custom_kb = build_custom_kb_of_departments(self, user["faculty_id"])
                            self.send_message(chat_id, MT.invalid_response_use_keyboard(), reply_markup=custom_kb)

                    elif user["state"] == 4:
                        # Kullanıcı ayarlamalar yapıyor
                        if text.strip().lower() in [MT.ayarla_done_button().lower(), "tamamla"]:
                            # Tamamla
                            self.api.delete_message(chat_id, user["bot_last_msg_id"])
                            self.send_message(chat_id, MT.ayarla_done(), reply_markup=self.api.build_remove_keyboard())
                            dbsvc["users"].update_column_with_value("state", 3, "id=%s", [user["id"]])
                        else:
                            # Kanal aboneliğini aç/kapat
                            if channel := dbsvc["channels"].getone("name=%s", [text[:-2]]):
                                toggle_subscription(dbsvc, user["id"], channel["id"])
                            # (Aşağıdaki 3 satır iki durumda da ortak, o yüzden if'i ikiye böldüm)
                            custom_kb = build_custom_kb_for_ayarla(self, user["id"])
                            self.api.delete_message(chat_id, msg_id)  # Kullanıcının mesajını (mesela "Genel Duyurular") sil
                            self.api.delete_message(chat_id, user["bot_last_msg_id"])  # Botun mesajını (mesela "...") sil
                            if channel:
                                ok, sent_msg = self.send_message(chat_id, MT.ayarla_waiting(), reply_markup=custom_kb)
                            else:
                                # Özel klavyeden seçmedi (böyle bir kanal yok)
                                ok, sent_msg = self.send_message(chat_id, MT.invalid_response_use_keyboard(), reply_markup=custom_kb)
                            if ok:
                                dbsvc["users"].update_column_with_value("bot_last_msg_id", sent_msg["result"]["message_id"], "id=%s", [user["id"]])

                    elif user["state"] == 5:
                        # Kullanıcıdan sıfırlama için onay alınıyor
                        if text.strip().lower() == "onayla":
                            dbsvc["users"].deletebyid(user["id"])
                            self.send_message(chat_id, MT.sifirla_done(), reply_markup=self.api.build_remove_keyboard())
                        else:
                            self.send_message(chat_id, MT.user_canceled_sifirla(), reply_markup=self.api.build_remove_keyboard())
                            dbsvc["users"].update_column_with_value("state", 3, "id=%s", [user["id"]])

                    else:
                        # Kullanıcıdan mesaj beklemiyorduk
                        self.send_message(chat_id, MT.could_not_understand())
                else:
                    # Kullanıcı veritabanında yok
                    self.send_message(chat_id, MT.not_met(), reply_markup=self.api.build_remove_keyboard())

        else:
            # FIXME Beklenmedik durum: Gelen mesajda text yok
            pprint(msg)
            self.send_message(chat_id, MT.oops())

    def handle_command(self, msg_id, chat_id, cmd):
        if cmd == "/start":
            if user := dbsvc["users"].getone("chat_id=%s", [chat_id]):
                # Kullanıcı zaten varsa
                if user["state"] == 0:  # Ama bir terslik (mesela kodun *a* satırında göçmesi) sonucu state 1 olamamışsa:
                    # Tanış ama kullanıcıyı yeniden oluşturmaya çalışma!
                    self.send_message(chat_id, MT.ask_name(), reply_markup=self.api.build_remove_keyboard())
                    dbsvc["users"].update_column_with_value("state", 1, "id=%s", [user["id"]])
                elif user["state"] == 5:
                    # Eğer kullanıcı /sifirla'ya cevap olarak /start girmişse vazgeçti say
                    self.send_message(chat_id, MT.user_canceled_sifirla(), reply_markup=self.api.build_remove_keyboard())
                    dbsvc["users"].update_column_with_value("state", 3, "id=%s", [user["id"]])
                elif user["state"] < 3:
                    # Tanışma zaten devam ediyor
                    custom_kb = build_custom_kb_for_curr_state(self, user["id"], user["state"])
                    self.send_message(chat_id, MT.meeting_already_ongoing(), reply_markup=custom_kb)
                else:
                    # Zaten tanışmıştık
                    self.send_message(chat_id, MT.already_met())
            else:
                dbsvc["users"].insert(chat_id)
                user = dbsvc["users"].getone("chat_id=%s", [chat_id])
                custom_kb = build_custom_kb_of_faculties(self)
                self.send_message(chat_id, MT.ask_faculty(), reply_markup=custom_kb)
                dbsvc["users"].update_column_with_value("state", 1, "id=%s", [user["id"]])
        else:
            if user := dbsvc["users"].getone("chat_id=%s", [chat_id]):
                if user["state"] == 5:
                    # Eğer kullanıcı /sifirla'ya cevap olarak bir komut girmişse vazgeçti say
                    self.send_message(chat_id, MT.user_canceled_sifirla(), reply_markup=self.api.build_remove_keyboard())
                    dbsvc["users"].update_column_with_value("state", 3, "id=%s", [user["id"]])
                elif user["state"] != 3:
                    # Diğer komutları işleme!, önce mevcut olanı tamamla
                    custom_kb = build_custom_kb_for_curr_state(self, user["id"], user["state"])
                    self.send_message(chat_id, MT.finish_cmd_first(), reply_markup=custom_kb)
                else:

                    if cmd == "/ayarla":
                        self.send_message(chat_id, MT.ayarla_start())
                        custom_kb = build_custom_kb_for_ayarla(self, user["id"])
                        ok, sent_msg = self.send_message(chat_id, MT.ayarla_waiting(), reply_markup=custom_kb)
                        if ok:
                            dbsvc["users"].update_column_with_value("bot_last_msg_id", sent_msg["result"]["message_id"], "id=%s", [user["id"]])
                            dbsvc["users"].update_column_with_value("state", 4, "id=%s", [user["id"]])

                    elif cmd == "/sifirla":
                        self.send_message(chat_id, MT.sifirla_start(), reply_markup=self.api.build_remove_keyboard())
                        dbsvc["users"].update_column_with_value("state", 5, "id=%s", [user["id"]])

                    else:
                        # Böyle bir komut yok
                        self.send_message(chat_id, MT.could_not_understand())

            else:
                # Kullanıcı veritabanında yok
                self.send_message(chat_id, MT.not_met(), reply_markup=self.api.build_remove_keyboard())


bot = Bot(BOT_CONFIG)

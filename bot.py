from tgbot import BaseBot
from tgbots.kto_karatay_duyuru_bot.message_texts import message_texts as mt
from tgbots.kto_karatay_duyuru_bot.db import dbsvc
from tgbots.kto_karatay_duyuru_bot.helpers import (
    create_subscriptions_to_special_channels,
    build_custom_kb_of_faculties, build_custom_kb_of_departments, build_custom_kb_for_ayarla,
    build_custom_kb_for_curr_state,
    sanitize_and_validate_user_name,
    toggle_subscription
)
from tgbots.kto_karatay_duyuru_bot.config import bot_config
from pprint import pprint


class Bot(BaseBot):
    def __init__(self, config, dbconn):
        super().__init__(config)
        self.dbconn = dbconn

    def send_msg(self, chat_id, text, **kwargs):
        ok, r = self.api.send_message(chat_id, text, **kwargs)
        if not ok:
            if r["description"] == "Forbidden: bot was blocked by the user":
                # Kullanıcı botu silmişse sen de kullanıcıyı sil
                dbsvc["users"].delete("id=%s", [chat_id])
            else:
                raise Exception(r)
        return ok, r

    def handle_update(self, update):
        if msg := update.get("message"):
            chat_id = msg["chat"]["id"]
            text = msg.get("text")
            print(f"{chat_id}:\n{text}\n")
            msg_id = msg.get("message_id")
            if text:

                if text.startswith("/"):
                    if text == "/start":
                        if user := dbsvc["users"].getone("id=%s", [chat_id]):
                            # Kullanıcı zaten varsa
                            if user["state"] == 0:  # Ama bir terslik (mesela kodun *a* satırında göçmesi) sonucu state 1 olamamışsa:
                                # Tanış ama kullanıcıyı yeniden oluşturmaya çalışma!
                                self.send_msg(chat_id, mt.ask_name(), reply_markup=self.api.build_remove_keyboard())
                                dbsvc["users"].update_column_with_value("state", 1, "id=%s", [user["id"]])
                            elif user["state"] == 6:
                                # Eğer kullanıcı /sifirla'ya cevap olarak /start girmişse vazgeçti say
                                self.send_msg(chat_id, mt.user_canceled_sifirla(), reply_markup=self.api.build_remove_keyboard())
                                dbsvc["users"].update_column_with_value("state", 4, "id=%s", [user["id"]])
                            elif user["state"] < 4:
                                # Tanışma zaten devam ediyor
                                custom_kb = build_custom_kb_for_curr_state(self, chat_id, user_state=user["state"])
                                self.send_msg(chat_id, mt.meeting_already_ongoing(), reply_markup=custom_kb)
                            else:
                                # Zaten tanışmıştık
                                self.send_msg(chat_id, mt.already_met())
                        else:
                            dbsvc["users"].insert(chat_id)
                            self.send_msg(chat_id, mt.ask_name(), reply_markup=self.api.build_remove_keyboard())  # *a*
                            dbsvc["users"].update_column_with_value("state", 1, "id=%s", [chat_id])
                    else:
                        if user := dbsvc["users"].getone("id=%s", [chat_id]):
                            if user["state"] == 6:
                                # Eğer kullanıcı /sifirla'ya cevap olarak bir komut girmişse vazgeçti say
                                self.send_msg(chat_id, mt.user_canceled_sifirla(), reply_markup=self.api.build_remove_keyboard())
                                dbsvc["users"].update_column_with_value("state", 4, "id=%s", [user["id"]])
                            elif user["state"] != 4:
                                # Diğer komutları işleme!, önce mevcut olanı tamamla
                                custom_kb = build_custom_kb_for_curr_state(self, chat_id, user_state=user["state"])
                                self.send_msg(chat_id, mt.finish_cmd_first(), reply_markup=custom_kb)
                            else:

                                if text == "/ayarla":
                                    self.send_msg(chat_id, mt.ayarla_start())
                                    custom_kb = build_custom_kb_for_ayarla(self, chat_id)
                                    ok, sent_msg = self.send_msg(chat_id, mt.ayarla_waiting(), reply_markup=custom_kb)
                                    if ok:
                                        dbsvc["users"].update_column_with_value("bot_last_msg_id", sent_msg["result"]["message_id"], "id=%s", [user["id"]])
                                        dbsvc["users"].update_column_with_value("state", 5, "id=%s", [user["id"]])

                                elif text == "/sifirla":
                                    self.send_msg(chat_id, mt.sifirla_start(), reply_markup=self.api.build_remove_keyboard())
                                    dbsvc["users"].update_column_with_value("state", 6, "id=%s", [user["id"]])

                                else:
                                    # Böyle bir komut yok
                                    self.send_msg(chat_id, mt.could_not_understand())
                        else:
                            # Kullanıcı veritabanında yok
                            self.send_msg(chat_id, mt.not_met(), reply_markup=self.api.build_remove_keyboard())
                else:
                    if user := dbsvc["users"].getone("id=%s", [chat_id]):
                        if user["state"] == 1:
                            # Kullanıcı ismini yazdı
                            user_name = sanitize_and_validate_user_name(text)
                            if user_name != None:
                                dbsvc["users"].update_column_with_value("name", user_name, "id=%s", [user["id"]])
                                custom_kb = build_custom_kb_of_faculties(self)
                                self.send_msg(chat_id, mt.ask_faculty(), reply_markup=custom_kb)
                                dbsvc["users"].update_column_with_value("state", 2, "id=%s", [user["id"]])
                            else:
                                # İsim uygun değil
                                self.send_msg(chat_id, mt.invalid_user_name(), reply_markup=self.api.build_remove_keyboard())

                        elif user["state"] == 2:
                            # Kullanıcı fakülte seçti
                            if faculty := dbsvc["faculties"].getone("name=%s", [text]):
                                dbsvc["users"].update_column_with_value("faculty_id", faculty["id"], "id=%s", [user["id"]])
                                custom_kb = build_custom_kb_of_departments(self, faculty["id"])
                                self.send_msg(chat_id, mt.ask_department(), reply_markup=custom_kb)
                                dbsvc["users"].update_column_with_value("state", 3, "id=%s", [user["id"]])
                            else:
                                # Özel klavyeden seçmedi (böyle bir fakülte yok)
                                custom_kb = build_custom_kb_of_faculties(self)
                                self.send_msg(chat_id, mt.invalid_response_use_keyboard(), reply_markup=custom_kb)

                        elif user["state"] == 3:
                            # Kullanıcı bölüm seçti
                            if department := dbsvc["departments"].getone("name=%s", [text]):
                                dbsvc["users"].update_column_with_value("department_id", department["id"], "id=%s", [user["id"]])
                                faculty_channel = dbsvc["channels"].getone("item_type=%s AND item_id=%s", [1, user["faculty_id"]])
                                department_channel = dbsvc["channels"].getone("item_type=%s AND item_id=%s", [2, department["id"]])
                                dbsvc["subscriptions"].insert(user["id"], faculty_channel["id"])
                                dbsvc["subscriptions"].insert(user["id"], department_channel["id"])
                                create_subscriptions_to_special_channels(dbsvc, chat_id)
                                self.send_msg(chat_id, mt.meeting_done(user["name"]), reply_markup=self.api.build_remove_keyboard())
                                dbsvc["users"].update_column_with_value("state", 4, "id=%s", [user["id"]])
                            else:
                                # Özel klavyeden seçmedi (böyle bir bölüm yok)
                                department_list = [department["name"] for department in dbsvc["departments"].get("faculty_id=%s", user["faculty_id"])]
                                department_list.sort()
                                custom_kb = self.api.build_vertical_custom_keyboard(department_list, one_time=True)
                                self.send_msg(chat_id, mt.invalid_response_use_keyboard(), reply_markup=custom_kb)

                        elif user["state"] == 5:
                            # Kullanıcı ayarlamalar yapıyor
                            if text.strip().lower() in [mt.ayarla_done_button().lower(), "tamamla"]:
                                # Tamamla
                                self.api.delete_message(chat_id, user["bot_last_msg_id"])
                                self.send_msg(chat_id, mt.ayarla_done(), reply_markup=self.api.build_remove_keyboard())
                                dbsvc["users"].update_column_with_value("state", 4, "id=%s", [user["id"]])
                            else:
                                # Kanal aboneliğini aç/kapat
                                if channel := dbsvc["channels"].getone("name=%s", [text[:-2]]):
                                    toggle_subscription(dbsvc, user["id"], channel["id"])
                                # (Aşağıdaki 3 satır iki durumda da ortak, o yüzden if'i ikiye böldüm)
                                custom_kb = build_custom_kb_for_ayarla(self, chat_id)
                                self.api.delete_message(chat_id, msg_id)  # Kullanıcının mesajını (mesela "Genel Duyurular") sil
                                self.api.delete_message(chat_id, user["bot_last_msg_id"])  # Botun mesajını (mesela "...") sil
                                if channel:
                                    ok, sent_msg = self.send_msg(chat_id, mt.ayarla_waiting(), reply_markup=custom_kb)
                                else:
                                    # Özel klavyeden seçmedi (böyle bir kanal yok)
                                    ok, sent_msg = self.send_msg(chat_id, mt.invalid_response_use_keyboard(), reply_markup=custom_kb)
                                if ok:
                                    dbsvc["users"].update_column_with_value("bot_last_msg_id", sent_msg["result"]["message_id"], "id=%s", [user["id"]])

                        elif user["state"] == 6:
                            # Kullanıcıdan sıfırlama için onay alınıyor
                            if text.strip().lower() == "onayla":
                                dbsvc["users"].delete("id=%s", [user["id"]])
                                self.send_msg(chat_id, mt.sifirla_done(), reply_markup=self.api.build_remove_keyboard())
                            else:
                                self.send_msg(chat_id, mt.user_canceled_sifirla(), reply_markup=self.api.build_remove_keyboard())
                                dbsvc["users"].update_column_with_value("state", 4, "id=%s", [user["id"]])

                        else:
                            # Kullanıcıdan mesaj beklemiyorduk
                            self.send_msg(chat_id, mt.could_not_understand())
                    else:
                        # Kullanıcı veritabanında yok
                        self.send_msg(chat_id, mt.not_met(), reply_markup=self.api.build_remove_keyboard())

            else:
                # Beklenmedik durum: Gelen mesajda text yok
                pprint(update)
                self.send_msg(chat_id, mt.oops())
        else:
            # Beklenmedik durum: Gelen olay mesaj değil
            pprint(update)


# bot = Bot(bot_config, dbconn)
bot = Bot(bot_config, None)

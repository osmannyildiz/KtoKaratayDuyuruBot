from tgbot import BaseBot
from tgbots.kto_karatay_duyuru_bot.message_texts import message_texts as mt
from tgbots.kto_karatay_duyuru_bot.db_helpers import (
    get_user, set_user, create_user, delete_user, user_exists,
    get_faculties, get_faculty_by_name,
    get_departments_by_faculty_id, get_department_by_name,
    get_channel_by_name, get_channel_by_faculty_id, get_channel_by_department_id,
    create_subscription, toggle_subscription_alt
)
from tgbots.kto_karatay_duyuru_bot.helpers import (
    create_subscriptions_to_special_channels,
    build_custom_kb_of_faculties, build_custom_kb_of_departments, build_custom_kb_for_ayarla,
    build_custom_kb_for_curr_state,
    sanitize_and_validate_user_name
)
from pprint import pprint


class Bot(BaseBot):
    def send_msg(self, chat_id, text, **kwargs):
        ok, r = self.api.send_message(chat_id, text, **kwargs)
        if not ok:
            if r["description"] == "Forbidden: bot was blocked by the user":
                # kullanıcı botu silmişse sen de kullanıcıyı sil
                delete_user(self, chat_id)
            else:
                raise Exception(r)
        return ok, r

    def handle_update(self, update):
        # return
        if msg := update.get("message"):
            chat_id = msg.get("chat").get("id")
            text = msg.get("text")
            print(chat_id)
            print(text)
            msg_id = msg.get("message_id")
            if chat_id and text:

                if text.startswith("/"):
                    if text == "/start":
                        if user_exists(self, chat_id):
                            # kullanıcı zaten varsa
                            user_state = get_user(self, chat_id, "state")[0]

                            if user_state == 0:  # ama bir terslik (mesela kodun *a* satırında göçmesi) sonucu state 1 olamamışsa:
                                # tanış ama kullanıcıyı yeniden oluşturmaya çalışma!
                                self.send_msg(chat_id, mt.ask_name(), reply_markup=self.api.build_remove_keyboard())
                                set_user(self, chat_id, "state", 1)
                            elif user_state == 6:
                                # eğer kullanıcı /sifirla'ya cevap olarak /start girmişse vazgeçti say
                                self.send_msg(chat_id, mt.user_canceled_sifirla(), reply_markup=self.api.build_remove_keyboard())
                                set_user(self, chat_id, "state", 4)
                            elif user_state < 4:
                                # tanışma zaten devam ediyor
                                custom_kb = build_custom_kb_for_curr_state(self, chat_id, user_state=user_state)
                                self.send_msg(chat_id, mt.meeting_already_ongoing(), reply_markup=custom_kb)
                            else:
                                # zaten tanıştık
                                self.send_msg(chat_id, mt.already_met())
                        else:
                            create_user(self, chat_id)
                            self.send_msg(chat_id, mt.ask_name(), reply_markup=self.api.build_remove_keyboard())  # *a*
                            set_user(self, chat_id, "state", 1)
                    else:
                        if user_exists(self, chat_id):
                            user_state = get_user(self, chat_id, "state")[0]

                            if user_state == 6:
                                # eğer kullanıcı /sifirla'ya cevap olarak bir komut girmişse vazgeçti say
                                self.send_msg(chat_id, mt.user_canceled_sifirla(), reply_markup=self.api.build_remove_keyboard())
                                set_user(self, chat_id, "state", 4)
                            elif user_state != 4:
                                # diğer komutları işleme!, önce mevcut olanı tamamla
                                custom_kb = build_custom_kb_for_curr_state(self, chat_id, user_state=user_state)
                                self.send_msg(chat_id, mt.finish_cmd_first(), reply_markup=custom_kb)
                            else:

                                if text == "/ayarla":
                                    self.send_msg(chat_id, mt.ayarla_start())
                                    custom_kb = build_custom_kb_for_ayarla(self, chat_id)
                                    ok, sent_msg = self.send_msg(chat_id, mt.ayarla_waiting(), reply_markup=custom_kb)
                                    if ok:
                                        set_user(self, chat_id, "bot_last_msg_id", sent_msg["result"]["message_id"])
                                        set_user(self, chat_id, "state", 5)

                                elif text == "/sifirla":
                                    self.send_msg(chat_id, mt.sifirla_start(), reply_markup=self.api.build_remove_keyboard())
                                    set_user(self, chat_id, "state", 6)

                                else:
                                    # böyle bir komut yok
                                    self.send_msg(chat_id, mt.could_not_understand())
                        else:
                            # kullanıcı veritabanında yok
                            self.send_msg(chat_id, mt.not_met(), reply_markup=self.api.build_remove_keyboard())
                else:
                    if user_exists(self, chat_id):
                        user_state = get_user(self, chat_id, "state")[0]

                        if user_state == 1:
                            # kullanıcı ismini yazdı
                            user_name = sanitize_and_validate_user_name(text)
                            if user_name != None:
                                set_user(self, chat_id, "name", user_name)
                                custom_kb = build_custom_kb_of_faculties(self)
                                self.send_msg(chat_id, mt.ask_faculty(), reply_markup=custom_kb)
                                set_user(self, chat_id, "state", 2)
                            else:
                                # isim uygun değil
                                self.send_msg(chat_id, mt.invalid_user_name(), reply_markup=self.api.build_remove_keyboard())

                        elif user_state == 2:
                            # kullanıcı fakülte seçti
                            faculty_row = get_faculty_by_name(self, text, "id")
                            if faculty_row:
                                faculty_id = faculty_row[0]
                                set_user(self, chat_id, "faculty_id", faculty_id)
                                custom_kb = build_custom_kb_of_departments(self, faculty_id)
                                self.send_msg(chat_id, mt.ask_department(), reply_markup=custom_kb)
                                set_user(self, chat_id, "state", 3)
                            else:
                                # özel klavyeden seçmedi (böyle bir fakülte yok)
                                custom_kb = build_custom_kb_of_faculties(self)
                                self.send_msg(chat_id, mt.invalid_response_use_keyboard(), reply_markup=custom_kb)

                        elif user_state == 3:
                            # kullanıcı bölüm seçti
                            department_row = get_department_by_name(self, text, "id")
                            if department_row:
                                department_id = department_row[0]
                                set_user(self, chat_id, "department_id", department_id)
                                faculty_id = get_user(self, chat_id, "faculty_id")[0]
                                create_subscription(self, chat_id, get_channel_by_faculty_id(self, faculty_id, "id")[0])
                                create_subscription(self, chat_id, get_channel_by_department_id(self, department_id, "id")[0])
                                create_subscriptions_to_special_channels(self, chat_id)
                                user_name = get_user(self, chat_id, "name")[0]
                                self.send_msg(chat_id, mt.meeting_done(user_name), reply_markup=self.api.build_remove_keyboard())
                                set_user(self, chat_id, "state", 4)
                            else:
                                # özel klavyeden seçmedi (böyle bir bölüm yok)
                                faculty_id = get_user(self, chat_id, "faculty_id")[0]
                                department_list = [row[0] for row in get_departments_by_faculty_id(self, faculty_id, "name")]
                                department_list.sort()
                                custom_kb = self.api.build_vertical_custom_keyboard(department_list, one_time=True)
                                self.send_msg(chat_id, mt.invalid_response_use_keyboard(), reply_markup=custom_kb)

                        elif user_state == 5:
                            # kullanıcı ayarlamalar yapıyor
                            if text.strip().lower() in [mt.ayarla_done_button().lower(), "tamamla"]:
                                # tamamla
                                self.api.delete_message(chat_id, get_user(self, chat_id, "bot_last_msg_id")[0])
                                self.send_msg(chat_id, mt.ayarla_done(), reply_markup=self.api.build_remove_keyboard())
                                set_user(self, chat_id, "state", 4)
                            else:
                                # kanal aç/kapa
                                channel_row = get_channel_by_name(self, text[:-2], "id")
                                if channel_row:
                                    channel_id = channel_row[0]
                                    toggle_subscription_alt(self, chat_id, channel_id)
                                # aşağıdaki 3 satır iki durumda da ortak, o yüzden if'i ikiye böldüm
                                custom_kb = build_custom_kb_for_ayarla(self, chat_id)
                                self.api.delete_message(chat_id, msg_id)  # kullanıcının mesajını (mesela "Genel Duyurular") sil
                                self.api.delete_message(chat_id, get_user(self, chat_id, "bot_last_msg_id")[0])  # botun mesajını (mesela "...") sil
                                if channel_row:
                                    ok, sent_msg = self.send_msg(chat_id, mt.ayarla_waiting(), reply_markup=custom_kb)
                                else:
                                    # özel klavyeden seçmedi (böyle bir kanal yok)
                                    ok, sent_msg = self.send_msg(chat_id, mt.invalid_response_use_keyboard(), reply_markup=custom_kb)
                                if ok:
                                    set_user(self, chat_id, "bot_last_msg_id", sent_msg["result"]["message_id"])

                        elif user_state == 6:
                            # kullanıcıdan sıfırlama için onay alınıyor
                            if text.strip().lower() == "onayla":
                                delete_user(self, chat_id)
                                self.send_msg(chat_id, mt.sifirla_done(), reply_markup=self.api.build_remove_keyboard())
                            else:
                                self.send_msg(chat_id, mt.user_canceled_sifirla(), reply_markup=self.api.build_remove_keyboard())
                                set_user(self, chat_id, "state", 4)

                        else:
                            # kullanıcıdan mesaj beklemiyorduk
                            self.send_msg(chat_id, mt.could_not_understand())
                    else:
                        # kullanıcı veritabanında yok
                        self.send_msg(chat_id, mt.not_met(), reply_markup=self.api.build_remove_keyboard())

            else:
                # garip durum: gelen mesajda chat_id veya text yok
                pprint(update)
                self.send_msg(chat_id, mt.could_not_understand_msg())
        else:
            # garip durum: gelen olay mesaj değil
            pprint(update)

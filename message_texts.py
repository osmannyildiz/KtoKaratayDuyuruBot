from random import choice


class MessageTexts:
    @staticmethod
    def ask_name():
        return "Merhaba, ben KTO Karatay Duyuru Bot. Kısaca KKDB diyebilirsin.\nSenin ismin nedir?"

    @staticmethod
    def ask_faculty():
        return "Güzel! Şimdi seni daha iyi tanımak için birkaç soru soracağım.\nÖncelikle, hangi fakültede okuyorsun?"

    @staticmethod
    def ask_department():
        return "Peki, bölümün nedir?"

    @staticmethod
    def meeting_done(user_name):
        return f"Tanıştığımıza memnun oldum, {user_name} 😊\n- Yeni bir duyuru yayınlandığında sana haber vereceğim, böylece hiçbir haberi kaçırmayacaksın.\n- İlgini çekeceğini düşündüğüm duyuru kanallarını senin için aktifleştirdim.\n- Abone olduğun duyuru kanallarını görmek ve değiştirmek için istediğin zaman /ayarla yazabilirsin."

    @classmethod
    def ayarla_start(cls):
        return f'İşte tüm duyuru kanallarının listesi. İstediğin kanalları etkinleştirdikten/devre dışı bıraktıktan sonra listenin başındaki "{cls.ayarla_done_button()}" butonuna basabilirsin.'

    @staticmethod
    def ayarla_waiting():
        return "..."

    @staticmethod
    def ayarla_done():
        return "Tamamdır, ayarlarını kaydettim."

    @staticmethod
    def ayarla_done_button():
        return "Tamamla 👍"

    @staticmethod
    def sifirla_start():
        return 'Emin misin? Ayarların silinecek ve yeni duyuruları benden haber alamayacaksın.\nEğer eminsen "onayla" yaz.'

    @staticmethod
    def sifirla_done():
        return "Tamam, seni unuttum.\nBelki bir gün tekrar tanışırız 🍀"

    @staticmethod
    def user_canceled_sifirla():
        return "Sanırım sıfırlamaktan vazgeçtin.\nVazgeçmediysen tekrar /sifirla yazabilirsin."

    @staticmethod
    def already_met():
        return "Seninle tanışmıştık, hatırlıyorum 👋\nBaştan tanışmak istiyorsan /sifirla komutunu dene."

    @staticmethod
    def not_met():
        return "Çıkaramadım, tanışıyor muyuz?\nİstersen /start yaz, tanışalım."

    @staticmethod
    def meeting_already_ongoing():
        return "Zaten şu anda tanışmamız devam ediyor. Sana bir şey sordum, cevabını bekliyorum."

    @staticmethod
    def finish_cmd_first():
        return "Hey, öncelikle halihazırda devam eden işi tamamlamalısın!"

    @staticmethod
    def invalid_user_name():
        return choice([
            "İsmini doğru yazdığından emin misin? Eğer doğruysa, lütfen sadeleştirerek yazmayı dene.",
            "İsmini doğru yazdığından emin misin? Eğer doğruysa, lütfen sadeleştirerek yazmayı dene. Veritabanım sana minnettar kalacak."
        ])

    @staticmethod
    def invalid_response_use_keyboard():
        return choice([
            "Lütfen açılan özel klavyedeki seçenekleri kullan.",
            "Cevabı kendin yazmak yerine açılan özel klavyedeki seçeneklerden seçmelisin."
        ])

    @staticmethod
    def could_not_understand():
        return choice([
            "Üzgünüm, seninle her konuda sohbet edebilecek kadar zeki değilim... Henüz 😉",
            "Iıı şey... Bu konuda pek bir fikrim yok.",
            "Ne demek istediğini anlayamadım..."
        ])

    @staticmethod
    def oops():
        return "Amanın! Az önce ne oldu öyle?"

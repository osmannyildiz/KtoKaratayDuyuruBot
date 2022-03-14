from random import choice


class MessageTexts:
    @staticmethod
    def hello():
        return "Merhaba, ben KTO Karatay Duyuru Bot. Kısaca KKDB diyebilirsin. 🤖\nŞimdi seni daha iyi tanımak için birkaç soru soracağım."

    @staticmethod
    def ask_faculty():
        return "Öncelikle, hangi fakültede okuyorsun?"

    @staticmethod
    def ask_department():
        return "Peki, bölümün nedir?"

    @staticmethod
    def meeting_done():
        return f"Tanıştığımıza memnun oldum 😊\n\n📣 Yeni bir duyuru yayınlandığında sana hemen haber vereceğim, böylece hiçbir gelişmeyi kaçırmayacaksın.\n\n📣 İlgini çekeceğini düşündüğüm duyuru kanallarını senin için aktifleştirdim.\n\n📣 Abone olduğun duyuru kanallarını görmek ve değiştirmek için istediğin zaman mesaj kutusunun solundaki menüyü kullanabilirsin."

    @classmethod
    def toggle_start(cls):
        return f'İşte duyuru kanallarının listesi. İstediğin kanalları etkinleştirdikten/devre dışı bıraktıktan sonra listenin başındaki "{cls.toggle_done_button()}" seçeneğine basabilirsin.'

    @staticmethod
    def toggle_waiting():
        return "..."

    @staticmethod
    def toggle_done():
        return "Tamamdır, ayarlarını kaydettim."

    @staticmethod
    def toggle_done_button():
        return "Tamamla 👍"

    @staticmethod
    def forget():
        return 'Seni unutmamı ve yeni duyuruları haber vermememi istiyorsan sağ üstteki üç nokta menüsünden "Sohbeti sil (Delete chat)" seçeneğini kullanabilirsin.'

    @staticmethod
    def already_met():
        return "Seninle tanışmıştık, hatırlıyorum 👋"

    @staticmethod
    def not_met():
        return "Çıkaramadım, tanışıyor muyuz?\nİstersen /start yaz, tanışalım."

    @staticmethod
    def meeting_already_ongoing():
        return "Zaten şu anda tanışmamız devam ediyor. Sana bir şey sordum, cevabını bekliyorum."

    @staticmethod
    def finish_cmd_first():
        return "Hey, öncelikle halihazırda devam eden işi tamamlayalım!"

    @staticmethod
    def invalid_response_use_keyboard():
        return choice([
            "Lütfen açılan listedeki seçenekleri kullan.",
            "Cevabı kendin yazmak yerine açılan listedeki seçeneklerden seçmelisin."
        ])

    @staticmethod
    def could_not_understand():
        return choice([
            "Üzgünüm, seninle her konuda sohbet edebilecek kadar zeki değilim... Henüz 🦾😉",
            "Iıı şey... Bu konuda pek bir fikrim yok.",
            "Ne demek istediğini anlayamadım..."
        ])

    @staticmethod
    def oops():
        return "Amanın! Az önce ne oldu öyle?"

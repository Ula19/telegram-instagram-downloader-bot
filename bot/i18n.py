"""Мультиязычность — русский, узбекский, английский
Использование: from bot.i18n import t
  t("start.welcome", lang="en", name="John")
"""
from bot.emojis import E


TRANSLATIONS = {
    # === /start ===
    "start.welcome": {
        "ru": (
            f"{E['bot']} <b>Привет, {{name}}!</b>\n\n"
            f"{E['video']} Я помогу тебе скачать видео, фото и истории из Instagram.\n\n"
            f"{E['pin']} <b>Как пользоваться:</b>\n"
            f"Просто отправь мне ссылку на пост, Reels или историю — "
            f"и я пришлю тебе медиа! {E['plane']}\n\n"
            f"Выбери действие ниже:"
        ),
        "uz": (
            f"{E['bot']} <b>Salom, {{name}}!</b>\n\n"
            f"{E['video']} Instagram'dan video, rasm va Stories yuklab olishda yordam beraman.\n\n"
            f"{E['pin']} <b>Qanday foydalanish:</b>\n"
            f"Menga post, Reels yoki story havolasini yuboring — "
            f"men sizga media faylni yuboraman! {E['plane']}\n\n"
            f"Quyidagi tugmalardan birini tanlang:"
        ),
        "en": (
            f"{E['bot']} <b>Hello, {{name}}!</b>\n\n"
            f"{E['video']} I'll help you download videos, photos and Stories from Instagram.\n\n"
            f"{E['pin']} <b>How to use:</b>\n"
            f"Just send me a link to a post, Reels or Story — "
            f"and I'll send you the media! {E['plane']}\n\n"
            f"Choose an action below:"
        ),
    },

    # === Кнопки главного меню (иконки через icon_custom_emoji_id) ===
    "btn.download": {
        "ru": "Скачать видео",
        "uz": "Video yuklab olish",
        "en": "Download video",
    },
    "btn.profile": {
        "ru": "Мой профиль",
        "uz": "Mening profilim",
        "en": "My profile",
    },
    "btn.help": {
        "ru": "Помощь",
        "uz": "Yordam",
        "en": "Help",
    },
    "btn.back": {
        "ru": "Назад",
        "uz": "Orqaga",
        "en": "Back",
    },
    "btn.language": {
        "ru": "Сменить язык",
        "uz": "Tilni o'zgartirish",
        "en": "Change language",
    },

    # === Скачивание ===
    "download.prompt": {
        "ru": (
            f"{E['download']} <b>Скачивание видео из Instagram</b>\n\n"
            f"Отправь мне ссылку на:\n"
            f"• Пост (фото/видео)\n"
            f"• Reels\n"
            f"• Историю\n\n"
            f"{E['link']} Пример: <code>https://www.instagram.com/reel/...</code>"
        ),
        "uz": (
            f"{E['download']} <b>Instagram'dan video yuklab olish</b>\n\n"
            f"Menga quyidagi havolani yuboring:\n"
            f"• Post (rasm/video)\n"
            f"• Reels\n"
            f"• Story\n\n"
            f"{E['link']} Misol: <code>https://www.instagram.com/reel/...</code>"
        ),
        "en": (
            f"{E['download']} <b>Download video from Instagram</b>\n\n"
            f"Send me a link to:\n"
            f"• Post (photo/video)\n"
            f"• Reels\n"
            f"• Story\n\n"
            f"{E['link']} Example: <code>https://www.instagram.com/reel/...</code>"
        ),
    },
    "download.processing": {
        "ru": f"{E['clock']} Скачиваю... Подожди немного",
        "uz": f"{E['clock']} Yuklab olinmoqda... Biroz kuting",
        "en": f"{E['clock']} Downloading... Please wait",
    },
    "download.not_instagram": {
        "ru": (
            f"{E['search']} Это не похоже на ссылку Instagram.\n\n"
            f"Отправь ссылку вида:\n"
            f"<code>https://www.instagram.com/...</code>"
        ),
        "uz": (
            f"{E['search']} Bu Instagram havolasiga o'xshamaydi.\n\n"
            f"Quyidagi ko'rinishdagi havolani yuboring:\n"
            f"<code>https://www.instagram.com/...</code>"
        ),
        "en": (
            f"{E['search']} This doesn't look like an Instagram link.\n\n"
            f"Send a link like:\n"
            f"<code>https://www.instagram.com/...</code>"
        ),
    },
    "download.only_video": {
        "ru": f"{E['camera']} Пока поддерживаются только видео, Reels и Stories.",
        "uz": f"{E['camera']} Hozircha faqat video, Reels va Stories qo'llab-quvvatlanadi.",
        "en": f"{E['camera']} Currently only videos, Reels and Stories are supported.",
    },
    "download.promo": {
        "ru": f"\n\n{E['download']} Скачивай бесплатно через @{{bot_username}}",
        "uz": f"\n\n{E['download']} @{{bot_username}} orqali bepul yuklab oling",
        "en": f"\n\n{E['download']} Download for free via @{{bot_username}}",
    },
    "download.profile_photo": {
        "ru": f"{E['camera']} Фото профиля @{{username}}",
        "uz": f"{E['camera']} @{{username}} profil rasmi",
        "en": f"{E['camera']} Profile photo of @{{username}}",
    },

    # === Inline-режим (кнопки над результатами — без HTML) ===
    "inline.hint": {
        "ru": "Вставь ссылку на пост, Reels или профиль",
        "uz": "Post, Reels yoki profil havolasini kiriting",
        "en": "Paste a post, Reels or profile link",
    },
    "inline.rate_limit": {
        "ru": "Слишком много запросов — подожди минуту",
        "uz": "Juda ko'p so'rovlar — bir daqiqa kuting",
        "en": "Too many requests — wait a minute",
    },
    "inline.need_sub": {
        "ru": "Сначала подпишись на каналы — открой бота",
        "uz": "Avval kanallarga obuna bo'ling — botni oching",
        "en": "Subscribe to channels first — open the bot",
    },
    "inline.error": {
        "ru": "Не получилось — попробуй скачать в боте",
        "uz": "Xatolik — botda yuklab olishga urinib ko'ring",
        "en": "Failed — try downloading in the bot",
    },
    "inline.title_video": {
        "ru": "Отправить видео",
        "uz": "Video yuborish",
        "en": "Send video",
    },
    "inline.title_photo": {
        "ru": "Отправить фото",
        "uz": "Rasm yuborish",
        "en": "Send photo",
    },

    # === Описания команд бота (для меню Telegram) ===
    "cmd.start": {
        "ru": "Запустить бота",
        "uz": "Botni boshlash",
        "en": "Start the bot",
    },
    "cmd.menu": {
        "ru": "Главное меню",
        "uz": "Asosiy menyu",
        "en": "Main menu",
    },
    "cmd.profile": {
        "ru": "Мой профиль",
        "uz": "Mening profilim",
        "en": "My profile",
    },
    "cmd.help": {
        "ru": "Помощь",
        "uz": "Yordam",
        "en": "Help",
    },
    "cmd.language": {
        "ru": "Сменить язык",
        "uz": "Tilni o'zgartirish",
        "en": "Change language",
    },

    # === Профиль ===
    "profile.title": {
        "ru": (
            f"{E['profile']} <b>Твой профиль</b>\n\n"
            f"{E['edit']} Имя: {{full_name}}\n"
            f"{E['info']} ID: <code>{{user_id}}</code>\n"
            f"{E['download']} Скачиваний (всего): {{downloads}}\n"
        ),
        "uz": (
            f"{E['profile']} <b>Sizning profilingiz</b>\n\n"
            f"{E['edit']} Ism: {{full_name}}\n"
            f"{E['info']} ID: <code>{{user_id}}</code>\n"
            f"{E['download']} Yuklashlar (jami): {{downloads}}\n"
        ),
        "en": (
            f"{E['profile']} <b>Your profile</b>\n\n"
            f"{E['edit']} Name: {{full_name}}\n"
            f"{E['info']} ID: <code>{{user_id}}</code>\n"
            f"{E['download']} Downloads (total): {{downloads}}\n"
        ),
    },

    # === Помощь ===
    "help.text": {
        "ru": (
            f"{E['book']} <b>Помощь</b>\n\n"
            f"{E['star']} Отправь ссылку на пост Instagram — получишь видео или фото\n"
            f"{E['star']} Поддерживаются: посты, Reels, истории\n"
            f"{E['lock']} Приватные аккаунты не поддерживаются\n\n"
            f"{E['plane']} По вопросам: @{{admin_username}}"
        ),
        "uz": (
            f"{E['book']} <b>Yordam</b>\n\n"
            f"{E['star']} Instagram post havolasini yuboring — video yoki rasm olasiz\n"
            f"{E['star']} Qo'llab-quvvatlanadi: postlar, Reels, stories\n"
            f"{E['lock']} Yopiq akkauntlar qo'llab-quvvatlanmaydi\n\n"
            f"{E['plane']} Savollar uchun: @{{admin_username}}"
        ),
        "en": (
            f"{E['book']} <b>Help</b>\n\n"
            f"{E['star']} Send an Instagram post link — get a video or photo\n"
            f"{E['star']} Supported: posts, Reels, stories\n"
            f"{E['lock']} Private accounts are not supported\n\n"
            f"{E['plane']} Contact: @{{admin_username}}"
        ),
    },

    # === Подписка ===
    "sub.welcome": {
        "ru": (
            f"{E['bot']} <b>Привет!</b>\n\n"
            f"{E['video']} Этот бот скачивает видео, фото и Stories "
            f"из Instagram — быстро и бесплатно!\n\n"
            f"{E['lock']} <b>Для начала подпишись на каналы ниже:</b>\n\n"
            f"После подписки нажми «{E['check']} Проверить подписку»"
        ),
        "uz": (
            f"{E['bot']} <b>Salom!</b>\n\n"
            f"{E['video']} Bu bot Instagram'dan video, rasm va Stories "
            f"yuklab oladi — tez va bepul!\n\n"
            f"{E['lock']} <b>Boshlash uchun quyidagi kanallarga obuna bo'ling:</b>\n\n"
            f"Obuna bo'lgandan keyin «{E['check']} Obunani tekshirish» tugmasini bosing"
        ),
        "en": (
            f"{E['bot']} <b>Hello!</b>\n\n"
            f"{E['video']} This bot downloads videos, photos and Stories "
            f"from Instagram — fast and free!\n\n"
            f"{E['lock']} <b>To start, subscribe to the channels below:</b>\n\n"
            f"After subscribing, tap «{E['check']} Check subscription»"
        ),
    },
    "sub.not_subscribed": {
        "ru": (
            f"{E['cross']} <b>Ты ещё не подписался на все каналы:</b>\n\n"
            f"Подпишись и нажми «{E['check']} Проверить подписку» ещё раз."
        ),
        "uz": (
            f"{E['cross']} <b>Siz hali barcha kanallarga obuna bo'lmadingiz:</b>\n\n"
            f"Obuna bo'ling va «{E['check']} Obunani tekshirish» tugmasini qayta bosing."
        ),
        "en": (
            f"{E['cross']} <b>You haven't subscribed to all channels yet:</b>\n\n"
            f"Subscribe and tap «{E['check']} Check subscription» again."
        ),
    },
    "sub.success": {
        "ru": (
            f"{E['check']} <b>Отлично, {{name}}!</b>\n\n"
            f"Теперь ты можешь пользоваться ботом! {E['plane']}\n\n"
            f"Отправь ссылку на пост, Reels или историю Instagram."
        ),
        "uz": (
            f"{E['check']} <b>Ajoyib, {{name}}!</b>\n\n"
            f"Endi siz botdan foydalanishingiz mumkin! {E['plane']}\n\n"
            f"Instagram post, Reels yoki story havolasini yuboring."
        ),
        "en": (
            f"{E['check']} <b>Great, {{name}}!</b>\n\n"
            f"You can now use the bot! {E['plane']}\n\n"
            f"Send a link to an Instagram post, Reels or Story."
        ),
    },
    "btn.check_sub": {
        "ru": "Проверить подписку",
        "uz": "Obunani tekshirish",
        "en": "Check subscription",
    },
    "sub.check_alert_fail": {
        "ru": "Подпишись на все каналы!",
        "uz": "Barcha kanallarga obuna bo'ling!",
        "en": "Subscribe to all channels!",
    },
    "sub.check_alert_ok": {
        "ru": "Подписка подтверждена!",
        "uz": "Obuna tasdiqlandi!",
        "en": "Subscription confirmed!",
    },
    "sub.not_required": {
        "ru": "Подписка не требуется!",
        "uz": "Obuna talab qilinmaydi!",
        "en": "No subscription required!",
    },

    # === Ошибки ===
    "error.session": {
        "ru": f"{E['lock']} <b>Нужна авторизация</b>\n\nДля скачивания Stories нужен INSTAGRAM_SESSION_ID.",
        "uz": f"{E['lock']} <b>Avtorizatsiya kerak</b>\n\nStories yuklab olish uchun INSTAGRAM_SESSION_ID kerak.",
        "en": f"{E['lock']} <b>Authorization required</b>\n\nINSTAGRAM_SESSION_ID is needed to download Stories.",
    },
    "error.story_expired": {
        "ru": f"{E['clock']} <b>История не найдена</b>\n\nВозможно, она уже истекла (24 часа) или аккаунт приватный.",
        "uz": f"{E['clock']} <b>Story topilmadi</b>\n\nEhtimol, u allaqachon o'chirilgan (24 soat) yoki akkaunt yopiq.",
        "en": f"{E['clock']} <b>Story not found</b>\n\nIt may have expired (24 hours) or the account is private.",
    },
    "error.private": {
        "ru": f"{E['lock']} <b>Аккаунт приватный</b>\n\nК сожалению, скачивание из приватных аккаунтов невозможно.",
        "uz": f"{E['lock']} <b>Akkaunt yopiq</b>\n\nAfsuski, yopiq akkauntlardan yuklab olish mumkin emas.",
        "en": f"{E['lock']} <b>Private account</b>\n\nUnfortunately, downloading from private accounts is not possible.",
    },
    "error.not_found": {
        "ru": f"{E['cross']} <b>Пост не найден</b>\n\nВозможно, он удалён или ссылка неправильная.",
        "uz": f"{E['cross']} <b>Post topilmadi</b>\n\nEhtimol, u o'chirilgan yoki havola noto'g'ri.",
        "en": f"{E['cross']} <b>Post not found</b>\n\nIt may have been deleted or the link is incorrect.",
    },
    "error.unsupported": {
        "ru": f"{E['warning']} <b>Ссылка не поддерживается</b>\n\nПоддерживаются: посты, Reels и Stories.",
        "uz": f"{E['warning']} <b>Havola qo'llab-quvvatlanmaydi</b>\n\nQo'llab-quvvatlanadi: postlar, Reels va Stories.",
        "en": f"{E['warning']} <b>Link not supported</b>\n\nSupported: posts, Reels and Stories.",
    },
    "error.too_large": {
        "ru": f"{E['package']} <b>Файл слишком большой</b>\n\nTelegram ограничивает размер файла до 50 МБ.",
        "uz": f"{E['package']} <b>Fayl juda katta</b>\n\nTelegram fayl hajmini 50 MB bilan cheklaydi.",
        "en": f"{E['package']} <b>File too large</b>\n\nTelegram limits file size to 50 MB.",
    },
    "error.timeout": {
        "ru": f"{E['clock']} <b>Превышено время ожидания</b>\n\nПопробуй ещё раз через пару минут.",
        "uz": f"{E['clock']} <b>Kutish vaqti tugadi</b>\n\nBir necha daqiqadan keyin qayta urinib ko'ring.",
        "en": f"{E['clock']} <b>Request timed out</b>\n\nPlease try again in a few minutes.",
    },
    "error.generic": {
        "ru": f"{E['cross']} <b>Не удалось скачать</b>\n\nПопробуй позже или проверь ссылку.",
        "uz": f"{E['cross']} <b>Yuklab olib bo'lmadi</b>\n\nKeyinroq urinib ko'ring yoki havolani tekshiring.",
        "en": f"{E['cross']} <b>Download failed</b>\n\nTry again later or check the link.",
    },
    "error.rate_limit": {
        "ru": f"{E['clock']} <b>Слишком много запросов!</b>\n\nПодожди {{seconds}} секунд и попробуй снова.",
        "uz": f"{E['clock']} <b>Juda ko'p so'rovlar!</b>\n\n{{seconds}} soniya kuting va qayta urinib ko'ring.",
        "en": f"{E['clock']} <b>Too many requests!</b>\n\nWait {{seconds}} seconds and try again.",
    },
    "error.profile_failed": {
        "ru": (
            f"{E['cross']} <b>Не удалось скачать фото профиля @{{username}}</b>\n\n"
            f"Возможно, аккаунт не существует или Instagram временно блокирует запросы.\n\n"
            f"{E['bulb']} Чтобы скачать медиа — отправь ссылку на пост, Reels или историю."
        ),
        "uz": (
            f"{E['cross']} <b>@{{username}} profil rasmini yuklab bo'lmadi</b>\n\n"
            f"Ehtimol, akkaunt mavjud emas yoki Instagram so'rovlarni vaqtincha bloklamoqda.\n\n"
            f"{E['bulb']} Media yuklab olish uchun post, Reels yoki story havolasini yuboring."
        ),
        "en": (
            f"{E['cross']} <b>Couldn't download profile photo of @{{username}}</b>\n\n"
            f"The account may not exist or Instagram is temporarily blocking requests.\n\n"
            f"{E['bulb']} To download media — send a link to a post, Reels or Story."
        ),
    },

    # === Выбор языка ===
    "lang.choose": {
        "ru": f"{E['gear']} <b>Выберите язык:</b>",
        "uz": f"{E['gear']} <b>Tilni tanlang:</b>",
        "en": f"{E['gear']} <b>Choose language:</b>",
    },
    "lang.changed": {
        "ru": f"{E['check']} Язык изменён на русский",
        "uz": f"{E['check']} Til o'zbek tiliga o'zgartirildi",
        "en": f"{E['check']} Language changed to English",
    },

    # === Админ-панель ===
    "admin.title": {
        "ru": f"{E['gear']} <b>Админ-панель</b>\n\nВыбери действие:",
        "uz": f"{E['gear']} <b>Admin panel</b>\n\nAmalni tanlang:",
        "en": f"{E['gear']} <b>Admin panel</b>\n\nChoose an action:",
    },
    "admin.no_access": {
        "ru": f"{E['lock']} У тебя нет доступа к админке.",
        "uz": f"{E['lock']} Sizda admin panelga kirish huquqi yo'q.",
        "en": f"{E['lock']} You don't have access to admin panel.",
    },
    "admin.stats": {
        "ru": (
            f"{E['chart']} <b>Статистика бота</b>\n\n"
            f"{E['users']} Всего юзеров: <b>{{total_users}}</b>\n"
            f"{E['star']} Новых юзеров сегодня: <b>{{today_users}}</b>\n"
            f"{E['download']} Всего скачиваний: <b>{{total_downloads}}</b>\n"
            f"{E['megaphone']} Каналов: <b>{{total_channels}}</b>"
        ),
        "uz": (
            f"{E['chart']} <b>Bot statistikasi</b>\n\n"
            f"{E['users']} Jami foydalanuvchilar: <b>{{total_users}}</b>\n"
            f"{E['star']} Bugungi yangi foydalanuvchilar: <b>{{today_users}}</b>\n"
            f"{E['download']} Jami yuklashlar: <b>{{total_downloads}}</b>\n"
            f"{E['megaphone']} Kanallar: <b>{{total_channels}}</b>"
        ),
        "en": (
            f"{E['chart']} <b>Bot statistics</b>\n\n"
            f"{E['users']} Total users: <b>{{total_users}}</b>\n"
            f"{E['star']} New users today: <b>{{today_users}}</b>\n"
            f"{E['download']} Total downloads: <b>{{total_downloads}}</b>\n"
            f"{E['megaphone']} Channels: <b>{{total_channels}}</b>"
        ),
    },
    "admin.channels_empty": {
        "ru": f"{E['megaphone']} <b>Каналы</b>\n\nСписок пуст. Добавь канал кнопкой ниже.",
        "uz": f"{E['megaphone']} <b>Kanallar</b>\n\nRo'yxat bo'sh. Quyidagi tugma orqali kanal qo'shing.",
        "en": f"{E['megaphone']} <b>Channels</b>\n\nList is empty. Add a channel using the button below.",
    },
    "admin.channels_title": {
        "ru": f"{E['megaphone']} <b>Каналы для подписки:</b>\n",
        "uz": f"{E['megaphone']} <b>Obuna kanallari:</b>\n",
        "en": f"{E['megaphone']} <b>Subscription channels:</b>\n",
    },
    "admin.add_channel_id": {
        "ru": (
            f"{E['megaphone']} <b>Добавление канала</b>\n\n"
            f"Отправь <b>ID канала</b> (числовой, например <code>-1001234567890</code>)\n\n"
            f"{E['bulb']} Узнать ID: добавь бота @getmyid_bot в канал"
        ),
        "uz": (
            f"{E['megaphone']} <b>Kanal qo'shish</b>\n\n"
            f"<b>Kanal ID</b> raqamini yuboring (masalan <code>-1001234567890</code>)\n\n"
            f"{E['bulb']} ID bilish: @getmyid_bot ni kanalga qo'shing"
        ),
        "en": (
            f"{E['megaphone']} <b>Add channel</b>\n\n"
            f"Send the <b>channel ID</b> (numeric, e.g. <code>-1001234567890</code>)\n\n"
            f"{E['bulb']} Get ID: add @getmyid_bot to the channel"
        ),
    },
    "admin.add_channel_title": {
        "ru": f"{E['edit']} Теперь отправь <b>название канала</b> (для отображения юзеру):",
        "uz": f"{E['edit']} Endi <b>kanal nomini</b> yuboring (foydalanuvchiga ko'rsatiladi):",
        "en": f"{E['edit']} Now send the <b>channel name</b> (displayed to the user):",
    },
    "admin.add_channel_link": {
        "ru": (
            f"{E['link']} Теперь отправь <b>ссылку или юзернейм канала</b>\n\n"
            f"Принимаю любой формат:\n"
            f"• <code>https://t.me/your_channel</code>\n"
            f"• <code>@your_channel</code>\n"
            f"• <code>your_channel</code>"
        ),
        "uz": (
            f"{E['link']} Endi <b>kanal havolasi yoki username</b> yuboring\n\n"
            f"Istalgan formatda:\n"
            f"• <code>https://t.me/your_channel</code>\n"
            f"• <code>@your_channel</code>\n"
            f"• <code>your_channel</code>"
        ),
        "en": (
            f"{E['link']} Now send the <b>channel link or username</b>\n\n"
            f"Any format accepted:\n"
            f"• <code>https://t.me/your_channel</code>\n"
            f"• <code>@your_channel</code>\n"
            f"• <code>your_channel</code>"
        ),
    },
    "admin.channel_added": {
        "ru": f"{E['check']} <b>Канал добавлен!</b>",
        "uz": f"{E['check']} <b>Kanal qo'shildi!</b>",
        "en": f"{E['check']} <b>Channel added!</b>",
    },
    "admin.confirm_delete": {
        "ru": f"{E['warning']} <b>Удалить канал?</b>\n\nID: <code>{{channel_id}}</code>\n\nЭто действие нельзя отменить.",
        "uz": f"{E['warning']} <b>Kanalni o'chirishni xohlaysizmi?</b>\n\nID: <code>{{channel_id}}</code>\n\nBu amalni qaytarib bo'lmaydi.",
        "en": f"{E['warning']} <b>Delete channel?</b>\n\nID: <code>{{channel_id}}</code>\n\nThis action cannot be undone.",
    },
    "admin.id_not_number": {
        "ru": f"{E['cross']} ID должен быть числом. Попробуй ещё раз:",
        "uz": f"{E['cross']} ID raqam bo'lishi kerak. Qayta urinib ko'ring:",
        "en": f"{E['cross']} ID must be a number. Try again:",
    },
    "admin.title_too_long": {
        "ru": f"{E['cross']} Название слишком длинное (макс 200 символов)",
        "uz": f"{E['cross']} Nom juda uzun (maks 200 belgi)",
        "en": f"{E['cross']} Name is too long (max 200 characters)",
    },
    "admin.link_invalid": {
        "ru": f"{E['cross']} Не удалось распознать ссылку.\nПопробуй ещё:",
        "uz": f"{E['cross']} Havolani aniqlab bo'lmadi.\nQayta urinib ko'ring:",
        "en": f"{E['cross']} Could not parse the link.\nTry again:",
    },
    "btn.admin_stats": {
        "ru": "Статистика",
        "uz": "Statistika",
        "en": "Statistics",
    },
    "btn.admin_channels": {
        "ru": "Каналы",
        "uz": "Kanallar",
        "en": "Channels",
    },
    "btn.admin_home": {
        "ru": "Главное меню",
        "uz": "Bosh menyu",
        "en": "Main menu",
    },
    "btn.admin_add": {
        "ru": "Добавить канал",
        "uz": "Kanal qo'shish",
        "en": "Add channel",
    },
    "btn.admin_back": {
        "ru": "Назад",
        "uz": "Orqaga",
        "en": "Back",
    },
    "btn.admin_cancel": {
        "ru": "Отмена",
        "uz": "Bekor qilish",
        "en": "Cancel",
    },
    "btn.admin_confirm_del": {
        "ru": "Да, удалить",
        "uz": "Ha, o'chirish",
        "en": "Yes, delete",
    },
    "btn.admin_cancel_del": {
        "ru": "Отмена",
        "uz": "Bekor qilish",
        "en": "Cancel",
    },
    "btn.admin_panel": {
        "ru": "Админ-панель",
        "uz": "Admin panel",
        "en": "Admin panel",
    },
    "btn.admin_broadcast": {
        "ru": "Рассылка",
        "uz": "Xabar yuborish",
        "en": "Broadcast",
    },
    "admin.broadcast_prompt": {
        "ru": (
            f"{E['plane']} <b>Массовая рассылка</b>\n\n"
            f"Отправь текст/фото/видео для рассылки.\n"
            f"Поддерживается HTML-разметка."
        ),
        "uz": (
            f"{E['plane']} <b>Ommaviy xabar</b>\n\n"
            f"Yuborish uchun matn/rasm/video yuboring.\n"
            f"HTML formatlash qo'llab-quvvatlanadi."
        ),
        "en": (
            f"{E['plane']} <b>Mass broadcast</b>\n\n"
            f"Send text/photo/video to broadcast.\n"
            f"HTML formatting is supported."
        ),
    },
    "admin.broadcast_preview": {
        "ru": f"{E['eye']} <b>Предпросмотр</b>\n\nОтправить это сообщение всем юзерам?",
        "uz": f"{E['eye']} <b>Oldindan ko'rish</b>\n\nBu xabarni barcha foydalanuvchilarga yuborishni xohlaysizmi?",
        "en": f"{E['eye']} <b>Preview</b>\n\nSend this message to all users?",
    },
    "admin.broadcast_confirm": {
        "ru": "Да, отправить",
        "uz": "Ha, yuborish",
        "en": "Yes, send",
    },
    "admin.broadcast_cancel": {
        "ru": "Отмена",
        "uz": "Bekor qilish",
        "en": "Cancel",
    },
    "admin.broadcast_started": {
        "ru": f"{E['plane']} Рассылка запущена... Ожидай отчёт.",
        "uz": f"{E['plane']} Xabar yuborilmoqda... Hisobotni kuting.",
        "en": f"{E['plane']} Broadcast started... Wait for report.",
    },
    "admin.broadcast_done": {
        "ru": (
            f"{E['chart']} <b>Рассылка завершена!</b>\n\n"
            f"{E['check']} Доставлено: <b>{{success}}</b>\n"
            f"{E['cross']} Ошибок: <b>{{failed}}</b>\n"
            f"{E['users']} Всего: <b>{{total}}</b>"
        ),
        "uz": (
            f"{E['chart']} <b>Xabar yuborish tugadi!</b>\n\n"
            f"{E['check']} Yetkazildi: <b>{{success}}</b>\n"
            f"{E['cross']} Xatolar: <b>{{failed}}</b>\n"
            f"{E['users']} Jami: <b>{{total}}</b>"
        ),
        "en": (
            f"{E['chart']} <b>Broadcast complete!</b>\n\n"
            f"{E['check']} Delivered: <b>{{success}}</b>\n"
            f"{E['cross']} Failed: <b>{{failed}}</b>\n"
            f"{E['users']} Total: <b>{{total}}</b>"
        ),
    },
}


def t(key: str, lang: str = "ru", **kwargs) -> str:
    """Получить перевод по ключу и языку"""
    translations = TRANSLATIONS.get(key, {})
    text = translations.get(lang, translations.get("en", f"[{key}]"))
    if kwargs:
        text = text.format(**kwargs)
    return text


def detect_language(language_code: str | None) -> str:
    """Определяет язык по Telegram: ru → русский, uz → узбекский, остальное → английский"""
    if not language_code:
        return "en"
    if language_code.startswith("ru"):
        return "ru"
    if language_code.startswith("uz"):
        return "uz"
    return "en"


def get_bot_commands(lang: str) -> list:
    """Возвращает список BotCommand на нужном языке — для set_my_commands"""
    from aiogram.types import BotCommand
    return [
        BotCommand(command="start",    description=t("cmd.start",    lang)),
        BotCommand(command="menu",     description=t("cmd.menu",     lang)),
        BotCommand(command="profile",  description=t("cmd.profile",  lang)),
        BotCommand(command="help",     description=t("cmd.help",     lang)),
        BotCommand(command="language", description=t("cmd.language", lang)),
    ]

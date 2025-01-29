import sys
from threading import Timer

from telebot.types import InputMediaPhoto, InputMediaVideo

import keyboards
from CONSTANTS import *
from Control.scrollStateManager import ScrollStateManager
from Model.redisManager import *
import logging
import traceback
import telebot
from Model.repository import repository
from Control.search import *
from messageModule import show_result


class botManager:
    def __init__(self, bot, redis_manager: redisManager):
        self.bot = bot
        self.redis_manager = redis_manager
        self.repository = repository(self.redis_manager)
        self.register_handlers()
        self.scroll_manager = ScrollStateManager()
        self._setup_logging()

    def error_handler(self, func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # گرفتن اطلاعات خط خطا
                error_info = traceback.extract_tb(e.__traceback__)
                error_line = error_info[-1].lineno
                error_file = error_info[-1].filename

                error_message = f"""
                خطا در فایل: {error_file}
                خط: {error_line}
                پیغام خطا: {str(e)}
                """

                self.logger.error(error_message)
                # می‌توانید اینجا پیام خطا را برای ادمین ارسال کنید
                return None

        return wrapper

    def _setup_logging(self):

        """تنظیم سیستم لاگینگ"""
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('bot_debug.log', encoding="utf-8"),
                logging.StreamHandler(sys.stdout)  # نمایش در کنسول

            ]

        )
        self.logger = logging.getLogger("TeleBot")
        self.logger.setLevel(logging.DEBUG)

    def can_enter_text_search_state(self, message):
        user_id = message.from_user.id
        current_state = self.repository.get_state(user_id)

        if message.text == search_by_text_btn_txt:
            if current_state in [start_state, image_search_state]:
                return True
        return False

    def can_enter_wait_for_text_query_state(self, message):
        user_id = message.from_user.id
        current_state = self.repository.get_state(user_id)
        if current_state == text_search_state:
            return True
        else:
            return False

    def can_enter_searching_text_state(self, message):
        user_id = message.from_user.id
        current_state = self.repository.get_state(user_id)
        print(f'current_state:{current_state}')  # اضافه کنید
        if current_state == searching_text_state:
            return True
        else:
            return False

    def register_handlers(self):

        # سایر هندلرها

        @self.bot.message_handler(commands=['help', 'start'])
        def start_state_handler(message):
            user_id = message.from_user.id
            self.repository.set_profile(message)
            self.bot.send_message(message.chat.id, start_message, reply_markup=keyboards.main_menu())
            self.repository.set_state(user_id, start_state)

        @self.bot.message_handler(func=self.can_enter_text_search_state)
        def text_search_state_handler(message):
            user_id = message.from_user.id
            self.bot.send_message(message.chat.id, enter_text_query_to_search)
            self.repository.set_state(user_id, text_search_state)

        @self.bot.message_handler(func=self.can_enter_wait_for_text_query_state)
        def wait_for_text_query_state_handler(message):
            user_id = message.from_user.id

            if message.text in [search_by_text_btn_txt, search_by_image_btn_txt]:
                self.bot.send_message(message.chat.id, wrong_query_to_search)
                return

            self.bot.send_message(message.chat.id, searching_query)
            try:
                api_result = searchService.text_search_product_ids_api_url(q=message.text)
                product_ids = searchService.fetch_text_result_product_ids(api_result)

                if not product_ids:
                    self.bot.send_message(message.chat.id, "متاسفانه محصولی با این مشخصات پیدا نشد.")
                    return

                self.repository.set_search_product_ids(user_id, product_ids)
                self.scroll_manager.set_scroll_state(user_id, 0, len(product_ids))

                first_product_id = product_ids[0]
                product_details = self.repository.get_product_details(first_product_id)

                if not product_details:
                    product_details = searchService.get_product_details(first_product_id)
                    self.repository.set_product_details(first_product_id, product_details)

                self._send_product_message(message, product_details)
                self.repository.set_state(user_id, text_search_state)

            except Exception as e:
                self.logger.error(f"خطا در پردازش جستجو: {str(e)}")
                self.bot.send_message(message.chat.id, "متأسفانه در جستجوی محصول مشکلی پیش آمد.")

        @self.bot.callback_query_handler(func=lambda call: call.data in [prev_product, next_product])
        def handle_navigation(call):
            try:
                user_id = call.from_user.id
                if call.data == next_product:
                    current_product_idx = self.scroll_manager.next_product(user_id)
                elif call.data == prev_product:
                    current_product_idx = self.scroll_manager.prev_product(user_id)

                product_ids = self.repository.get_search_product_ids(user_id)
                product_id = product_ids[current_product_idx]
                product_details = self.repository.get_product_details(product_id) or searchService.get_product_details(
                    product_id)

                self._send_product_message(call.message, product_details, edit=True)
                self.bot.answer_callback_query(call.id)

            except Exception as e:
                self.logger.error(f"خطا در ناوبری: {str(e)}")

    def _prepare_gallery_media_group(self, product_details: dict) -> list:
        """آماده‌سازی گروه مدیا برای گالری محصول

        این متد یک گروه مدیا از تصاویر و ویدئوهای محصول ایجاد می‌کند.
        گالری به صورت یک لیست از URLها دریافت می‌شود و هر URL می‌تواند
        مربوط به عکس یا ویدئو باشد.
        """
        media_group = []
        gallery = product_details.get('gallery', [])  # دریافت گالری به صورت لیست

        # اگر گالری خالی است، برمی‌گردیم
        if not gallery:
            self.logger.warning(f"گالری خالی برای محصول دریافت شد: {product_details.get('title', 'نامشخص')}")
            return []

        # تهیه کپشن برای اولین مدیا
        caption = (
            f"نام محصول:\n{product_details.get('title', 'نامشخص')}\n"
            f"قیمت: {product_details.get('price', 'نامشخص')} تومان\n"
            f"ارسال رایگان: {'بله' if product_details.get('free_shipping_to_iran') else 'خیر'}\n"
            f"شهر: {product_details.get('city', 'نامشخص')}\n"
            f"لینک محصول:\n{product_details.get('product_link', '')}"
        )

        # چون گالری حالا یک لیست است، مستقیماً روی آن حلقه می‌زنیم
        for i, media_url in enumerate(gallery):
            try:
                # تشخیص نوع مدیا و ساخت آبجکت مناسب
                is_video = media_url.endswith('.mp4')
                if is_video:
                    media = InputMediaVideo(media_url, caption=caption if i == 0 else '')
                else:
                    media = InputMediaPhoto(media_url, caption=caption if i == 0 else '')
                media_group.append(media)

            except Exception as e:
                self.logger.error(f"خطا در پردازش مدیای شماره {i}: {str(e)}")
                continue  # به پردازش بقیه مدیاها ادامه می‌دهیم

        # اگر هیچ مدیایی با موفقیت اضافه نشد
        if not media_group:
            self.logger.warning("هیچ مدیایی با موفقیت به گروه اضافه نشد")
            return []

        self.logger.info(f"گروه مدیا با {len(media_group)} آیتم با موفقیت ساخته شد")
        return media_group

    def _send_product_message(self, message, product_details, edit=False):
        try:
            gallery = product_details.get('gallery', [])[:10]
            caption = (
                f"نام محصول:\n{product_details.get('title', 'نامشخص')}\n"
                f"قیمت: {product_details.get('price', 'نامشخص')} تومان\n"
                f"ارسال رایگان: {'بله' if product_details.get('free_shipping_to_iran') else 'خیر'}\n"
                f"شهر: {product_details.get('city', 'نامشخص')}\n"
                f"لینک محصول:\n{product_details.get('product_link', '')}"
            )

            media_group = []
            for i, media_url in enumerate(gallery):
                media = InputMediaVideo(media_url, caption=caption if i == 0 else '') if media_url.endswith(
                    '.mp4') else InputMediaPhoto(media_url, caption=caption if i == 0 else '')
                media_group.append(media)

            if edit:
                for i, msg_id in enumerate(self._collection_message_ids):
                    if i < len(media_group):
                        self.bot.edit_message_media(
                            chat_id=message.chat.id,
                            message_id=msg_id,
                            media=media_group[i]
                        )
            else:
                sent_messages = self.bot.send_media_group(message.chat.id, media_group)
                self._collection_message_ids = [msg.message_id for msg in sent_messages]
                self.bot.send_message(
                    message.chat.id,
                    "برای مشاهده محصولات دیگر:",
                    reply_markup=keyboards.search_gallery_navigation_buttons()
                )

            self.repository.set_state(message.from_user.id, wait_for_text_query_state)

        except Exception as e:
            self.logger.error(f"خطا در ارسال پیام محصول: {str(e)}")
            self.bot.send_message(message.chat.id, "متأسفانه در نمایش محصول مشکلی پیش آمد.")

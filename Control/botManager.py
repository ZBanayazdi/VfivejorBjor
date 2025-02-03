import sys
import types
from threading import Timer

from telebot.types import InputMediaPhoto, InputMediaVideo

import keyboards
from CONSTANTS import *
from Control.scrollStateManager import ScrollStateManager
from Model.convert_to_persian_numbers import price_digits_converter, text_digits_converter
from Model.redisManager import *
import logging
import traceback
import telebot
from Model.repository import repository
from Control.search import *


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
        print('can_enter_text_search_state')
        current_state = self.repository.get_state(user_id)

        if message.text == search_by_text_btn_txt:
            if current_state in [start_state, image_search_state]:
                return True
        return False

    def can_enter_image_search_state(self, message):
        user_id = message.from_user.id
        print('can_enter_image_search_state')
        current_state = self.repository.get_state(user_id)

        if message.text == search_by_image_btn_txt:
            if current_state in [start_state, text_search_state]:
                return True
        return False

    def can_enter_wait_for_text_query_state(self, message):
        user_id = message.from_user.id
        print('can_enter_wait_for_text_query_state')
        current_state = self.repository.get_state(user_id)
        if current_state == text_search_state:
            return True
        else:
            return False

    def can_enter_wait_for_image_query_state(self, message):
        user_id = message.from_user.id
        print('can_enter_wait_for_image_query_state')
        current_state = self.repository.get_state(user_id)
        if current_state == image_search_state:
            return True
        else:
            return False

    def can_enter_searching_text_state(self, message):
        user_id = message.from_user.id
        print('can_enter_searching_text_state')
        current_state = self.repository.get_state(user_id)
        print(f'current_state:{current_state}')  # اضافه کنید
        if current_state == searching_text_state:
            return True
        else:
            return False

    def can_enter_handle_text_in_image_search(self, message):
        if message.content_type == 'text' and self.repository.get_state(message.from_user.id) == image_search_state \
                and message.text in [search_by_text_btn_txt, search_by_image_btn_txt]:
            return True
        else:
            return False

    def register_handlers(self):

        # سایر هندلرها

        @self.bot.message_handler(commands=['help', 'start'])
        def start_state_handler(message):
            user_id = message.from_user.id
            self.repository.set_profile(message)
            self.bot.send_message(message.chat.id, start_message, reply_markup=keyboards.main_menu(), parse_mode="HTML")
            self.repository.set_state(user_id, start_state)

        @self.bot.message_handler(func=self.can_enter_text_search_state)
        def text_search_state_handler(message):
            user_id = message.from_user.id
            self.bot.send_message(message.chat.id, enter_text_query_to_search)
            self.repository.set_state(user_id, text_search_state)

        @self.bot.message_handler(func=self.can_enter_image_search_state)
        def image_search_state_handler(message):
            print('image_search_state_handler')
            user_id = message.from_user.id
            self.bot.send_message(message.chat.id, enter_image_query_to_search)
            self.repository.set_state(user_id, image_search_state)

        @self.bot.message_handler(func=self.can_enter_wait_for_text_query_state)
        def wait_for_text_query_state_handler(message):
            print('wait_for_text_query_state_handler')
            user_id = message.from_user.id

            if message.text in [search_by_text_btn_txt, search_by_image_btn_txt]:
                self.bot.send_message(message.chat.id, wrong_text_query_to_search)
                return
            searching_msg = self.bot.send_message(message.chat.id, searching_query)
            self._searching_message_id = searching_msg.message_id

            try:
                api_result = searchService.text_search_product_ids_api_url(q=message.text)
                product_ids = searchService.fetch_result_product_ids(api_result)

                if not product_ids:
                    caption = (f'متاسفانه چیزی ئیدا نکردیم!'
                               f'\nشاید با عبارتی غیر از {message.text} بتونی به چیزی که میخواهی برسی')
                    try:
                        with open('product_not_found.PNG', 'rb') as photo:
                            self.bot.send_photo(
                                chat_id=message.chat.id,
                                photo=photo,
                                caption=caption
                            )

                    except Exception as e:
                        self.logger.error(f"Error sending not found image: {str(e)}")
                        self.bot.send_message(
                            chat_id=message.chat.id,
                            text=caption
                        )
                    self.bot.send_message(chat_id=message.chat.id, text=new_query)

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
                self.bot.send_message(chat_id=message.chat.id, text=new_query)

        @self.bot.message_handler(func=self.can_enter_handle_text_in_image_search)
        def handle_text_in_image_search(message):
            current_state = self.repository.get_state(message.from_user.id)

            """هندلر برای پیام‌های متنی در حالت جستجوی تصویری"""
            if message.text in search_by_image_btn_txt:
                self.bot.send_message(message.chat.id, wrong_image_query_to_search)
                return
            else:
                self.bot.send_message(message.chat.id, enter_image_query_to_search)

        @self.bot.message_handler(content_types=['photo'], func=self.can_enter_wait_for_image_query_state)
        def wait_for_image_query_state_handler(message):
            user_id = message.from_user.id

            searching_msg = self.bot.send_message(message.chat.id, searching_query)
            self._searching_message_id = searching_msg.message_id
            print('h')
            try:
                file_info = self.bot.get_file(message.photo[-1].file_id)
                self.logger.info(f"Got file info: {file_info.file_path}")
                print('h2')

                # Download the file
                file = self.bot.download_file(file_info.file_path)
                self.logger.info(f"File downloaded, size: {len(file)} bytes")

                # Perform the search
                api_result = searchService.image_search_product_ids_api_url(file=file)
                print(f'api_result:{api_result}')
                product_ids = searchService.fetch_result_product_ids(api_result)
                print(f'product_ids:{product_ids}')
                if not product_ids:
                    caption = (f'متاسفانه چیزی ئیدا نکردیم!'
                               f'\nشاید با عبارتی غیر از {message.text} بتونی به چیزی که میخواهی برسی')
                    try:
                        with open('product_not_found.PNG', 'rb') as photo:
                            self.bot.send_photo(
                                chat_id=message.chat.id,
                                photo=photo,
                                caption=caption
                            )
                    except Exception as e:
                        self.logger.error(f"Error sending not found image: {str(e)}")
                        self.bot.send_message(
                            chat_id=message.chat.id,
                            text=caption
                        )
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

        @self.bot.callback_query_handler(func=lambda call: call.data in [next_product])
        def handle_navigation(call):
            current_product_idx = 0
            """Handle navigation between products using prev/next buttons"""
            try:
                user_id = call.from_user.id
                if call.data == next_product:
                    current_product_idx = self.scroll_manager.next_product(user_id)

                # دریافت محصول جدید
                product_ids = self.repository.get_search_product_ids(user_id)
                product_id = product_ids[current_product_idx]
                product_details = self.repository.get_product_details(product_id) or searchService.get_product_details(
                    product_id)

                if not product_details:
                    self.bot.answer_callback_query(call.id, "خطا در دریافت اطلاعات محصول")
                    return

                # ارسال محصول جدید با پاک کردن قبلی‌ها
                self._send_product_message(call.message, product_details, edit=True)

                # تایید callback
                self.bot.answer_callback_query(call.id)

            except Exception as e:
                self.logger.error(f"خطا در ناوبری: {str(e)}")
                self.bot.answer_callback_query(call.id, "خطا در نمایش محصول")

    def _prepare_gallery_media_group(self, product_details: dict) -> list:
        """آماده‌سازی گروه مدیا برای گالری محصول

        این متد یک گروه مدیا از تصاویر و ویدئوهای محصول ایجاد می‌کند.
        گالری به صورت یک لیست از URLها دریافت می‌شود و هر URL می‌تواند
        مربوط به عکس یا ویدئو باشد.
        """
        media_group = []
        _gallery = product_details.get('gallery', [])  # دریافت گالری به صورت لیست

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
        for i, media_url in enumerate(_gallery):
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
        """ارسال پیام محصول با آلبوم تصاویر"""
        user_id = message.from_user.id
        chat_id = message.chat.id

        try:
            # اول چک کنیم که محصول و گالری وجود دارن
            if not product_details:
                self.logger.error("Product details is empty")
                self.bot.send_message(chat_id, "اطلاعات محصول در دسترس نیست.")
                return

            gallery = product_details.get('gallery', [])[:10]  # محدود به 10 آیتم
            if not gallery:
                self.logger.warning(f"Empty gallery for product: {product_details.get('title', 'unknown')}")
                self.bot.send_message(chat_id, "این محصول تصویری ندارد.")
                return

            # کپشن محصول
            caption = (
                f"📦 {text_digits_converter(product_details.get('title', 'نمیدونم!'))}\n"
                f"🏷️ قیمت: {price_digits_converter(product_details.get('price', 'نمیدونم!'))} تومان \n"
                f"🕊 ارسال رایگان: {'بله' if product_details.get('free_shipping_to_iran') else 'خیر'}\n"
                f"📍 شهر: {product_details.get('city', 'نمیدونم!')}\n"
                f"\n"
                f"{product_details.get('vendor_link', 'نمیدونم!')}\n"
                f"{product_details.get('product_link', 'نمیدونم!')}"
            )

            # ساخت آلبوم با validation
            media = []
            valid_urls = []
            if media:
                media[0].caption = caption
                media[0].parse_mode = 'HTML'  # اضافه کردن این خط

            for url in gallery:
                if not isinstance(url, str) or not url.strip():
                    self.logger.warning(f"Invalid URL found: {url}")
                    continue

                url = url.strip()
                try:
                    # اول چک کنیم URL معتبر هست
                    if not (url.startswith('http://') or url.startswith('https://')):
                        self.logger.warning(f"Invalid URL format: {url}")
                        continue

                    # چک کردن در دسترس بودن URL
                    response = httpx.head(url, timeout=5.0)
                    if response.status_code != 200:
                        self.logger.warning(f"URL not accessible: {url}, status: {response.status_code}")
                        continue

                    valid_urls.append(url)

                except Exception as e:
                    self.logger.warning(f"Error validating URL {url}: {str(e)}")
                    continue

            # اگر هیچ URL معتبری نداشتیم
            if not valid_urls:
                self.bot.send_message(
                    chat_id=chat_id,
                    text="متأسفانه تصاویر این محصول در حال حاضر در دسترس نیستند."
                )
                self.bot.send_message(chat_id,new_query)
                return

            # ساخت media group با URLهای معتبر
            for url in valid_urls:
                try:
                    if url.endswith('.mp4'):
                        media.append(InputMediaVideo(url))
                    else:
                        media.append(InputMediaPhoto(url))
                except Exception as e:
                    self.logger.error(f"Error creating media input for {url}: {str(e)}")
                    continue

            # اضافه کردن کپشن به اولین مدیا
            if media:
                media[0].caption = caption
                media[0].parse_mode = 'HTML'

            # ارسال مدیا گروپ
            try:
                # اول محتوای جدید را می‌فرستیم
                album_messages = self.bot.send_media_group(chat_id, media)
                new_album_message_ids = [msg.message_id for msg in album_messages]

                nav_message = self.bot.send_message(
                    chat_id=chat_id,
                    text='اگه دوست داشتی میتونی بعدی رو هم ببینی',
                    reply_markup=keyboards.search_gallery_navigation_buttons()
                )
                new_nav_message_id = nav_message.message_id

                # حذف پیام‌های قبلی در صورت نیاز
                if edit:
                    if hasattr(self, '_searching_message_id'):
                        try:
                            self.bot.delete_message(chat_id, self._searching_message_id)
                            delattr(self, '_searching_message_id')
                        except Exception as e:
                            self.logger.warning(f"Failed to delete searching message: {str(e)}")

                    if hasattr(self, '_nav_message_id'):
                        try:
                            self.bot.delete_message(chat_id, self._nav_message_id)
                        except Exception as e:
                            self.logger.warning(f"Failed to delete nav message: {str(e)}")

                # ذخیره شناسه‌های جدید
                self._album_message_ids = new_album_message_ids
                self._nav_message_id = new_nav_message_id

                # تنظیم وضعیت جدید
                self.repository.set_state(user_id, wait_for_text_query_state)
                self.bot.send_message(chat_id=chat_id, text=new_query)

            except telebot.apihelper.ApiException as e:
                self.logger.error(f"Telegram API error: {str(e)}")
                self.bot.send_message(chat_id, "متأسفانه در نمایش محصول مشکلی پیش آمد.")

        except Exception as e:
            self.logger.error(f"Error in _send_product_message: {str(e)}")
            self.bot.send_message(chat_id, "متأسفانه در نمایش محصول مشکلی پیش آمد.")

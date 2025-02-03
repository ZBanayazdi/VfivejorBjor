# import logging
#
# import redis
# import json
#
# from CONSTANTS import text_search_state, image_search_state
#
# from datetime import timedelta
# class redisManager:
#     def __init__(self):
#         self.users = redis.Redis(host='localhost', port=6379, db=0
#                                  , decode_responses=True)
#         self.PRODUCT_TTL = timedelta(hours=1)  # تنظیم TTL به یک ساعت
#
#         # راه‌اندازی لاگر
#         self.logger = logging.getLogger('RedisManager')
#         self.logger.setLevel(logging.DEBUG)
#
#         # اگر هنوز handler برای لاگر تنظیم نشده، اضافه می‌کنیم
#         if not self.logger.handlers:
#             # handler برای نمایش لاگ‌ها در کنسول
#             console_handler = logging.StreamHandler()
#             console_handler.setLevel(logging.DEBUG)
#
#             # فرمت لاگ‌ها
#             formatter = logging.Formatter(
#                 '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
#             )
#             console_handler.setFormatter(formatter)
#
#             # اضافه کردن handler به لاگر
#             self.logger.addHandler(console_handler)
#
#             # اضافه کردن handler برای ذخیره لاگ‌ها در فایل
#             file_handler = logging.FileHandler('redis_manager.log', encoding='utf-8')
#             file_handler.setLevel(logging.DEBUG)
#             file_handler.setFormatter(formatter)
#             self.logger.addHandler(file_handler)
#
#
#
#
#
#
#
#
#
#     def set_user_profile(self, message):
#         user_id = message.from_user.id
#         if message.from_user.first_name:
#             self.users.hset(f'user:{user_id}', 'first_name', message.from_user.first_name)
#         if message.from_user.username:
#             self.users.hset(f'user:{user_id}', 'username', message.from_user.username)
#         if message.from_user.last_name:
#             self.users.hset(f'user:{user_id}', 'last_name', message.from_user.last_name)
#
#     def get_user_profile(self, user_id):
#         user_profile = self.users.hgetall(f'user:{user_id}')
#         return user_profile if user_profile else None
#
#     def set_user_status(self, user_id, status):
#         if status:
#             self.users.hset(f'user:{user_id}', 'status', status)
#         else:
#             print(f"Error: status is None or empty for user {user_id}")
#
#     def get_user_status(self, user_id):
#         user_status = self.users.hget(f'user:{user_id}', 'status')
#         return user_status if user_status else None
#
#     def set_user_query(self, user_id, query):
#         if query:
#             self.users.hset(f'user:{user_id}', 'query', query)
#         else:
#             print(f"Error: query is None or empty for user {user_id}")
#
#     def get_user_query(self, user_id):
#         query = self.users.hget(f'user:{user_id}', 'query')
#         return query if query else None
#
#     # redisManager.py
#     def set_user_result_product_ids(self, user_id: str, product_ids: list):
#         key = f"user:{user_id}:search_product_ids"
#         self.users.delete(key)
#         if product_ids:
#             return self.users.rpush(key, *product_ids)
#         return 0
#
#     def get_user_result_product_ids(self, user_id: str) -> list:
#         return self.users.lrange(f"user:{user_id}:search_product_ids", 0, -1)
#
#     # def set_product_details(self, product_id: str, details: dict):
#     #     """
#     #     ذخیره جزئیات محصول با TTL یک ساعته در Redis با پردازش دقیق مقادیر None
#     #     """
#     #     key = f"product:{product_id}"
#     #     pipe = self.users.pipeline()
#     #
#     #     try:
#     #         # چاپ داده‌های ورودی برای بررسی
#     #         print("Original details:", details)
#     #
#     #         # تبدیل مقادیر به فرمت مناسب برای Redis
#     #         processed_details = {}
#     #         for k, v in details.items():
#     #             # چاپ هر کلید و مقدار برای دیباگ
#     #             print(f"Processing key: {k}, value: {v}, type: {type(v)}")
#     #
#     #             if v is None:
#     #                 processed_details[k] = ""  # استفاده از رشته خالی به جای "None"
#     #             elif isinstance(v, dict):
#     #                 try:
#     #                     processed_details[k] = json.dumps(v)
#     #                 except TypeError as e:
#     #                     print(f"Error converting dict to JSON for key {k}: {e}")
#     #                     # اگر تبدیل به JSON با خطا مواجه شد، سعی می‌کنیم مقادیر None درون دیکشنری را هم تبدیل کنیم
#     #                     cleaned_dict = {dk: ('' if dv is None else dv) for dk, dv in v.items()}
#     #                     processed_details[k] = json.dumps(cleaned_dict)
#     #             elif isinstance(v, (list, tuple)):
#     #                 # تبدیل لیست‌ها به JSON با پردازش مقادیر None
#     #                 cleaned_list = ['' if item is None else str(item) for item in v]
#     #                 processed_details[k] = json.dumps(cleaned_list)
#     #             else:
#     #                 # تبدیل همه مقادیر دیگر به رشته
#     #                 processed_details[k] = str(v) if v is not None else ''
#     #
#     #         # چاپ داده‌های پردازش شده برای بررسی
#     #         print("Processed details:", processed_details)
#     #
#     #         # حذف کلید قبلی اگر وجود دارد
#     #         pipe.delete(key)
#     #         # ذخیره اطلاعات جدید با مقادیر پردازش شده
#     #         pipe.hset(key, mapping=processed_details)
#     #         # تنظیم TTL
#     #         pipe.expire(key, int(self.PRODUCT_TTL.total_seconds()))
#     #         # اجرای همه دستورات در یک تراکنش
#     #         pipe.execute()
#     #         return True
#     #
#     #     except Exception as e:
#     #         print(f"Error saving product details: {str(e)}")
#     #         # چاپ جزئیات بیشتر خطا
#     #         print(f"Error type: {type(e)}")
#     #         print(f"Failed details structure: {type(details)}")
#     #         if hasattr(e, '__traceback__'):
#     #             import traceback
#     #             traceback.print_tb(e.__traceback__)
#     #         return False
#     #
#     # def get_product_details(self, product_id: str) -> dict:
#     #     """
#     #     بازیابی جزئیات محصول از Redis با تبدیل مناسب انواع داده‌ها.
#     #
#     #     این متد داده‌های ذخیره شده را از Redis بازیابی می‌کند و آنها را به فرمت مناسب برمی‌گرداند:
#     #     - رشته‌های خالی به None تبدیل می‌شوند
#     #     - رشته‌های JSON به دیکشنری یا لیست تبدیل می‌شوند
#     #     - سایر مقادیر با حفظ نوع داده مناسب برگردانده می‌شوند
#     #
#     #     Args:
#     #         product_id (str): شناسه محصول مورد نظر
#     #
#     #     Returns:
#     #         dict: دیکشنری حاوی جزئیات محصول با مقادیر تبدیل شده به فرمت مناسب
#     #     """
#     #     key = f"product:{product_id}"
#     #
#     #     try:
#     #         # دریافت داده‌های خام از Redis
#     #         raw_details = self.users.hgetall(key)
#     #
#     #         # اگر هیچ داده‌ای یافت نشد، دیکشنری خالی برگردان
#     #         if not raw_details:
#     #             return {}
#     #
#     #         # پردازش و تبدیل داده‌های دریافتی
#     #         processed_details = {}
#     #         for k, v in raw_details.items():
#     #             # چاپ برای دیباگ
#     #             print(f"Processing retrieved key: {k}, value: {v}, type: {type(v)}")
#     #
#     #             # اگر مقدار رشته خالی است، آن را به None تبدیل می‌کنیم
#     #             if v == '':
#     #                 processed_details[k] = None
#     #                 continue
#     #
#     #             # سعی می‌کنیم مقدار را به عنوان JSON تفسیر کنیم
#     #             try:
#     #                 # اگر مقدار یک رشته JSON معتبر است
#     #                 if v.startswith('{') or v.startswith('['):
#     #                     processed_value = json.loads(v)
#     #                     # اگر دیکشنری برگشتی حاوی رشته خالی است، آن را به None تبدیل می‌کنیم
#     #                     if isinstance(processed_value, dict):
#     #                         processed_value = {dk: (None if dv == '' else dv)
#     #                                            for dk, dv in processed_value.items()}
#     #                     elif isinstance(processed_value, list):
#     #                         processed_value = [None if item == '' else item
#     #                                            for item in processed_value]
#     #                     processed_details[k] = processed_value
#     #                     continue
#     #             except json.JSONDecodeError:
#     #                 # اگر تبدیل به JSON موفق نبود، از مقدار اصلی استفاده می‌کنیم
#     #                 pass
#     #
#     #             # برای سایر مقادیر، آنها را به همان شکل نگه می‌داریم
#     #             processed_details[k] = v
#     #
#     #         return processed_details
#     #
#     #     except Exception as e:
#     #         print(f"Error getting product details: {str(e)}")
#     #         print(f"Error type: {type(e)}")
#     #         if hasattr(e, '__traceback__'):
#     #             import traceback
#     #             traceback.print_tb(e.__traceback__)
#     #         return {}
#     def set_product_details(self, product_id: str, details: dict):
#         """ذخیره جزئیات محصول در ردیس"""
#         try:
#             key = f"product:{product_id}"
#             processed_details = details.copy()
#
#             self.logger.debug(f"شروع ذخیره جزئیات محصول با ID: {product_id}")
#             self.logger.debug(f"جزئیات اولیه: {processed_details}")
#
#             # تبدیل گالری به JSON اگر لیست باشد
#             if 'gallery' in processed_details and isinstance(processed_details['gallery'], list):
#                 processed_details['gallery'] = json.dumps(processed_details['gallery'])
#                 self.logger.debug("گالری با موفقیت به JSON تبدیل شد")
#
#             # ذخیره در ردیس
#             self.users.hset(key, mapping=processed_details)
#             self.users.expire(key, int(self.PRODUCT_TTL.total_seconds()))
#
#             self.logger.info(f"جزئیات محصول {product_id} با موفقیت ذخیره شد")
#             return True
#
#         except Exception as e:
#             self.logger.error(f"خطا در ذخیره جزئیات محصول {product_id}: {str(e)}")
#             self.logger.exception("جزئیات خطا:")
#             return False
#
#     def get_product_details(self, product_id: str) -> dict:
#         try:
#             key = f"product:{product_id}"
#             details = self.users.hgetall(key)
#
#             # اگر گالری به صورت JSON ذخیره شده، آن را به لیست تبدیل می‌کنیم
#             if 'gallery' in details:
#                 try:
#                     details['gallery'] = json.loads(details['gallery'])
#                 except json.JSONDecodeError:
#                     details['gallery'] = []
#
#             return details
#         except Exception as e:
#             self.logger.error(f"خطا در بازیابی جزئیات محصول: {str(e)}")
#             return {}
import json
import logging
from datetime import timedelta

import redis


class redisManager:
    def __init__(self):
        self.users = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.PRODUCT_TTL = timedelta(hours=1)
        self.logger = logging.getLogger('RedisManager')
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

            file_handler = logging.FileHandler('redis_manager.log', encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def get_user_profile(self, user_id):
        user_profile = self.users.hgetall(f'user:{user_id}')
        return user_profile if user_profile else None

    def set_user_profile(self, message):
        user_id = message.from_user.id
        if message.from_user.first_name:
            self.users.hset(f'user:{user_id}', 'first_name', message.from_user.first_name)
        if message.from_user.username:
            self.users.hset(f'user:{user_id}', 'username', message.from_user.username)
        if message.from_user.last_name:
            self.users.hset(f'user:{user_id}', 'last_name', message.from_user.last_name)

    def set_user_status(self, user_id, status):
        if status:
            self.users.hset(f'user:{user_id}', 'status', status)
        else:
            self.logger.error(f"Error: status is None or empty for user {user_id}")

    def get_user_status(self, user_id):
        user_status = self.users.hget(f'user:{user_id}', 'status')
        return user_status if user_status else None

    def set_user_query(self, user_id, query):
        if query:
            self.users.hset(f'user:{user_id}', 'query', query)
        else:
            self.logger.error(f"Error: query is None or empty for user {user_id}")

    def get_user_query(self, user_id):
        query = self.users.hget(f'user:{user_id}', 'query')
        return query if query else None

    def set_search_product_ids(self, user_id: str, product_ids: list):
        key = f"user:{user_id}:search_product_ids"
        self.users.delete(key)
        if product_ids:
            return self.users.rpush(key, *product_ids)
        return 0

    def get_search_product_ids(self, user_id: str) -> list:
        return self.users.lrange(f"user:{user_id}:search_product_ids", 0, -1)

    def set_product_details(self, product_id: str, details: dict):
        try:
            key = f"product:{product_id}"
            processed_details = {}

            # تبدیل همه مقادیر None به رشته خالی
            for k, v in details.items():
                if v is None:
                    processed_details[k] = ""
                elif isinstance(v, (list, dict)):
                    processed_details[k] = json.dumps(v)
                else:
                    processed_details[k] = str(v)

            self.users.hset(key, mapping=processed_details)
            self.users.expire(key, int(self.PRODUCT_TTL.total_seconds()))
            return True
        except Exception as e:
            self.logger.error(f"خطا در ذخیره جزئیات محصول {product_id}: {str(e)}")
            return False

    def get_product_details(self, product_id: str) -> dict:
        try:
            key = f"product:{product_id}"
            details = self.users.hgetall(key)

            if 'gallery' in details:
                try:
                    details['gallery'] = json.loads(details['gallery'])
                except json.JSONDecodeError:
                    details['gallery'] = []
            return details
        except Exception as e:
            self.logger.error(f"خطا در بازیابی جزئیات محصول {product_id}: {str(e)}")
            return {}

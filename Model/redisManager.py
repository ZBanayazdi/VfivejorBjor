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

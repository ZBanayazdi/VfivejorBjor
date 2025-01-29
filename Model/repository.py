# from CONSTANTS import start_state
#
#
# class repository:
#     def __init__(self, redis_manager):
#         self.redis_manager = redis_manager
#         # self.user_profile = userProfile
#         self.current_state = None  # وضعیت فعلی کاربر
#         self.response = None
#         self.query = None
#
#     def set_profile(self, message):
#         self.redis_manager.set_user_profile(message)
#
#     def get_profile(self, user_id):
#         print(f'user_id in repository:{user_id}')
#
#         profile = self.redis_manager.get_user_profile(user_id)
#         print(f'profile in repository is:{profile}')
#         return profile
#
#     def set_state(self, user_id, new_state):
#         if new_state == 'start':
#             new_state = start_state
#         """تغییر وضعیت کاربر"""
#         self.current_state = new_state
#         # ذخیره وضعیت در Redis
#         self.redis_manager.set_user_status(user_id, new_state)
#
#     def get_state(self, user_id):
#         """دریافت وضعیت فعلی از Redis"""
#         state_name = self.redis_manager.get_user_status(user_id)
#         return state_name
#
#     def set_query(self, user_id, query):
#         self.redis_manager.set_user_query(user_id, query)
#
#     def get_query(self, user_id):
#         return self.redis_manager.get_user_query(user_id)
#
#     def set_result_product_ids(self, user_id: str, product_ids: list):
#         """ذخیره لیست آیدی محصولات جستجو شده"""
#         return self.redis_manager.set_user_result_product_ids(user_id, product_ids)
#
#     def get_result_product_ids(self, user_id: str) -> list:
#         """دریافت لیست آیدی محصولات جستجو شده"""
#         return self.redis_manager.get_user_result_product_ids(user_id)
#
#     def set_product_details(self, product_id: str, details: dict):
#         """ذخیره جزئیات محصول با TTL یک ساعته"""
#         return self.redis_manager.set_product_details(product_id, details)
#
#     def get_product_details(self, product_id: str) -> dict:
#         """دریافت جزئیات محصول از کش"""
#         return self.redis_manager.get_product_details(product_id)
from CONSTANTS import start_state


class repository:
   def __init__(self, redis_manager):
       self.redis_manager = redis_manager
       self.current_state = None
       self.response = None
       self.query = None

   def set_profile(self, message):
       self.redis_manager.set_user_profile(message)

   def get_profile(self, user_id):
       return self.redis_manager.get_user_profile(user_id)

   def set_state(self, user_id, new_state):
       if new_state == 'start':
           new_state = start_state
       self.current_state = new_state
       self.redis_manager.set_user_status(user_id, new_state)

   def get_state(self, user_id):
       return self.redis_manager.get_user_status(user_id)

   def set_query(self, user_id, query):
       self.redis_manager.set_user_query(user_id, query)

   def get_query(self, user_id):
       return self.redis_manager.get_user_query(user_id)

   def set_search_product_ids(self, user_id: str, product_ids: list):
       return self.redis_manager.set_search_product_ids(user_id, product_ids)

   def get_search_product_ids(self, user_id: str) -> list:
       return self.redis_manager.get_search_product_ids(user_id)

   def set_product_details(self, product_id: str, details: dict):
       return self.redis_manager.set_product_details(product_id, details)

   def get_product_details(self, product_id: str) -> dict:
       return self.redis_manager.get_product_details(product_id)
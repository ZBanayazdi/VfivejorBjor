class ScrollStateManager:
    """مدیریت وضعیت اسکرول کاربران در مشاهده محصولات"""

    def __init__(self):
        # دیکشنری برای نگهداری وضعیت اسکرول هر کاربر
        # ساختار: {user_id: {"product_index": int, "total_products": int}}
        self._scroll_states = {}

    def set_scroll_state(self, user_id: str, product_index: int, total_products: int = None):
        """
        تنظیم وضعیت اسکرول برای یک کاربر

        Args:
            user_id: شناسه یکتای کاربر
            product_index: شماره محصول فعلی
            total_products: تعداد کل محصولات
        """
        if user_id not in self._scroll_states:
            self._scroll_states[user_id] = {
                "product_index": 0,
                "total_products": 0
            }

        state = self._scroll_states[user_id]
        state["product_index"] = product_index

        if total_products is not None:
            state["total_products"] = total_products

    def get_scroll_state(self, user_id: str) -> tuple:
        """
        دریافت وضعیت اسکرول فعلی کاربر

        Returns:
            tuple: (product_index, total_products)
        """
        if user_id not in self._scroll_states:
            return 0, 0

        state = self._scroll_states[user_id]
        return state["product_index"], state["total_products"]

    def next_product(self, user_id: str) -> int:
        """رفتن به محصول بعدی"""
        if user_id not in self._scroll_states:
            return 0

        state = self._scroll_states[user_id]
        if state["product_index"] < state["total_products"] - 1:
            state["product_index"] += 1

        return state["product_index"]

    def prev_product(self, user_id: str) -> int:
        """رفتن به محصول قبلی"""
        if user_id not in self._scroll_states:
            return 0

        state = self._scroll_states[user_id]
        if state["product_index"] > 0:
            state["product_index"] -= 1

        return state["product_index"]

    def clear_state(self, user_id: str):
        """پاک کردن وضعیت اسکرول کاربر"""
        if user_id in self._scroll_states:
            del self._scroll_states[user_id]
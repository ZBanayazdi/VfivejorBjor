def price_digits_converter(text):
    """تبدیل اعداد به فارسی با فرمت صحیح قیمت"""
    persian_numbers = {
        '0': '۰',
        '1': '۱',
        '2': '۲',
        '3': '۳',
        '4': '۴',
        '5': '۵',
        '6': '۶',
        '7': '۷',
        '8': '۸',
        '9': '۹',
    }

    if not isinstance(text, str):
        text = str(text)
    # تبدیل به تومان (حذف صفر آخر)
    if len(text) > 1:
        text = text[:-1]
    # حذف هرچیزی بجز اعداد
    num = ''.join(filter(str.isdigit, text))

    # تبدیل به عدد فارسی
    result = ''
    for i, digit in enumerate(num):
        result += persian_numbers[digit]
        # اضافه کردن ٬ بعد از هر سه رقم از سمت راست
        if i < len(num) - 1 and (len(num) - i - 1) % 3 == 0:
            result += '٬'

    return result


def text_digits_converter(text: str) -> str:
    """
    دریافت متن و تبدیل اعداد انگلیسی به فارسی در صورت وجود.

    :param text: متنی که ممکن است شامل اعداد انگلیسی باشد.
    :return: متن با اعداد فارسی.
    """
    english_to_farsi_digit_map = {
        '0': '۰',  # صفر فارسی
        '1': '۱',  # یک فارسی
        '2': '۲',  # دو فارسی
        '3': '۳',  # سه فارسی
        '4': '۴',  # چهار فارسی
        '5': '۵',  # پنج فارسی
        '6': '۶',  # شش فارسی
        '7': '۷',  # هفت فارسی
        '8': '۸',  # هشت فارسی
        '9': '۹',  # نه فارسی
    }

    converted_text = "".join(
        english_to_farsi_digit_map[char] if char in english_to_farsi_digit_map else char
        for char in text
    )

    return converted_text



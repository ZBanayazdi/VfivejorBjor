from telebot.types import InlineKeyboardButton, KeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

from CONSTANTS import search_by_text_btn_txt, search_by_image_btn_txt, next_product_btn_text, basalam_link_btn_text, \
    base_url, next_product, utm_data


def main_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    search_by_text_btn = KeyboardButton(search_by_text_btn_txt)
    search_by_pic_post_btn = KeyboardButton(search_by_image_btn_txt)
    keyboard.add(search_by_pic_post_btn, search_by_text_btn)
    return keyboard


def search_gallery_navigation_buttons():
    next_product_btn = InlineKeyboardButton(next_product_btn_text, callback_data=next_product)
    basalam_link_btn = InlineKeyboardButton(basalam_link_btn_text, url=f'{base_url}{utm_data}')

    markup = InlineKeyboardMarkup(row_width=1)
    markup.row(basalam_link_btn,next_product_btn)
    return markup

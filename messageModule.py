import traceback
from threading import Timer

from telebot.types import InputMediaVideo, InputMediaPhoto, logger

from CONSTANTS import text_search_state, image_search_state, enter_text_query_to_search, wait_for_text_query_state, \
    enter_image_query_to_search, wait_for_image_query_state, photo, video
from Control.search import searchService
from keyboards import search_gallery_navigation_buttons


def set_caption(res=None, product_id=None, message=None):
    if res:
        result_product = res[f"product_{product_id}"]
        # استفاده از متد get برای جلوگیری از KeyError
        caption = (
            f'نام محصول:\n  {result_product.get("name", "نمیدونم!")}\n'
            f'قیمت محصول: {result_product.get("price", "نمیدونم!")}\n'
            f'هزینه ارسال: {result_product.get("free_shipping", "نمیدونم!")}\n'
            f'شهر: {result_product.get("city", "نمیدونم!")}\n'
            f'لینک غرفه دار:\n{result_product.get("vendor_link", "نمیدونم!")}\n'
        )
        return caption
    elif not res:
        if not message or not message.text:
            return ""
        product_not_found_caption = (
            f'<b>متاسفانه چیزی پیدا نکردیم!</b>'
            f'\n\nشاید با عبارتی غیر از '
            f'<b>"{message.text}"</b>'
            f'\nبتونی به چیزی که میخوای برسی'
            f'\n\nعبارتی که جستجو کردید را اصلاح کنید'
        )
        return product_not_found_caption


def show_result(bot, repository, message, result_product_ids):
    user_id = message.from_user.id
    first_product_id = result_product_ids[0]
    print(f'first_product_id:{first_product_id}')
    is_cached_first_product = repository.get_product_details(first_product_id)
    print(f'is_cached_first_product:{is_cached_first_product}')
    try:
        if is_cached_first_product == {}:
            first_product_details = searchService.get_product_details(first_product_id)
            print(f'first_product_details:{first_product_details}')
            is_set=repository.set_product_details(first_product_id, first_product_details)
            if is_set:
                show_result_message(bot, repository, message)
    except:
        _handle_no_results(bot, message)


def _handle_no_results(bot, message):
    """پردازش حالت بدون نتیجه"""
    print("Handling no results case")
    try:
        send_media_message(
            bot,
            photo,
            open('product_not_found.PNG', 'rb'),
            set_caption(message=message),
            message
        )
    except Exception as e:
        print(f"Error handling no results: {str(e)}")
        bot.send_message(
            message.chat.id,
            "متأسفانه نتیجه‌ای برای جستجوی شما پیدا نشد."
        )


def send_media_message(bot, media_type, item, caption, message=None, call=None, edit_message=False,
                       reply_markup=None):
    try:
        chat_id = None
        message_id = None

        # دریافت صحیح chat_id و message_id
        if call and call.message:
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            print(f"Using call data - Chat ID: {chat_id}, Message ID: {message_id}")
        elif message:
            chat_id = message.chat.id
            message_id = message.message_id
            print(f"Using message data - Chat ID: {chat_id}, Message ID: {message_id}")

        if not chat_id:
            print("Error: Could not determine chat_id")
            return

        # اگر قراره پیام رو ادیت کنیم
        if edit_message and message_id:
            try:
                if media_type == video:
                    media = InputMediaVideo(
                        media=item,
                        caption=caption,
                        parse_mode='HTML'
                    )
                else:  # photo
                    media = InputMediaPhoto(
                        media=item,
                        caption=caption,
                        parse_mode='HTML'
                    )

                print(f"Editing message - Type: {media_type}, Chat ID: {chat_id}, Message ID: {message_id}")

                bot.edit_message_media(
                    media=media,
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=reply_markup
                )
                print("Message edited successfully")

            except Exception as e:
                print(f'Error in edit_message_media: {str(e)}')
                print(f'Media type: {media_type}')
                print(f'Item: {item}')
                traceback.print_exc()

        # اگر پیام جدید میفرستیم
        else:
            print(f"Sending new message - Type: {media_type}, Chat ID: {chat_id}")
            if media_type == video:
                bot.send_video(
                    chat_id=chat_id,
                    video=item,
                    caption=caption,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
            elif media_type == photo:
                bot.send_photo(
                    chat_id=chat_id,
                    photo=item,
                    caption=caption,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
            print("New message sent successfully")

    except Exception as e:
        print(f'Error in send_media_message: {str(e)}')
        print(f'Parameters - Media type: {media_type}, Edit mode: {edit_message}')
        print(f'Call exists: {call is not None}, Message exists: {message is not None}')
        traceback.print_exc()


def show_result_message(bot, repository, msg):
    user_id = msg.from_user.id
    response = repository.get_response(user_id)
    print(f'response from show_result_message:{response}')

    # اضافه کردن لاگ برای بررسی response
    logger.info(f"Got response for user {user_id}: {response}")

    if not response:
        bot.logger.error(f"Error: response is None or empty for user {user_id}")
        bot.send_media_message(
            photo,
            open('product_not_found.PNG', 'rb'),
            set_caption(message=msg),
            msg
        )
        return

    repository.set_state(user_id, text_search_state)

    if repository.get_state(msg.from_user.id) == text_search_state:
        repository.set_scroll_state(user_id, 0, 0)

        current_product_id, current_gallery_index, total_products, total_gallery_items = (
            repository.get_scroll_state(user_id)
        )

        # اضافه کردن لاگ برای بررسی وضعیت
        logger.info(f"Current status - Product: {current_product_id}, Gallery: {current_gallery_index}")
        logger.info(f"Totals - Products: {total_products}, Gallery items: {total_gallery_items}")

        try:
            caption_text = set_caption(response, current_product_id)
            gallery_item = response[f'product_{current_product_id}']['gallery'].get(
                f'gallery_item_{current_gallery_index}'
            )

            logger.info(f"Gallery item found: {gallery_item is not None}")
            logger.info(f"Caption text: {caption_text}")

            if gallery_item:
                if '.mp4' in gallery_item:
                    return send_media_message(bot, video, gallery_item, caption_text, msg, None, False,
                                              search_gallery_navigation_buttons())
                else:
                    return send_media_message(bot, photo, gallery_item, caption_text, msg, None, False,
                                              search_gallery_navigation_buttons())

            else:
                logger.error("No gallery item found")
                return False

        except Exception as e:
            logger.error(f"Error processing result: {str(e)}", exc_info=True)
            bot.send_media_message(
                photo,
                open('product_not_found.PNG', 'rb'),
                set_caption(message=msg),
                msg
            )
            return False

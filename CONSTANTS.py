TOKEN = '8115143632:AAGaZJxxt4Wt6PGBeNAGjRsbKYh9WUwSCE4'
headers = {
    "Accept": "application/json; charset=utf-8",
    "Content-Type": "application/json; charset=utf-8",
    "Authorization": f"Bearer {TOKEN}"
}
base_url = 'https://basalam.com/'
product_ids_api_url = "https://search.basalam.com/ai-engine/api"
product_details_api_url = "https://core.basalam.com/api_v2/product/"
utm_data='?utm_source=telegram&utm_medium=bot&utm_campaign=jorbjor'
rows = '100'
payload = {
    "q": "عسل",  # عبارت جستجو به فارسی
    'rows': 15,  # تعداد نتایج مورد نظر
    "start": 0,  # شروع از نتیجه اول
    "filters": {
        "minPrice": 0,  # حداقل قیمت
        "maxPrice": 100000,  # حداکثر قیمت
        "minRating": 4,  # حداقل امتیاز
        "freeShipping": 0,  # ارسال رایگان (0 = خیر، 1 = بله)
        "sameCity": 0  # شهر مشابه (0 = خیر، 1 = بله)
    }
}
# start_message = '''
# باسلام!
# من بات جور به جور هستم. بیا باهم بازارگردی کنیم
#
# از صفحه کلید انتخاب کنید:
# بازارگردی با نام محصول
# بازارگردی با تصویر یا پست محصول
#
# در طول اجرای برنامه هر وقت خواستید نوع جستجو را تغییر دهید از این صفحه کلید استفاده کنید
#
# با /start هم میتونی به اول اجرا برگردی
#
# اینم از لینک باسلام
# https://basalam.com/
#
# بزن بریم!
# '''
start_message = '''
باسلام!
من بات جور به جور هستم. بیا باهم بازارگردی کنیم

از صفحه کلید انتخاب کنید:
بازارگردی با نام محصول
بازارگردی با تصویر یا پست محصول

در طول اجرای برنامه هر وقت خواستید نوع جستجو را تغییر دهید از این صفحه کلید استفاده کنید

با /start هم میتونی به اول اجرا برگردی

<a href="https://basalam.com/">🔗 باسلام؛ بازار بی مرز</a>

بزن بریم!
'''

# RESPONSE_FIELDS
id='id'
products = 'products'
product_link='product_link'
title = 'title'
price = 'price'
free_shipping_to_same_city = 'free_shipping_to_same_city'
free_shipping_to_iran = 'free_shipping_to_iran'
identifier = 'identifier'
photo = 'photo'
photos ='photos'
video = 'video'
videos = 'videos'
gallery = 'gallery'
city='city'
vendor='vendor'
vendor_link='vendor_link'

# TEXTS
search_by_text_btn_txt = 'بازارگردی با نام محصول'
search_by_image_btn_txt = 'بازارگردی با تصویر محصول'
enter_text_query_to_search = '''
عالیه،
حالا هر متنی رو که به من بدی عنوان محصول برات جستجو میکنم'''
enter_image_query_to_search = '''
عالیه، حالا تصویر محصول رو برام بفرست
 میتونی یه پست رو هم با من به اشتراک بذاری'''

wrong_text_query_to_search=f'''
نوع جستجو را که متنی انتخاب کرده بودی
حالا یا نام محصول مورد نظر را ارسال کنید

یا اگر میخواهید بر اساس تصویر جستجو کنید
از صفحه کلید نوع جستجو را به تصویری تغییر بدهید
'''
wrong_image_query_to_search=f'''
نوع جستجو را که تصویری انتخاب کرده بودی
حالا یا تصویر مورد نظر را ارسال کنید

یا اگر میخواهید بر اساس متن جستجو کنید
از صفحه کلید نوع جستجو را به متنی تغییر بدهید
'''
select_keyboard_options = 'لطفا یکی از گزینه های صفحه کلید را انتخاب کنید'
searching_query = 'صبر کن ای دل که صبر سیرت اهل صفاست ...'
new_query="جستجوی جدید"

text_search = 'text_search'
image_search = 'image_search'

# STATES
start_state = 'start_state'
search_type_selected = 'search_type_selected'
text_search_state = 'text_search_state'
image_search_state = 'image_search_state'
wait_for_text_query_state='wait_for_text_query_state'
wait_for_image_query_state='wait_for_image_query_state'
searching_text_state = 'searching_text_state'
searching_image_state = 'searching_image_state'
states = [start_state,
          text_search_state,
          image_search_state,
          wait_for_text_query_state,
          wait_for_image_query_state,
          searching_text_state,
          searching_image_state,
          ]

# BUTTON TEXTS AND CALLBACKS
# TEXTS
next_product_btn_text = 'محصول بعدی'
basalam_link_btn_text = 'باسلام؛ بازار بی مرز'

# CALLBACKS
next_product = 'next_product'
basalam_link = 'basalam_link'

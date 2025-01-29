TOKEN = '8115143632:AAGaZJxxt4Wt6PGBeNAGjRsbKYh9WUwSCE4'
headers = {
    "Accept": "application/json; charset=utf-8",
    "Content-Type": "application/json; charset=utf-8",
    "Authorization": f"Bearer {TOKEN}"
}
# basalam_api_url = "https://search.basalam.com/ai-engine/api/v2.0/product/search"
base_url = 'https://basalam.com/'
product_ids_api_url = "https://search.basalam.com/ai-engine/api"
product_details_api_url = "https://core.basalam.com/api_v2/product/"

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
start_message = '''
باسلام!
من بات جور به جور هستم. بیا باهم بازارگردی کنیم

از صفحه کلید انتخاب کنید:
بازارگردی با نام محصول
بازارگردی با تصویر یا پست محصول

در طول اجرای برنامه هر وقت خواستید نوع جستجو را تغییر دهید از این صفحه کلید استفاده کنید

با /start هم میتونی به اول اجرا برگردی

اینم از لینک باسلام
https://basalam.com/

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
search_by_image_btn_txt = 'بازارگردی با تصویر یا پست محصول'
enter_text_query_to_search = 'نام محصول را وارد کنید'
enter_image_query_to_search = 'تصویر یا پست محصول را ارسال کنید'
wrong_query_to_search = '''
مجددا نوع جستجو را وارد کردید
نام محصول را وارد کنید
درصورتی که میخواهید نوع جستجو را تغییر دهید از کیبورد اقدام کنید'''
select_keyboard_options = 'لطفا یکی از گزینه های صفحه کلید را انتخاب کنید'
searching_query = 'صبر کن ای دل که صبر سیرت اهل صفاست ...'


edit_text_query = 'عبارتی که جستجو کردی را اصلاح کنید'
text_search = 'text_search'
image_search = 'image_search'

# STATES
start_state = 'start_state'
search_type_selected = 'search_type_selected'
text_search_state = 'text_search_state'
image_search_state = 'image_search_state'
wait_for_text_query_state='wait_for_text_query_state'
wait_for_image_query_state='wait_for_image_query_state'
# enter_text_query_to_search_state = 'enter_text_query_to_search_state'
# enter_image_query_to_search_state = 'enter_image_query_to_search_state'
searching_text_state = 'searching_text_state'
searching_image_state = 'searching_image_state'
# response_received = 'response_received'
states = [start_state,
          text_search_state,
          image_search_state,
          wait_for_text_query_state,
          wait_for_image_query_state,
          searching_text_state,
          searching_image_state,
          # response_received
          ]

# BUTTON TEXTS AND CALLBACKS
# TEXTS
prev_product_btn_text = 'محصول قبلی'
next_product_btn_text = 'محصول بعدی'
prev_gallery_btn_text = 'گالری قبلی'
next_gallery_btn_text = 'گالری بعدی'
basalam_link_btn_text = 'لینک باسلام'

# CALLBACKS
prev_product = 'prev_product'
next_product = 'next_product'
prev_gallery_item = 'prev_gallery_item'
next_gallery_item = 'next_gallery_item'
nav_btns = (prev_product, next_product, prev_gallery_item, next_gallery_item)
basalam_link = 'basalam_link'

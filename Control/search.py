from dataclasses import dataclass
from typing import Dict, List

import httpx
from tenacity import retry, stop_after_attempt, wait_fixed

from CONSTANTS import base_url, product_ids_api_url, utm_data


@dataclass
class productFields:
    """کلاس نگهداری فیلدهای مورد نیاز محصول"""
    title: str
    price: int
    free_shipping_to_same_city: int
    free_shipping_to_iran: int
    city: str
    vendor_link: str
    product_link: str
    photo: str


class searchService:
    # base_url = "https://search.basalam.com/ai-engine/api"
    #
    headers = {
        "Accept": "application/json; charset=utf-8",
    }

    @classmethod
    @retry(reraise=True, retry=stop_after_attempt(10), wait=wait_fixed(10))
    def text_search_product_ids_api_url(cls, q: str):
        url = '{}{}'.format(product_ids_api_url, '/v2.0/product/search')
        params = {
            "q": q,
            "size": 50
        }

        with httpx.Client(http2=True) as client:
            response = client.get(url, params=params, timeout=10.0, headers=cls.headers)
            response.raise_for_status()

            if response.status_code == 200:
                json_response = response.json()
                print(f"JSON Response received: {bool(json_response)}")
                print(f"JSON Response received: {json_response}")
                return json_response

    @classmethod
    @retry(reraise=True, retry=stop_after_attempt(10), wait=wait_fixed(10))
    def image_search_product_ids_api_url(cls, file: bytes):
        url = '{}{}'.format(product_ids_api_url, '/v1.0/image/search')
        try:
            # تغییر نحوه ارسال فایل
            files = {
                'file': ('image.jpg', file, 'multipart/form-data')  # تغییر Content-Type
            }

            # حذف Content-Type از headers چون multipart/form-data خودش تنظیم میشه
            headers = {
                "Accept": "application/json"
            }

            print(f"Sending request to {url}")
            print(f"File size: {len(file)} bytes")

            with httpx.Client(http2=True) as client:
                response = client.post(
                    url,
                    files=files,
                    headers=headers,
                    timeout=10.0
                )

                print(f"Response status: {response.status_code}")
                print(f"Response text: {response.text[:200]}")

                response.raise_for_status()

                if response.status_code == 200:
                    json_response = response.json()
                    print(f"JSON Response received: {bool(json_response)}")
                    return json_response

        except httpx.RequestError as e:
            print(f"Request error occurred: {str(e)}")
            raise
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            raise

    @classmethod
    def fetch_result_product_ids(cls, response_data):
        """
        استخراج شناسه‌های محصولات از پاسخ API (برای هر دو حالت جستجوی متنی و تصویری)

        Args:
            response_data: پاسخ API که میتواند لیست یا دیکشنری باشد

        Returns:
            list: لیستی از شناسه‌های محصولات
        """
        print(f"Processing response data of type: {type(response_data)}")

        if not response_data:
            print("Warning: Empty response data")
            return []

        # استخراج محصولات از پاسخ API
        result_products = []

        if isinstance(response_data, dict):
            # برای جستجوی متنی - پاسخ به شکل دیکشنری است
            print("Processing dictionary response (text search)")
            if 'products' in response_data:
                result_products = response_data['products']
            elif 'items' in response_data:
                result_products = response_data['items']
        elif isinstance(response_data, list):
            # برای جستجوی تصویری - پاسخ به شکل لیست است
            print("Processing list response (image search)")
            result_products = response_data
        else:
            print(f"Error: Unexpected response type: {type(response_data)}")
            return []

        # استخراج شناسه‌ها
        product_ids = []
        for product in result_products:
            if not product:
                continue

            try:
                # برای دیکشنری‌های حاوی id
                if isinstance(product, dict):
                    product_id = product.get('id')
                    if product_id:
                        product_ids.append(product_id)
                # برای مواردی که خود محصول یک شناسه است
                elif isinstance(product, str):
                    product_ids.append(product)
            except Exception as e:
                print(f"Error processing product: {str(e)}")
                continue

        # گزارش نتیجه
        print(f"Successfully extracted {len(product_ids)} product IDs")
        return product_ids

    @classmethod
    @retry(reraise=True, retry=stop_after_attempt(10), wait=wait_fixed(10))
    def search_by_image(cls, file: bytes):
        url = '{}{}'.format(product_ids_api_url, '/v1.0/image/search')

        try:
            # تغییر نحوه ارسال فایل
            files = {
                'file': ('image.jpg', file, 'multipart/form-data')  # تغییر Content-Type
            }

            print(f"Sending request to {url}")
            print(f"File size: {len(file)} bytes")

            with httpx.Client(http2=True) as client:
                response = client.post(
                    url,
                    files=files,
                    headers=cls.headers,
                    timeout=10.0
                )

                print(f"Response status: {response.status_code}")
                print(f"Response text: {response.text[:200]}")

                response.raise_for_status()

                if response.status_code == 200:
                    json_response = response.json()
                    print(f"JSON Response received: {bool(json_response)}")
                    return json_response

        except httpx.RequestError as e:
            print(f"Request error occurred: {str(e)}")
            raise
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            raise

    @classmethod
    @retry(reraise=True, retry=stop_after_attempt(10), wait=wait_fixed(10))
    def get_product_details(cls, product_id: str) -> Dict:
        """
        Retrieves detailed information for a specific product using its ID.

        Args:
            product_id (str): The unique identifier of the product

        Returns:
            Dict: A dictionary containing the product's detailed information

        Raises:
            httpx.RequestError: If there's an error making the HTTP request
            httpx.HTTPStatusError: If the server returns an error status code
        """
        # Construct the API URL for product details
        url = f'https://core.basalam.com/api_v2/product/{product_id}'

        try:
            # Make the HTTP request using httpx
            with httpx.Client(http2=True) as client:
                response = client.get(
                    url,
                    headers=cls.headers,
                    timeout=10.0
                )

                # Raise an exception for bad status codes
                response.raise_for_status()

                if response.status_code == 200:
                    # Parse and return the JSON response
                    json_response = response.json()

                    # Process the response to extract relevant information
                    # ساخت دیکشنری گالری برای نگهداری عکس‌ها و ویدئو
                    gallery = []

                    # اضافه کردن ویدئو به گالری (اگر وجود داشته باشد)
                    # چون فقط یک ویدئو داریم، مستقیم به سراغ original می‌رویم
                    if json_response.get('video') and isinstance(json_response['video'], dict):
                        if 'original' in json_response['video']:
                            gallery.append(json_response['video']['original'])

                    photo_dict = json_response.get('photo')
                    if photo_dict and 'medium' in photo_dict:
                        gallery.append(photo_dict['medium'])

                    # اضافه کردن عکس‌ها به گالری
                    # photos یک لیست از دیکشنری‌هاست
                    if json_response.get('photos') and isinstance(json_response['photos'], list):
                        for photo_dict in json_response['photos']:
                            if isinstance(photo_dict, dict) and 'medium' in photo_dict:
                                gallery.append(photo_dict['medium'])

                                # ساخت دیکشنری نهایی محصول
                    processed_product = {
                        'title': json_response.get('title', 'نمیدونم!'),
                        'price': json_response.get('price', 'نمیدونم!'),
                        'free_shipping_to_same_city': json_response.get('free_shipping_to_same_city', 'نمیدونم!'),
                        'free_shipping_to_iran': json_response.get('free_shipping_to_iran', 'نمیدونم!'),
                        'city': json_response['vendor']['city'].get('title', 'نمیدونم!') if json_response.get(
                            'city') else 'نمیدونم!',
                        'vendor_link': f'<a href="{base_url}{json_response["vendor"]["identifier"]}{utm_data}">🔗 مشاهده غرفه</a>' if json_response.get(
                            'vendor') else 'نمیدونم!',
                        'product_link': f'<a href="{base_url}{json_response["vendor"]["identifier"]}/product/{json_response["id"]}{utm_data}">🔗 مشاهده محصول</a>' if json_response.get(
                            'vendor') and json_response.get('id') else 'نمیدونم!',
                        'gallery': gallery
                    }

                    return processed_product

        except httpx.RequestError as e:
            print(f"Request error occurred: {str(e)}")
            raise
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            raise

    @classmethod
    def fetch_text_result_product_ids(cls, response_data):
        print(f"Response data type: {type(response_data)}")
        print(f"Response data content: {response_data}")

        product_ids = []

        if not response_data:
            print("Response data is empty")
            return []

        # اگر response_data یک لیست باشد
        if isinstance(response_data, list):
            result_products = response_data
        # اگر response_data یک دیکشنری باشد
        elif isinstance(response_data, dict):
            if 'products' in response_data:
                result_products = response_data['products']
            elif 'items' in response_data:
                result_products = response_data['items']
            else:
                result_products = []
        else:
            print(f"Unexpected response_data type: {type(response_data)}")
            return []

        print(f"result_products type: {type(result_products)}")
        print(f"result_products content: {result_products}")

        # پردازش محصولات
        for product in result_products:
            if not product:
                continue

            try:
                if isinstance(product, dict) and 'id' in product:
                    product_ids.append(product['id'])
                elif isinstance(product, str):  # اگر خود محصول یک شناسه باشد
                    product_ids.append(product)
            except Exception as e:
                print(f"Error processing product: {e}")
                continue

        print(f"Found {len(product_ids)} product IDs")
        for ids in product_ids:
            print(f'Product ID: {ids}')
        print('*' * 50)

        return product_ids

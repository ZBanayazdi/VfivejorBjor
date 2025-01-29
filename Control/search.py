from dataclasses import dataclass
from typing import Dict, List

import httpx
import asyncio
from tenacity import retry, stop_after_attempt, wait_fixed

import CONSTANTS
from CONSTANTS import (products, id, title, price, free_shipping_to_same_city, free_shipping_to_iran,
                       identifier, base_url, video, photos, product_ids_api_url, city, vendor, vendor_link,
                       product_link,
                       product_details_api_url, photos)


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

    # @classmethod
    # @retry(reraise=True, retry=stop_after_attempt(10), wait=wait_fixed(10))
    # def search_by_image(cls, file: bytes):
    #     url = '{}{}'.format(cls.base_url, '/v1.0/image/search')
    #
    #     try:
    #         # تغییر نحوه ارسال فایل
    #         files = {
    #             'file': ('image.jpg', file, 'multipart/form-data')  # تغییر Content-Type
    #         }
    #
    #         # حذف Content-Type از headers چون multipart/form-data خودش تنظیم میشه
    #         headers = {
    #             "Accept": "application/json"
    #         }
    #
    #         print(f"Sending request to {url}")
    #         print(f"File size: {len(file)} bytes")
    #
    #         with httpx.Client(http2=True) as client:
    #             response = client.post(
    #                 url,
    #                 files=files,
    #                 headers=headers,
    #                 timeout=10.0
    #             )
    #
    #             print(f"Response status: {response.status_code}")
    #             print(f"Response text: {response.text[:200]}")
    #
    #             response.raise_for_status()
    #
    #             if response.status_code == 200:
    #                 json_response = response.json()
    #                 print(f"JSON Response received: {bool(json_response)}")
    #                 return json_response
    #
    #     except httpx.RequestError as e:
    #         print(f"Request error occurred: {str(e)}")
    #         raise
    #     except httpx.HTTPStatusError as e:
    #         print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
    #         raise
    #     except Exception as e:
    #         print(f"Unexpected error: {str(e)}")
    #         raise
    #
    # @classmethod
    # def filter_image_search_result(cls, response_data):
    #     product_cntr = 0
    #     result = {}
    #     for product in response_data:
    #         gallery_item_cntr = 0
    #         product_data = {name: product.get(name, None), price: product.get(price, None),
    #                         free_shipping: product[vendor].get(freeShippingToIran, None),
    #                         city: product[vendor][owner].get(city, None),
    #                         vendor_link: f"{base_url}{product[vendor][identifier]}"}
    #         product_data[gallery] = {}
    #         videos_dict = product.get(video, {})
    #
    #         if videos_dict:
    #             print(f'videos_dict:{videos_dict}')
    #             for key, value in videos_dict.items():
    #                 print(f'{key}:{value}')
    #
    #             primary_video = videos_dict.get('PRIMARY', '')
    #             print(f'primary_video:{primary_video}')
    #             product_data[gallery][f'gallery_item_{gallery_item_cntr}'] = primary_video
    #             gallery_item_cntr += 1
    #
    #         photos_dict = product.get(photo, {})
    #
    #         if photos_dict:
    #             print(f'photo_dict:{photos_dict}')
    #             for key, value in photos_dict.items():
    #                 print(f'{key}:{value}')
    #             small_photo = photos_dict.get('SMALL', '')
    #             print(f'small_photo:{small_photo}')
    #
    #             product_data[gallery][f'gallery_item_{gallery_item_cntr}'] = small_photo
    #             gallery_item_cntr += 1
    #
    #         result[f'product_{product_cntr}'] = product_data
    #         product_cntr += 1
    #     print(f'search_result:{result}')
    #     for key, value in result.items():
    #         print(f'{key}:{value}')
    #     print('*' * 50)
    #     return result

    @classmethod
    def fetch_text_result_product_ids(cls, response_data):
        print(f"Response data type: {type(response_data)}")
        print(f"Response data keys: {response_data.keys()}")
        print(f"Response data content: {response_data}")

        product_ids = []

        if not response_data:
            print("Response data is empty")
            return {}

        if 'products' in response_data:
            result_products = response_data['products']
        elif 'items' in response_data:
            result_products = response_data['items']
        else:
            result_products = response_data

        print(f"result_products type: {type(result_products)}")
        print(f"result_products content: {result_products}")

        if isinstance(result_products, dict):
            items = result_products.items()
        elif isinstance(result_products, list):
            items = enumerate(result_products)
        else:
            print(f"Unexpected result_products type: {type(result_products)}")
            return {}

        for _, product in items:
            if product is None:
                continue

            try:
                product_ids.append(product.get('id', None))
            except Exception as e:
                continue

        for ids in product_ids:
            print(f'{ids}')
        print('*' * 50)
        return product_ids

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
                        'title': json_response.get('title', None),
                        'price': json_response.get('price', None),
                        'free_shipping_to_same_city': json_response.get('free_shipping_to_same_city', None),
                        'free_shipping_to_iran': json_response.get('free_shipping_to_iran', None),
                        'city': json_response['vendor']['city'].get('title', None) if json_response.get(
                            'city') else None,
                        'vendor_link': f"{base_url}{json_response['vendor']['identifier']}" if json_response.get(
                            'vendor') else None,
                        'product_link': f"{base_url}{json_response['vendor']['identifier']}/product/{json_response['id']}" if json_response.get(
                            'vendor') and json_response.get('id') else None,
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

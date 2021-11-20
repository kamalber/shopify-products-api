import requests
from model import Product
import re
import time
import json
import datetime


keys = {}
with open("keys.json") as f:
    keys = json.load(f)

# shopify api credentials
api_key = keys['api_key']
password = keys['api_secret']
store = keys['store']


url = "https://"+api_key+":"+password + \
      "@"+store+".myshopify.com/admin/api/2021-04/products.json"

url_delete_all = url + "?fields=id&limit=250&since_id=6952463138999"

product_list_url = url+"?fields=id,variants&limit=200"

inventory_url = "https://"+api_key+":"+password + \
    "@"+store+".myshopify.com/admin/api/2021-04/inventory_items/"


product_list = []  # shopifyProducts to be filed from shopify getAllProducts


def getAllProducts():  # get all shopify products and save them into a json file
    print("Getting all shopify products ....")
    getProducts(product_list_url)
    with open('data.json', 'w') as f:
        json.dump(product_list, f)
    print("Shopify products List size : "+str(len(product_list)))


def getProducts(url):  # get shopify products
    global index
    index = index+1
    print("page : "+str(index))

    time.sleep(501/1000)
    headers = {"Accept": "application/json",
               "Content-Type": "application/json",
               "X-Shopify-Access-Token": password}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()
        products = data['products']

        for p in products:
            product_list.append(p)

        if "rel=\"next\"" in r.headers['Link']:
            next = ''
            urls = findUrlInString(r.headers['Link'])
            if len(urls) == 1:
                next = urls[0]
            else:
                next = urls[1]
            getProducts(next)

    except requests.exceptions.Timeout as e:
        print(e)
        time.sleep(2)
        getProducts(url)
    # Tell the user their URL was bad and try a different one
    except requests.exceptions.RequestException as e:
        # catastrophic error. bail.
        raise SystemExit(e)


def createProduct(product: Product):
    url = "https://"+api_key+":"+password + \
        "@"+store+".myshopify.com/admin/api/2021-04/products.json"
    pushProduct("create", url, product)


def updateProduct(product: Product, product_id):
    url = "https://"+api_key+":"+password + \
        "@"+store+".myshopify.com/admin/api/2021-04/products/" + \
        str(product_id)+".json"
    pushProduct("update", url, product)


def pushProduct(call, api_product, product: Product):
    time.sleep(520/1000)
    images = []

    if len(product.pictures) > 0:
        for img in product.pictures:
            images.append({'src': img})

    status = "active"

    payload = {
        "product": {
            "title": product.title,
            "body_html": product.description,
            "images": images,
            "product_type": product.category,
            "vendor": product.brandName,
            # "metafields_global_description_tag": product.description,
            "status": status,
            "variants": [

                {
                    "barcode": product.barcode,
                    "price": product.price,
                    "compare_at_price": product.compare_at_price,
                    "tracked": True,
                    # "inventory_item_id": 1,  # to be gotten by get inventory endpoint
                    "inventory_quantity": product.quantity,
                    "sku": product.sku,
                    "weight": product.weight,
                    "weight_unit": "lb"
                }
            ]
        }
    }

    headers = {"Accept": "application/json",
               "Content-Type": "application/json",
               "X-Shopify-Access-Token": password}

    try:
        r = ""
        if call == "create":
            r = requests.post(api_product, json=payload,
                              headers=headers, timeout=10)
        else:
            r = requests.put(api_product, json=payload,
                             headers=headers, timeout=10)
        data = r.json()
        if "errors" in data.keys():
            print(data, flush=True)
        if r.status_code == 201 or (call == "update" and r.status_code == 200):
            product_id = data['product']['id']
            inventory_id = data['product']['variants'][0]['inventory_item_id']

            created_string = " product with id : " + \
                str(product_id) + " : "+call+"d , SKU : "+product.sku

            print(created_string, flush=True)

            inventory_data = {
                "id": inventory_id,
                "cost": product.netPrice
            }

            if call == "update":
                inventory_data = getInventoryItem(inventory_id)
                if inventory_data is None:
                    inventory_data = {
                        "id": inventory_id,
                        "cost": product.netPrice
                    }
                    inventory_data['id'] = inventory_id
                inventory_data['cost'] = product.netPrice

            updateInventoryItem(inventory_data)

        return r.status_code
    except requests.exceptions.Timeout as e:
        print(e, flush=True)
        return None

    # Tell the user their URL was bad and try a different one
    except requests.exceptions.RequestException as e:
        # catastrophic error. bail.
        raise SystemExit(e)

# assing product with matched collection


def pushProductToCollection(product_id, collection_id):

    time.sleep(520/1000)
    url = "https://"+api_key+":"+password + \
        "@"+store+".myshopify.com/admin/api/2021-04/collects.json"

    payload = {
        "collect": {
            "product_id": product_id,
            "collection_id": collection_id
        }
    }

    headers = {"Accept": "application/json",
               "Content-Type": "application/json",
               "X-Shopify-Access-Token": password}
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=10)
        print(" pushed product to collect ")
        print(r.data())
        return r.status_code
    except requests.exceptions.Timeout as e:
        print(e, flush=True)
    # Tell the user their URL was bad and try a different one
    except requests.exceptions.RequestException as e:
        # catastrophic error. bail.
        raise SystemExit(e)


def createCustomCollection(title):

    time.sleep(520/1000)
    url = url = "https://"+api_key+":"+password + \
        "@"+store+".myshopify.com/admin/api/2021-04/custom_collections.json"

    payload = {
        "custom_collection": {
            "title": title
        }
    }

    headers = {"Accept": "application/json",
               "Content-Type": "application/json",
               "X-Shopify-Access-Token": password}

    try:
        r = requests.post(url, json=payload, headers=headers, timeout=10)
        data = r.json()
        if r.status_code == 201:
            return data['custom_collection']['id']
        else:
            return None
    except requests.exceptions.Timeout as e:
        print(e, flush=True)
    # Tell the user their URL was bad and try a different one
    except requests.exceptions.RequestException as e:
        # catastrophic error. bail.
        raise SystemExit(e)


# shopify products list , that contains all shopify products
# url
# product_list : an empty list of ShopifyProductDTO , that is passed as reference
index = 0


# get http url from  text


def findUrlInString(string):
    # findall() has been used
    # with valid conditions for urls in string
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex, string)
    return [x[0] for x in url]


def getInventoryItem(inventory_id):
    time.sleep(520/1000)
    url = inventory_url+str(inventory_id)+".json"
    headers = {"Accept": "application/json",
               "Content-Type": "application/json",
               "X-Shopify-Access-Token": password}

    try:
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()
        if r.status_code == 200:
            return data['inventory_item']
        else:
            return None
    except requests.exceptions.Timeout as e:
        print(e, flush=True)
    # Tell the user their URL was bad and try a different one
    except requests.exceptions.RequestException as e:
        # catastrophic error. bail.
        raise SystemExit(e)


def updateInventoryItem(inventory_data):
    time.sleep(520/1000)
    url = inventory_url+str(inventory_data['id'])+".json"

    payload = {
        "inventory_item": inventory_data
    }

    headers = {"Accept": "application/json",
               "Content-Type": "application/json",
               "X-Shopify-Access-Token": password}

    try:
        r = requests.put(url, json=payload, headers=headers, timeout=10)
        data = r.json()
        if r.status_code == 200:
            return data['inventory_item']['id']
        else:
            inventory_string = "Inventory not updated, inventory_id : " + \
                str(inventory_data['id'])
            print(inventory_string, flush=True)
            return None
    except requests.exceptions.Timeout as e:
        print(e, flush=True)
    # Tell the user their URL was bad and try a different one
    except requests.exceptions.RequestException as e:
        # catastrophic error. bail.
        raise SystemExit(e)


def getCurrentTime():
    date = datetime.datetime.now(datetime.timezone.utc)
    return date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

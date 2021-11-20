
from model import Product
import shopifyService as shopify_service


def new_product_test():
    p = Product()

    p.title = "product 1"
    p.brandName = "brand 1"
    p.title = "product title 1"
    p.category = "category 1"
    # pictures
    p.pictures.append(
        "https://cdn.pixabay.com/photo/2018/06/17/20/35/chain-3481377_960_720.jpg")
    # description
    p.description = '<h3>' + p.title + '</h3>' +\
        '<p>' + ' product description' + '</p>' + \
        '<h3 >Links & Downloads:</h3 >' +\
        '<p><ul>' + ' no links' +\
        '</ul></p>'
    p.price = 200
    p.cost = 80
    p.compare_at_price = 300
    p.quantity = 20
    p.weight = 20
    p.sku = 'sku-1'
    p.barcode = '1235547'
    return p


def create_product():
    shopify_product = new_product_test()
    shopify_service.createProduct(shopify_product)


def get_shopify_products():
    shopify_service.getAllProducts()


def update_shopify_product(product_id):
    shopify_product = new_product_test()
    shopify_service.updateProduct(shopify_product, product_id)


# testing the api for creating product
create_product()

# testing the api for getting all products
get_shopify_products()

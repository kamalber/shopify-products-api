import json


class Product:
    def __init__(self):
        self.id = 0
        self.productId = ''
        self.title = ''
        self.price = 0
        self.cost = 0
        self.netPrice = 0
        self.compare_at_price = 0
        self.quantity = 0
        self.description = ''
        self.status = ''
        self.pictures = []
        self.brandName = ''
        self.gallery = ''
        self.category = ''
        self.country = ''
        self.site = ''
        self.shipping = ''
        self.weight = 0
        self.category_id = 0
        self.sku = ''
        self.barcode = ''

    def __str__(self):
        return f"Id: {self.id}, title: {self.title}"


class ShopifyProductDTO:
    def __init__(self):
        self.id = 0
        self.sku = ''

    def __str__(self):
        return f"Id : {self.id}, sku : {self.sku}"


class ShopifyCategory:
    id = 0
    name = ''

    def __init__(self, id, name):
        self.id = id
        self.name = name


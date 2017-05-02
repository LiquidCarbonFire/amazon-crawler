import settings
from pymongo import MongoClient
from datetime import datetime
import pprint

client = MongoClient('mongodb://localhost:27017/')
db = client.amazon_products

class Product(object):
	def __init__(self, 
		dp_id, 
		title,
		price, 
		images, 
		shipping, 
		product_url, 
		bougth_together, 
		related_items, 
		also_bougth, 
		comparisions, 
		short_description,
		long_description,
		information,
		customer_questions,
		reviews_stars,
		reviews_counter,
		top_reviews):

		super(Product, self).__init__()
		self.dp_id = dp_id
		self.title = title
		self.price = price
		self.images = images
		self.shipping = shipping
		self.product_url = product_url
		self.bougth_together = bougth_together
		self.related_items = related_items
		self.also_bougth = also_bougth
		self.comparisions = comparisions
		self.short_description = short_description
		self.long_description = long_description
		self.information = information
		self.customer_questions = customer_questions
		self.reviews_stars = reviews_stars
		self.reviews_counter = reviews_counter
		self.top_reviews = top_reviews

	def save(self):
		posts = db.posts
		posts.update_one({'dp_id':self.dp_id}, 
			{'$set': {
			'title':self.title,
			'dp_id' : self.dp_id, 
			'title' : self.title,
			'price' : self.price, 
			'images' : self.images, 
			'shipping' : self.shipping, 
			'product_url' : self.product_url, 
			'bougth_together' : self.bougth_together, 
			'related_items' : self.related_items, 
			'also_bougth' : self.also_bougth, 
			'comparisions' : self.comparisions, 
			'short_description' : self.short_description,
			'long_description' : self.long_description,
			'information' : self.information,
			'customer_questions' : self.customer_questions,
			'reviews_stars' : self.reviews_stars,
			'reviews_counter' : self.reviews_counter,
			'top_reviews' : self.top_reviews,
			"created_date": datetime.now()
			}}, 
			upsert=True)

# for doc in db.posts.find():
# 	print(doc)

# p = Product(
#  	dp_id =  "test",
# 	title = "LG 5",
# 	price = "$345",
# 	images = "", 
# 	shipping = "", 
# 	product_url = "", 
# 	bougth_together = "", 
# 	related_items = "", 
# 	also_bougth = "", 
# 	comparisions = "", 
# 	short_description = "",
# 	long_description = "",
# 	information = "",
# 	customer_questions = "",
# 	reviews_stars = "",
# 	reviews_counter = "",
# 	top_reviews = "")

# p.save()
# # pprint.pprint(posts.find())
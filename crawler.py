import sys
from datetime import datetime

import eventlet
import redis

import settings
from models import Product
from helpers import make_request, log, format_url, enqueue_url, dequeue_url, flush_all
from extractors import get_title, get_url, get_price, get_primary_img

crawl_time = datetime.now()

pool = eventlet.GreenPool(settings.max_threads)
pile = eventlet.GreenPile(pool)


def begin_crawl():
    flush_all()
    out = open("nodes.txt", "a")
    # explode out all of our category `start_urls` into subcategories
    count = 0
    with open(settings.start_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue  # skip blank and commented out lines
            enqueue_url("https://www.amazon.com/b/?node=" + line + "&page=1")
            count += 1
        log("Found {} subcategories".format(count))
        return count
            # page, html = make_request(line)
            # count = 0

            # # .generic-subnav-flyout-link.generic-subnav-flyout-link-large-titles

            # subcategories = page.select("#nav-subnav > .nav-a")
            # subcategories.pop(0)
            # for subcategory in subcategories:
            #     link = subcategory["href"]
            #     subc_name = subcategory.get_text()
            #     out.write(subc_name + "::" + link + "\n")
            #     print(subc_name )
            #     if "deals" in subc_name.lower() or "best" in subc_name.lower():
            #         continue
            #     if not link:
            #         continue

            #     # check for more subcategories
            #     #blog style categories ex: https://www.amazon.com/Home-Audio-Electronics/b/ref=sd_allcat_hat?ie=UTF8&node=667846011
            #     page, html = make_request(link)
            #     blog_categories = page.select(".list-item__category-link")
            #     is_blog = False

            #     for blog_category in blog_categories:
            #         link = blog_category["href"]
            #         blog_name = blog_category.get_text()
            #         print("--" + blog_name )
            #         out.write("--" + blog_name + "::" + link + "\n")
                    
            #         page, html = make_request(link)
            #         blog_sub_categories = page.select(".categoryRefinementsSection > ul > li > a")
            #         main_sub_c = len(page.select("li.shoppingEngineExpand"))
            #         for _ in range(main_sub_c):
            #             blog_sub_categories.pop(0) 
            #         for blog_sub_category in blog_sub_categories:
            #             link = blog_sub_category["href"]
            #             blog_sub_name = blog_sub_category.get_text().replace("\n", "").split(" (")[0]
            #             print("----" + blog_sub_name)
            #             out.write("----" + blog_sub_name + "::" + link + "\n")
            #             is_blog = True
            #             count += 1
            #             enqueue_url(link)

            #         if not is_blog:
            #             count += 1
            #             enqueue_url(link)

            #     if not is_blog:
            #         count += 1
            #         enqueue_url(link)

            # log("Found {} subcategories on {}".format(count, line))
            
            # look for subcategory links on this page
            # subcategories = page.findAll("div", "bxc-grid__image")  # downward arrow graphics
            # subcategories.extend(page.findAll("li", "sub-categories__list__item"))  # carousel hover menu
            # sidebar = page.find("div", "browseBox")
            # if sidebar:
            #     subcategories.extend(sidebar.findAll("li"))  # left sidebar

            # for subcategory in subcategories:
            #     link = subcategory.find("a")
            #     if not link:
            #         continue
            #     link = link["href"]
            #     count += 1
            #     enqueue_url(link)

            # log("Found {} subcategories on {}".format(count, line))


def fetch_listing():

    global crawl_time
    out_0 = open("products-0.txt", "a")
    out_many = open("products-many.txt", "a")

    url = dequeue_url()
    if not url:
        log("WARNING: No URLs found in the queue. Retrying...")
        pile.spawn(fetch_listing)
        return

    page, html = make_request(url)
    if not page:
        return

    # print(url)
    items = page.find_all("li", class_="s-result-item")
    log("Found {} items on {}".format(len(items), url))

    if len(items) == 0:
        out_0.write(str(url) + "\n")
    else:
        out_many.write(str(url) + "\n")

        # input()

    # for item in items[:settings.max_details_per_listing]:
    #     try:
    #         out.write(item.get_text() + "\n")
    #     except:
    #         pass
        
    #     product_url = get_url(item)
    #     product_price = get_price(item)

    #     product = ProductRecord(
    #         title=product_title,
    #         product_url=format_url(product_url),
    #         listing_url=format_url(url),
    #         price=product_price,
    #         primary_img=product_image,
    #         crawl_time=crawl_time

    #     )
    #     product_id = product.save()
    #     # download_image(product_image, product_id)

    # # add next page to queue
    next_link = page.find("a", id="pagnNextLink")
    if next_link:
        log(" Found 'Next' link on {}: {}".format(url, next_link["href"]))
        page_number = int(url.split("&page=")[1]) + 1
        enqueue_url(url.split("&page=")[0] + "&page=" + str(page_number))
        pile.spawn(fetch_listing)


if __name__ == '__main__':

    if len(sys.argv) > 1 and sys.argv[1] == "start":
        log("Seeding the URL frontier with subcategory URLs")
        count = begin_crawl()  # put a bunch of subcategory URLs into the queue

    log("Beginning crawl at {}".format(crawl_time))
    [pile.spawn(fetch_listing) for _ in range(count)]
    pool.waitall()
  
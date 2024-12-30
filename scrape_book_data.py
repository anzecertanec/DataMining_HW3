from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import csv
import time

# Initialize the WebDriver
service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)

def scrape_books_to_scrape():
    base_url = "http://books.toscrape.com/catalogue/page-{}.html"
    # seting the link to the website we want to scrap
    page = 1
    books_data = []

    while True:
        driver.get(base_url.format(page))
        time.sleep(2)  # we wait till the website is loaded

        # Makes shour books are present
        books = driver.find_elements(By.CLASS_NAME, "product_pod")
        if not books:
            break

        for book in books:
            # Extracts the book name from the tite atribute so that it is not cut off
            title_element = book.find_element(By.TAG_NAME, "h3").find_element(By.TAG_NAME, "a")
            title = title_element.get_attribute("title")

            # Extracts a books properties (price, rating and avalibility)
            price = book.find_element(By.CLASS_NAME, "price_color").text
            availability = book.find_element(By.CLASS_NAME, "instock.availability").text.strip()
            rating_element = book.find_element(By.CLASS_NAME, "star-rating")
            rating = rating_element.get_attribute("class").split()[-1]

            # Checks the detalis page for the current book to obtain the catagory information
            book_link = book.find_element(By.TAG_NAME, "a").get_attribute("href")
            driver.get(book_link)
            category = driver.find_element(By.CSS_SELECTOR, ".breadcrumb li:nth-child(3) a").text
            driver.back()

            #adds the information about the current book into books_data
            books_data.append({
                "Title": title,
                "Price": price,
                "Availability": availability,
                "Rating": rating,
                "Category": category
            })

        page += 1

    return books_data

#Saves data in a csv format
def save_to_csv(data, filename="books_data2.csv"):
    keys = data[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

#excecutes the functions defined above
try:
    books_data = scrape_books_to_scrape()
    save_to_csv(books_data)
    print("Data scraped and saved to books_data.csv successfully!")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    driver.quit()

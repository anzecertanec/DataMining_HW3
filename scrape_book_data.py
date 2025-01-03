from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

import csv
import time

# Initialize the WebDriver
service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)

def scrape_books_to_scrape():
    base_url = "http://books.toscrape.com/catalogue/page-{}.html"
    page = 1
    books_data = []

    while True:
        driver.get(base_url.format(page))
        time.sleep(2)  # Wait for the website to load
        books = driver.find_elements(By.CLASS_NAME, "product_pod")
        if not books:
            break

        for book in books:
            # scrape the title
            title_element = book.find_element(By.TAG_NAME, "h3").find_element(By.TAG_NAME, "a")
            title = title_element.get_attribute("title")

            # Extract book properties (price, rating, and availability)
            price = book.find_element(By.CLASS_NAME, "price_color").text
            rating_element = book.find_element(By.CLASS_NAME, "star-rating")
            rating = rating_element.get_attribute("class").split()[-1]

            # Navigate to book details page to get the availability and category
            book_link = book.find_element(By.TAG_NAME, "a").get_attribute("href")
            driver.get(book_link)

            try:
                # Extract availability text
                availability_element = driver.find_element(By.CSS_SELECTOR, "p.instock.availability")
                availability = availability_element.text.strip()
            except Exception:
                availability = "Availability not found"

            # Extract category
            try:
                category = driver.find_element(By.CSS_SELECTOR, ".breadcrumb li:nth-child(3) a").text
            except Exception:
                category = "Category not found"

            driver.back()  # Go back to the list page

            # Add the current book's information to the list
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
def save_to_csv(data, filename="books_data.csv"):
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


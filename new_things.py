from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import csv
import time
import pandas as pd

# Initialize the WebDriver
service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)

def search_amazon_category(books):
    books_with_new_categories = []

    for _, book in books.iterrows():
        title = book['Title']

        # Google search query
        search_query = f"kindle amazon {title}"
        driver.get("https://www.google.com")
        time.sleep(2)  # Wait for the Google page to load

        # Perform search
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)  # Wait for search results to load

        # Click the first search result
        try:
            first_result = driver.find_element(By.CSS_SELECTOR, "h3")
            first_result.click()
            time.sleep(5)  # Wait for the page to load

            # Extract category from the Amazon Kindle page
            try:
                breadcrumb_elements = driver.find_elements(By.CSS_SELECTOR, "#wayfinding-breadcrumbs_feature_div ul li span.a-list-item a")
                categories = [element.text for element in breadcrumb_elements if element.text.strip()]
                category = " > ".join(categories)
            except Exception:
                category = "Category not found"

        except Exception:
            category = "No search result"

        # Append the book title and new category
        books_with_new_categories.append({
            "Title": title,
            "New Category": category
        })
        print(title)
        print(category)

    return books_with_new_categories

def save_to_csv(data, filename="books_with_new_categories.csv"):
    keys = data[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

# Load the books data from the CSV file
books_data = pd.read_csv("books_data.csv")

try:
    books_with_categories = search_amazon_category(books_data)
    save_to_csv(books_with_categories)
    print("Data saved to books_with_new_categories.csv successfully!")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    driver.quit()

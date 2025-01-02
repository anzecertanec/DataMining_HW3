from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd

# List of valid categories
valid_categories = [
    "Travel", "Mystery", "Historical Fiction", "Sequential Art", "Classics", "Philosophy", "Romance",
    "Womens Fiction", "Fiction", "Children's", "Religion", "Nonfiction", "Music", "Default",
    "Science Fiction", "Sports and Games", "Fantasy", "New Adult", "Young Adult", "Science", "Poetry",
    "Paranormal", "Art", "Psychology", "Autobiography", "Parenting", "Adult Fiction", "Humor",
    "Horror", "History", "Food and Drink", "Christian Fiction", "Business", "Biographies", "Thriller",
    "Contemporary", "Spirituality", "Academic", "Self-Help", "Historical", "Christian", "Suspense",
    "Short Stories", "Novels", "Health", "Politics", "Cultural", "Erotica", "Crime"
]

# Initialize the WebDriver
service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)

def scrape_books_to_scrape():
    base_url = "https://books.toscrape.com/catalogue/category/books/default_15/page-{}.html"
    page = 1
    books_data = []

    while True:
        driver.get(base_url.format(page))
        time.sleep(2)  # Wait for the page to load

        # Ensure books are present
        books = driver.find_elements(By.CLASS_NAME, "product_pod")
        if not books:
            break

        for book in books:
            title_element = book.find_element(By.TAG_NAME, "h3").find_element(By.TAG_NAME, "a")
            title = title_element.get_attribute("title")
            book_link = book.find_element(By.TAG_NAME, "a").get_attribute("href")
            driver.get(book_link)
            try:
                description = driver.find_element(By.CSS_SELECTOR, "#product_description ~ p").text
            except Exception:
                description = "No description available"
            price = driver.find_element(By.CLASS_NAME, "price_color").text
            availability = driver.find_element(By.CLASS_NAME, "instock.availability").text.strip()
            rating_element = driver.find_element(By.CLASS_NAME, "star-rating")
            rating = rating_element.get_attribute("class").split()[-1]
            category = "Default"

            books_data.append({
                "Title": title,
                "Price": price,
                "Availability": availability,
                "Rating": rating,
                "Category": category,
                "Description": description
            })
            driver.back()

        page += 1  # Move to the next page

    return books_data

def search_amazon_category(books):
    books_with_new_categories = []

    for _, book in books.iterrows():
        title = book['Title']

        # Google search query
        search_query = f"kindle amazon {title}"
        driver.get("https://www.google.com")
        time.sleep(4)  # Wait for the Google page to load

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

    return pd.DataFrame(books_with_new_categories)

def save_to_csv(data, filename):
    data.to_csv(filename, index=False, encoding="utf-8")

try:
    books_data_with_description = scrape_books_to_scrape()
    books_df = pd.DataFrame(books_data_with_description)
    save_to_csv(books_df, "Books_data_with_description.csv")
    print("Book descriptions scraped and saved successfully!")

    books_with_new_categories = search_amazon_category(books_df)
    books_with_new_categories['category_real'] = books_with_new_categories['New Category'].apply(
        lambda x: ', '.join([category for category in valid_categories if category in x])
    )
    save_to_csv(books_with_new_categories, "books_with_new_categories_finished.csv")
    print("Categories assigned and saved successfully!")

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    driver.quit()



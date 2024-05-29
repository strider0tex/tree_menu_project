from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import time

def get_element(driver, by, value, timeout=10):
    try:
        return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
    except TimeoutException:
        print(f"Timeout occurred while waiting for element by {by}: {value}")
    except NoSuchElementException:
        print(f"Element not found by {by}: {value}")
    return None

def get_elements(driver, by, value, timeout=10):
    try:
        return WebDriverWait(driver, timeout).until(EC.presence_of_all_elements_located((by, value)))
    except TimeoutException:
        print(f"Timeout occurred while waiting for elements by {by}: {value}")
    except NoSuchElementException:
        print(f"No elements found by {by}: {value}")
    return []

def handle_exceptions(driver, action):
    try:
        return action()
    except TimeoutException:
        print("Timeout occurred while waiting for element")
    except NoSuchElementException:
        print("Element not found")
    return None

def extract_reviews_from_current_page():
    reviews_elements = handle_exceptions(driver, lambda: get_elements(driver, By.CSS_SELECTOR, "div.review-item"))
    if reviews_elements:
        for review_element in reviews_elements:
            author_element = review_element.find_element(By.CSS_SELECTOR, "span.review-item-header__author")
            author = author_element.text.strip()

            pros = ""
            cons = ""
            comment = ""
            try:
                pros = review_element.find_element(By.XPATH, ".//p[text()='Достоинства']/following-sibling::div").text.strip()
            except NoSuchElementException:
                pros = "Не указаны"

            try:
                cons = review_element.find_element(By.XPATH, ".//p[text()='Недостатки']/following-sibling::div").text.strip()
            except NoSuchElementException:
                cons = "Не указаны"

            try:
                comment = review_element.find_element(By.XPATH, ".//p[text()='Комментарий']/following-sibling::div").text.strip()
            except NoSuchElementException:
                comment = "Отсутствует"

            print("Автор отзыва:", author)
            print("Достоинства:", pros)
            print("Недостатки:", cons)
            print("Комментарий:", comment)
            print("---")

    return bool(reviews_elements)

product_url = input("Введите ссылку на товар: ")

options = Options()
# options.add_argument("--headless")  #если открыть в фоновом режиме будет captha
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)

driver.get(product_url + '#?details_block=reviews')

try:
    product_image_element = handle_exceptions(driver, lambda: get_element(driver, By.CSS_SELECTOR,
                                                                          "div.gallery_swiper img.gallery__thumb-img",
                                                                          timeout=20))
    if product_image_element:
        product_image_url = product_image_element.get_attribute("src")
        print("Фото товара:", product_image_url)

    product_name_element = handle_exceptions(driver, lambda: get_element(driver, By.CSS_SELECTOR, "h1.pdp-header__title"))
    if product_name_element:
        product_name = product_name_element.text.strip()
        print("Название товара:", product_name)

    product_price_element = handle_exceptions(driver, lambda: get_element(driver, By.CSS_SELECTOR, "span.sales-block-offer-price__price-final"))
    if product_price_element:
        product_price = product_price_element.text.strip()
        print("Цена товара:", product_price)

    old_price_element = handle_exceptions(driver, lambda: get_element(driver, By.CSS_SELECTOR, "del.crossed-old-price-with-discount__crossed-old-price"))
    if old_price_element:
        old_price = old_price_element.text.strip()
        print("Зачеркнутая цена:", old_price)
    else:
        print("Зачеркнутая цена: отсутствует")

    rating_wrapper_element = handle_exceptions(driver, lambda: get_element(driver, By.CSS_SELECTOR,
                                                                           "div.reviews-rating__counts-wrapper"))
    if rating_wrapper_element:
        try:
            rating_element = rating_wrapper_element.find_element(By.CSS_SELECTOR,
                                                                 "span.reviews-rating__reviews-rating-count")
            product_rating = rating_element.text.strip()
        except NoSuchElementException:
            product_rating = "Рейтинг отсутствует"

        try:
            reviews_count_element = rating_wrapper_element.find_element(By.CSS_SELECTOR,
                                                                        "span.reviews-rating__reviews-count")
            reviews_count = reviews_count_element.text.strip()
        except NoSuchElementException:
            reviews_count = "Отзывов нет"

        print(f"Общий рейтинг и количество отзывов: {product_rating} {reviews_count}")
    else:
        print("Отзовы и рейтинг отсутствуют")

    while True:
        if not extract_reviews_from_current_page():
            print("Отзывы на текущей странице не найдены")
            break

        next_button = handle_exceptions(driver, lambda: get_element(driver, By.CSS_SELECTOR, "li.next a[rel='next']"))
        if next_button:
            next_button.click()
            print("Переход на следующую страницу")
            time.sleep(2)

        else:
            print("Следующая страница не найдена")
            break

except Exception as e:
    print("Ошибка:", e)

finally:
    driver.quit()


import json
import time
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def build_match_url(item):
    return f"https://www.fotmob.com/en-GB/matches/{item['team_slug']}/{item['match_id']}#{item['internal_id']}"

def get_review_info(driver, match_url):
    review_info = {
        "match_url": match_url,
        "review_url": "",
        "title": "",
        "content": ""
    }

    driver.get(match_url)
    time.sleep(3)

    try:
        review_element = WebDriverWait(driver, 8).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'ReviewArticlesComponent')]//a"))
        )
        review_url = review_element.get_attribute("href")
        review_info["review_url"] = review_url
    except Exception as e:
        print(f"[SKIP] No review link found for {match_url} – {e}")
        return review_info

    driver.get(review_url)
    time.sleep(2)

    try:
        try:
            title_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "h2"))
            )
        except:
            title_element = driver.find_element(By.TAG_NAME, "h1")
        review_info["title"] = title_element.text.strip()
    except Exception as e:
        print(f"[WARN] Could not find title for {review_url} – {e}")

    try:
        paragraphs = driver.find_elements(By.CSS_SELECTOR, "div[class*='ContentBodyWrapperCSS'] p")
        content = "\n".join([p.text.strip() for p in paragraphs if p.text.strip()])
        review_info["content"] = content
    except Exception as e:
        print(f"[WARN] Could not extract content for {review_url} – {e}")

    return review_info

def crawl_single_match_review(season, match_id):
    with open(f"match_links_{season}.json", "r", encoding="utf-8") as f:
        match_data = json.load(f)
    match = next((m for m in match_data if m["match_id"] == match_id), None)
    if not match:
        print(f"[ERROR] Match {match_id} not found in match_links_{season}.json")
        return None

    chromedriver_autoinstaller.install()
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--lang=en-GB")
    options.add_argument("--window-size=375,812")
    options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)
    try:
        match_url = build_match_url(match)
        review_info = get_review_info(driver, match_url)
        # _id를 match_id와 internal_id 조합으로 생성
        review_info["_id"] = f"{match['match_id']}_{match.get('internal_id')}"
        review_info["match_id"] = match["match_id"]
        review_info["internal_id"] = match.get("internal_id")
        print(f"Review crawling completed: {match['match_id']}")
        return review_info
    except Exception as e:
        print(f"[ERROR] Failed to crawl review from {match_id} – {e}")
        return None
    finally:
        driver.quit()






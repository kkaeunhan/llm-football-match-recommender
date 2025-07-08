import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def build_review_url(match_info):
    """
    match_info dict를 받아 URL 생성
    """
    return f"https://www.fotmob.com/en-GB/matches/{match_info['team_slug']}/{match_info['match_id']}#{match_info['internal_id']}"

def get_review_info(driver, match_url):
    """
    주어진 match_url에서 리뷰 정보 추출
    """
    review_info = {
        "match_url": match_url,
        "review_url": "",
        "title": "",
        "content": ""
    }

    print(f"Visiting match page: {match_url}")
    driver.get(match_url)
    time.sleep(3)  # JS 로딩 시간 고려

    try:
        # 리뷰 버튼 셀렉터 시도
        review_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'ReviewArticlesComponent')]//a"))
        )
        review_url = review_element.get_attribute("href")
        review_info["review_url"] = review_url
    except Exception as e:
        print(f"[SKIP] No review link found for {match_url} – {e}")
        return review_info

    # 리뷰 페이지 접속
    driver.get(review_url)
    time.sleep(2)

    try:
        # 제목 추출: h2 → 실패 시 h1
        try:
            title_element = WebDriverWait(driver, 8).until(
                EC.presence_of_element_located((By.TAG_NAME, "h2"))
            )
        except:
            title_element = driver.find_element(By.TAG_NAME, "h1")
        review_info["title"] = title_element.text.strip()
    except Exception as e:
        print(f"[WARN] Could not find title for {review_url} – {e}")

    try:
        # 본문 내용 추출
        paragraphs = driver.find_elements(By.CSS_SELECTOR, "div[class*='ContentBodyWrapperCSS'] p")
        content = "\n".join([p.text.strip() for p in paragraphs if p.text.strip()])
        review_info["content"] = content
    except Exception as e:
        print(f"[WARN] Could not extract content for {review_url} – {e}")

    return review_info

def crawl_single_match_review(season, match_info):
    """
    지정 경기의 리뷰 크롤링 후 dict 반환
    """
    chromedriver_autoinstaller.install()
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,800")
    options.add_argument("--lang=en-GB")
    options.add_argument("--headless")  # 디버깅 시 주석 처리
    driver = webdriver.Chrome(options=options)

    try:
        match_url = build_review_url(match_info)
        review_info = get_review_info(driver, match_url)
        review_info["_id"] = f"{match_info['match_id']}_{match_info.get('internal_id')}"
        review_info["match_id"] = match_info["match_id"]
        review_info["internal_id"] = match_info.get("internal_id")
        print(f"Review crawling completed: {match_info['match_id']} ({match_info.get('internal_id')})")
        return review_info
    except Exception as e:
        print(f"[ERROR] Failed to crawl review from {match_info['match_id']} ({match_info.get('internal_id')}) – {e}")
        return None
    finally:
        driver.quit()






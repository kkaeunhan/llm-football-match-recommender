import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller

def build_match_url(season, match_id, team_slug=None, internal_id=None):
    if team_slug and internal_id:
        return f"https://www.fotmob.com/en-GB/matches/{team_slug}/{match_id}#{internal_id}"
    else:
        return f"https://www.fotmob.com/en-GB/matches/{match_id}"

def fetch_match_data(url, match_id, internal_id):
    chromedriver_autoinstaller.install()
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--lang=en-GB")
    options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(3)

    # 팀 이름
    team_names = driver.find_elements(By.CSS_SELECTOR, "span[class*='TeamNameItself-TeamNameOnTabletUp']")
    home_team = team_names[0].text.strip() if len(team_names) >= 1 else ""
    away_team = team_names[1].text.strip() if len(team_names) >= 2 else ""

    # 팀 로고
    team_logos = driver.find_elements(By.XPATH, "//div[contains(@class, 'TeamIconWrapper')]//img")
    home_logo = team_logos[0].get_attribute("src") if len(team_logos) >= 1 else ""
    away_logo = team_logos[1].get_attribute("src") if len(team_logos) >= 2 else ""

    # 스코어
    try:
        score = driver.find_element(By.XPATH, "//span[contains(@class, 'MFHeaderStatusScore')]").text.strip()
    except:
        score = ""

    # 득점 이벤트
    goal_data = []
    try:
        event_container = driver.find_elements(By.CSS_SELECTOR, "div[class*='EventContainer']")[0]
        goal_items = event_container.find_elements(By.TAG_NAME, "li")
        for item in goal_items:
            spans = item.find_elements(By.TAG_NAME, "span")
            if len(spans) >= 2:
                scorer = spans[0].text.strip()
                time_str = spans[1].text.strip()
                if scorer and time_str:
                    goal_data.append((scorer, time_str))
    except Exception as e:
        pass

    # 경기 날짜
    try:
        date_elem = driver.find_element(By.CSS_SELECTOR, "div[class*='MatchDate'] time")
        match_date = date_elem.get_attribute("datetime")
        if not match_date:
            match_date = date_elem.text.strip()
    except:
        match_date = ""
    if not match_date:
        try:
            date_div = driver.find_element(By.CSS_SELECTOR, "div[class*='MatchDate']")
            match_date = date_div.text.strip()
        except:
            match_date = ""

    # 경기장
    try:
        venue = driver.find_element(By.CSS_SELECTOR, "a[class*='VenueCSS'] span").text.strip()
    except:
        venue = ""

    # 심판
    try:
        referee = driver.find_element(By.CSS_SELECTOR, "div[class*='RevereeCSS'] span").text.strip()
    except:
        referee = ""

    # 관중 수
    try:
        attendance = driver.find_element(By.CSS_SELECTOR, "div[class*='AttendanceCSS'] span").text.strip()
    except:
        attendance = ""

    driver.quit()

    # _id를 match_id와 internal_id 조합으로 생성
    return {
        "_id": f"{match_id}_{internal_id}",
        "match_id": match_id,
        "internal_id": internal_id,
        "url": url,
        "home_team": home_team,
        "away_team": away_team,
        "home_logo": home_logo,
        "away_logo": away_logo,
        "score": score,
        "goals": goal_data,
        "match_date": match_date,
        "venue": venue,
        "referee": referee,
        "attendance": attendance
    }

def crawl_single_match_basic(season, match_id):
    with open(f"match_links_{season}.json", "r", encoding="utf-8") as f:
        match_data = json.load(f)
    match_info = next((m for m in match_data if m["match_id"] == match_id), None)
    if not match_info:
        print(f"[ERROR] match_id {match_id} not found in match_links_{season}.json")
        return None

    url = build_match_url(
        season,
        match_id,
        team_slug=match_info.get("team_slug"),
        internal_id=match_info.get("internal_id")
    )
    return fetch_match_data(url, match_id, match_info.get("internal_id"))









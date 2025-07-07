import json
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def build_commentary_url(item):
    return f"https://www.fotmob.com/en-GB/matches/{item['team_slug']}/{item['match_id']}#{item['internal_id']}:tab=ticker"

def split_event(event_text):
    parts = event_text.strip().split("\n")
    if len(parts) >= 2:
        time_str = parts[0]
        if parts[1].startswith("+"):
            time_str += "\n" + parts[1]
            event_name = parts[2] if len(parts) > 2 else ""
        else:
            event_name = parts[1]
    else:
        time_str = parts[0]
        event_name = ""
    return time_str, event_name

def enable_key_events_only(driver):
    try:
        toggle_button = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[class*='Toggle']"))
        )
        aria_checked = toggle_button.get_attribute("aria-checked")
        if aria_checked == "false":
            toggle_button.click()
            time.sleep(1)
    except Exception as e:
        print(f"[WARN] Could not toggle Key Events: {e}")

def get_commentary(driver, match_url):
    commentary_data = {
        "match_url": match_url,
        "commentaries": []
    }
    try:
        driver.get(match_url)
        time.sleep(3)
        enable_key_events_only(driver)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='LiveTickerContent']"))
        )
        event_items = driver.find_elements(By.CSS_SELECTOR, "div[class*='LiveTickerItemCSS']")
        for event in event_items:
            try:
                try:
                    event_text_elem = event.find_element(By.CSS_SELECTOR, "h3[class*='LiveTickerEventHeaderCSS']")
                    event_text = event_text_elem.text.strip()
                    time_str, event_name = split_event(event_text)
                except:
                    time_str, event_name = "", ""
                try:
                    content_elem = event.find_element(By.CSS_SELECTOR, "div[class*='LiveTickerItemContent']")
                    content_text = content_elem.text.strip()
                except:
                    content_text = ""
                if time_str or event_name or content_text:
                    commentary_data["commentaries"].append({
                        "time": time_str,
                        "event": event_name,
                        "content": content_text
                    })
            except Exception as e:
                print(f"[WARN] Failed to parse event: {e}")
                continue
        try:
            summary_elem = driver.find_element(By.CSS_SELECTOR, "div[class*='LiveTickerTextEventContent']")
            summary_text = summary_elem.text.strip()
            if summary_text:
                commentary_data["commentaries"].insert(0, {
                    "time": "Summary",
                    "event": "Summary",
                    "content": summary_text
                })
        except:
            pass
    except Exception as e:
        print(f"[ERROR] Failed to get commentary from {match_url}: {e}")
    return commentary_data

def crawl_single_match_commentary(season, match_id):
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
    options.add_argument("--window-size=375,812")
    options.add_argument("--lang=en-GB")
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    try:
        commentary = get_commentary(driver, build_commentary_url(match))
        # _id를 match_id와 internal_id 조합으로 생성
        commentary["_id"] = f"{match['match_id']}_{match.get('internal_id')}"
        commentary["match_id"] = match["match_id"]
        commentary["internal_id"] = match.get("internal_id")
        print(f"Commentary crawling completed: {match['match_id']}")
        return commentary
    except Exception as e:
        print(f"[ERROR] Failed to crawl commentary for {match_id}: {e}")
        return None
    finally:
        driver.quit()













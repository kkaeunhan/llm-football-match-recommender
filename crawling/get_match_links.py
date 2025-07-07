import json
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple
import sys


def get_all_round_urls(season_str: str, max_round: int = 38) -> List[Tuple[int, str]]:
    base = f"https://www.fotmob.com/en-GB/leagues/47/matches/premier-league?season={season_str}&group=by-round"
    return [(i, f"{base}&round={i}") for i in range(max_round)]

def create_driver():
    chromedriver_autoinstaller.install()
    options = Options()
    options.add_argument("--window-size=375,812")
    options.add_argument("--disable-gpu")
    return webdriver.Chrome(options=options)

def extract_matches_from_round(args: Tuple[int, str], retry: int = 2) -> List[dict]:
    round_index, url = args
    for attempt in range(retry + 1):
        driver = create_driver()
        try:
            driver.get(url)
            try:
                WebDriverWait(driver, 12).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a[href^='/en-GB/matches/']"))
                )
            except Exception:
                print(f"[Round {round_index + 1}] Timeout waiting for matches to load (Attempt {attempt + 1})")
                driver.quit()
                continue

            soup = BeautifulSoup(driver.page_source, "html.parser")
            match_data = []
            seen = set()
            anchors = soup.select("a[href^='/en-GB/matches/']")

            for a in anchors:
                href = a.get("href")
                if not href or href in seen:
                    continue
                seen.add(href)

                try:
                    parts = href.split('/')
                    if len(parts) < 5:
                        continue
                    team_slug = parts[3]
                    match_id = parts[4].split('#')[0]
                    internal_id = parts[4].split('#')[1].split(":")[0] if '#' in parts[4] else None

                    match_data.append({
                        "round": round_index + 1,
                        "team_slug": team_slug,
                        "match_id": match_id,
                        "internal_id": internal_id
                    })
                except Exception:
                    continue

            print(f"[Round {round_index + 1}] {len(match_data)} matches")
            return match_data
        finally:
            driver.quit()

    print(f"[Round {round_index + 1}] Failed after {retry + 1} attempts")
    return []


def get_all_match_metadata(season_str: str) -> List[dict]:
    urls = get_all_round_urls(season_str)
    all_matches = []
    failed_rounds = []

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(extract_matches_from_round, u): u[0] for u in urls}
        for future in as_completed(futures):
            round_index = futures[future]
            try:
                result = future.result()
                if not result:
                    failed_rounds.append(round_index + 1)
                all_matches.extend(result)
            except Exception as e:
                print(f"[Round {round_index + 1}] Unexpected error: {e}")
                failed_rounds.append(round_index + 1)

    if failed_rounds:
        print("These rounds had 0 matches or failed:", sorted(failed_rounds))

    return all_matches


if __name__ == "__main__":
    season = sys.argv[1] if len(sys.argv) > 1 else "2024-2025"
    print(f"Fetching season: {season}")
    matches = get_all_match_metadata(season)

    print(f"Total matches collected: {len(matches)}")
    with open(f"match_links_{season}.json", "w", encoding="utf-8") as f:
        json.dump(matches, f, indent=2, ensure_ascii=False)
    print(f"Saved to match_links_{season}.json")







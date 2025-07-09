import json
from dotenv import load_dotenv
from match_basic_fetcher import crawl_single_match_basic
from match_commentary_fetcher import crawl_single_match_commentary
from match_review_fetcher import crawl_single_match_review
from save_to_mongo import save_to_mongo
from get_match_links import get_all_match_metadata

# 환경변수 로드
load_dotenv(dotenv_path="./env/.env")

SEASON_LIST = ["2019-2020", "2018-2019", "2017-2018", "2016-2017", "2015-2016"]
SEASONS_WITH_REVIEW = ["2024-2025", "2023-2024"]

def process_season(season):
    print(f"\n=== Processing season: {season} ===")
    try:
        with open(f"match_links_{season}.json", "r", encoding="utf-8") as f:
            match_data = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] match_links_{season}.json not found. Run get_match_links.py first.")
        return

    # 1. Basic 크롤링 및 저장
    all_basic_data = []
    for idx, match in enumerate(match_data, start=1):
        print(f"[{idx}/{len(match_data)}] Basic crawling: {match['match_id']} ({match.get('internal_id')})")
        basic = crawl_single_match_basic(season, match)
        if basic:
            all_basic_data.append(basic)
    save_to_mongo(season, all_basic_data, "basic")


if __name__ == "__main__":
    for season in SEASON_LIST:
        process_season(season)







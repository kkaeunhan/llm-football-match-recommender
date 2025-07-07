import json
from dotenv import load_dotenv
from match_basic_fetcher import crawl_single_match_basic
from match_commentary_fetcher import crawl_single_match_commentary
from match_review_fetcher import crawl_single_match_review
from save_to_mongo import save_to_mongo
from get_match_links import get_all_match_metadata

# 환경변수 로드
load_dotenv(dotenv_path="./env/.env")

SEASON_LIST = ["2024-2025"]
SEASONS_WITH_REVIEW = ["2024-2025", "2022-2023"]

def generate_match_links(season):
    print(f"=== Generating match_links for season: {season} ===")
    matches = get_all_match_metadata(season)
    with open(f"match_links_{season}.json", "w", encoding="utf-8") as f:
        json.dump(matches, f, indent=2, ensure_ascii=False)
    print(f"Saved to match_links_{season}.json")

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
        basic = crawl_single_match_basic(season, match['match_id'])
        if basic:
            all_basic_data.append(basic)
    save_to_mongo(season, all_basic_data, "match_basic")

    # 2. Commentary 크롤링 및 저장
    all_commentary_data = []
    for idx, match in enumerate(match_data, start=1):
        print(f"[{idx}/{len(match_data)}] Commentary crawling: {match['match_id']} ({match.get('internal_id')})")
        commentary = crawl_single_match_commentary(season, match['match_id'])
        if commentary:
            all_commentary_data.append(commentary)
    save_to_mongo(season, all_commentary_data, "match_commentary")

    # 3. Review 크롤링 및 저장 (리뷰 시즌만)
    if season in SEASONS_WITH_REVIEW:
        all_review_data = []
        for idx, match in enumerate(match_data, start=1):
            print(f"[{idx}/{len(match_data)}] Review crawling: {match['match_id']} ({match.get('internal_id')})")
            review = crawl_single_match_review(season, match['match_id'])
            if review:
                all_review_data.append(review)
        save_to_mongo(season, all_review_data, "match_review")

if __name__ == "__main__":
    for season in SEASON_LIST:
        generate_match_links(season)
        process_season(season)








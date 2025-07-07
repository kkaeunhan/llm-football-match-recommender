import os
from pymongo import MongoClient
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv(dotenv_path="./env/.env")

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "football_data"

def save_to_mongo(season, data_list, kind):
    """
    시즌별 하위 컬렉션(basic, commentary, review)에 데이터 저장
    - kind: 'basic', 'commentary', 'review'
    """
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    # 컬렉션명 예시: season_2024-2025.basic
    collection_name = f"season_{season}.{kind}"
    collection = db[collection_name]
    for doc in data_list:
        if doc and "_id" in doc:
            collection.update_one({"_id": doc["_id"]}, {"$set": doc}, upsert=True)
    client.close()
    print(f"[OK] Saved {len(data_list)} docs to {DB_NAME}.{collection_name}")








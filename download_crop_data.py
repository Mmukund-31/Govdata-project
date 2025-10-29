import requests
import pandas as pd

API_KEY = "579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b"
DATASET_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
LIMIT = 10


def fetch_crop_data():
    print("🚜 Fetching Crop Production data (sample, 10 rows)...")

    params = {
        "api-key": API_KEY,
        "format": "json",
        "limit": LIMIT
    }

    response = requests.get(DATASET_URL, params=params)

    print(f"HTTP Status: {response.status_code}")
    if response.status_code != 200:
        print("❌ Error:", response.text)
        return

    try:
        data = response.json()
    except Exception as e:
        print("❌ Failed to parse JSON response.")
        print("Raw response below:\n", response.text[:1000])
        return

    if "records" not in data:
        print("❌ No 'records' field in response.")
        return

    records = data["records"]
    df = pd.DataFrame(records)
    print(f"✅ Fetched {len(df)} rows.")
    df.to_csv("crop_production_sample.csv", index=False)
    print("💾 Saved as crop_production_sample.csv")


if __name__ == "__main__":
    fetch_crop_data()

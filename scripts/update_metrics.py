
import os, json, datetime, pathlib, requests
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Metric, Dimension, RunReportRequest
from google.oauth2 import service_account

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "static" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUT = DATA_DIR / "metrics.json"

def fetch_ga4(property_id: str, sa_json: str):
    creds_info = json.loads(sa_json)
    creds = service_account.Credentials.from_service_account_info(creds_info, scopes=['https://www.googleapis.com/auth/analytics.readonly'])
    client = BetaAnalyticsDataClient(credentials=creds)
    end = datetime.date.today()
    start = end - datetime.timedelta(days=29)
    req = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="date")],
        metrics=[Metric(name="totalUsers"), Metric(name="sessions"), Metric(name="screenPageViews")],
        date_ranges=[DateRange(start_date=str(start), end_date=str(end))],
    )
    resp = client.run_report(req)
    days, users, sessions, pageviews = [], [], [], []
    for row in resp.rows:
        d = row.dimension_values[0].value
        days.append(f"{d[:4]}-{d[4:6]}-{d[6:]}")
        users.append(int(row.metric_values[0].value))
        sessions.append(int(row.metric_values[1].value))
        pageviews.append(int(row.metric_values[2].value))
    return {
        "days": days,
        "users": users,
        "sessions": sessions,
        "pageviews": pageviews,
        "totals": {
            "users": sum(users),
            "sessions": sum(sessions),
            "pageviews": sum(pageviews)
        }
    }

def fetch_adsense(account_id: str, client_id: str, client_secret: str, refresh_token: str):
    # OAuth token
    tok = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }).json()
    access = tok.get("access_token")
    if not access:
        raise RuntimeError(f"OAuth error: {tok}")

    end = datetime.date.today()
    start = end - datetime.timedelta(days=29)
    url = f"https://adsense.googleapis.com/v2/{account_id}/reports:generate"
    payload = {
        "dateRange": {"startDate": {"year": start.year, "month": start.month, "day": start.day},
                      "endDate": {"year": end.year, "month": end.month, "day": end.day}},
        "metrics": ["ESTIMATED_EARNINGS"],
        "dimensions": ["DATE"],
        "currencyCode": "EUR"
    }
    r = requests.post(url, headers={"Authorization": f"Bearer {access}"}, json=payload)
    data = r.json()
    days, rev = [], []
    for row in data.get("rows", []):
        d = row["dimensionValues"][0]["value"]
        v = float(row["metricValues"][0]["value"])
        days.append(d)
        rev.append(v)
    # Normalize date format
    days = [f"{d[:4]}-{d[5:7]}-{d[8:10]}" if '-' in d else d for d in days]
    return {"days": days, "revenue": rev, "total_revenue": sum(rev), "currency": "EUR"}

def main():
    ga_json = os.environ.get("GA4_SERVICE_ACCOUNT_JSON", "")
    prop = os.environ.get("GA4_PROPERTY_ID", "")
    ga = {"days":[], "users":[], "sessions":[], "pageviews":[], "totals":{"users":0,"sessions":0,"pageviews":0}}
    if ga_json and prop:
        try:
            ga = fetch_ga4(prop, ga_json)
        except Exception as e:
            print("GA4 error:", e)

    ads = {"days":[], "revenue":[], "total_revenue":0.0, "currency":"EUR"}
    cid = os.environ.get("ADSENSE_CLIENT_ID","")
    cs = os.environ.get("ADSENSE_CLIENT_SECRET","")
    rtok = os.environ.get("ADSENSE_REFRESH_TOKEN","")
    acc = os.environ.get("ADSENSE_ACCOUNT_ID","")
    if cid and cs and rtok and acc:
        try:
            ads = fetch_adsense(acc, cid, cs, rtok)
        except Exception as e:
            print("AdSense error:", e)

    out = {
        "updated_at": datetime.datetime.utcnow().isoformat(timespec="seconds")+"Z",
        "ga4": ga,
        "adsense": ads
    }
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("Wrote", OUT)

if __name__ == "__main__":
    main()

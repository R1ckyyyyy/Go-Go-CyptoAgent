import requests
import json

PROXY = "http://127.0.0.1:7890"

proxies = {
    "http": PROXY,
    "https": PROXY,
}

def test_proxy():
    print(f"Testing Proxy: {PROXY}")
    
    # 1. Check IP
    try:
        print("\n[1] Checking IP via Proxy...")
        r = requests.get("http://ip-api.com/json", proxies=proxies, timeout=10)
        data = r.json()
        print(f"   IP: {data.get('query')}")
        print(f"   Country: {data.get('country')}")
        print(f"   Region: {data.get('regionName')}")
    except Exception as e:
        print(f"   ❌ Failed to check IP: {e}")

    # 2. Check Binance Connectivity
    try:
        print("\n[2] Checking Binance Connectivity...")
        url = "https://api.binance.com/api/v3/time"
        r = requests.get(url, proxies=proxies, timeout=10)
        print(f"   Status Code: {r.status_code}")
        if r.status_code == 200:
            print("   ✅ Connected to Binance successfully!")
            print(f"   Server Time: {r.json()['serverTime']}")
        else:
            print(f"   ❌ Failed with status: {r.status_code}")
            print(f"   Response: {r.text[:200]}")
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")

if __name__ == "__main__":
    test_proxy()

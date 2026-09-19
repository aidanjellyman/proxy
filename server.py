from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def get_rolimons_items():
    try:
        r = requests.get("https://www.rolimons.com/itemapi/itemdetails", headers=HEADERS, timeout=10)
        return r.json().get("items", {})
    except:
        return {}

def get_user_limiteds(user_id):
    limiteds = []
    cursor = ""
    for _ in range(10):  # max 10 pages
        url = f"https://inventory.roblox.com/v1/users/{user_id}/assets/collectibles?limit=100&cursor={cursor}"
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            data = r.json()
            limiteds += data.get("data", [])
            cursor = data.get("nextPageCursor") or ""
            if not cursor:
                break
        except:
            break
    return limiteds

@app.route("/stats")
def stats():
    user_id = request.args.get("userId")
    if not user_id:
        return jsonify({"error": "No userId provided"}), 400

    result = {}

    # Badges
    try:
        r = requests.get(f"https://badges.roblox.com/v1/users/{user_id}/badges?limit=100", headers=HEADERS, timeout=10)
        result["badgeCount"] = len(r.json().get("data", []))
    except:
        result["badgeCount"] = 0

    # Followers
    try:
        r = requests.get(f"https://friends.roblox.com/v1/users/{user_id}/followers/count", headers=HEADERS, timeout=10)
        result["followers"] = r.json().get("count", 0)
    except:
        result["followers"] = 0

    # Following
    try:
        r = requests.get(f"https://friends.roblox.com/v1/users/{user_id}/followings/count", headers=HEADERS, timeout=10)
        result["following"] = r.json().get("count", 0)
    except:
        result["following"] = 0

    # Created experiences
    try:
        r = requests.get(f"https://develop.roblox.com/v1/user/{user_id}/universes?limit=100", headers=HEADERS, timeout=10)
        games = r.json().get("data", [])
        result["createdExperiences"] = len(games)
        result["experienceVisits"] = sum(g.get("visits", 0) for g in games)
    except:
        result["createdExperiences"] = 0
        result["experienceVisits"] = 0

    # Net worth (limiteds via Rolimons)
    try:
        rolimons = get_rolimons_items()
        limiteds = get_user_limiteds(user_id)
        net_worth = 0
        for item in limiteds:
            asset_id = str(item.get("assetId", ""))
            if asset_id in rolimons:
                item_data = rolimons[asset_id]
                # Rolimons format: [name, acronym, rap, value, default_value, demand, trend, projected, hyped, rare]
                value = item_data[3]  # Rolimons value
                rap = item_data[2]    # RAP fallback
                net_worth += value if value > 0 else rap
        result["netWorth"] = net_worth
        result["limitedCount"] = len(limiteds)
    except:
        result["netWorth"] = 0
        result["limitedCount"] = 0

    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

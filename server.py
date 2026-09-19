from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

HEADERS = {"Accept": "application/json"}

@app.route("/stats")
def stats():
    user_id = request.args.get("userId")
    if not user_id:
        return jsonify({"error": "No userId provided"}), 400

    result = {}

    # Badges
    try:
        r = requests.get(f"https://badges.roblox.com/v1/users/{user_id}/badges?limit=100", headers=HEADERS)
        result["badges"] = r.json().get("data", [])
        result["badgeCount"] = len(result["badges"])
    except: result["badgeCount"] = 0

    # Followers
    try:
        r = requests.get(f"https://friends.roblox.com/v1/users/{user_id}/followers/count", headers=HEADERS)
        result["followers"] = r.json().get("count", 0)
    except: result["followers"] = 0

    # Following
    try:
        r = requests.get(f"https://friends.roblox.com/v1/users/{user_id}/followings/count", headers=HEADERS)
        result["following"] = r.json().get("count", 0)
    except: result["following"] = 0

    # Created experiences
    try:
        r = requests.get(f"https://develop.roblox.com/v1/user/{user_id}/universes?limit=100", headers=HEADERS)
        games = r.json().get("data", [])
        result["createdExperiences"] = len(games)
        result["experienceVisits"] = sum(g.get("visits", 0) for g in games)
    except:
        result["createdExperiences"] = 0
        result["experienceVisits"] = 0

    # Collectibles
    try:
        r = requests.get(f"https://inventory.roblox.com/v1/users/{user_id}/assets/collectibles?limit=100", headers=HEADERS)
        result["collectibles"] = len(r.json().get("data", []))
    except: result["collectibles"] = 0

    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

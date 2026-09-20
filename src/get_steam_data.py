import requests
import json
import os

API_KEY = os.environ["STEAM_API_KEY"]
STEAM_ID = '76561198040348887'

BASE_URL = "https://api.steampowered.com"


def get(endpoint, params):
    params["key"] = API_KEY
    r = requests.get(f"{BASE_URL}/{endpoint}", params=params)
    r.raise_for_status()
    return r.json()


def get_games(steam_id):
    data = get(
        "IPlayerService/GetOwnedGames/v1/",
        {
            "steamid": steam_id,
            "include_appinfo": True,
            "include_played_free_games": True,
        }
    )
    return data["response"].get("games", [])


def get_achievements(steam_id, app_id):
    return get(
        "ISteamUserStats/GetPlayerAchievements/v1/",
        {
            "steamid": steam_id,
            "appid": app_id,
        }
    )


def get_achievement_stats(steam_id, app_id):
    my_achievement_one = get_achievements(steam_id, app_id)
    achievements = my_achievement_one['playerstats']['achievements']
    total_achievements = len(achievements)
    achieved = sum([1 for i in achievements if i['achieved']])
    return achieved, total_achievements


# %%
my_games = get_games(STEAM_ID)

my_games_sorted = sorted(my_games, key=lambda x: x['playtime_forever'], reverse=True)

my_games_data = list()

for my_games_one in my_games_sorted:
    my_games_data_one = dict()

    name = my_games_one['name']
    app_id = my_games_one['appid']
    play_time_forever = my_games_one['playtime_forever']

    img_icon_url = (
        f"https://media.steampowered.com/"
        f"steamcommunity/public/images/apps/"
        f"{my_games_one['appid']}/{my_games_one['img_icon_url']}.jpg"
    )

    hours, minutes = divmod(play_time_forever, 60)

    # 先不统计成就，因为每个游戏都要发起一次网络请求，太慢了，并且容易报错
    # achieved, total_achievements = get_achievement_stats(STEAM_ID, app_id)

    my_games_data.append({
        "name": name,
        "appid": app_id,
        "play_time_forever": play_time_forever,
        "img_icon_url": img_icon_url,
        # "achieved": achieved,
        # "total_achievements": total_achievements,
        # "achieved_str": f"{achieved} / {total_achievements}",
        "playtime_forever_str": f"{hours} 小时 {minutes} 分钟"})

with open("steam_data.json", "w") as f:
    json.dump(my_games_data, f, ensure_ascii=False, indent=4)

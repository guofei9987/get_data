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


# %%获取成就需要每个游戏单独请求，为提高效率/减少报错，对于时长不变的不做更新
json_filename = "steam_data.json"


def get_steam_old_data(json_filename):
    # 上次保存在 json 中的数据
    steam_data_old = dict()
    try:
        with open(json_filename, "r") as f:
            steam_data_json = json.load(f)
            for game_one_old in steam_data_json:
                steam_data_old[game_one_old['name']] = game_one_old
    except FileNotFoundError:
        steam_data_old = {}
    return steam_data_old


steam_data_old = get_steam_old_data(json_filename)

# %%

my_games = get_games(STEAM_ID)

my_games_sorted = sorted(my_games, key=lambda x: x['playtime_forever'], reverse=True)

my_games_data = list()

max_achieve_gets = 5
cnt_achieve_gets = 0

for my_games_one in my_games_sorted:
    my_games_data_one = dict()

    name = my_games_one['name']
    app_id = my_games_one['appid']
    play_time_forever = my_games_one['playtime_forever']

    # 不统计少于 60分钟的游戏
    if play_time_forever < 600:
        pass

    img_icon_url = (
        f"https://media.steampowered.com/"
        f"steamcommunity/public/images/apps/"
        f"{my_games_one['appid']}/{my_games_one['img_icon_url']}.jpg"
    )

    hours, minutes = divmod(play_time_forever, 60)

    # 先不统计成就，因为每个游戏都要发起一次网络请求，太慢了，并且容易报错
    # achieved, total_achievements = get_achievement_stats(STEAM_ID, app_id)

    # 只统计时长有变动游戏的【成就】
    if name not in steam_data_old \
            or 'achieved' not in steam_data_old[name] \
            or play_time_forever != steam_data_old[name]['playtime_forever'] \
            or cnt_achieve_gets < max_achieve_gets:
        achieved, total_achievements = get_achievement_stats(STEAM_ID, app_id)
        cnt_achieve_gets += 1
        print(cnt_achieve_gets)
    else:
        achieved, total_achievements = steam_data_old[name]['achieved'], steam_data_old[name]['total_achievements']

    my_games_data.append({
        "name": name,
        "appid": app_id,
        "play_time_forever": play_time_forever,
        "img_icon_url": img_icon_url,
        "achieved": achieved,
        "total_achievements": total_achievements,
        "achieved_str": f"{achieved} / {total_achievements}",
        "playtime_forever_str": f"{hours} 小时 {minutes} 分钟"})

with open(json_filename, "w") as f:
    json.dump(my_games_data, f, ensure_ascii=False, indent=4)

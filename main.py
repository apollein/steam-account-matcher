import os
from steam_web_api import Steam
import time
from scipy.stats import entropy
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()
f = open("{}/tests_steam.html".format(os.getcwd()), "r")
home_content = f.read()
f.close()

def print_genres(genres):
	out = []
	for genre in genres:
		out.append(genre['description'])
	return out

def check_hash(hash):
	try:
		num = int(hash)
		return num < 2147483647
	except:
		return False

@app.get('/', response_class=HTMLResponse)
def home():
	return home_content

@app.get('/meow/{user1}/{user2}/{hash}')
def get_score(user1: str, user2: str, hash: str):
	if not check_hash(hash):
		return {}
	steam = Steam("YOUR_API_KEY")
	output = {'hash': hash}
	users = [user1, user2]
	divs = {}
	for _user in users:
		try:
			user = steam.users.search_user(_user)
			steamid = user['player']['steamid']
			user = user['player']['personaname']
		except Exception as e:
			steamid = _user
			user = steam.users.get_user_details(steamid)['player']['personaname']
		output[_user] = {'username': user}
		games = steam.users.get_owned_games(steamid)
		genres_ranking = {}
		genres_total = 0
		divs[_user]=[]
		for game in games['games']:
			appid = game['appid']
			game_details = steam.apps.get_app_details(appid, filters="genres")
			if 'data' in game_details[str(appid)]:
				genres = print_genres(game_details[str(appid)]['data']['genres'])
				for genre in genres:
					if genre not in genres_ranking:
						genres_ranking[genre]=0
					genres_ranking[genre]+=1
					genres_total+=1
		for genre in genres_ranking:
			divs[_user].append((genres_ranking[genre]/genres_total)*100.0)
		sorted_genres_ranking={k: v for k, v in sorted(genres_ranking.items(), key=lambda item: item[1], reverse=True)}
		output[_user]['metadata'] = []
		for genre in sorted_genres_ranking:
			output[_user]['metadata'].append({"genre": genre, "percentage": (genres_ranking[genre]/genres_total)*100.0})

	ent0 = entropy(divs[users[0]])
	ent1 = entropy(divs[users[1]])
	output[users[0]]["entropy"] = entropy(divs[users[0]])
	output[users[1]]["entropy"] = entropy(divs[users[1]])
	output["score"] = format(abs(abs(ent0-ent1)-1), ".4f")
	return output

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import random
import re
from flask import Flask, request, jsonify
from cachetools import LRUCache, TTLCache
from flask_cors import CORS

# proxies = {
#   "http": "http://your_proxy_url",
#   "https": "https://your_proxy_url"
# }

MAX_CACHE_SIZE = 100 # items
CACHE_TTL = 10800 # 3 hours (seconds)

BASE_URL = 'https://www.anitube.vip'
# LATEST_RELEASE = 'categoria/lancamentos'
# TITLE_EPISODE_PATTERN = r"^(.+) – Episódio (\d+)$" anitube.biz
TITLE_EPISODE_PATTERN = r"^(.+) -*.* ep (\d+)$"
# EPISODE_ID_PATTERN = r"https:\/\/www\.anitube\.biz\/(\d+)" anitube.biz
EPISODE_ID_PATTERN = r"^.+\/(\d+)$"


app = Flask(__name__)

cache = TTLCache(MAX_CACHE_SIZE, CACHE_TTL)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

def get_random_user_agent():
  user_agent = UserAgent()
  return user_agent.random

def make_request(url, referer=None):
  user_agent = get_random_user_agent()
  headers = {'User-Agent': user_agent}

  if referer:
    headers['Referer'] = referer

  try:
    # response = requests.get(url, headers=headers, proxies=proxies)
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    return soup

  except requests.exceptions.RequestException as e:
    print(f"Erro na solicitação: {e}")
    return None

def get_recent_episodes(page = 1):
  result = {}
  anime_list = []
  title = None
  episode = None
  image = None
  episodeId = None
  url = None

  urlPath = "{0}/?page={1}".format(BASE_URL, page)

  soup = make_request(urlPath)

  if soup:
    print(soup.title.text)

    soup_anime_list = soup.find("div", class_="mContainer_content").find_all("div", class_="epi_loop_item")

    for anime in soup_anime_list:
      title_text = anime.a["title"]
      extract_title_ep = re.match(TITLE_EPISODE_PATTERN, title_text)
      
      if extract_title_ep:
        title = extract_title_ep.group(1)
        episode = extract_title_ep.group(2)
      else:
        title = title_text

      url = anime.a["href"]
      episodeId = re.match(EPISODE_ID_PATTERN, url).group(1)
      image = anime.a.div.img["src"]

      anime_obj = {
        "title": title,
        "image": image,
        "episode": episode,
        "episodeID": episodeId,
        "url": url
      }

      anime_list.append(anime_obj)
      
    pagination = soup.find("div", class_="pagination")
    hasNextPage = pagination.find("a", class_="page-numbers current").findNext("a").text.strip().isnumeric()

    result = {
      "currentPage": page,
      "hasNextPage": hasNextPage,
      "hasPreviousPage": page > 1,
      "results": anime_list
    }

  return result

def search_anime(anime_name):
  if anime_name == "":
    return {"message": "You must enter a valid anime name"}
  
  url_path = "{0}/busca.php?s={1}&submit=Buscar".format(BASE_URL, anime_name)
  
  soup = make_request(url_path)
  
  if soup:
    soup_anime_list = soup.find("div", class_="lista_de_animes").find_all("div", class_="ani_loop_item")
    anime_list = []
    
    for anime in soup_anime_list:
      title = anime.find("div", class_="ani_loop_item_infos").find("a", class_="ani_loop_item_infos_nome").text
      image = anime.find("div", class_="ani_loop_item_img").a.img["src"]
      url = anime.find("div", class_="ani_loop_item_infos").find("a", class_="ani_loop_item_infos_nome")["href"]
      
      anime_obj = {
        "title": title,
        "image": image,
        "url": url
      }
      
      anime_list.append(anime_obj)
    
    result = {
      "currentPage": 1,
      "hasNextPage": False,
      "hasPreviousPage": False,
      "results": anime_list
    }
  
  return result


@app.route('/latest', methods=['GET'])
def recent_episodes():
  page = int(request.args.get('page', 1))
  page_length = int(24)

  start = (page - 1) * page_length
  end = start + page_length

  cache_key = f'latest_page_{page}'

  if cache_key in cache:
    latest = cache[cache_key]
  else:
    latest = get_recent_episodes(page)
    if latest:
      cache[cache_key] = latest

  return jsonify(latest)


@app.route('/search', methods=['GET'])
def search():
  name = request.args.get('name')
  cache_key = name
  
  if cache_key in cache:
    response = cache[cache_key]
  else:
    response = search_anime(name)
    if response:
        cache[cache_key] = response
  
  return jsonify(response)
    if response:
        cache[cache_key] = response
  
  return jsonify(response)

if __name__ == '__main__':
  app.run(debug=True, port=4000)

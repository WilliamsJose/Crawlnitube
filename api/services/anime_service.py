from time import sleep
import requests
from bs4 import BeautifulSoup
import re
from fake_useragent import UserAgent
from flask import current_app
from api.utils.cache_tools import has_cached, save_in_cache

def get_random_user_agent():
  user_agent = UserAgent()
  return user_agent.random

def make_request(url, referer=None):
  user_agent = get_random_user_agent()
  headers = {'User-Agent': user_agent}

  if referer:
    headers['Referer'] = referer

  try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    return soup

  except requests.exceptions.RequestException as e:
    print(f"Request Error: {e}")
    return None

def get_recent_episodes(page=1):
  cache_key = f"latest_{page}"
  
  cache = has_cached(cache_key)
  if cache != None:
    return cache
  
  result = {}
  anime_list = []
  title = None
  episode = None
  image = None
  episodeId = None
  url = None
  BASE_URL = current_app.config['BASE_URL']
  EPISODE_ID_PATTERN = current_app.config['EPISODE_ID_PATTERN']
  TITLE_EPISODE_PATTERN = current_app.config['TITLE_EPISODE_PATTERN']

  urlPath = f"{BASE_URL}/?page={page}"

  soup = make_request(urlPath)

  if soup:
    print(soup.title.text)

    soup_anime_list = soup.find("div", class_="mContainer_content").find_all("div", class_="epi_loop_item")

    for anime in soup_anime_list:
      title_text = anime.a["title"]
      extract_title_ep = re.match(TITLE_EPISODE_PATTERN, title_text.lower())
      
      if extract_title_ep:
        title = extract_title_ep.group(1).replace("-", "").strip()
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

  save_in_cache(cache_key, result)
  return result

def search_anime(anime_name):
  if anime_name == "":
    return {"message": "You must enter a valid anime name"}
  
  cache_key = f"search_{anime_name}"
  
  cache = has_cached(cache_key)
  if cache != None:
    return cache
  
  BASE_URL = current_app.config['BASE_URL']
  
  url_path = f"{BASE_URL}/busca.php?s={anime_name}&submit=Buscar"
  
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
  
  save_in_cache(cache_key, result)
  return result

def stream_episode_by_id(id, quality = "appfullhd"):
  if id:
    url = f"https://ikaros.anicdn.net/{quality}/{id}.mp4"
    referer_url = f"https://www.anitube.vip/playerricas.php?&img=https://www.anitube.vip/media/videos/tmb/{id}/default.jpg&url=https://ikaros.anicdn.net/{quality}/{id}.mp4"
    
    headers = {
      "Referer": referer_url
    }
    
    soup = requests.get(url, headers=headers)
    if soup:
      print(soup.status_code)
      return soup.content
  return None

def find_anime_info(anime_or_video_id):
  
  cache_key = f"info_{anime_or_video_id}"
  
  cache = has_cached(cache_key)
  if cache != None:
    return cache
  
  should_continue = False
  BASE_URL = current_app.config['BASE_URL']

  if anime_or_video_id.strip().isnumeric():
    soup = make_request(f"{BASE_URL}/video/{anime_or_video_id}")
    if soup:
      url = soup.find("i", class_="spr listaEP").find_parent("a", class_="ep_control")["href"]
      anime_info_url = f"{BASE_URL}{url}"
      sleep(0.2)
      soup = make_request(anime_info_url)
      if soup:
        should_continue = True
  else:
    soup = make_request(f"{BASE_URL}/anime/{anime_or_video_id}")
    if soup:
      should_continue = True
    
  if should_continue:
    anime_object = {}
    anime_object["title"] = soup.find("div", class_="anime_container_titulo").text
    anime_infos = soup.find("div", class_="anime_infos").find_all("div", class_="anime_info")
    for info in anime_infos:
      links = info.find_all("a")
      if len(links) > 0:
        txt_aux = ""
        for link in links:
          txt_aux += "{0} ".format(link.get_text())
          
        anime_object[info.b.text.replace(":", "")] = txt_aux.strip()
      else:
        anime_object[info.b.text.replace(":", "")] = info.b.next_sibling.text.strip()
  
    save_in_cache(cache_key, anime_object)
    return anime_object
  else:
    return None
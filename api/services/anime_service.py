from time import sleep
import requests
from bs4 import BeautifulSoup
import re
from fake_useragent import UserAgent
from flask import current_app
from api.utils.cache_tools import has_cached, save_in_cache
from api.utils.time_tools import time_to_minutes
from api.utils.logger import log_error
from api.utils.string_tools import normalize_string
from api.utils.season_mapper import map_season

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
    log_error(f"Could not request url: {url}", e)
    return None

def get_recent_episodes(page=1):
  cache_key = f"latest_{page}"
  
  cache = has_cached(cache_key)
  if cache != None:
    return cache
  
  result = {}
  BASE_URL = current_app.config['BASE_URL']

  urlPath = f"{BASE_URL}/?page={page}"

  soup = make_request(urlPath)

  if soup:
    try:
      soup_anime_list = soup.find("div", class_="mContainer_content").find_all("div", class_="epi_loop_item")

      episodes = extract_episodes(soup_anime_list, "epi_loop_img_time")
        
      pagination = soup.find("div", class_="pagination")
      hasNextPage = pagination.find("a", class_="page-numbers current").findNext("a").text.strip().isnumeric()

      result["currentPage"] = page
      result["hasNextPage"] = hasNextPage
      result["results"] = episodes
      
      save_in_cache(cache_key, result)
    except Exception as e:
      log_error("An error occurred while scrapping", e)
      return {"status": 404}

  return result

def extract_episodes(soup_anime_list, time_class):
  anime_list = []
  EPISODE_ID_PATTERN = current_app.config['EPISODE_ID_PATTERN']
  EPISODE_ID_PRINCIPAL_PATTERN = current_app.config['EPISODE_ID_PRINCIPAL_PATTERN']
  TITLE_EPISODE_PATTERN = current_app.config['TITLE_EPISODE_PATTERN']
  for anime in soup_anime_list:
    title_text = anime.a["title"]
    extract_title_ep = re.match(TITLE_EPISODE_PATTERN, title_text.lower())
      
    if extract_title_ep:
      title = extract_title_ep.group(1).replace("-", "").strip()
    else:
      title = title_text

    url = anime.a["href"]
    imageSrc = anime.a.div.img["src"]
    episodeID = re.match(EPISODE_ID_PRINCIPAL_PATTERN, imageSrc).group(1)
    episodeIDSecond = re.match(EPISODE_ID_PATTERN, url).group(1)
    timeStr = anime.a.div.find("div", class_=time_class).text
    minutes = time_to_minutes(timeStr)
    episode = str(anime.a.div.next_sibling.next_sibling.div.next_sibling.next_sibling.text)[3:].strip()
    isSeries = episode is not None
    
    if episodeID is None:
      episodeID = episodeIDSecond

    videoRef = f"/anime/stream?id={episodeID}"
    
    anime_obj = {
      "title": title,
      "image": imageSrc,
      "episode": episode,
      "episodeID": episodeID,
      "isSeries": isSeries,
      "time": minutes,
      "url": videoRef
    }

    anime_list.append(anime_obj)
  return anime_list

def search_anime(anime_name):
  if anime_name == "":
    return {"message": "You must enter a valid anime name"}
  
  cache_key = f"search_{anime_name}"
  
  cache = has_cached(cache_key)
  if cache != None:
    return cache
  
  BASE_URL = current_app.config['BASE_URL']
  ID_FROM_URL = current_app.config['ID_FROM_URL']
  result = {"status": 404}
  
  url_path = f"{BASE_URL}/busca.php?s={anime_name}&submit=Buscar"
  
  soup = make_request(url_path)
  
  if soup:
    try:
      soup_anime_list = soup.find("div", class_="lista_de_animes").find_all("div", class_="ani_loop_item")
      anime_list = []
      
      for anime in soup_anime_list:
        title = anime.find("div", class_="ani_loop_item_infos").find("a", class_="ani_loop_item_infos_nome").text
        image = anime.find("div", class_="ani_loop_item_img").a.img["src"]
        url = anime.find("div", class_="ani_loop_item_infos").find("a", class_="ani_loop_item_infos_nome")["href"]
        anime_id = re.match(ID_FROM_URL, url).group(1)
        
        anime_obj = {
          "title": title,
          "id": anime_id,
          "image": image,
          "url": url #mudar para url da api
        }
        
        anime_list.append(anime_obj)
      
      result = {
        "currentPage": 1,
        "hasNextPage": False,
        "results": anime_list
      }
    
      save_in_cache(cache_key, result)
    except Exception as e:
      log_error("An error occurred while scrapping", e)
  return result

def stream_episode_by_id(id, quality = "appfullhd", chunk_size=1024):
  if id:
    attempt = 1
    while(True):
      url = f"https://cdn8.anicdn.net/{quality}/{id}.mp4"
      # referer_url = f"https://www.anitube.vip/playerricas.php?&img=https://www.anitube.vip/media/videos/tmb/{id}/default.jpg&url=https://cdn8.anicdn.net/{quality}/{id}.mp4"
      referer_url = f"https://www.anitube.vip/"
      
      headers = {
        "Referer": referer_url,
        "wmsAuthSign": "c2VydmVyX3RpbWU9MS8yMS8yMDI1IDk6MTc6MzkgUE0maGFzaF92YWx1ZT1VR3NDMDhTdldycHBXMXFmdTlTd3lRPT0mdmFsaWRtaW51dGVzPTEwODAwJnN0cm1fbGVuPTA="
      }
    
      try:
        # tentar retornar o player de uma vez, ao inves de pegar os bytes
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        # return response.content, response.status_code
        i = 0
        for chunk in response.iter_content(chunk_size=chunk_size):
          if chunk:
            print("chunk ", i)
            i = i + 1
            yield bytes(chunk)
        print("completed")
      except Exception as e:
        log_error(f"Stream error attempt - {attempt}: ", e)
        if attempt == 1:
          quality = "apphd2"
        elif attempt == 2:
          quality = "apphd"
        elif attempt == 3:
          break
        attempt += 1
        continue

  return None, '404'

def find_anime_info(anime_or_video_id, page):
  cache_key = f"info_{anime_or_video_id}_page_{page}"
  cache = has_cached(cache_key)
  
  if cache != None:
    return cache
  
  BASE_URL = current_app.config['BASE_URL']
  ID_FROM_INFO_URL = current_app.config['ID_FROM_INFO_URL']
  
  try:
    if anime_or_video_id.strip().isnumeric():
      soup = make_request(f"{BASE_URL}/video/{anime_or_video_id}")
      if soup:
        url = soup.find("i", class_="spr listaEP").find_parent("a", class_="ep_control")["href"]
        anime_info_url = f"{BASE_URL}{url}/page/{page}"
        sleep(0.2)
        soup = make_request(anime_info_url)
    else:
      soup = make_request(f"{BASE_URL}/anime/{anime_or_video_id}/page/{page}")
      
    if soup:
      anime_object = {}
      
      soup_episodes = soup.find_all("div", class_="animepag_episodios_item")
      episodes = extract_episodes(soup_episodes, "animepag_episodios_item_time")
      pagination = soup.find("div", class_="pagination")
      has_next_page = pagination.find("a", class_="page-numbers current").findNext("a").text.strip().isnumeric()
      meta_url = soup.find("meta", attrs={"property": "og:url"})["content"]
      anime_id = re.compile(ID_FROM_INFO_URL).search(meta_url).group(1)
      poster_url = soup.find("div", class_="anime_img").img["src"]
      infos = soup.find_all("div", class_="anime_info")
      alt_title = str(infos[0].b.next_sibling.text).strip()
      total_episodes = str(infos[1].b.next_sibling.text).strip()
      release_date = str(infos[2].b.next_sibling.text).strip() if str(infos[2].b.next_sibling.text).strip() != "" else str(infos[2].a.text).strip()
      author = str(infos[3].b.next_sibling.text).strip()
      direction = str(infos[4].b.next_sibling.text).strip()
      studio = str(infos[5].b.next_sibling.text).strip()
      status = str(infos[6].b.next_sibling.text).strip()
      description = str(soup.find("div", class_="sinopse_container_content").text).strip()
      season = map_season(description)
      
      genres_list = infos[7].find_all("a")
      genres = []
      for genre in genres_list:
        genres.append(str(genre.text).strip())
      
      anime_object["title"] = str(soup.find("div", class_="anime_container_titulo").text).strip()
      anime_object["description"] = description
      anime_object["episodes"] = episodes
      anime_object["currentPage"] = page
      anime_object["hasNextPage"] = has_next_page
      anime_object["id"] = anime_id
      anime_object["posterUrl"] = poster_url
      anime_object["altTitle"] = alt_title
      anime_object["totalEpisodes"] = total_episodes
      anime_object["releaseDate"] = release_date
      anime_object["author"] = author
      anime_object["direction"] = direction
      anime_object["studio"] = studio
      anime_object["status"] = status
      anime_object["genres"] = genres
      anime_object["season"] = season
    
      if anime_object is not None:
        save_in_cache(cache_key, anime_object)
        return anime_object
  except Exception as e:
    log_error("An error occurred while scrapping", e)
    return {"status": 404}
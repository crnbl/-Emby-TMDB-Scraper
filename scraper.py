import os
import requests
import json
import time

# ================= 配置区域 =================
# 请在这里填入你的 TMDB API Key (去 themoviedb.org 免费申请)
API_KEY = "YOUR_TMDB_API_KEY_HERE" 

# 你的媒体文件夹路径 (如果是本地运行，填绝对路径；如果是 Docker，填容器内路径)
# 例如: "/movies" 或 "D:/Movies"
MEDIA_PATH = "." 
# ===========================================

TMDB_BASE_URL = "https://api.themoviedb.org/3"
HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

def search_movie(title, year=None):
    """搜索电影"""
    url = f"{TMDB_BASE_URL}/search/movie"
    params = {
        "query": title,
        "include_adult": "false",
        "language": "zh-CN",
        "page": 1
    }
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        data = response.json()
        if data.get("results"):
            # 简单匹配年份（如果有）
            for result in data["results"]:
                release_date = result.get("release_date", "")
                if year and release_date.startswith(str(year)):
                    return result
            # 如果没有匹配年份，返回第一个结果
            return data["results"][0]
    except Exception as e:
        print(f"搜索出错: {e}")
    return None

def search_tv(title, year=None):
    """搜索剧集"""
    url = f"{TMDB_BASE_URL}/search/tv"
    params = {
        "query": title,
        "language": "zh-CN",
        "page": 1
    }
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        data = response.json()
        if data.get("results"):
            return data["results"][0]
    except Exception as e:
        print(f"搜索剧集出错: {e}")
    return None

def get_details(media_type, tmdb_id):
    """获取详细信息 (中文)"""
    url = f"{TMDB_BASE_URL}/{media_type}/{tmdb_id}"
    params = {
        "language": "zh-CN",
        "append_to_response": "credits"
    }
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        return response.json()
    except Exception as e:
        print(f"获取详情出错: {e}")
    return None

def generate_nfo(details, media_type):
    """生成 Emby/Jellyfin 兼容的 NFO 内容"""
    if not details: return ""
    
    title = details.get("title") or details.get("name")
    plot = details.get("overview", "")
    year = (details.get("release_date") or details.get("first_air_date", "")).split("-")[0]
    
    # 提取导演和演员
    director = "Unknown"
    actors = []
    credits = details.get("credits", {})
    
    for crew in credits.get("crew", []):
        if crew.get("job") == "Director":
            director = crew.get("name")
            break
            
    for cast in credits.get("cast", [])[:5]: # 取前5个演员
        actors.append(cast.get("name"))

    nfo_content = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<movie>
  <title>{title}</title>
  <originaltitle>{details.get("original_title") or details.get("original_name")}</originaltitle>
  <plot>{plot}</plot>
  <year>{year}</year>
  <director>{director}</director>
  <studio>TMDB</studio>
  <uniqueid type="tmdb" default="true">{details.get('id')}</uniqueid>
"""
    for actor in actors:
        nfo_content += f"  <actor><name>{actor}</name></actor>\n"
        
    nfo_content += "</movie>" if media_type == "movie" else "</tvshow>"
    return nfo_content

def process_folder():
    """遍历文件夹并刮削"""
    if not os.path.exists(MEDIA_PATH):
        print(f"路径不存在: {MEDIA_PATH}")
        return

    for root, dirs, files in os.walk(MEDIA_PATH):
        for file in files:
            if file.endswith((".mkv", ".mp4", ".avi")):
                file_path = os.path.join(root, file)
                folder_path = root
                
                # 简单的文件名清洗作为搜索词
                search_title = os.path.splitext(file)[0]
                
                print(f"正在处理: {file}")
                
                # 这里做一个简单的判断，实际使用中可能需要更复杂的逻辑区分电影/剧集
                # 假设包含 S01E01 这种格式的是剧集
                is_tv = "S" in search_title.upper() and "E" in search_title.upper()
                
                data = None
                media_type = "movie"
                
                if is_tv:
                    media_type = "tv"
                    data = search_tv(search_title)
                else:
                    data = search_movie(search_title)
                    
                if data:
                    tmdb_id = data.get("id")
                    details = get_details(media_type, tmdb_id)
                    nfo_text = generate_nfo(details, media_type)
                    
                    nfo_path = os.path.join(folder_path, "movie.nfo" if not is_tv else "tvshow.nfo")
                    with open(nfo_path, "w", encoding="utf-8") as f:
                        f.write(nfo_text)
                    print(f"成功生成 NFO: {nfo_path}")
                else:
                    print(f"未找到匹配项: {search_title}")
                
                time.sleep(1) # 防止 API 限流

if __name__ == "__main__":
    print("开始刮削任务...")
    process_folder()

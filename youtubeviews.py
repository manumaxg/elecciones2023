# Carga de los paquetes necesarios
import pandas as pd
from googleapiclient.discovery import build
import datetime
import isodate
import pytz

#definición de las funciones
def build_service(api_key):
    service = build("youtube", "v3", developerKey=api_key)
    return service

def get_video_details_and_statistics(service, video_id):
    video_response = service.videos().list(
        part="snippet,contentDetails,statistics",
        id=video_id
    ).execute()
    
    if not video_response.get('items'):
        return None  # Return None if video is not found
    
    video_info = video_response['items'][0]
    video_link = f"https://www.youtube.com/watch?v={video_id}"
    tags = video_info['snippet'].get('tags', [])
    published_at_raw = video_info['snippet']['publishedAt']
        
    return {
        'title': video_info['snippet']['title'],
        'description': video_info['snippet']['description'],
        'channel_title': video_info['snippet']['channelTitle'],
        'channel_id': video_info['snippet']['channelId'],
        'duration': video_info['contentDetails']['duration'],
        'views': video_info['statistics']['viewCount'],
        'likes': video_info['statistics'].get('likeCount', 0),
        'dislikes': video_info['statistics'].get('dislikeCount', 0),
        'comments': video_info['statistics'].get('commentCount', 0),
        'video_link': video_link,
        'tags': tags,
        'published_at': published_at_raw
    }

def search_videos(service, query, published_after, published_before, video_duration, max_pages=30):
    next_page_token = None
    all_videos = []
    
    for _ in range(max_pages):
        search_response = service.search().list(
            q=query,
            part="id,snippet",
            maxResults=50,
            type="video",
            publishedAfter=published_after,
            publishedBefore=published_before,
            videoDuration=video_duration,
            order="viewCount",
            pageToken=next_page_token
        ).execute()

        for search_result in search_response.get("items", []):
            video_id = search_result['id']['videoId']
            video_details = get_video_details_and_statistics(service, video_id)
            all_videos.append(video_details)

        next_page_token = search_response.get("nextPageToken")
        if not next_page_token:
            break  

    return all_videos

#cargo los datos que se repiten en todas las busquedas. Pedir una api key propia para usar el código
api_key = "completar con la api key propia"
service = build_service(api_key)
published_after = datetime.datetime(2023, 1, 1).isoformat() + "Z"
published_before = datetime.datetime(2023, 11, 18).isoformat() + "Z"

#Búsqueda para videos de Milei
query = "Javier Milei"
videos_milei_medium = search_videos(service, query, published_after, published_before, "medium")
videos_milei_long = search_videos(service, query, published_after, published_before, "long")
df_milei_medium = pd.DataFrame(videos_milei_medium)
df_milei_long = pd.DataFrame(videos_milei_long)
df_milei = pd.concat([df_milei_medium, df_milei_long])
df_milei[['views', 'likes', 'dislikes', 'comments']] = df_milei[['views', 'likes', 'dislikes', 'comments']].apply(pd.to_numeric)
df_milei["Candidato"] = "Javier Milei"

#Búsqueda para videos de Massa
query = "Sergio Massa"
videosmassa = search_videos(service, query, published_after, published_before, "medium")
videosmassa_long = search_videos(service, query, published_after, published_before, "long")
df_massa_medium = pd.DataFrame(videosmassa)
df_massa_long = pd.DataFrame(videosmassa_long)
df_massa = pd.concat([df_massa_medium, df_massa_long])
df_massa[['views', 'likes', 'dislikes', 'comments']] = df_massa[['views', 'likes', 'dislikes', 'comments']].apply(pd.to_numeric)
df_massa[['views', 'likes', 'dislikes', 'comments']] = df_massa[['views', 'likes', 'dislikes', 'comments']].apply(pd.to_numeric)
df_massa["Candidato"] = "Sergio Massa"

#Búsqueda para videos de Bullrich
query = "Patricia Bullrich"
videosbullrich_medium = search_videos(service, query, published_after, published_before, "medium")
videosbullrich_long = search_videos(service, query, published_after, published_before, "long")
df_bullrich_medium = pd.DataFrame(videosbullrich_medium)
df_bullrich_long = pd.DataFrame(videosbullrich_long)
df_bullrich = pd.concat([df_bullrich_medium, df_bullrich_long])
df_bullrich[['views', 'likes', 'dislikes', 'comments']] = df_bullrich[['views', 'likes', 'dislikes', 'comments']].apply(pd.to_numeric)
df_bullrich["Candidato"] = "Patricia Bullrich"

# Junto los distintos dfs y preparo los datos para las visualizaciones 

df_todos_los_candidatos = pd.concat([df_milei, df_massa, df_bullrich])
df_todos_los_candidatos["Duracion"] = df_todos_los_candidatos["duration"].apply(lambda x: isodate.parse_duration(x).total_seconds()/60)
df_todos_los_candidatos.sort_values(by='views', ascending=False)
df_todos_los_candidatos["published_at"] = df_todos_los_candidatos["published_at"].str.split("T").str[0]

df_todos_los_candidatos['video_link'].value_counts()
#quiero agregar una columna con el value counts
video_link_counts = df_todos_los_candidatos['video_link'].value_counts()

# Ahora, creamos una nueva columna 'link_count' mapeando los conteos de vuelta al DataFrame original
df_todos_los_candidatos['link_count'] = df_todos_los_candidatos['video_link'].map(video_link_counts)
df_todos_los_candidatos["link_count"] = df_todos_los_candidatos["link_count"].astype(int)
df_todos_los_candidatos["views"] = df_todos_los_candidatos["views"].astype(int)
df_todos_los_candidatos["views for channels"] = df_todos_los_candidatos["views"] / df_todos_los_candidatos["link_count"]

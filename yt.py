import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import streamlit as st
import random
from googleapiclient.discovery import build
import yt_dlp
from dotenv import load_dotenv
import glob

load_dotenv()
api_key = os.getenv("YOUTUBE_API_KEY")

def get_videos_by_emotion(song, max_results=15):
    youtube = build('youtube', 'v3', developerKey=api_key)
    region = ['PK', 'IN']
    regionCode = random.choice(region)
    try:
        request = youtube.search().list(
            q=song,
            part='snippet',
            type='video',
            maxResults=max_results,
            regionCode=regionCode
        )
        response = request.execute()
        return response['items']
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return []

def DownloadingAudio(videoURL):
    try:
        download_dir = 'downloads'
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        progress_bar = st.progress(0)
        status_text = st.empty()

        def progress_hook(d):
            if d['status'] == 'downloading':
                total_bytes = d.get('total_bytes', 1)
                downloaded_bytes = d.get('downloaded_bytes', 0)
                progress = downloaded_bytes / total_bytes
                progress_bar.progress(progress)
                status_text.info(f"Downloading... {progress*100:.1f}%")
            elif d['status'] == 'finished':
                status_text.success("Download completed!")

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([videoURL])

        st.session_state.show_player = True
        st.rerun()
        
    except Exception as e:
        st.error(f"Error: {e}")

def yt_main(emotion):
    st.header(f"Detected Emotion: {emotion.capitalize()}")

    # emotion_keywords = {
    #     'happy': ["Joyful", "Energetic", "Upbeat", "Cheerful"],
    #     'sad': ["Melancholic", "Heartbroken", "Sorrowful", "Gloomy"],
    #     'angry': ["Aggressive", "Furious", "Mad", "Rage"],
    #     'fear': ["Terrified", "Anxious", "Spooky", "Tense"],
    #     'disgust': ["Revolted", "Repulsed", "Gross", "Vile"],
    #     'neutral': ["Calm", "Relaxed", "Balanced", "Mellow"],
    #     'surprise': ["Astonished", "Amazed", "Excited", "Shocked"]
    # }

    genres = ["Pop", "Rock", "Hip-Hop/Rap", "Electronic", "Classical", "Bollywood", "Punjabi", "Sufi"]

    # Initialize session state
    for key, default in [
        ('emotion_detected', False), ('videos', []), ('songs_fetched', False),
        ('show_player', False), ('current_song_index', 0)
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    if emotion:
        st.session_state.emotion_detected = True

    if st.session_state.emotion_detected:
        if not st.session_state.songs_fetched:
            st.subheader("Music Preferences")
            
            # col1 = st.columns(1)
            # with col1:
            #     emotion_filter = st.selectbox("Mood Filter", emotion_keywords.get(emotion, []))
            # with col1:
            genre = st.selectbox("Genre", genres)
            
            if st.button("Find Music"):
                with st.spinner("Searching for songs..."):
                    song_query = f"{emotion} Mood, {genre} Songs"
                    print(f"Searching for: {song_query}")
                    st.session_state.videos = get_videos_by_emotion(song_query)
                    if st.session_state.videos:
                        st.session_state.songs_fetched = True
                        st.success(f"Found {len(st.session_state.videos)} songs!")
                        st.rerun()

        if st.session_state.songs_fetched:
            st.subheader("Recommended Songs")
            songs_titles = [video['snippet']['title'] for video in st.session_state.videos]
            
            for i, title in enumerate(songs_titles[:15]):
                if st.button(f"Download: {title[:60]}...", key=f"download_{i}"):
                    selected_video = st.session_state.videos[i]
                    video_id = selected_video['id']['videoId']
                    video_url = f'https://www.youtube.com/watch?v={video_id}'
                    DownloadingAudio(video_url)

            if st.button("Back to Search"):
                st.session_state.songs_fetched = False
                st.session_state.videos = []
                st.rerun()

    if st.session_state.show_player:
        show_music_player()

def show_music_player():
    download_dir = 'downloads'
    mp3_files = glob.glob(os.path.join(download_dir, '*.mp3'))
    
    if not mp3_files:
        st.warning("No songs found in downloads folder.")
        return

    st.subheader("Music Player")

    current_song = mp3_files[st.session_state.current_song_index]
    song_name = os.path.basename(current_song).replace('.mp3', '')
    
    st.write(f"**Now Playing:** {song_name}")
    st.write(f"Track {st.session_state.current_song_index + 1} of {len(mp3_files)}")

    with open(current_song, 'rb') as audio_file:
        st.audio(audio_file.read(), format='audio/mp3')

    st.subheader("Playlist")
    for i, song_path in enumerate(mp3_files):
        song_name = os.path.basename(song_path).replace('.mp3', '')
        is_current = i == st.session_state.current_song_index
        
        if is_current:
            st.write(f"🎵 **{i+1}. {song_name}** (Now Playing)")
        else:
            if st.button(f"Play: {i+1}. {song_name}", key=f"play_{i}"):
                st.session_state.current_song_index = i
                st.rerun()
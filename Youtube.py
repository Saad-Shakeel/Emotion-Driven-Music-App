import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow logs
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import streamlit as st
import random
from googleapiclient.discovery import build
import yt_dlp


# Function to get videos based on emotion
def get_videos_by_emotion(api_key, song, max_results=15):
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
        videos = response['items']
        return videos
    except Exception as e:
        st.write("Connection Error:", e)
        return []

# Function to stream and play video as MP3
def DownloadingAudio(videoURL):
    try:
        download_dir = 'downloads'
        
        # Create 'downloads' folder if it doesn't exist
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        # Improved video URL handling (consider validation and error handling)
        video_url = videoURL

        # Create a single progress bar object
        progress_bar = st.progress(0)
        progress_text = st.empty()

        # Define a callback function to handle download progress
        def progress_hook(d):
            if d['status'] == 'downloading':
                total_bytes = d.get('total_bytes', 1)
                downloaded_bytes = d.get('downloaded_bytes', 0)

                # Update the single progress bar
                progress = downloaded_bytes / total_bytes
                progress_bar.progress(progress)

                # Update the progress text
                progress_text.write(f"Downloading: {d['filename']} - {downloaded_bytes / 1024:.2f} KB of {total_bytes / 1024:.2f} KB")

            elif d['status'] == 'finished':
                # Once the download is finished, show a completion message
                progress_text.write("Downloading!")

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
            info_dict = ydl.extract_info(video_url, download=False)  

            if 'entries' in info_dict:  # Handle playlists (if applicable)
                filename = ydl.prepare_filename(info_dict['entries'][0])
                # st.write(f"Downloading audio for: {filename}")
                ydl.download([video_url])
            else:
                filename = ydl.prepare_filename(info_dict)
                # st.write(f"Downloading audio for: {filename}")
                ydl.download([video_url])

        st.write("Download completed successfully!")
        
    except Exception as e:
        st.write(f"Error: {e}")

def YoutubeMain(emotion):
    st.header(f"Detected Emotion is '{emotion.capitalize()}'")
    api_key = 'ENTER_API_KEY'  # Replace with your actual API key
    
    # Define emotion keywords and genres
    emotion_keywords = {
        'happy': ["Joyful", "Energetic", "Upbeat", "Cheerful"],
        'sad': ["Melancholic", "Heartbroken", "Sorrowful", "Gloomy"],
        'angry': ["Aggressive", "Furious", "Mad", "Rage"],
        'fear': ["Terrified", "Anxious", "Spooky", "Tense"],
        'disgust': ["Revolted", "Repulsed", "Gross", "Vile"],
        'neutral': ["Calm", "Relaxed", "Balanced", "Mellow"],
        'surprise': ["Astonished", "Amazed", "Excited", "Shocked"]
    }

    genres = ["Pop", "Rock", "Hip-Hop/Rap", "Electronic", "Classical", "Bollywood", "Punjabi", "Sufi"]

    # Initialize session state variables if not already initialized
    if 'emotion_detected' not in st.session_state:
        st.session_state.emotion_detected = False
    if 'videos' not in st.session_state:
        st.session_state.videos = []
    if 'songs_fetched' not in st.session_state:
        st.session_state.songs_fetched = False  

    # Set emotion detected to True if an emotion is passed to the function
    if emotion:
        st.session_state.emotion_detected = True

    # Show options for filtering songs based on emotion
    if st.session_state.emotion_detected:
        if not st.session_state.songs_fetched:  # Only show options if songs haven't been fetched
            emotion_filter = st.selectbox(f"Select {emotion.capitalize()} Emotion Filter", emotion_keywords.get(emotion, []))
            genre = st.selectbox("Select Genre", genres)

            if st.button("Get Songs"):
                song_query = f"New {emotion_filter} {genre} Songs"
                st.write(f"Searching {emotion.capitalize()} Songs")
                # Retrieve videos based on the query
                st.session_state.videos = get_videos_by_emotion(api_key, song_query)
                if not st.session_state.videos:
                    st.write("No videos found.")
                    return
                
                st.session_state.songs_fetched = True  

        # After songs have been fetched, show download options
        if st.session_state.songs_fetched:
            songs_titles = [video['snippet']['title'] for video in st.session_state.videos]
            video_choice = st.selectbox("Recommended Songs List", options=songs_titles)
            
            if st.button("Download Selected Song"):
                selected_video = next((video for video in st.session_state.videos if video['snippet']['title'] == video_choice), None)
                if selected_video:
                    video_id = selected_video['id']['videoId']
                    video_url = f'https://www.youtube.com/watch?v={video_id}'
                    st.write(f"Downloading: {selected_video['snippet']['title']}")
                    DownloadingAudio(video_url)

            # Add a button to reset the state
            if st.button("Back"):
                st.session_state.songs_fetched = False  
                st.session_state.videos = [] 
                st.rerun()
                YoutubeMain(emotion)

    else:
        st.write("No emotion detected yet.")




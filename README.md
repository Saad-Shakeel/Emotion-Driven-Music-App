Emotion-Driven-Music-App is an AI-powered application designed to detect real-time emotions through facial recognition and provide personalized music recommendations based on the user's mood. The project integrates with the YouTube API to fetch relevant songs and allows users to download the recommended tracks directly from YouTube.

The core functionality of MoodTunes revolves around using machine learning models to identify emotions such as happiness, sadness, anger, surprise, and neutrality. Once the emotion is detected, the app queries YouTube for suitable music that matches the emotional tone, ensuring a personalized and engaging experience for the user.

Key Features:
Real-Time Emotion Detection: Uses a webcam feed to analyze facial expressions and detect emotions using AI-based models.
Music Recommendation: Suggests songs aligned with the detected mood, pulling music data from YouTube.
Song Download: Allows users to download recommended songs using the YouTube API and Pytube.
Streamlit Interface: Built with Streamlit, offering an intuitive and responsive web app interface with options to view, expand, and download music.
Technologies Used:
Python: The backbone of the application.
OpenCV: For capturing real-time webcam input and facial recognition.
TensorFlow/Keras: For the deep learning emotion detection model.
YouTube API & Pytube: To search, fetch, and download songs.
Streamlit: For creating a clean, easy-to-use UI.

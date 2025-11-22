import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow logs
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import cv2
import numpy as np
import streamlit as st
from keras.models import model_from_json
import os
import Youtube

@st.cache_resource
def load_model():
    # Load the model
    json_file = open("emotionDetection.json", 'r')
    model_json = json_file.read()
    model = model_from_json(model_json)
    model.load_weights("emotionDetection.h5")
    return model

def extract_features(image):
    feature = np.array(image)
    feature = feature.reshape(1, 48, 48, 1)
    return feature / 255.0

# Function to detect emotion from face
def detect_emotion(face, model, labels):
    face = cv2.resize(face, (48, 48))
    face = extract_features(face)
    prediction = model.predict(face)
    emotion_label = labels[prediction.argmax()]
    return emotion_label

def main():
    st.set_page_config(
        page_title="Emotion-Driven Music App", 
        page_icon="🎧", 
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("Welcome to the Emotion-Driven Music Recommendation System!")
    st.subheader("Emotion Recognition with AI-Powered Song Suggestions and YouTube Downloading")

    # Load the model
    model = load_model()

    # Labels for emotions
    labels = {
        0: 'angry',
        1: 'disgust',
        2: 'fear',
        3: 'happy',
        4: 'neutral',
        5: 'sad',
        6: 'surprise'
    }

    # Haar Cascade for face detection
    haar_file = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(haar_file)

    # Initialize session state for storing the last detected emotion
    if 'last_emotion' not in st.session_state:
        st.session_state.last_emotion = "No emotion detected"

    # Button to start emotion detection
    start_detection = st.button("Start Webcam")

    if start_detection:
        # Open the webcam
        webcam = cv2.VideoCapture(0)
        stframe = st.empty()  # Placeholder for webcam video feed
        detected_emotion = st.empty()  # Placeholder for detected emotion

        stop_detection = st.button("Detect Mood")

        while webcam.isOpened():
            ret, frame = webcam.read()
            if not ret:
                st.write("Failed to read from webcam.")
                break

            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            emotion_label = "No face detected"
            for (x, y, w, h) in faces:
                face = gray[y:y+h, x:x+w]
                emotion_label = detect_emotion(face, model, labels)

                # Draw rectangle around face and label the emotion
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                cv2.putText(frame, emotion_label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            # Store the last detected emotion in session state
            st.session_state.last_emotion = emotion_label

            # Display the frame with emotion in Streamlit
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            stframe.image(frame_rgb, channels="RGB")

            # Display the detected emotion
            detected_emotion.write(f"Detected Emotion: {emotion_label}")

            # Update emotion detected state
            if emotion_label != "No face detected":
                st.session_state.emotion_detected = True
            else:
                st.session_state.emotion_detected = False

            # If the stop button is pressed, break the loop and release the webcam
            if stop_detection:
                webcam.release()
                break

    # After stopping, call the YouTube function with the last detected emotion
    if st.session_state.last_emotion != "No emotion detected":
        Youtube.YoutubeMain(st.session_state.last_emotion)

if __name__ == "__main__":
    main()

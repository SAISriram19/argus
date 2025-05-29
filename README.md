# argus
# Gemini Live Voice & Visual Q&A

This project is a Python application that allows users to interact with Google's Gemini AI model using voice commands and live webcam input. It provides a real-time, conversational Q&A experience where you can ask questions about what the webcam sees or general knowledge questions, and receive spoken responses.

## Features

*   **Live Webcam Input**: Utilizes the system's webcam to capture video frames.
*   **Voice-to-Text (STT)**: Captures user questions via microphone using the `SpeechRecognition` library.
*   **Gemini AI Integration**: Sends the recognized text and current webcam frame (if video mode is active) to the Gemini API (`gemini-1.5-flash-latest` model) for processing.
*   **Text-to-Speech (TTS)**: Speaks out Gemini's responses using the `pyttsx3` library (system's default TTS engine).
*   **Interactive GUI**: Built with Tkinter, providing a visual interface to display the webcam feed, conversation log, and control buttons (Toggle Video, Toggle Mic).
*   **Environment Variable Management**: Securely loads API keys (`GEMINI_API_KEY`) from a `.env` file.
*   **Error Handling**: Includes basic error handling for API calls, webcam issues, and STT/TTS processes.
*   **Logging**: Basic logging to `gemini_live.log` (currently logs configuration loading).

## Project Structure

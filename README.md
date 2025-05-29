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


## Prerequisites

*   Python 3.7+ (Python 3.9 was used for `.venv` in the example)
*   A Google Gemini API Key.
*   (Optional) An ElevenLabs API Key if you plan to integrate ElevenLabs for TTS in the future.
*   A functional webcam and microphone.
*   Git (for version control).

## Setup and Installation

1.  **Clone the Repository (if you've pushed it to GitHub):**
    ```bash
    git clone https://github.com/SAISriram19/argus.git
    cd argus
    ```
    If you are working locally and haven't pushed yet, you can skip this step.

2.  **Create and Activate a Python Virtual Environment:**
    It's highly recommended to use a virtual environment to manage project dependencies.
    ```bash
    python -m venv .venv
    ```
    Activate the environment:
    *   **Windows (Command Prompt/PowerShell):**
        ```bash
        .venv\Scripts\activate
        ```
    *   **macOS/Linux (bash/zsh):**
        ```bash
        source .venv/bin/activate
        ```

3.  **Install Dependencies:**
    Create a `requirements.txt` file in the root of your project (`d:\code\argus\requirements.txt`) with the following content:
    ```plaintext:d%3A%5Ccode%5Cargus%5Crequirements.txt
    google-generativeai
    python-dotenv
    Pillow
    opencv-python
    SpeechRecognition
    pyttsx3
    # pyaudio # Often needed by SpeechRecognition, installation can vary
    ```
    Then, install the packages:
    ```bash
    pip install -r requirements.txt
    ```
    *   **Note on PyAudio:** `SpeechRecognition` often relies on `PyAudio` for microphone access. `PyAudio` can sometimes be tricky to install. 
        *   On Windows, you might be able to install it via pip if you have Microsoft Visual C++ Build Tools. If not, you might find pre-compiled wheels from sources like Christoph Gohlke's Python Extension Packages for Windows.
        *   On Linux, you usually need to install `portaudio` development libraries first (e.g., `sudo apt-get install portaudio19-dev`).
        *   On macOS, `brew install portaudio` might be needed.

4.  **Configure API Keys:**
    Create a file named `.env` in the project root directory (`d:\code\argus\.env`). Add your API keys to this file:
    ```env
    GEMINI_API_KEY="YOUR_GOOGLE_GEMINI_API_KEY"
    ELEVENLABS_API_KEY="YOUR_ELEVENLABS_API_KEY" # If you plan to use it
    ```
    Replace `"YOUR_GOOGLE_GEMINI_API_KEY"` and `"YOUR_ELEVENLABS_API_KEY"` with your actual keys.
    **Important:** Ensure `.env` is listed in your `.gitignore` file to prevent committing your secret keys to version control.

## How to Run Argus

1.  Ensure your webcam and microphone are connected to your computer and are not being used by other applications.
2.  Activate your Python virtual environment if it's not already active.
3.  Navigate to the project directory (`d:\code\argus`) in your terminal.
4.  Execute the main script:
    ```bash
    python main.py
    ```

## Using the Application

*   Upon launching, the application window will display the live feed from your webcam.
*   **Video Button (`Video: ON`/`Video: OFF`):** Controls whether the current video frame is included with your spoken question to the Gemini API. Toggle as needed.
*   **Microphone Button (`Mic: ON`/`Mic: OFF`):** 
    *   Click to change to `Mic: ON`. The application will start listening.
    *   Speak your question clearly.
    *   The system will transcribe your speech, display it, and send it (along with the video frame if enabled) to Gemini.
    *   Gemini's response will be shown in the conversation log and spoken aloud.
    *   After processing, the mic will automatically revert to `Mic: OFF`. Click it again to ask a new question.
*   **Conversation Log:** This area shows a history of your questions (as transcribed) and Gemini's responses.
*   **Close [X] Button:** Safely exits the application, releasing webcam and other resources.

## Application Workflow

1.  **Initialization**: The application starts by setting up essential components: webcam capture (OpenCV), Speech-to-Text engine (`SpeechRecognition`), Text-to-Speech engine (`pyttsx3`), and loads API keys from `.env`.
2.  **GUI Setup**: The main window and its widgets (video display, buttons, text areas) are created using Tkinter.
3.  **Video Processing**: A dedicated thread continuously captures frames from the webcam and updates the video display label in the GUI. The latest frame is stored for potential use in API calls.
4.  **User Interaction (Voice Command)**:
    a.  User clicks the "Mic: ON" button.
    b.  A new thread is initiated for the `listen_and_process_speech` function.
    c.  The system listens for audio input. If speech is detected, it's transcribed to text.
    d.  The transcribed text becomes the `prompt`.
5.  **Gemini API Call**:
    a.  The `call_gemini_api` function is triggered.
    b.  A request is constructed containing the text prompt. If video mode is active, the current webcam frame (as a PIL Image) is also included in the request.
    c.  The request is sent to the Gemini API.
6.  **Response Handling**:
    a.  Gemini's response is received.
    b.  The textual part of the response is extracted and displayed in the conversation log.
    c.  The TTS engine speaks the textual response.
7.  **State Reset**: The microphone state is reset to 'OFF', and the application awaits further user interaction.

## Future Development Ideas

*   **Enhanced Error Reporting**: More specific user feedback for different types of errors (API, network, hardware).
*   **ElevenLabs TTS Integration**: Option to use ElevenLabs for higher-quality, more natural-sounding voice responses (requires `ELEVENLABS_API_KEY`).
*   **Conversation History**: Ability to save and load conversation logs.
*   **Customizable Prompts/Personas**: Allow users to define system instructions for Gemini to tailor its personality or response style.
*   **Model Selection**: UI option to choose different Gemini models if available/applicable.
*   **Improved UI/UX**: Modernize the interface, perhaps using a different GUI framework or custom styling.
*   **Wake Word Activation**: Implement a wake word (e.g., "Hey Argus") to activate listening instead of relying solely on button clicks.
*   **Streaming Responses**: For long Gemini responses, stream the text as it arrives to improve perceived responsiveness.


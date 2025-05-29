import os
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image, ImageTk
import cv2  # Import OpenCV
import time  # To add a small delay
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox # simpledialog removed
import threading
import speech_recognition as sr # For STT
import pyttsx3 # For TTS

class GeminiLiveApp:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("Gemini Live Voice & Visual Q&A")

        # --- State Variables ---
        self.is_video_mode_active = True
        self.is_listening_active = False # Replaces is_mic_muted
        self.is_processing_speech = False # To prevent concurrent STT
        self.is_running = False
        self.webcam_thread = None
        self.speech_thread = None
        self.prompt = "" # Current active prompt from voice

        # --- API and Model Setup ---
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            messagebox.showerror("API Key Error", "GEMINI_API_KEY not found. Please set it in your .env file.")
            self.root.destroy()
            return
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash-latest')

        # --- Webcam Setup ---
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Webcam Error", "Could not open webcam.")
            self.root.destroy()
            return
        self.current_frame_pil = None

        # --- Speech Recognition (STT) Setup ---
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5) # Adjust for noise

        # --- Text-to-Speech (TTS) Setup ---
        self.tts_engine = pyttsx3.init()
        
        # --- UI Elements ---
        self.create_widgets()
        
        # --- Start Processes ---
        self.is_running = True
        self.webcam_thread = threading.Thread(target=self.video_processing_loop, daemon=True)
        self.webcam_thread.start()
        self.update_response_text("System Ready. Click 'Mic: OFF' to start listening.", clear_previous=True)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(expand=True, fill=tk.BOTH)

        self.video_label = ttk.Label(main_frame, text="Initializing Webcam...")
        self.video_label.pack(pady=10, expand=True, fill=tk.BOTH)

        controls_frame = ttk.Frame(main_frame, padding="5")
        controls_frame.pack(fill=tk.X)

        self.video_button = ttk.Button(controls_frame, text="Video: ON", command=self.toggle_video_mode)
        self.video_button.pack(side=tk.LEFT, padx=5)

        self.mic_button = ttk.Button(controls_frame, text="Mic: OFF", command=self.toggle_listening_mode)
        self.mic_button.pack(side=tk.LEFT, padx=5)
        
        self.close_button = ttk.Button(controls_frame, text="Close [X]", command=self.on_closing, style="Danger.TButton")
        self.close_button.pack(side=tk.RIGHT, padx=5)
        
        style = ttk.Style()
        style.configure("Danger.TButton", foreground="white", background="red")

        self.prompt_display_label = ttk.Label(main_frame, text="Your Question: (Speak when Mic is ON)")
        self.prompt_display_label.pack(fill=tk.X, pady=5)

        response_label = ttk.Label(main_frame, text="Conversation Log:")
        response_label.pack(fill=tk.X, pady=(10,0))
        self.response_text = scrolledtext.ScrolledText(main_frame, height=10, wrap=tk.WORD, state=tk.DISABLED)
        self.response_text.pack(pady=5, expand=True, fill=tk.BOTH)

    def speak_text(self, text_to_speak):
        try:
            self.tts_engine.say(text_to_speak)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"TTS Error: {e}")
            self.update_response_text(f"TTS Error: {e}")

    def listen_and_process_speech(self):
        if not self.is_listening_active or self.is_processing_speech:
            return

        self.is_processing_speech = True
        self.root.after(0, self.prompt_display_label.config, {"text": "Your Question: Listening..."})
        self.update_response_text("Listening for your question...")

        with self.microphone as source:
            try:
                # self.recognizer.adjust_for_ambient_noise(source, duration=0.2) # Re-adjust if needed
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            except sr.WaitTimeoutError:
                self.update_response_text("No speech detected. Try again.")
                self.root.after(0, self.prompt_display_label.config, {"text": "Your Question: (Speak when Mic is ON)"})
                self.is_processing_speech = False
                # self.toggle_listening_mode() # Optionally turn off mic automatically
                return
            except Exception as e:
                self.update_response_text(f"STT Listen Error: {e}")
                self.is_processing_speech = False
                return


        try:
            self.update_response_text("Recognizing...")
            recognized_text = self.recognizer.recognize_google(audio)
            self.prompt = recognized_text # Set the current prompt
            self.root.after(0, self.prompt_display_label.config, {"text": f"Your Question: {self.prompt}"})
            self.update_response_text(f"You said: {self.prompt}")

            # Trigger Gemini call now that we have a prompt
            self.call_gemini_api()

        except sr.UnknownValueError:
            self.update_response_text("Could not understand audio. Please try again.")
            self.root.after(0, self.prompt_display_label.config, {"text": "Your Question: (Speak when Mic is ON)"})
        except sr.RequestError as e:
            self.update_response_text(f"Google Speech Recognition service error; {e}")
        finally:
            self.is_processing_speech = False
            # Keep listening if mode is still active, or user can click again
            if self.is_listening_active:
               self.speech_thread = threading.Thread(target=self.listen_and_process_speech, daemon=True)
               self.speech_thread.start()


    def toggle_listening_mode(self):
        self.is_listening_active = not self.is_listening_active
        if self.is_listening_active:
            self.mic_button.config(text="Mic: ON")
            self.update_response_text("Microphone ON. Speak your question.")
            # Start listening in a new thread to avoid blocking UI
            if not self.is_processing_speech:
                 self.speech_thread = threading.Thread(target=self.listen_and_process_speech, daemon=True)
                 self.speech_thread.start()
        else:
            self.mic_button.config(text="Mic: OFF")
            self.update_response_text("Microphone OFF.")
            self.is_processing_speech = False # Ensure this is reset

    def toggle_video_mode(self):
        self.is_video_mode_active = not self.is_video_mode_active
        status = "ON" if self.is_video_mode_active else "OFF"
        self.video_button.config(text=f"Video: {status}")
        self.update_response_text(f"Video mode set to {status}.")

    def video_processing_loop(self):
        """Handles webcam frame capture and display."""
        while self.is_running:
            ret, frame = self.cap.read()
            if not ret:
                self.root.after(100, self.update_response_text, "Error: Webcam stream ended.")
                break
            
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(cv2image)
            self.current_frame_pil = pil_img # Store for API call
            
            # Consider resizing for performance if frames are very large
            # display_pil_img = pil_img.resize((640, 480), Image.LANCZOS) # Example resize
            imgtk = ImageTk.PhotoImage(image=pil_img) # Use original for API, potentially resized for display

            self.root.after(0, self.video_label.config, {"image": imgtk})
            self.root.after(0, setattr, self.video_label, "image", imgtk) 

            time.sleep(0.03) # Approx 30 FPS for video display

    def call_gemini_api(self):
        """Called after speech is recognized and self.prompt is set."""
        if not self.prompt:
            self.update_response_text("No question to ask Gemini.")
            return

        self.update_response_text("Sending to Gemini...")
        
        content_to_send = [self.prompt]
        if self.is_video_mode_active and self.current_frame_pil:
            content_to_send.append(self.current_frame_pil)
        elif self.is_video_mode_active and not self.current_frame_pil:
            self.update_response_text("Video mode is ON, but no frame available yet. Waiting for frame.")
            return # Wait for next frame cycle if needed
        
        try:
            response = self.model.generate_content(content_to_send, request_options={"timeout": 20})
            
            answer_text = ""
            if response.parts:
                for part in response.parts:
                    if hasattr(part, 'text'):
                        answer_text += part.text + "\n"
            elif hasattr(response, 'text') and response.text:
                answer_text = response.text
            else:
                answer_text = "Gemini did not provide a text response."
                if response.prompt_feedback:
                    answer_text += f"\nPrompt Feedback: {response.prompt_feedback}"
            
            final_answer = answer_text.strip()
            self.update_response_text(f"Gemini: {final_answer}")
            
            # Speak the answer
            tts_thread = threading.Thread(target=self.speak_text, args=(final_answer,), daemon=True)
            tts_thread.start()

        except Exception as e:
            error_msg = f"Gemini API Error: {str(e)}"
            if "DeadlineExceeded" in str(e): error_msg = "Gemini API call timed out."
            elif "ResourceExhausted" in str(e): error_msg = "Gemini API rate limit likely hit."
            self.update_response_text(error_msg)
            self.speak_text("Sorry, there was an error contacting Gemini.")
        finally:
            self.prompt = "" # Clear prompt after processing, ready for next voice input
            # self.root.after(0, self.prompt_display_label.config, {"text": "Your Question: (Speak when Mic is ON)"})


    def update_response_text(self, text, clear_previous=False):
        if not self.root.winfo_exists(): return # Avoid error if window closed
        
        self.response_text.config(state=tk.NORMAL)
        if clear_previous:
            self.response_text.delete(1.0, tk.END)
        
        timestamp = time.strftime("%H:%M:%S")
        self.response_text.insert(tk.END, f"[{timestamp}] {text}\n")
        self.response_text.see(tk.END)
        self.response_text.config(state=tk.DISABLED)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.is_running = False
            self.is_listening_active = False # Stop any listening attempts
            
            if self.speech_thread and self.speech_thread.is_alive():
                # STT listen() can block, difficult to interrupt cleanly without more complex eventing
                print("Waiting for speech thread to complete if active...")
            
            if self.webcam_thread and self.webcam_thread.is_alive():
                self.webcam_thread.join(timeout=1)
            if self.cap:
                self.cap.release()
            
            self.tts_engine.stop() # Stop any ongoing speech
            self.root.destroy()

def main():
    root = tk.Tk()
    app = GeminiLiveApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
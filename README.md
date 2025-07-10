# Vid.AI 🎬🤖

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/) [![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Welcome to **Vid.AI**, an end-to-end video generator that creates educational videos in minutes—automatically generating narration, fetching relevant images, producing a female-voiced audio track, and stitching everything into a polished MP4!

---

## 🚀 Features

- **Script Generation**  
  Leverages GPT-3.5-turbo to produce a 5–10 minute narration script plus visual cue markers in square brackets.

- **Image Fetching**  
  Uses Pexels API to download high-quality, relevant images for each visual cue.

- **Natural Female Voice**  
  Employs `pyttsx3` with a female voice profile and adjusted speech rate for a professional tone.

- **Ken Burns Effect**  
  Applies subtle pan-and-zoom on images for cinematic flair.

- **Subtitle Export**  
  Generates an SRT subtitle file aligned to narration segments.

---

## 📦 Installation

1. Clone the repo  
   ```bash
   git clone https://github.com/yourusername/Vid.AI.git
   cd Vid.AI
   ```

2. Create & activate a virtualenv  
   ```bash
   python -m venv venv
   source venv/Scripts/activate    # Windows
   source venv/bin/activate        # macOS/Linux
   ```

3. Install dependencies  
   ```bash
   pip install -r requirements.txt
   ```

4. Create your `.env`  
   ```dotenv
   OPENROUTER_API_KEY=your_openrouter_key
   PEXELS_API_KEY=your_pexels_key
   ```

---

## ⚙️ Usage

Run the CLI with your topic of choice:
```bash
python app.py "Photosynthesis in Plants"
```

Output files will appear in:  
```
/images       # downloaded images
/audio        # TTS-generated MP3
/output       # final video .mp4 & subtitles.srt
```

---

## 📂 Project Structure

```
e:\Vid.AI
├── .env                  # API keys
├── app.py                # main entrypoint
├── fetch_images.py       # Pexels image downloader
├── generate_script.py    # OpenRouter script generator
├── generate_audio.py     # pyttsx3 TTS engine
├── create_video.py       # video composer (MoviePy + Ken Burns)
├── generate_subtitles.py # .srt subtitle exporter
├── requirements.txt      # pip deps
└── README.md             # this document
```

---

## 🛠️ Contributing

1. Fork the repo  
2. Create your feature branch (`git checkout -b feature/YourFeature`)  
3. Commit your changes (`git commit -m "Add awesome feature"`)  
4. Push to branch (`git push origin feature/YourFeature`)  
5. Open a Pull Request

Please adhere to the existing code style, add tests where applicable, and ensure all new features are documented.

---

## ❓ Troubleshooting

- **Missing voices in `pyttsx3`**  
  Ensure your system has at least one female voice installed (e.g., Microsoft Zira on Windows).

- **API rate limits**  
  Check your Pexels & OpenRouter quota and adjust `count` or prompt frequency accordingly.

- **Slow video rendering**  
  Lower `fps` or reduce image resolution in `create_video.py`.

---

## 📄 License

This project is released under the [MIT License](LICENSE). Enjoy and build amazing educational videos with ease!  

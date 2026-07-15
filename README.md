# LoopMeter 🚀

A lightweight, neon-styled desktop companion for Windows. It features a real-time system monitor (CPU/RAM load) and an infinite media looper. Drop in any MP4, GIF, or image, and let it loop continuously on your screen.

## ✨ Features

* **Infinite Media Loop:** Supports MP4, GIF, and images. 
* **Audio Sync:** Automatically looks for an `.mp3` with the matching name in the same folder and plays it in sync with your video.
* **System Monitor:** Real-time, sleek neon progress bars for CPU and RAM load.
* **Borderless & Customizable:** Drag it anywhere, resize on the fly (Right-Click + Drag), or pin it on top of all windows.
* **Instant Close:** Exit the app instantly with a single press of the `Esc` key.

---

## 📥 How to Run

1. Go to the **Releases** section on the right side of this page.
2. Download the latest `LoopMeter.exe`.
3. Double-click to run! No installation or Python setup required.

---

## ⚠️ Note on Windows Defender (False Positive)

Because this app is written in Python and compiled into a single `.exe` file using `PyInstaller`, **Windows Defender or other antivirus software might flag it as suspicious** (e.g., *Trojan:Win32/Preventor*). 

This is a **false positive** common to almost all compiled Python apps. 
* **Why does this happen?** The compiled `.exe` unpacks its internal libraries into a temporary folder on startup, which looks suspicious to antivirus heuristics. Additionally, the file is not digitally signed.
* **Is it safe?** Absolutely. The entire source code is open and available right here in `main.py`. You can inspect every line of code yourself or run it directly from the source if you prefer not to use the `.exe`.

# Installing FFmpeg for Full Audio Functionality

## Why FFmpeg?

FFmpeg is required for:
- Merging multiple audio segments with crossfade
- Adding silence/pauses between speakers  
- Professional audio processing and effects

Without FFmpeg, the podcast generator will still work but will only output the first audio segment.

## Installation Options

### Option 1: Chocolatey (Easiest for Windows)

1. Open PowerShell as Administrator
2. Install Chocolatey if you don't have it:
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
   ```
3. Install FFmpeg:
   ```powershell
   choco install ffmpeg
   ```
4. Restart your terminal and verify:
   ```bash
   ffmpeg -version
   ```

### Option 2: Manual Installation

1. Download FFmpeg from: https://www.gyan.dev/ffmpeg/builds/
   - Click "ffmpeg-release-essentials.zip"
2. Extract the ZIP file to `C:\ffmpeg`
3. Add to PATH:
   - Open System Properties → Environment Variables
   - Edit "Path" under System variables
   - Add: `C:\ffmpeg\bin`
4. Restart terminal and verify:
   ```bash
   ffmpeg -version
   ```

### Option 3: Winget (Windows 11)

```bash
winget install ffmpeg
```

## Verify Installation

After installing, restart the Flask server:

```bash
python app.py
```

You should no longer see the FFmpeg warning, and podcasts will be fully merged with professional audio effects!

## Alternative: Use Docker (Advanced)

If you prefer not to install FFmpeg locally, you can run the entire app in Docker where FFmpeg is pre-installed.

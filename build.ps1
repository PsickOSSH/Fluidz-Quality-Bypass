Remove-Item -Recurse -Force .\build, .\dist -ErrorAction SilentlyContinue
Remove-Item .\Fluidz_Quality_Bypass.spec -ErrorAction SilentlyContinue

pyinstaller --clean --onefile --windowed `
  --name "Fluidz_Quality_Bypass" `
  --icon "icon.ico" `
  --add-data "icon.ico;." `
  --add-binary "ffmpeg.exe;." `
  --add-binary "ffprobe.exe;." `
  patch_videos_gui.py
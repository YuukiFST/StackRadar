# Script para gerar o executável Standalone garantindo que o Ícone vá junto
# Precisamos garantir que o PyInstaller está disponível:
# uv pip install pyinstaller

$IconFile = "radar_copy_icon_124877.ico"
$MainScript = "src\stackradar\app.py"

Write-Host "Iniciando build do arquivo standalone com ícone..." -ForegroundColor Cyan

pyinstaller --noconfirm --onedir --windowed `
  --icon "$IconFile" `
  --add-data "$IconFile;." `
  --name "StackRadar" `
  $MainScript

Write-Host "Build concluído! O executável está na pasta 'dist\StackRadar'." -ForegroundColor Green

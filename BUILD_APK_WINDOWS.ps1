# MetaSearch Universal - Build Automatique Windows
# Double-cliquez ce fichier .ps1 pour compiler l'APK

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🔍 MetaSearch Universal - Build APK Windows          ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Vérifier si WSL est installé
$wsl = wsl --list --quiet 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "📦 WSL non detecte. Installation..." -ForegroundColor Yellow
    Write-Host "Cela peut prendre 5-10 minutes. Ne fermez pas cette fenetre." -ForegroundColor Yellow
    wsl --install -d Ubuntu
    Write-Host ""
    Write-Host "🔄 REDEMARREZ VOTRE PC, puis relancez ce script." -ForegroundColor Red -BackgroundColor Black
    Write-Host ""
    pause
    exit
}

Write-Host "✅ WSL detecte" -ForegroundColor Green

# Chemin du projet
$projectPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectPath = $projectPath -replace '\', '/'
$projectPath = $projectPath -replace '^([A-Z]):', '/mnt/$1'.ToLower()

Write-Host "📁 Projet: $projectPath" -ForegroundColor Gray

# Commandes WSL
$commands = @"
# Mettre a jour
sudo apt-get update -qq

# Installer les dependances
sudo apt-get install -y -qq build-essential git zip unzip openjdk-17-jdk autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev cmake libffi-dev libssl-dev automake python3-dev python3-pip python3-venv

# Installer buildozer
pip3 install --user buildozer cython

# Aller dans le projet
cd "$projectPath"

# Nettoyer et compiler
export PATH=\$HOME/.local/bin:\$PATH
buildozer android clean 2>/dev/null || true
buildozer -v android debug

# Copier l'APK vers un dossier accessible
mkdir -p /mnt/c/Users/\$USER/Desktop/MetaSearch_APK 2>/dev/null || mkdir -p /mnt/c/Users/\$USER/Bureau/MetaSearch_APK
cp bin/*.apk /mnt/c/Users/\$USER/Desktop/MetaSearch_APK/ 2>/dev/null || cp bin/*.apk /mnt/c/Users/\$USER/Bureau/MetaSearch_APK/
"@

Write-Host ""
Write-Host "🔨 Lancement de la compilation dans WSL..." -ForegroundColor Cyan
Write-Host "⏳ PREMIER BUILD = 30-60 minutes (telechargement Android SDK)" -ForegroundColor Yellow
Write-Host "☕ Laissez tourner, allez prendre un cafe!" -ForegroundColor Yellow
Write-Host ""

# Executer dans WSL
$commands | wsl bash -s

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ COMPILATION TERMINEE !" -ForegroundColor Green -BackgroundColor Black
    Write-Host ""

    # Chercher l'APK sur le bureau
    $desktop = [Environment]::GetFolderPath("Desktop")
    $apkDir = Join-Path $desktop "MetaSearch_APK"

    if (Test-Path $apkDir) {
        $apks = Get-ChildItem $apkDir -Filter "*.apk"
        if ($apks) {
            Write-Host "📱 APK trouve:" -ForegroundColor Green
            foreach ($apk in $apks) {
                Write-Host "   $($apk.FullName)" -ForegroundColor Cyan
                Write-Host "   Taille: $([math]::Round($apk.Length/1MB, 1)) Mo" -ForegroundColor Gray
            }
            Write-Host ""
            Write-Host "📲 Installation sur Android:" -ForegroundColor White
            Write-Host "   1. Transferez le fichier sur votre telephone" -ForegroundColor Gray
            Write-Host "   2. Activez 'Sources inconnues' dans Parametres > Securite" -ForegroundColor Gray
            Write-Host "   3. Ouvrez le fichier APK et installez" -ForegroundColor Gray
            Write-Host ""
            Write-Host "🔐 Mode Master MDP: master123 (changez-le!)" -ForegroundColor Yellow

            # Ouvrir le dossier
            Start-Process explorer.exe $apkDir
        }
    }
} else {
    Write-Host ""
    Write-Host "❌ Erreur de compilation" -ForegroundColor Red
    Write-Host "Relancez le script, le build reprendra la ou il en etait." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Appuyez sur une touche pour fermer..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

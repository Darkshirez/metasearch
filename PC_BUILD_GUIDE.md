# 🖥️ GUIDE PC - Compiler MetaSearch sur Windows

## Prérequis
- Windows 10/11
- 15 Go d'espace disque libre
- Connexion Internet

## Étape 1 : Activer PowerShell (1 minute)

1. Cliquez droit sur le bouton Démarrer
2. Cliquez sur **Windows PowerShell (admin)** ou **Terminal (admin)**
3. Tapez cette commande et appuyez Entrée :

```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope CurrentUser
```

Tapez `O` (pour Oui) et Entrée.

## Étape 2 : Lancer le build (30-60 min)

1. Extrayez le ZIP `metasearch_v3.zip` sur votre Bureau
2. Double-cliquez sur **BUILD_APK_WINDOWS.ps1**
3. Si WSL n'est pas installé, le script l'installe automatiquement
4. **REDÉMARREZ** votre PC si WSL vient d'être installé
5. Relancez le script après le redémarrage
6. Attendez la fin de la compilation

## Étape 3 : Récupérer l'APK

L'APK sera automatiquement copiée sur votre Bureau dans le dossier **MetaSearch_APK**.

## Étape 4 : Installer sur Android

1. Connectez votre téléphone en USB
2. Copiez l'APK dans le dossier `Téléchargements` du téléphone
3. Sur le téléphone : **Paramètres > Sécurité > Sources inconnues** → Activez
4. Ouvrez l'APK avec un gestionnaire de fichiers et installez

## 🔐 Mode Master

- Ouvrez l'app → onglet **🔐**
- MDP : `master123`
- **Changez immédiatement !**

## ❌ Si ça ne marche pas

| Problème | Solution |
|---|---|
| "WSL not found" | Redémarrez le PC et relancez |
| "Permission denied" | Relancez PowerShell en admin |
| Build trop long | C'est normal au premier build (30-60 min) |
| Erreur Java | Le script l'installe auto, relancez |

## 📞 Support

Si le script échoue, ouvrez PowerShell en admin, allez dans le dossier du projet et tapez :
```bash
wsl
sudo apt update
sudo apt install -y build-essential openjdk-17-jdk python3-pip
pip3 install buildozer cython
buildozer android debug
```

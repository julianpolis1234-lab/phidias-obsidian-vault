@echo off
chcp 65001 >nul
title Centinela Git Auto-Sync (Obsidian Vault)
color 0A

echo ======================================================================
echo           🔄 CENTINELA GIT AUTO-SYNC (OBSIDIAN VAULT) 🔄
echo ======================================================================
echo.
echo Monitoreando cambios en tu Obsidian Vault cada 8 segundos...
echo Cualquier cambio se commitea y se sube a GitHub automáticamente.
echo (Puedes minimizar esta ventana para que trabaje en silencio).
echo.

cd /d "C:\Users\MSI\Documents\Obsidian Vault"
python git_autosync_obsidian.py

pause

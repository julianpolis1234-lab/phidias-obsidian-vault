@echo off
chcp 65001 >nul
title Publicar Obsidian Vault en GitHub + Auto-Sync
color 0B

echo ======================================================================
echo       🐙 PUBLICADOR AUTOMÁTICO DE OBSIDIAN VAULT EN GITHUB 🐙
echo ======================================================================
echo.
echo Repositorio: C:\Users\MSI\Documents\Obsidian Vault
echo.

cd /d "C:\Users\MSI\Documents\Obsidian Vault"

:: 1. Verificar Git
where git >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Git no está instalado en este equipo.
    pause
    exit /b 1
)

:: 2. Verificar estado de autenticación de GitHub CLI
echo [1/3] Verificando sesión de GitHub...
gh auth status >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo.
    echo ------------------------------------------------------------------
    echo  No hay sesión de GitHub iniciada en tu consola.
    echo  A continuación se abrirá tu navegador para iniciar sesión en 1 clic:
    echo ------------------------------------------------------------------
    echo.
    gh auth login --web -h github.com -p https
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] No se pudo autenticar con GitHub.
        pause
        exit /b 1
    )
)

echo  ✓ Sesión de GitHub verificada correctamente.
echo.

:: 3. Verificar si ya existe remote origin
git remote | findstr /i "origin" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [2/3] Creando repositorio en tu cuenta de GitHub...
    echo.
    echo Selecciona la privacidad del repositorio:
    echo   [1] Privado (Recomendado - solo tú puedes verlo)
    echo   [2] Público (Cualquiera con el enlace puede verlo)
    echo.
    set /p "PRIV_CHOICE=Elige 1 o 2 (Enter para Privado): "
    
    if "%PRIV_CHOICE%"=="2" (
        set "VISIBILITY=--public"
    ) else (
        set "VISIBILITY=--private"
    )

    gh repo create phidias-obsidian-vault %VISIBILITY% --source=. --remote=origin --push
    if %ERRORLEVEL% neq 0 (
        echo [AVISO] Si ya tenías el repositorio creado en GitHub, ingresa la URL:
        set /p "REPO_URL=Pega la URL de tu repositorio (https://github.com/...): "
        if not "%REPO_URL%"=="" (
            git remote add origin %REPO_URL%
            git branch -M main
            git push -u origin main
        )
    )
) else (
    echo [2/3] El repositorio ya tiene un remote vinculado.
    git push -u origin main
)

echo.
echo [3/3] Iniciando Centinela de Auto-Sincronización en segundo plano...
start "" /min "C:\Users\MSI\Documents\Obsidian Vault\INICIAR_AUTOSYNC.bat"

echo.
echo ======================================================================
echo  ✓ ¡TU OBSIDIAN VAULT ESTÁ PUBLICADO EN GITHUB!
echo  ✓ El centinela de auto-sincronización está activo en segundo plano.
echo  ✓ Cada vez que hagas un cambio en Obsidian, se guardará y subirá solo.
echo ======================================================================
echo.
pause

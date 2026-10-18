#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sincronizador Automático Git para Obsidian Vault.
Monitorea cambios en el Vault y realiza auto-commit + auto-push a GitHub.
"""

import os
import sys
import time
import subprocess
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def get_vault_path() -> Path:
    # Si este script está dentro del Vault o se pasa por argumento
    if (Path(__file__).parent / ".obsidian").exists():
        return Path(__file__).parent
    # Fallback predeterminado
    return Path(os.path.expanduser("~")) / "Documents" / "Obsidian Vault"


def run_git(cmd: list, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, encoding="utf-8", errors="replace")


def check_has_remote(vault_path: Path) -> bool:
    res = run_git(["git", "remote"], vault_path)
    return bool(res.stdout.strip())


def auto_commit_and_push(vault_path: Path) -> bool:
    # 1. Verificar cambios
    status_res = run_git(["git", "status", "--porcelain"], vault_path)
    changes = status_res.stdout.strip()
    if not changes:
        return False  # No hay cambios pendientes

    logging.info(f"Detectados cambios en Obsidian:\n{changes[:300]}")
    time.sleep(2)  # Pequeña pausa para permitir que Obsidian termine de escribir

    # 2. git add -A
    run_git(["git", "add", "-A"], vault_path)

    # 3. git commit
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_msg = f"auto(vault): sincronización automática [{now_str}]"
    commit_res = run_git(["git", "commit", "-m", commit_msg], vault_path)
    if commit_res.returncode == 0:
        logging.info(f"✓ Commit realizado: {commit_msg}")
    else:
        logging.warning(f"Aviso en commit: {commit_res.stderr.strip() or commit_res.stdout.strip()}")

    # 4. git push si tiene remote
    if check_has_remote(vault_path):
        logging.info("Enviando cambios a GitHub (git push)...")
        push_res = run_git(["git", "push", "origin", "main"], vault_path)
        if push_res.returncode == 0:
            logging.info("✓ Push exitoso a GitHub!")
            return True
        else:
            logging.warning(f"Reintentando con pull rebase: {push_res.stderr.strip()}")
            run_git(["git", "pull", "--rebase", "origin", "main"], vault_path)
            retry_push = run_git(["git", "push", "origin", "main"], vault_path)
            if retry_push.returncode == 0:
                logging.info("✓ Push exitoso a GitHub tras rebase!")
                return True
            else:
                logging.error(f"Error al hacer push: {retry_push.stderr.strip()}")
                return False
    else:
        logging.info("Repositorio local al día (Sin remote de GitHub vinculado todavía).")
        return True


def watch_and_sync_loop(vault_path: Path, interval: int = 8):
    logging.info(f"Iniciando centinela de auto-sincronización en: {vault_path}")
    logging.info(f"Intervalo de comprobación: cada {interval} segundos. Presiona Ctrl+C para salir.")
    while True:
        try:
            auto_commit_and_push(vault_path)
            time.sleep(interval)
        except KeyboardInterrupt:
            logging.info("Centinela detenido por el usuario.")
            break
        except Exception as e:
            logging.error(f"Excepción en bucle de sincronización: {e}")
            time.sleep(interval)


if __name__ == "__main__":
    v_path = get_vault_path()
    if "--once" in sys.argv:
        auto_commit_and_push(v_path)
    else:
        watch_and_sync_loop(v_path)

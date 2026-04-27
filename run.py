"""
Punto de entrada del proyecto Competitividad Turística.

Uso:
    python run.py              Ver comandos disponibles
    python run.py assets       Ejecuta el pipeline de datos y genera archivos consolidados
    python run.py deploy       Copia archivos al repo Jekyll
    python run.py ver          Lanza el dashboard de Streamlit localmente
    python run.py test         Ejecuta tests + linting
    python run.py all          Pipeline completo: assets -> deploy
"""

from __future__ import annotations

import os
import subprocess
import sys

_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def _supports_color() -> bool:
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

_COLOR = _supports_color()

def _green(text: str) -> str:
    return f"\033[92m{text}\033[0m" if _COLOR else text

def _cyan(text: str) -> str:
    return f"\033[96m{text}\033[0m" if _COLOR else text

def _red(text: str) -> str:
    return f"\033[91m{text}\033[0m" if _COLOR else text

def _bold(text: str) -> str:
    return f"\033[1m{text}\033[0m" if _COLOR else text

def _yellow(text: str) -> str:
    return f"\033[93m{text}\033[0m" if _COLOR else text


def _run(cmd: list[str], label: str) -> bool:
    print(f"\n{_cyan('>')} {_bold(label)}")
    print(f"  {' '.join(cmd)}\n")
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.join(_PROJECT_ROOT, "src") + os.pathsep + env.get("PYTHONPATH", "")

    result = subprocess.run(cmd, cwd=_PROJECT_ROOT, env=env)
    if result.returncode != 0:
        print(f"\n{_red('X')} {label} falló (exit code {result.returncode})")
        return False
    print(f"\n{_green('OK')} {label}")
    return True


def cmd_assets() -> bool:
    return _run([sys.executable, "-m", "competitividad_turistica.cli.generate"], "Assets - Ejecutando pipeline de datos")


def cmd_deploy() -> bool:
    return _run([sys.executable, "-m", "competitividad_turistica.cli.deploy"], "Deploy - Copiando al repo Jekyll")


def cmd_ver() -> bool:
    dashboard_path = os.path.join("src", "competitividad_turistica", "products", "dashboard", "app.py")
    print(f"\n{_cyan('>')} {_bold('Iniciando Dashboard Streamlit')}")
    return _run([sys.executable, "-m", "streamlit", "run", dashboard_path], "Streamlit Dashboard")


def cmd_test() -> bool:
    ok1 = _run([sys.executable, "-m", "pytest", "tests/", "-v"], "Tests - pytest")
    ok2 = _run([sys.executable, "-m", "ruff", "check", "src/", "tests/"], "Linting - ruff")
    return ok1 and ok2


def cmd_all() -> bool:
    if not cmd_assets():
        return False
    return cmd_deploy()


COMMANDS = {
    "assets":  lambda _: cmd_assets(),
    "deploy":  lambda _: cmd_deploy(),
    "ver":     lambda _: cmd_ver(),
    "test":    lambda _: cmd_test(),
    "all":     lambda _: cmd_all(),
}


def cmd_help() -> None:
    print(f"""
{_bold('Competitividad Turística - Comandos disponibles')}

  python run.py {_green('assets')}   Ejecuta el pipeline de datos
  python run.py {_green('deploy')}   Copia archivos al repo Jekyll
  python run.py {_green('ver')}      Lanza el dashboard de Streamlit
  python run.py {_green('test')}     Ejecuta tests (pytest) + linting (ruff)
  python run.py {_green('all')}      Pipeline completo: assets -> deploy

{_yellow('Ejemplo:')} python run.py all
""")


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help", "help"):
        cmd_help()
        sys.exit(0)
    command = args[0]
    if command not in COMMANDS:
        print(f"{_red('Error:')} Comando desconocido '{command}'")
        cmd_help()
        sys.exit(1)
    ok = COMMANDS[command](args[1:])
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

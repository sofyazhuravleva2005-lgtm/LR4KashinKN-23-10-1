#!/usr/bin/env bash
#
# deploy.sh — Скрипт развертывания Django-шаблона приложения.
#
# Что делает:
#   1. Проверяет окружение (Python, Poetry, переменные).
#   2. Устанавливает зависимости проекта.
#   3. Применяет миграции базы данных.
#   4. Собирает статические файлы.
#   5. (Опционально) создаёт суперпользователя из переменных окружения.
#   6. Запускает сервер Django.
#
# Использование:
#   ./deploy.sh                # полный цикл: установка + миграции + запуск
#   ./deploy.sh setup          # только подготовка (без запуска сервера)
#   ./deploy.sh run            # только запуск сервера
#   ./deploy.sh migrate        # только миграции
#   ./deploy.sh collectstatic  # только сбор статики
#   ./deploy.sh createsuperuser# создать суперпользователя из env
#
# Переменные окружения:
#   REPLIT_DOMAINS              — список разрешённых доменов (обязательно).
#   PORT                        — порт для запуска (по умолчанию 3000).
#   HOST                        — хост для запуска (по умолчанию 0.0.0.0).
#   DJANGO_SUPERUSER_USERNAME   — логин суперпользователя (опционально).
#   DJANGO_SUPERUSER_EMAIL      — email суперпользователя (опционально).
#   DJANGO_SUPERUSER_PASSWORD   — пароль суперпользователя (опционально).
#

set -euo pipefail

# ---------- Настройки ----------
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-3000}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

# ---------- Утилиты вывода ----------
log()  { printf '\033[1;34m[deploy]\033[0m %s\n' "$*"; }
ok()   { printf '\033[1;32m[ok]\033[0m %s\n'    "$*"; }
warn() { printf '\033[1;33m[warn]\033[0m %s\n'  "$*"; }
err()  { printf '\033[1;31m[error]\033[0m %s\n' "$*" >&2; }

# ---------- Проверки окружения ----------
check_env() {
  log "Проверка окружения..."

  if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    err "Не найден интерпретатор Python ($PYTHON_BIN)."
    exit 1
  fi
  ok "Python: $($PYTHON_BIN --version)"

  if [[ -z "${REPLIT_DOMAINS:-}" ]]; then
    warn "Переменная REPLIT_DOMAINS не задана. Использую localhost."
    export REPLIT_DOMAINS="localhost,127.0.0.1"
  fi

  cd "$PROJECT_ROOT"
}

# ---------- Установка зависимостей ----------
install_deps() {
  log "Установка зависимостей..."

  if command -v poetry >/dev/null 2>&1 && [[ -f "pyproject.toml" ]]; then
    poetry install --no-interaction --no-root || {
      warn "Poetry не справился, пробую через pip."
      "$PYTHON_BIN" -m pip install --upgrade pip
      "$PYTHON_BIN" -m pip install "Django>=5.0,<6.0"
    }
  elif [[ -f "requirements.txt" ]]; then
    "$PYTHON_BIN" -m pip install --upgrade pip
    "$PYTHON_BIN" -m pip install -r requirements.txt
  else
    "$PYTHON_BIN" -m pip install --upgrade pip
    "$PYTHON_BIN" -m pip install "Django>=5.0,<6.0"
  fi

  ok "Зависимости установлены."
}

# ---------- Миграции ----------
run_migrations() {
  log "Применение миграций базы данных..."
  "$PYTHON_BIN" manage.py migrate --noinput
  ok "Миграции применены."
}

# ---------- Сбор статики ----------
collect_static() {
  log "Сбор статических файлов..."
  if "$PYTHON_BIN" manage.py collectstatic --noinput >/dev/null 2>&1; then
    ok "Статика собрана."
  else
    warn "collectstatic пропущен (не настроен STATIC_ROOT)."
  fi
}

# ---------- Суперпользователь ----------
create_superuser() {
  if [[ -n "${DJANGO_SUPERUSER_USERNAME:-}" \
     && -n "${DJANGO_SUPERUSER_PASSWORD:-}" \
     && -n "${DJANGO_SUPERUSER_EMAIL:-}" ]]; then
    log "Создание суперпользователя '$DJANGO_SUPERUSER_USERNAME'..."
    "$PYTHON_BIN" manage.py createsuperuser --noinput \
      --username "$DJANGO_SUPERUSER_USERNAME" \
      --email    "$DJANGO_SUPERUSER_EMAIL" 2>/dev/null \
      && ok "Суперпользователь создан." \
      || warn "Суперпользователь уже существует или не удалось создать."
  else
    log "Переменные DJANGO_SUPERUSER_* не заданы — пропускаю создание суперпользователя."
  fi
}

# ---------- Запуск сервера ----------
run_server() {
  log "Запуск Django runserver на ${HOST}:${PORT}..."
  exec "$PYTHON_BIN" manage.py runserver "${HOST}:${PORT}"
}

# ---------- Основной поток ----------
main() {
  local cmd="${1:-all}"

  case "$cmd" in
    all)
      check_env
      install_deps
      run_migrations
      collect_static
      create_superuser
      run_server
      ;;
    setup)
      check_env
      install_deps
      run_migrations
      collect_static
      create_superuser
      ok "Подготовка завершена. Запустите './deploy.sh run' для старта сервера."
      ;;
    run)
      check_env
      run_server
      ;;
    migrate)
      check_env
      run_migrations
      ;;
    collectstatic)
      check_env
      collect_static
      ;;
    createsuperuser)
      check_env
      create_superuser
      ;;
    install)
      check_env
      install_deps
      ;;
    -h|--help|help)
      sed -n '2,30p' "$0"
      ;;
    *)
      err "Неизвестная команда: $cmd"
      err "Используйте: $0 [all|setup|run|install|migrate|collectstatic|createsuperuser|help]"
      exit 1
      ;;
  esac
}

main "$@"

#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env"

echo "=== Настройка .env для Polya_bot ==="
echo

read -r -p "Введите BOT_TOKEN: " BOT_TOKEN
if [[ -z "${BOT_TOKEN}" ]]; then
  echo "BOT_TOKEN не может быть пустым." >&2
  exit 1
fi

echo
echo "ADMIN_USER_IDS — один id или несколько через запятую."
echo "Первый id будет использоваться как основной контакт (кнопка «Написать сейчас»)."
read -r -p "Введите ADMIN_USER_IDS: " ADMIN_USER_IDS
CLEANED=$(echo "${ADMIN_USER_IDS}" | tr -d '[:space:]')
if [[ -z "${CLEANED}" ]]; then
  echo "ADMIN_USER_IDS не может быть пустым." >&2
  exit 1
fi
if [[ ! "${CLEANED}" =~ ^[0-9]+(,[0-9]+)*$ ]]; then
  echo "ADMIN_USER_IDS должен быть числом или числами через запятую (например: 123,456)." >&2
  exit 1
fi

cat > "${ENV_FILE}" <<EOF
BOT_TOKEN=${BOT_TOKEN}
ADMIN_USER_IDS=${CLEANED}
EOF

echo
echo ".env создан: ${ENV_FILE}"
echo "Дальше: docker compose up -d --build"

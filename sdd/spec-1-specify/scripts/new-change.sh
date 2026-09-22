#!/bin/sh
# Создаёт каталог нового изменения sdd из шаблонов скилла spec-specify.
#
# Использование (из корня проекта-потребителя):
#   new-change.sh <имя>
#
# <имя> — "<id>-<slug>", где <id> — внешний идентификатор задачи (например
# PRJ-123) или порядковый номер NNN, <slug> — короткое kebab-case имя
# по-английски. Примеры: PRJ-123-dark-mode, 004-rate-limit-login.
set -eu

usage() {
	echo "использование: $0 <id>-<slug>   (например: $0 PRJ-123-dark-mode)" >&2
	exit 2
}

[ $# -eq 1 ] || usage
name=$1

case $name in
"" | -* | *- | *--*) usage ;;
*[!a-zA-Z0-9-]*)
	echo "ошибка: '$name' — допустимы только латиница, цифры и дефисы (kebab-case)" >&2
	exit 1
	;;
esac

dir=".specs/$name"
if [ -e "$dir" ]; then
	echo "ошибка: $dir уже существует — для обновления правь файлы на месте" >&2
	exit 1
fi

templates_dir=$(CDPATH= cd -- "$(dirname -- "$0")/../templates" && pwd)
mkdir -p "$dir"
for f in proposal.md spec.md; do
	cp "$templates_dir/$f" "$dir/$f"
done

echo "создано: $dir/proposal.md, $dir/spec.md"
echo "дальше: заполни их по инструкциям скилла spec-specify"

#!/bin/sh
# Установщик скиллов: https://gitrepo.ru/neonxp/skills
#
# Использование:
#   install.sh [НАБОР] [--agents СПИСОК|all]   установка (без НАБОР — все наборы)
#   install.sh --remove [НАБОР] [--agents …]   удаление копий и симлинков
#   install.sh --list                          списки наборов и агентов
#
# Правила установки — AGENTS.md в корне репозитория. Источник истины: ~/.agents/skills/
set -eu

REPO="${SKILLS_REPO:-https://gitrepo.ru/neonxp/skills}"
BRANCH="${SKILLS_BRANCH:-master}"
STORE="$HOME/.agents/skills"
SELF="${0:-}"

usage() {
	cat <<EOF
Установщик скиллов из $REPO

Использование:
  install.sh [НАБОР] [--agents СПИСОК|all]   установка (без НАБОР — все наборы)
  install.sh --remove [НАБОР] [--agents …]   удаление копий и симлинков
  install.sh --list                          списки наборов и агентов

Набор — верхняя директория репозитория, содержащая SKILL.md (например: mindcode).
--agents создаёт симлинки только для агентов с классом «симлинк» из AGENTS.md
(имена — как в таблице, через запятую, регистр не важен; полный список: --list).
Без --agents симлинки не создаются.
EOF
}

# Источник файлов: клон рядом со скриптом — или загрузка tarball (случай curl | sh),
# когда скрипт запущен не из репозитория.
if [ -f "$SELF" ] && [ -f "$(dirname "$SELF")/AGENTS.md" ]; then
	SRC="$(cd "$(dirname "$SELF")" && pwd)"
else
	TMP="$(mktemp -d)"
	echo "Загружаю $REPO (ветка $BRANCH)…"
	curl -fsSL "$REPO/archive/$BRANCH.tar.gz" | tar -xz -C "$TMP"
	SRC="$(cd "$TMP"/*/ && pwd)"
fi

all_skill_dirs() {
	find "$SRC" -name SKILL.md -not -path "*/.git/*" -exec dirname {} \; | sort
}

skill_dirs() { # $1 — набор или пусто (все)
	all_skill_dirs | if [ -n "${1:-}" ]; then grep "/$1/"; else cat; fi
}

list_agents() { # агенты класса «симлинк»: ИМЯ<tab>ДИРЕКТОРИЯ
	awk -F'|' '
		/^\| \*\*/ {
			name = $2; gsub(/\*/, "", name); gsub(/^ +| +$/, "", name);
			dir  = $3; gsub(/`/, "", dir);
			cls  = $4; gsub(/^ +| +$/, "", cls);
			if (cls == "симлинк") {
				sub(/\(.*/, "", dir); gsub(/\/+$/, "", dir); gsub(/^ +| +$/, "", dir);
				if (dir ~ /^~/) print name "\t" dir
			}
		}' "$SRC/AGENTS.md"
}

agent_selected() { # $1 — имя агента; AGENTS пусто/список/all
	[ -n "$AGENTS" ] || return 1
	[ "$AGENTS" = "all" ] && return 0
	name_lc="$(echo "$1" | tr "[:upper:]" "[:lower:]")"
	case ",$(echo "$AGENTS" | tr "[:upper:]" "[:lower:]"),"
	in *",${name_lc},"*) return 0 ;;
	esac
	return 1
}

expand_dir() {
	case "$1" in
	"~"*) printf '%s\n' "$HOME${1#\~}" ;;
	*) printf '%s\n' "$1" ;;
	esac
}

MODE="install"
GROUP=""
AGENTS=""
while [ $# -gt 0 ]; do
	case "$1" in
	--remove)
		MODE="remove"
		;;
	--list)
		MODE="list"
		;;
	--agents)
		[ $# -ge 2 ] || {
			echo "Ошибка: --agents требует список имён или all" >&2
			exit 1
		}
		AGENTS="$2"
		shift
		;;
	-h | --help)
		usage
		exit 0
		;;
	-*)
		echo "Ошибка: неизвестный флаг $1 (см. --help)" >&2
		exit 1
		;;
	*)
		[ -z "$GROUP" ] || {
			echo "Ошибка: укажите один набор (доступны: $(all_skill_dirs | awk -F/ -v s="$SRC/" '{sub(s,"",$0); print $1}' | sort -u | tr '\n' ' '))" >&2
			exit 1
		}
		GROUP="$1"
		;;
	esac
	shift
done

if [ "$MODE" = "list" ]; then
	echo "Наборы (верхние директории со скиллами):"
	all_skill_dirs | awk -F/ -v s="$SRC/" '{sub(s, "", $0); print "  " $1 "  →  скилл " $NF}'
	echo
	echo "Агенты, которым ставится симлинк (--agents «Имя», через запятую, или all):"
	list_agents | awk -F"\t" '{printf "  %-24s %s\n", $1, $2}'
	echo
	echo "Агенты, читающие ~/.agents/skills/ напрямую, и классы «вручную»/«—» — см. AGENTS.md."
	exit 0
fi

if [ -n "$GROUP" ] && ! skill_dirs "$GROUP" | grep -q .; then
	echo "Ошибка: набор «$GROUP» не найден. Доступны: $(all_skill_dirs | awk -F/ -v s="$SRC/" '{sub(s, "", $0); print $1}' | sort -u | tr '\n' ' ')" >&2
	exit 1
fi

if [ "$MODE" = "remove" ]; then
	skill_dirs "$GROUP" | while read -r dir; do
		name="$(basename "$dir")"
		rm -rf "$STORE/$name"
		echo "  − удалена копия $STORE/$name"
	done
	if [ -n "$AGENTS" ]; then
		list_agents | while IFS="$(printf '\t')" read -r name dir; do
			agent_selected "$name" || continue
			skill_dirs "$GROUP" | while read -r d; do
				skill="$(basename "$d")"
				link="$(expand_dir "$dir")/$skill"
				if [ -L "$link" ]; then
					rm "$link"
					echo "  − удалён симлинк $link"
				fi
			done
		done
	fi
	echo "Готово."
	exit 0
fi

mkdir -p "$STORE"
echo "Установка в $STORE:"
skill_dirs "$GROUP" | while read -r dir; do
	name="$(basename "$dir")"
	rm -rf "$STORE/$name"
	cp -R "$dir" "$STORE/$name"
	echo "  + $name"
done

if [ -n "$AGENTS" ]; then
	echo "Симлинки агентам:"
	list_agents | while IFS="$(printf '\t')" read -r name dir; do
		agent_selected "$name" || continue
		skill_dirs "$GROUP" | while read -r d; do
			skill="$(basename "$d")"
			target="$(expand_dir "$dir")"
			mkdir -p "$target"
			ln -sfn "$STORE/$skill" "$target/$skill"
			echo "  + $name: $target/$skill → $STORE/$skill"
		done
	done
fi

echo "Готово. Скиллы в $STORE — источник истины (правила: AGENTS.md)."

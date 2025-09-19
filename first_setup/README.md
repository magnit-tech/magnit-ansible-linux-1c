````markdown
# Роль first_setup - Первичная настройка сервера для 1С

Роль для первоначальной подготовки сервера перед установкой 1С:Предприятие.

## Назначение

Автоматизирует:
- Создание системных пользователей и групп
- Настройку файловой системы
- Установку зависимостей
- Копирование шрифтов
- Подготовку каталогов

## Переменные

### Основные переменные

| Переменная | По умолчанию | Описание |
|------------|--------------|----------|
| `srv1c_user` | `usr1cv8` | Пользователь для служб 1С |
| `srv1c_group` | `grp1cv8` | Группа для 1С |
| `base_dir` | `/opt/1cv8` | Базовый каталог установки |

### Пути каталогов

```yaml
font_dir: "/usr/share/fonts/truetype/1c"
temp_dir: "/tmp/1c_install"
log_dir: "/var/log/1c"
````

### Настройки шрифтов

| Переменная | Значение |
|------------|----------|
| `copy_fonts` | true |
| `fonts_source` | "{{ playbook\_dir }}/fonts" |

## Зависимости

- Требуется sudo-доступ
- Доступ к интернету для установки пакетов
- 2+ ГБ свободного места

## Пример использования

В `group_vars/serv1C.yml`:

```yaml
first_setup:
  srv1c_user: "custom_1c_user"
  base_dir: "/opt/custom_1c_path"
```

## Выполняемые задачи

1. Создание пользователя и группы:
```bash
sudo groupadd {{ srv1c_group }}
sudo useradd -g {{ srv1c_group }} {{ srv1c_user }}
```
2. Создание каталогов:
```
/opt/1cv8/
├── conf
├── logs
└── distr
```
3. Копирование шрифтов:
```bash
cp {{ fonts_source }}/* {{ font_dir }}/
fc-cache -f -v
```
4. Установка пакетов:
    - `fontconfig`
    - `libgsf-1-common`
    - `ttf-mscorefonts-installer`

## Рекомендации

1. Для повторного запуска с очисткой:
```bash
ansible-playbook -i hosts side.yml --tags first_setup -e "clean_old=true"
```
2. Для пропуска установки шрифтов:
```bash
ansible-playbook -i hosts side.yml --tags first_setup -e "copy_fonts=false"
```

## Troubleshooting

| Ошибка | Решение |
|--------|---------|
| User already exists | Использовать `force_recreate: true` |
| Fonts not loading | Проверить права в `{{ font_dir }}` |
| Permission denied | Проверить sudo-права |

---


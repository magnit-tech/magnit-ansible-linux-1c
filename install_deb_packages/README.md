роль install_deb_packages

```markdown
# Роль `install_deb_packages` - Установка DEB-пакетов

Роль для управления установкой DEB-пакетов на целевых серверах.

## Назначение

Автоматизирует:
- Установку и обновление DEB-пакетов
- Настройку репозиториев
- Установку локальных .deb файлов
- Управление зависимостями

## Основные переменные

### Основные параметры

| Переменная | По умолчанию | Описание |
|------------|--------------|----------|
| `deb_repositories` | [] | Список репозиториев |
| `deb_packages` | [] | Пакеты из репозиториев |
| `local_deb_files` | [] | Локальные .deb файлы |

### Пример конфигурации

```yaml
deb_repositories:
  - deb http://archive.ubuntu.com/ubuntu focal main restricted
  - deb http://archive.ubuntu.com/ubuntu focal-updates main restricted

deb_packages:
  - fontconfig
  - ttf-mscorefonts-installer
  - libgsf-1-common

local_deb_files:
  - /distr/deb/custom-package.deb
```

## Зависимости

- Доступ к интернету (для пакетов из репозиториев)
- Настроенные sudo-права
- Доступ к локальным .deb файлам

## Пример использования

### В `group_vars/all.yml`:
```yaml
install_deb_packages:
  deb_packages:
    - htop
    - mc
    - ncdu
```

### В playbook:
```yaml
- hosts: all
  roles:
    - role: install_deb_packages
      vars:
        deb_repositories:
          - deb http://ppa.launchpad.net/ansible/ansible/ubuntu focal main
```

## Выполняемые задачи

1. Добавление репозиториев:
   ```bash
   add-apt-repository -y "deb http://archive.ubuntu.com/ubuntu focal main"
   ```

2. Обновление кэша пакетов:
   ```bash
   apt-get update -y
   ```

3. Установка пакетов:
   ```bash
   apt-get install -y fontconfig ttf-mscorefonts-installer
   ```

4. Установка локальных пакетов:
   ```bash
   dpkg -i /distr/deb/custom-package.deb
   ```

## Особенности работы

### Поддерживаемые источники:
- Официальные репозитории
- PPA-репозитории
- Локальные .deb файлы

### Обработка зависимостей:
- Автоматическое разрешение зависимостей
- Проверка уже установленных пакетов
- Возможность принудительной переустановки

## Управление пакетами

### Полезные команды:
```bash
# Проверить установленные пакеты
dpkg -l | grep package-name

# Удалить пакет
apt-get remove package-name

# Очистить кэш
apt-get clean
```

## Troubleshooting

| Проблема | Решение |
|----------|---------|
| Ошибка GPG | Добавить ключ: `apt-key adv --keyserver keyserver.ubuntu.com --recv-keys KEYID` |
| Пакет не найден | Проверить доступность репозитория |
| Конфликт версий | Использовать точную версию: `package=1.2.3` |


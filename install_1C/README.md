````markdown
# Роль `install_1C` - Установка платформы 1С:Предприятие

Роль для автоматизированной установки серверных компонентов 1С:Предприятие.

## Назначение

Автоматизирует:
- Установку серверных компонентов 1С
- Удаление предыдущих версий (опционально)
- Настройку параметров установки
- Проверку корректности установки

## Переменные

### Основные параметры

| Переменная | По умолчанию | Обязательная | Описание |
|------------|--------------|--------------|----------|
| `onec_version_name` | - | Да | Версия 1С (например 8.3.22.1709) |
| `install_distrib_path` | `/distr/platform` | Да | Путь к дистрибутиву |
| `install_file_name` | `setup-full-{{ onec_version_name }}-x86_64.run` | Нет | Имя файла дистрибутива |
| `remove_old_versions` | `true` | Нет | Удалять ли предыдущие версии |

### Параметры установки

```yaml
components:
  - server
  - server_admin
  - ws
  - libgs
````

### Пути установки

| Переменная | Значение по умолчанию |
|------------|-----------------------|
| `install_dir` | `/opt/1cv8` |
| `conf_dir` | `/opt/1cv8/conf` |
| `log_dir` | `/var/log/1cv8` |

## Зависимости

- Требуется выполненная роль `first_setup`
- 5+ ГБ свободного места
- Доступ к дистрибутиву платформы

## Пример использования

### В inventory файле:

```ini
[serv1C]
host1 onec_version_name=8.3.22.1709 install_distrib_path=/mnt/distr
```

### В group\_vars:

```yaml
install_1C:
  components:
    - server
    - server_admin
  remove_old_versions: false
```

## Выполняемые задачи

1. Проверка наличия дистрибутива:
```bash
ls -l {{ install_distrib_path }}/{{ install_file_name }}
```
2. Удаление старых версий (если `remove_old_versions=true`):
```bash
/opt/1cv8/x86_64/8.3.XX.XXXX/uninstall
```
3. Установка новых компонентов:
```bash
./setup-full-8.3.22.1709-x86_64.run --mode unattended --enable-components {{ components|join(',') }}
```
4. Проверка установки:
```bash
/opt/1cv8/x86_64/{{ onec_version_name }}/ragent --version
```

## Особенности установки

### Поддерживаемые компоненты:

- `server` - Сервер 1С
- `server_admin` - Администрирование
- `ws` - Веб-сервер
- `libgs` - Интеграция с СУБД

### Логи установки:

```
/var/log/1cv8/install.log
```

## Troubleshooting

| Ошибка | Решение |
|--------|---------|
| Дистрибутив не найден | Проверить `install_distrib_path` и `install_file_name` |
| Недостаточно места | Увеличить место в `/opt` |
| Ошибка удаления старых версий | Запустить с `remove_old_versions=false` |


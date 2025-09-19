````markdown
# Основной плейбук side.yml

Плейбук для базовой установки и настройки сервера 1С:Предприятие.

## Назначение

Автоматизирует:
- Первоначальную настройку сервера
- Установку платформы 1С
- Настройку сервисов ragent и RAS
- Публикацию информационных баз

## Схема работы

```mermaid
graph TD
    A[first_setup] --> B[install_1C]
    B --> C[install_ragent]
    C --> D[install_ras]
    D --> E[publishing]
````

## Переменные плейбука

Основные переопределяемые переменные в `group_vars` или `host_vars`:

| Переменная | По умолчанию | Описание |
|------------|--------------|----------|
| `onec_version_name` | - | Версия 1С (8.3.XX.XXXX) |
| `ins_dir_src` | `/distr/platform` | Путь к дистрибутивам |
| `SRV1CV8_PORT` | 1540 | Порт ragent |
| `SRV1CV8_REGPORT` | 1541 | Порт rmngr |
| `SRV1CV8_RANGE` | 1560:1591 | Диапазон портов rphost |
| `RAS_PORT` | 1539 | Порт сервера RAS |

## Запуск

```bash
ansible-playbook -i hosts side.yml -K
```

Параметры:

- `-K` - запрос пароля sudo
- `--tags` - выборочный запуск ролей (например, `--tags install_1C,publishing`)

## Состав ролей

1. [first\_setup](vector://vector/first_setup/README.md) - подготовка окружения
2. [install\_1C](vector://vector/install_1C/README.md) - установка платформы
3. [install\_ragent](vector://vector/install_ragent/README.md) - настройка сервисов
4. [install\_ras](vector://vector/install_ras/README.md) - сервер администрирования
5. [publishing](vector://vector/publishing/README.md) - публикация ИБ

## Пример inventory

```ini
[serv1C]
host1 ansible_host=some_host_ip onec_version_name=8.3.21.1393
host2 ansible_host=some_host_ip onec_version_name=8.3.22.1709

[serv1C:vars]
ansible_user=admin
SRV1CV8_DEBUG=true
```

## Рекомендации

1. Для повторной установки можно отключить `first_setup` (--skip-tags first\_setup)
2. Для отладки используйте флаг `SRV1CV8_DEBUG=true`
3. Логирование: добавить `-vvv` для подробного вывода

См. также [полную документацию](vector://vector/README.md) репозитория.

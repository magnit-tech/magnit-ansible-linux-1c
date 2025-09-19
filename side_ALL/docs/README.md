````markdown
# Плейбук side_ALL.yml - Полная установка инфраструктуры 1С


Полный плейбук для развертывания всей инфраструктуры 1С, включая:
- Установку платформы
- Настройку сервисов
- Публикацию баз
- Интеграцию с дополнительными системами

## Схема выполнения

```mermaid
graph LR
    A[first_setup] --> B[install_1C]
    B --> C[install_ragent]
    C --> D[install_ras]
    D --> E[publishing]
    E --> F[monitoring]
    F --> G[vector_logging]
    G --> H[security]
````

## Основные переменные

### Глобальные настройки

| Переменная | По умолчанию | Описание |
|------------|--------------|----------|
| `onec_version_name` | 8.3.22.1709 | Версия платформы |
| `ins_dir_src` | /distr/platform | Путь к дистрибутивам |
| `srv1c_service_user` | usr1cv8 | Пользователь служб |

### Настройки портов

| Переменная | Значение по умолчанию |
|------------|-----------------------|
| `SRV1CV8_PORT` | 1540 |
| `SRV1CV8_REGPORT` | 1541 |
| `SRV1CV8_RANGE` | 1560:1591 |
| `RAS_PORT` | 1539 |

### Флаги компонентов

```yaml
enable_monitoring: true    # Включение мониторинга
enable_vector_logging: true # Отправка логов в OpenSearch
enable_license_tools: true # Установка лицензионных утилит
```

## Запуск плейбука

### Полная установка

```bash
ansible-playbook -i hosts side_ALL.yml -K
```

### Выборочный запуск

```bash
# Только установка 1С и сервисов
ansible-playbook -i hosts side_ALL.yml --tags "1c_installation,services" -K

# Только веб-компоненты
ansible-playbook -i hosts side_ALL.yml --tags "web,publishing" -K
```

## Состав ролей

### Основные компоненты

1. **first\_setup** - Базовая настройка ОС
2. **install\_1C** - Установка платформы
3. **install\_ragent** - Сервисы кластера
4. **publishing** - Публикация ИБ

### Дополнительные компоненты

1. **setup\_apache** - Веб-сервер
2. **monitoring\_1C** - Мониторинг Zabbix
3. **install\_vector4opensearch** - Логирование

### Интеграции

1. **deploy\_configure\_keytabs** - Kerberos аутентификация
2. **install\_lictools** - Лицензирование

## Пример inventory

```ini
[serv1C]
srv1c-prod-01 ansible_host=some_host_ip onec_version_name=8.3.22.1709
srv1c-test-01 ansible_host=some_host_ip onec_version_name=8.3.21.1393

[web_servers]
web1c-01 ansible_host=some_host_ip

[serv1C:vars]
ansible_user=admin
SRV1CV8_DEBUG=true
```

## Логирование и отладка

### Просмотр логов

```bash
ansible-playbook -i hosts side_ALL.yml -vvv
```

### Проверка конфигурации

```bash
ansible-playbook -i hosts side_ALL.yml --check
```

## Рекомендации

1. **Порядок выполнения**:
```
first_setup → install_1C → services → web → monitoring
```
2. **Переопределение переменных**:
```bash
ansible-playbook -i hosts side_ALL.yml -e "onec_version_name=8.3.23.1689"
```
3. **Ограничение по хостам**:
```bash
ansible-playbook -i hosts side_ALL.yml --limit web_servers
```

## Troubleshooting

| Ошибка | Решение |
|--------|---------|
| Port already in use | Проверить `SRV1CV8_PORT` в `group_vars` |
| Missing distribution file | Убедиться в наличии файла в `{{ ins_dir_src }}` |
| Permission denied | Проверить права `srv1c_service_user` |

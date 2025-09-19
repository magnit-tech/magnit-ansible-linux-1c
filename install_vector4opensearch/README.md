```markdown
# Роль `install_vector4opensearch` - Настройка логирования в OpenSearch

Роль для настройки отправки логов 1С:Предприятие в OpenSearch через Vector.

## Назначение

Автоматизирует:
- Установку и настройку Vector
- Конфигурацию сбора логов 1С
- Настройку отправки в OpenSearch/ClickHouse
- Ротацию и обработку логов
- Интеграцию с мониторингом

## Основные переменные

### Обязательные параметры

| Переменная | По умолчанию | Описание |
|------------|--------------|----------|
| `vector_version` | `0.28.1` | Версия Vector |
| `opensearch_host` | `opensearch.example.com` | Хост OpenSearch |
| `logs_path` | `/var/log/1cv8` | Путь к логам 1С |

### Параметры OpenSearch

```yaml
opensearch:
  scheme: "https"
  port: 9200
  index: "1c-logs-%Y.%m.%d"
  auth:
    username: "vector-user"
    password: "{{ vault_opensearch_pass }}"
```

## Пример использования

### В `group_vars/logging_servers.yml`:
```yaml
install_vector4opensearch:
  opensearch_host: "opensearch.internal"
  logs_path: "/opt/1cv8/logs"
  vector_config:
    processing:
      batch_size: 1048576
    sinks:
      opensearch:
        compression: "gzip"
```

## Выполняемые задачи

1. Установка Vector:
   ```bash
   curl -1sLf 'https://repositories.timber.io/public/vector/cfg/setup/bash.deb.sh' | sudo bash
   apt-get install vector
   ```

2. Настройка конфигурации:
   ```bash
   /etc/vector/vector.yaml
   /etc/1cv8/conf/logcfg.xml
   ```

3. Включение сервиса:
   ```bash
   systemctl enable --now vector
   ```

## Конфигурация Vector

### Пример конфига:
```yaml
sources:
  1c_logs:
    type: "file"
    include: ["/var/log/1cv8/*.log"]

transforms:
  parse_1c:
    type: "remap"
    inputs: ["1c_logs"]
    source: |
      . = parse_log!(.message)

sinks:
  opensearch:
    type: "opensearch"
    inputs: ["parse_1c"]
    endpoint: "some_host_url"
```

## Интеграция с 1С

### Настройка logcfg.xml:
```xml
<log>
  <location>/var/log/1cv8/1c.log</location>
  <format>%d %t %l %m</format>
</log>
```

## Troubleshooting

| Проблема | Решение |
|----------|---------|
| Нет логов в OpenSearch | Проверить `vector logs` |
| Ошибка парсинга | Настроить transform-правила |
| Нехватка памяти | Увеличить `batch_size` |

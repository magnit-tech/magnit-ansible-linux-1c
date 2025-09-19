# Роль `setup_apache` - Настройка веб-сервера Apache для 1С

![Apache Version](https://img.shields.io/badge/Apache-2.4%2B-orange)
![1C Ready](https://img.shields.io/badge/1C%20Compatible-8.3%2B-blue)

Роль для полной настройки веб-сервера Apache для работы с 1С:Предприятие.

## Назначение

Автоматизирует:
- Установку и базовую настройку Apache
- Конфигурацию SSL/TLS
- Настройку модулей для работы с 1С
- Оптимизацию параметров производительности
- Настройку безопасности

## Основные переменные

### Обязательные параметры

| Переменная | По умолчанию | Описание |
|------------|--------------|----------|
| `apache_version` | 2.4 | Версия Apache |
| `apache_ssl_enabled` | true | Включение HTTPS |
| `apache_server_name` | `1c.example.com` | Имя сервера |

### Параметры SSL

```yaml
apache_ssl:
  cert_path: "/etc/ssl/certs/1c.crt"
  key_path: "/etc/ssl/private/1c.key"
  chain_path: "/etc/ssl/certs/ca.crt"
  dhparam_path: "/etc/ssl/dhparam.pem"
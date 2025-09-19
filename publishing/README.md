````markdown
# Роль `publishing` - Публикация информационных баз

Роль для автоматизированной публикации информационных баз на веб-сервере.

## Назначение
- Публикация ИБ в Apache/Nginx
- Настройка HTTPS доступа
- Конфигурация пулов рабочих процессов
- Управление параметрами публикации

## Основные переменные

### Обязательные параметры
```yaml
publishing_list:
  - name: "ib_name"
    desc: "Описание базы"
    db: "postgresql" # или "mssql"
    db_server: "db.example.com"
    db_name: "ib_db"
    db_user: "user1c"
    published: true
````

### Дополнительные настройки

| Переменная | По умолчанию | Описание |
|------------|--------------|----------|
| `apache_conf_dir` | `/etc/apache2/sites-available` | Каталог конфигов |
| `ssl_enabled` | true | Включение HTTPS |
| `workers_count` | 4 | Количество воркеров |

## Пример использования

```yaml
# В inventory или group_vars
publishing:
  publishing_list:
    - name: "Accounting"
      desc: "Основная бухгалтерия"
      db: "postgresql"
      db_server: "pgsql01.corp"
      db_name: "accounting_db"
```

## Выполняемые задачи

1. Создание конфигурационных файлов:
```
/etc/apache2/sites-available/ib_name.conf
```
2. Настройка прав доступа:
```bash
chown -R usr1cv8:grp1cv8 /var/www/ib_name
```
3. Активация сайта:
```bash
a2ensite ib_name.conf
```

## Особенности

- Поддержка Let's Encrypt (при `ssl_enabled=true`)
- Автоматическая перегенерация конфигов при изменении
- Интеграция с мониторингом

---

◀ [К списку ролей](vector://vector/README.md) | [Настройка Apache](vector://vector/setup_apache/README.md)

````

### setup_apache/README.md (Настройка Apache)
```markdown
# Роль `setup_apache` - Настройка веб-сервера Apache

![Apache](https://img.shields.io/badge/Apache-2.4%2B-orange)
![1C](https://img.shields.io/badge/1C-WebServer-blue)

Роль для базовой настройки Apache под требования 1С:Предприятие.

## Назначение
- Установка и настройка Apache
- Конфигурация модулей
- Настройка SSL/TLS
- Оптимизация параметров

## Основные переменные

### Обязательные параметры
```yaml
apache_modules:
  - "ssl"
  - "rewrite"
  - "proxy"
  - "proxy_http"
````

### Настройки производительности

| Переменная | Значение | Описание |
|------------|----------|----------|
| `max_workers` | 100 | Макс. соединений |
| `timeout` | 300 | Таймаут (сек) |
| `keepalive` | "On" | Keep-Alive |

## Пример конфигурации

```yaml
# В group_vars/web_servers.yml
setup_apache:
  ssl_cert: "/etc/ssl/certs/1c.crt"
  ssl_key: "/etc/ssl/private/1c.key"
  server_name: "1c.example.com"
```

## Выполняемые задачи

1. Установка пакетов:
```bash
apt install apache2 libapache2-mod-wsgi
```
2. Настройка модулей:
```bash
a2enmod ssl rewrite proxy
```
3. Генерация DH-параметров:
```bash
openssl dhparam -out /etc/ssl/dhparam.pem 2048
```

## Безопасность

- Отключение ненужных модулей
- Настройка безопасных шифров
- Ограничение доступа по IP (опционально)

## Troubleshooting

| Проблема | Решение |
|----------|---------|
| 502 Bad Gateway | Проверить workers |
| SSL ошибки | Проверить сертификаты |
| Медленная работа | Настроить кэширование |

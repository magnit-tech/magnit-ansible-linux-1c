````markdown
# Роль `install_ragent` - Настройка сервисов 1С:Предприятие

Роль для настройки и управления основными сервисами 1С:Предприятие.

## Назначение

Автоматизирует:
- Создание systemd-юнитов для сервисов 1С
- Настройку параметров запуска
- Управление портами сервисов
- Конфигурацию отладки

## Основные переменные

### Параметры сервисов

| Переменная | По умолчанию | Описание |
|------------|--------------|----------|
| `srv1c_user` | `usr1cv8` | Пользователь для запуска |
| `srv1c_group` | `grp1cv8` | Группа сервисов |
| `srv1c_home` | `/opt/1cv8` | Базовый каталог |

### Настройки портов

| Параметр | Значение по умолчанию | Диапазон |
|----------|-----------------------|----------|
| `ragent_port` | 1540 | 1500-1600 |
| `rmngr_port` | 1541 | 1500-1600 |
| `rphost_range` | 1560:1591 | 1550-1650 |

### Параметры отладки

```yaml
debug_enabled: false
debug_port: 1555
debug_usr: "debug_user"
````

## Зависимости

- Установленная платформа 1С (роль `install_1C`)
- Настроенные пользователи (роль `first_setup`)
- Доступные порты в firewall

## Пример конфигурации

### В `group_vars/serv1C.yml`:

```yaml
install_ragent:
  ragent_port: 1542
  rmngr_port: 1543
  debug_enabled: true
```

## Выполняемые задачи

1. Создание конфигурационных файлов:
```bash
/etc/systemd/system/srv1cv8@.service
/etc/1cv8/conf/ragent.conf
```
2. Настройка сервисов:
```bash
systemctl enable srv1cv8@{ragent,rmngr,rphost}.service
```
3. Открытие портов в firewall:
```bash
firewall-cmd --add-port={1540-1591}/tcp --permanent
```

## Управление сервисами

### Команды для ручного управления:

```bash
# Статус сервисов
systemctl status srv1cv8@ragent

# Перезапуск
systemctl restart srv1cv8@ragent

# Включение отладки
systemctl start srv1cv8@dbgs
```

## Особенности конфигурации

### Шаблон systemd-юнита:

```ini
[Unit]
Description=1C:Enterprise %i
After=network.target

[Service]
User={{ srv1c_user }}
ExecStart={{ srv1c_home }}/x86_64/{{ onec_version }}/%i -port %p
Restart=always
```

## Troubleshooting

| Проблема | Решение |
|----------|---------|
| Port conflict | Проверить `netstat -tulnp` |
| Permission denied | Проверить права `srv1c_user` |
| Service failed | Проверить `journalctl -u srv1cv8@ragent` |


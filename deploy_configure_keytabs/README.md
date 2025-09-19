```markdown
# Роль `deploy_configure_keytabs` - Развертывание и настройка keytab-файлов

Роль для безопасного развертывания и настройки Kerberos keytab-файлов на серверах 1С.

## Назначение

Автоматизирует:
- Развертывание keytab-файлов
- Настройку прав доступа
- Проверку валидности ключей
- Инициализацию Kerberos-тикетов
- Интеграцию с 1С:Предприятие

## Основные переменные

### Обязательные параметры

| Переменная | По умолчанию | Описание |
|------------|--------------|----------|
| `keytab_files` | [] | Список keytab-файлов |
| `keytab_owner` | `usr1cv8` | Владелец файлов |
| `keytab_group` | `grp1cv8` | Группа файлов |

### Пример конфигурации

```yaml
keytab_files:
  - src: "/distr/keytabs/srv1c.keytab"
    dest: "/opt/1cv8/conf/srv1c.keytab"
    mode: "0640"
    principal: "1cservice/server.example.com@EXAMPLE.COM"
```

## Зависимости

- Установленные компоненты 1С
- Настроенный Kerberos-клиент
- Доступ к контроллеру домена
- Настроенные DNS-имена

## Пример использования

### В `group_vars/serv1C.yml`:
```yaml
deploy_configure_keytabs:
  keytab_files:
    - src: "{{ playbook_dir }}/files/keytabs/srv1c.keytab"
      dest: "/opt/1cv8/conf/srv1c.keytab"
      principal: "1cservice/{{ inventory_hostname }}@CORP.DOMAIN"
```

## Выполняемые задачи

1. Развертывание keytab-файлов:
   ```bash
   install -o usr1cv8 -g grp1cv8 -m 640 srv1c.keytab /opt/1cv8/conf/
   ```

2. Проверка keytab:
   ```bash
   klist -kte /opt/1cv8/conf/srv1c.keytab
   ```

3. Получение тикета:
   ```bash
   kinit -kt /opt/1cv8/conf/srv1c.keytab 1cservice/server.example.com
   ```

4. Настройка 1С для использования keytab:
   ```bash
   /opt/1cv8/x86_64/8.3.XX.XXXX/ras --cluster <cluster_id> --set-keytab /opt/1cv8/conf/srv1c.keytab
   ```

## Особенности безопасности

- Проверка контрольных сумм файлов
- Строгие права доступа (640)
- Валидация principal-имен
- Автоматическая ротация логов

## Интеграция с 1С

### Параметры в конфигурации кластера:
```
[Security]
Keytab = /opt/1cv8/conf/srv1c.keytab
Kerberos = true
```

## Troubleshooting

| Проблема | Решение |
|----------|---------|
| Ошибка kinit | Проверить системное время и principal |
| Доступ запрещен | Проверить права на keytab-файл |
| Неверный principal | Обновить keytab на контроллере домена |

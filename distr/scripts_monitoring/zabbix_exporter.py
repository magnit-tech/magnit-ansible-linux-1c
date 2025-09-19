#!/usr/bin/env python3
# VER 1.02
import argparse
from pickle import TRUE
import subprocess
import psycopg2
import socket
from time import time
import shutil
import os

#==== Ограничение времени, которое могло пройти с момента перезапуска служб 1C ====
LIMIT_TIME_1C_RESTART = 300
#==== Глобальная переменная с иформацией о перезапуске служб 1C ====
is_1c_restart = False
#==== Путь к timestamp-файлу ====
TIMESTAMP_PATH = "/tmp/1c_restart_time.tmp"
#=========

#======== Основные параметры ========
zabbix_metric_1c  = "availability1c"        #Название метрики в Zabbix
zabbix_metric_lic = "availabilitykey"
ras_cluster_user  = ""                      #Пустые переменные необходимы для доменной аутентификации
ras_cluster_pass  = ""                      #Пустые переменные необходимы для доменной аутентификации

#======== Параметры СУБД ========
pg_zabbix_metric_1c = "availabilitysql"

#====== Параметры по-умолчанию ======
zabbix_sender_path   = "/usr/bin/zabbix_sender"
pathToPlatform1c     = "/opt/1cv8/x86_64/8.3.22.1851"
zabbix_server        = "some_host_ip"
zabbix_port          = "10055"

#=========Инициализация параметров
ras_server        = "" 
zabbix_host       = "" 
pg_user           = ""
pg_pass           = ""
pg_server         = ""
#=========

#====== Общие методы разбора сообщений rac ======

def fn_dict_by_rac_info(text):
   result = dict()
   list = text.split('\n')
   for element_of_list in list:
      if element_of_list=="":
         next
      list_of_data = element_of_list.split(':')
      if len(list_of_data)==2:
         key = list_of_data[0].strip()
         value = list_of_data[1].strip()
         result[key] = value
   return result
 
def fn_list_of_dict_by_rac_info(text):
   result = []
   list = text.split('\n\n')

   for i in range(len(list)-1):
      if list[i]=="":
         next
      info = fn_dict_by_rac_info(list[i])
      result.append(info)
   return result


#====== Базовые команды rac ======

def fn_server_info(ras_server, cluster_id, server_id):
   srvcmd = pathToPlatform1c + "/rac " + ras_server + " server --cluster=" + cluster_id
   srvcmd = srvcmd + "" if ras_cluster_user == "" else srvcmd + " --cluster-user=" + ras_cluster_user + " --cluster-pwd=" + ras_cluster_pass
   srvcmd = srvcmd + " info --server="+server_id

   cmdresult = subprocess.check_output(srvcmd, shell=True)
   dsvrname = cmdresult.decode()
   dsvrname = dsvrname.lower()
   result = fn_dict_by_rac_info(dsvrname)
   return result

def fn_list_servers(ras_server, cluster_id):
   srvcmd = pathToPlatform1c + "/rac " + ras_server + " server --cluster=" + cluster_id
   srvcmd = srvcmd + "" if ras_cluster_user == "" else srvcmd + " --cluster-user=" + ras_cluster_user + " --cluster-pwd=" + ras_cluster_pass
   srvcmd = srvcmd + " list"

   cmdresult = subprocess.check_output(srvcmd, shell=True)
   dsvrname = cmdresult.decode()
   dsvrname = dsvrname.lower()
   
   result = fn_list_of_dict_by_rac_info(dsvrname)
   return result

def fn_list_rules(ras_server, cluster_id, server_id):
   srvcmd = pathToPlatform1c + "/rac " + ras_server + " rule --cluster=" + cluster_id
   srvcmd = srvcmd + "" if ras_cluster_user == "" else srvcmd + " --cluster-user=" + ras_cluster_user + " --cluster-pwd=" + ras_cluster_pass
   srvcmd = srvcmd + " list --server=" + server_id

   cmdresult = subprocess.check_output(srvcmd, shell=True)
   dsvrname = cmdresult.decode()
   dsvrname = dsvrname.lower()
   result = fn_list_of_dict_by_rac_info(dsvrname)
   return result

def fn_list_process(ras_server, cluster_id):
   srvcmd = pathToPlatform1c + "/rac " + ras_server + " process --cluster=" + cluster_id
   srvcmd = srvcmd + "" if ras_cluster_user == "" else srvcmd + " --cluster-user=" + ras_cluster_user + " --cluster-pwd=" + ras_cluster_pass
   srvcmd = srvcmd + " list"

   cmdresult = subprocess.check_output(srvcmd, shell=True)
   dsvrname = cmdresult.decode()
   dsvrname = dsvrname.lower()
   result = fn_list_of_dict_by_rac_info(dsvrname)
   return result

def fn_list_clusters(ras_server):
   srvcmd = pathToPlatform1c + "/rac " + ras_server + " cluster list"
   srvcmd = srvcmd + "| awk '/^cluster/' | awk '{print $3}'"

   cmdresult = subprocess.check_output(srvcmd, shell=True)
   dsvrname = cmdresult.decode()
   dsvrname = dsvrname.lower()
   result = dsvrname.split('\n')
   return result

def fn_list_bases(ras_server, cluster_id):
   srvcmd = pathToPlatform1c + "/rac " + ras_server + " infobase --cluster=" + cluster_id
   srvcmd = srvcmd + "" if ras_cluster_user == "" else srvcmd + " --cluster-user=" + ras_cluster_user + " --cluster-pwd=" + ras_cluster_pass
   srvcmd = srvcmd + " summary list"

   cmdresult = subprocess.check_output(srvcmd, shell=True)
   dsvrname = cmdresult.decode()
   dsvrname = dsvrname.lower()
   result = fn_list_of_dict_by_rac_info(dsvrname)
   return result


#====== Методы для получения статуса сервера лицензирования ======

def fn_rule_is_license_service(rule_info):
   
   result = False
   
   if rule_info["object-type"]=='"licenseservice"' and rule_info["rule-type"] == "always":
      result = True
   
   return result

def fn_host_is_active(ras_server, cluster_id, host):
   result = False
   list_process = fn_list_process(ras_server, cluster_id)
   for process in list_process:
      if process["host"] == host and process["is-enable"]=="yes" and process["running"]=="yes":
         result = True
   return result

def fn_server_is_license_service(ras_server, cluster_id, server_id):
   
   list_rules = fn_list_rules(ras_server, cluster_id, server_id)
   have_rules_license_service = False
   for rule in list_rules:
      if fn_rule_is_license_service(rule)==True:
         have_rules_license_service = True

   return have_rules_license_service


#====== Методы для получения статуса информационной базы ======

def fn_base_id_by_name(ras_server, cluster_id, base_name):
   list_base = fn_list_bases(ras_server, cluster_id)
   
   for base in list_base:
      if base["name"] == base_name:
         return base["infobase"]


   raise Exception("База " + base_name + " не найдена") 

def fn_base_is_active(ras_server, cluster_id, base_id):
   srvcmd = pathToPlatform1c + "/rac " + ras_server + " infobase --cluster=" + cluster_id
   srvcmd = srvcmd + "" if ras_cluster_user == "" else srvcmd + " --cluster-user=" + ras_cluster_user + " --cluster-pwd=" + ras_cluster_pass
   srvcmd = srvcmd + " info --infobase=" + base_id + ' --infobase-user=usr --infobase-pwd=pwd2'
   cmdresult = subprocess.run(srvcmd, shell=True, timeout=10, capture_output=True)
   if cmdresult.returncode == 0:
      return True
   else:
      error_text = cmdresult.stderr.decode()
      if error_text.find("Недостаточно прав пользователя на информационную") > -1:
         return True
      elif error_text.find("Insufficient user rights for infobase") > -1:
         return True
      else:
         print (error_text)
         return False
   
def fn_base_is_active_by_name(ras_server, cluster_id, base_name):
   base_id = fn_base_id_by_name(ras_server, cluster_id, base_name)
   result = fn_base_is_active(ras_server, cluster_id, base_id)
   return result

def fn_base_is_destroy(ras_server, cluster_id, base_name):
   try:
      base_is_activ = fn_base_is_active_by_name(ras_server, cluster_id, base_name);
      return base_is_activ==False
   except Exception as e:
      print (e)
      return True

def fn_db_is_active(base_name):
   
   try:      
      conn = psycopg2.connect(dbname=base_name, user=pg_user, password=pg_pass, host=pg_server)           
      c = conn.cursor()
      c.execute("SELECT 1")
      return True
   except Exception as e:
      print (e)
      return False      


#====== Дополнительные методы ======

def send_result_zabbix(host,key,value):
   srvcmd = zabbix_sender_path +" -z " + zabbix_server + " -p " + zabbix_port + " -s " + host + " -k " + key + " -o " + value
   cmdresult = subprocess.check_output(srvcmd, shell=True, timeout=20)
   result = cmdresult.decode()
   print (result)

# Проверка начала перезапуска служб 1C
def check_1c_services_restart():
   global is_1c_restart
   try:
        with open(TIMESTAMP_PATH, 'r') as f:
            restart_time = float(f.read())
            current_time = time()
            spended_time = current_time - restart_time
            # print("Перезапуск служб 1C занял:", spended_time, "секунд")
            # Если перезагрузка служб 1C занимает менее указанного лимита
            if spended_time < LIMIT_TIME_1C_RESTART:
                is_1c_restart = True
   except FileNotFoundError:
        pass

# Проверка доступности сервера лицензирования 1С
def check_license_service():
   
   list_clusters = fn_list_clusters(ras_server)
   result = "0"

   list_servers = fn_list_servers(ras_server, list_clusters[0])
   for server in list_servers:
      if fn_server_is_license_service(ras_server, list_clusters[0], server["server"]) == True:
         if fn_host_is_active(ras_server, list_clusters[0], server["agent-host"])==True:
            result = "1"
            print('License service is active')
   if is_1c_restart:
      result = "1"

   send_result_zabbix(zabbix_host, zabbix_metric_lic, result)

# Проверка доступности базы на кластере 1С
def check_1c_base(base_name):
   list_clusters = fn_list_clusters(ras_server)
   if fn_base_is_destroy(ras_server, list_clusters[0], base_name):
      print ('Error base 1c')
      result = "0"
   else:
      print('Base 1c ok!')
      result = "1"
   if is_1c_restart:
      result = "1"

   send_result_zabbix(zabbix_host, zabbix_metric_1c, result)

# Проверка доступности базы на сервере СУБД
def check_pg_base(base_name):
   
   if fn_db_is_active(base_name):
      print('Base pg ok!')
      result = "1"
   else:
      
      print ('Error base pg')
      result = "0"

   send_result_zabbix(zabbix_host, pg_zabbix_metric_1c, result)

# Удаляем папки rac_* из логов тех. журнала
def remove_rac_directories():
   
   for root, dirs, files in os.walk("/var/1C"):
      for dir_name in dirs:
         if dir_name.startswith('rac_'): 
            dir_path = os.path.join(root, dir_name)            
            shutil.rmtree(dir_path)

def main(args):
   global is_1c_restart
   
   runmode = ''.join(args.runmode).lower()
   base_name = ''.join(args.base_name)

   global ras_server, zabbix_host, pg_user, pg_pass, pg_server, ras_cluster_user, ras_cluster_pass 

   ras_server        = ''.join(args.ras_server)    #Имя сервера 1С
   zabbix_host       = ''.join(args.zabbix_host)   #Название текущего сервера в Zabbix
   pg_user           = ''.join(args.pg_user)
   pg_pass           = ''.join(args.pg_pass)
   pg_server         = ''.join(args.pg_server)
   ras_cluster_user  = ''.join(args.ras_cluster_user)
   ras_cluster_pass  = "'"+''.join(args.ras_cluster_pass)+"'"
   remove_directory  = ''.join(args.remove_directory)

   hostname = socket.gethostname()
   
   if ras_server == '':
      ras_server = hostname + ':1545'

   if zabbix_host == '':
      zabbix_host = hostname

   if runmode == "1c":
      # Проверяем происходит ли перезапуск служб 1C
      check_1c_services_restart()
      check_1c_base(base_name)
   
   elif runmode == "pg":
      check_pg_base(base_name)
   
   elif runmode == "lic":
      # Проверяем происходит ли перезапуск служб 1C
      check_1c_services_restart()
      check_license_service()
   elif runmode == "all":
      # Проверяем происходит ли перезапуск служб 1C
      check_1c_services_restart()
      check_1c_base(base_name)
      check_pg_base(base_name)
      check_license_service()

   if remove_directory == "true":
      remove_rac_directories()
  
if __name__ == '__main__':
    # create the top-level parser
    parser = argparse.ArgumentParser()
    parser.add_argument('-rm', '--runmode', required=False, default="all", help="Возможные проверки: 1c - проверка доступности базы в кластере 1с, pg - проверка доступности базы в СУБД. По умолчанию 1c, lic - проверка доступности сервера лицензирования, all - проверка всех состояний")
    parser.add_argument('-bn', '--base_name', required=False, nargs='+', default="all", help="Имя базы в 1С или СУБД")
    parser.add_argument('-rs', '--ras_server', required=False, nargs='+', default="", help="Имя сервера 1С")
    parser.add_argument('-zh', '--zabbix_host', required=False, nargs='+', default="", help="Название текущего сервера в Zabbix")
    parser.add_argument('-pu', '--pg_user', required=False, nargs='+', default="", help="Имя пользователя Postgres")
    parser.add_argument('-pp', '--pg_pass', required=False, nargs='+', default="", help="Пароль пользователя Postgres")
    parser.add_argument('-ps', '--pg_server', required=False, nargs='+', default="", help="Имя сервера Postgres")
    parser.add_argument('-rcu', '--ras_cluster_user', required=False, nargs='+', default="", help="Имя администратора кластера 1С")
    parser.add_argument('-rcp', '--ras_cluster_pass', required=False, nargs='+', default="", help="Пароль администратора кластера 1С")
    parser.add_argument('-rmd', '--remove_directory', required=False, nargs='+', default="true", help="Удалять папки rac_* из логов тех. журнала, значения параметра - false или true")
    args = parser.parse_args()
    main(args)
    

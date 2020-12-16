#!/usr/bin/env python3

###### SCRIPT DE BACKUP ET DE RESTAURATION DE SERVEUR WEB ######

###########################################################
#
# Ecrit par : Yannick Martin
# Date de creation : 24 Juin 2020
# Derniere modification : 08 Juillet 2020
# Teste avec : Python 3
# Version : 1.2
#
##########################################################

import sys

if "backup" in sys.argv:


    # Import des librairies python

    import os
    import time
    import datetime
    import pipes
    import pysftp


    # Recuperation des identifiants

    from dotenv import load_dotenv
    from pathlib import Path
    env_path = Path('/opt/') / 'secrets.env'
    load_dotenv(dotenv_path=env_path)

    mysql_user = os.environ.get('mysql_user')
    mysql_password = os.environ.get('mysql_password')
    sftp_ip = os.environ.get('sftp_ip')
    sftp_id = os.environ.get('sftp-id')


    # Variables

    sftp_dir = '/opt/sftp_dir/'
    bck_dir = '/opt/backup/'


    # Date et heure

    DATETIME = time.strftime('%d%m%Y-%H')


    # Backup sql

    os.system("mysqldump wordpress --user='" + mysql_user + "' --password='" + mysql_password + "' > " + bck_dir + "/wordpress-" + pipes.quote(DATETIME) + ".sql")

    print ( )
    print ('Dump de wordpress effectué')


    # Backup de Nginx

    os.system("tar -zcvf " + bck_dir + "/nginx_av-" + pipes.quote(DATETIME) + ".tar.gz /etc/nginx/sites-available/myetp")
    os.system("tar -zcvf " + bck_dir + "/nginx_enb-" + pipes.quote(DATETIME) + ".tar.gz /etc/nginx/sites-enabled/myetp")

    print ( )
    print ('Sauvegarde de la configuration Nginx effectué')


    # Backup wordpress

    os.system("tar -zcvf " + bck_dir + "/wordpress_content-" + pipes.quote(DATETIME) + ".tar.gz /var/www/wordpress/wp-content")
    os.system("tar -zcvf " + bck_dir + "/wordpress_admin-" + pipes.quote(DATETIME) + ".tar.gz /var/www/wordpress/wp-admin")
    os.system("tar -zcvf " + bck_dir + "/wordpress_cfg-" + pipes.quote(DATETIME) + ".tar.gz /var/www/wordpress/wp-config.php")

    print ( )
    print ('Sauvegarde de Wordpress effectué')


    # Transfert du backup, du script de sauvegarde et de crontab

    with pysftp.Connection(sftp_ip, username=sftp_id) as sftp:
        with sftp.cd(sftp_dir):
            sftp.put(bck_dir + 'wordpress-' + pipes.quote(DATETIME) + '.sql')
            sftp.put(bck_dir + 'wordpress_content-' + pipes.quote(DATETIME) + '.tar.gz')
            sftp.put(bck_dir + 'wordpress_admin-' + pipes.quote(DATETIME) + '.tar.gz')
            sftp.put(bck_dir + 'wordpress_cfg-' + pipes.quote(DATETIME) + '.tar.gz')
            sftp.put(bck_dir + 'nginx_enb-' + pipes.quote(DATETIME) + '.tar.gz')
            sftp.put(bck_dir + 'nginx_av-' + pipes.quote(DATETIME) + '.tar.gz')
            sftp.put('/opt/backup_restore.py')
            sftp.put('/etc/cron.d/root')
        
    print ( )
    print ('Transfert des sauvegardes effectué')


    # Supression des fichiers de plus de 30 jours

    os.system("find " + bck_dir + " -mtime +30 -delete")
    sftp_cnx = pysftp.Connection(sftp_ip, username=sftp_id)
    sftp_cnx.execute("find " + sftp_dir + " -mtime +30 -delete")

    print ( )
    print ('Sauvegardes de plus de 30 jours éffacés')


    print ( )
    print ( )
    print ('Fin du script de sauvegarde')
    


if "restore" in sys.argv:

    # Import des librairies python

    import os

    # Creation du dossier de restauration
    
    os.system('mkdir -m 777 /opt/restore')
    
    
    # Vraiables

    sftp_dir = '/opt/sftp_dir/'
    restore_dir = '/opt/restore/'
    

    # Definition des sauvegardes a retablir

    nginx_enb = input("Veuillez entrer le nom de la sauvegarde nginx_enb à restaurer (sans l'extension .tar.gz) : ")
    print ("Vous avez choisi le fichier : ", nginx_enb)

    nginx_av = input("Veuillez entrer le nom de la sauvegarde nginx_av à restaurer (sans l'extension .tar.gz) : ")
    print ("Vous avez choisi le fichier : ", nginx_av)

    sql = input("Veuillez entrer le nom du dump SQL à restaurer (sans l'extension .sql) : ")
    print ("Vous avez choisi le fichier : ", sql)

    wp_content = input("Veuillez entrer le nom de la sauvegarde Wordpress content à restaurer (sans l'extension .tar.gz) : ")
    print ("Vous avez choisi le fichier : ", wp_content)

    wp_cfg = input("Veuillez entrer le nom de la sauvegarde Wordpress config à restaurer (sans l'extension .tar.gz) : ")
    print ("Vous avez choisi le fichier : ", wp_cfg)

    wp_admin = input("Veuillez entrer le nom de la sauvegarde Wordpress admin à restaurer (sans l'extension .tar.gz) : ")
    print ("Vous avez choisi le fichier : ", wp_admin)


    # Installation de pip

    os.system("apt-get install -y python3-pip")

    print ( )
    print ('pip installé')

    # Installation de pysftp

    os.system("python3 -m pip install pysftp")
    import pysftp

    print ( )
    print ('pysftp installé')


    # Installation de dotenv

    os.system("python3 -m pip install python-dotenv")


    # Installation de mysqldb

    os.system("apt-get install -y python3-mysqldb")
    import MySQLdb

    print ( )
    print ('MySQLdb installé')

    # Recuperation des identifiants

    from dotenv import load_dotenv
    from pathlib import Path
    env_path = Path('/opt/') / 'secrets.env'
    load_dotenv(dotenv_path=env_path)

    mysql_user = os.environ.get('mysql_user')
    mysql_password = os.environ.get('mysql_password')
    wp_user = os.environ.get('wp_user')
    wp_password = os.environ.get('wp_password')
    sftp_ip = os.environ.get('sftp_ip')
    sftp_id = os.environ.get('sftp_id')

    # Installation et configuration de MySQL

    install_mysql = "apt-get install -y mysql-server"
    os.system(install_mysql)

    cnx = MySQLdb.connect(host="localhost",user=mysql_user)
    cursor = cnx.cursor()
    cursor.execute("ALTER USER '" + mysql_user + "'@'localhost' IDENTIFIED WITH mysql_native_password BY '" + mysql_password + "'")
    cnx = MySQLdb.connect(host="localhost",user=mysql_user,password=mysql_password)
    cursor = cnx.cursor()
    cursor.execute("CREATE DATABASE wordpress DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci")
    cursor.execute("GRANT ALL ON wordpress.* TO '" + wp_user + "'@'localhost' IDENTIFIED BY '" + wp_password + "'")

    print ( )
    print ('Mysql installé et configuré')


    # Installation de Nginx

    install_nginx = "apt-get install -y nginx"
    os.system(install_nginx)

    print ( )
    print ('Nginx installé')


    # Installation de PHP

    install_php = "apt-get install -y php-fpm php-mysql"
    os.system(install_php)

    install_php_ext = "apt-get install -y php-curl php-gd php-intl php-mbstring php-soap php-xml php-xmlrpc php-zip"
    os.system(install_php_ext)

    print ( )
    print ('PHP installé')

    # Installation de Wordpress

    os.chdir("/tmp")
    os.system("curl -LO https://wordpress.org/latest.tar.gz")
    os.system("tar xzvf latest.tar.gz")
    os.system("cp /tmp/wordpress/wp-config-sample.php /tmp/wordpress/wp-config.php")
    os.system("cp -a /tmp/wordpress/. /var/www/wordpress")
    os.system("chown -R www-data:www-data /var/www/wordpress")

    print ( )
    print ('Wordpress installé')


    # Recuperation des fichiers de backup

    with pysftp.Connection(sftp_ip, username=sftp_id) as sftp:
        with sftp.cd(sftp_dir):
            sftp.get(sftp_dir + sql + ".sql", restore_dir + sql + ".sql")
            sftp.get(sftp_dir + wp_content + ".tar.gz", restore_dir + wp_content + ".tar.gz")
            sftp.get(sftp_dir + wp_cfg + ".tar.gz", restore_dir + wp_cfg + ".tar.gz")
            sftp.get(sftp_dir + wp_admin + ".tar.gz", restore_dir + wp_admin + ".tar.gz")
            sftp.get(sftp_dir + nginx_av + ".tar.gz", restore_dir + nginx_av + ".tar.gz")
            sftp.get(sftp_dir + nginx_enb + ".tar.gz", restore_dir + nginx_enb + ".tar.gz")
            sftp.get(sftp_dir + "backup_restore.py", "/opt/backup_restore.py")
            sftp.get(sftp_dir + "root", "/etc/cron.d/root")
        
    print ( ):
    print ('Fichiers de sauvegardes récupérés')



    # Restauration de Nginx

    os.system("tar -xvzf " + restore_dir + nginx_av + ".tar.gz -C /")
    os.system("tar -xvzf " + restore_dir + nginx_enb + ".tar.gz -C /")
    os.system("unlink /etc/nginx/sites-enabled/default")
    os.system("systemctl restart nginx")

    print ( )
    print ('Nginx réstauré')


    # Restauration de Wordpress

    os.system("tar -xvzf " + restore_dir + wp_content + ".tar.gz -C /")
    os.system("tar -xvzf " + restore_dir + wp_cfg + ".tar.gz -C /")
    os.system("tar -xvzf " + restore_dir + wp_admin + ".tar.gz -C /")

    print ( )
    print ('Wordpress réstauré')

    # Restauration du dump SQL

    os.system("mysql wordpress --user='" + mysql_user + "' --password='" + mysql_password + "' < " + restore_dir + sql + ".sql")

    print ( )
    print ('Base de données wordpress réstaurée')


    print ( )
    print ( )
    print ('Fin du script de restauration')

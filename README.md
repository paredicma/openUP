	OPENUP KÜMELEME(CLUSTER) ÇÖZÜMÜ 
------------------********************************-----------------

KURULUM ADIMLARI
	
1 - Master ve slave sunucuda fdisk -l komutu ile data dizini için kullanilacak diskin isletim sistemi tarafindan her iki sunucudada ayný isimle görürebildigi kontrol edilir.
SAN disk formatlanmamýþ ise mkfs.ext4 ile formatlanýr.
## fdisk -l
## mkfs.ext4  [Disk_adý]

2 - Master ve slave sunucularin root kullanicilarin birbirine sifresiz ssh baglantisi yapabilmesi için aralarinda ssh-keygen paylasimi olusturulur.
Master # ssh-keygen
Slave  # ssh-keygen
Master # scp /root/.ssh/id_rsa.pub [slave_ip]:/root/.ssh/authorized_keys
Slave  # scp /root/.ssh/id_rsa.pub [master_ip]:/root/.ssh/authorized_keys

3 - postgresql rpm leri master ve slave sunucuya yüklenir.
root # rpm -ivh postgresql93-libs.rhel6.x86_64
root # rpm -ivh postgresql93.rhel6.x86_64
root # rpm -ivh postgresql93-server.rhel6.x86_64
vb.

4 - Master ve slave sunucuda /pgdata  dizini olusturulur. Owner i postgres yapilir.
root # mkdir  /pgdata
root # chown postgres.postgres  /pgdata

5 - Master ve slave sunucuda /etc/init.d/ dizini altindaki postgresql service dosyasinda aþagidaki satirlar gerekli sekilde düzenlenir.
PGPORT=5432
PGDATA=/pgdata/data
PGLOG=/pgdata/pgstartup.log
	düzenleme yapýldýktan sonra her iki sunucuda aþaðýdaki komut çalýþýtýrýlarak postgresql servisini kendiliðinde çalýþmayacaðýndan emin olunur.

root # chkconfig postgresql off

6 - Master sunucuda aþaðýdaki komut ile san disk /pgdata dizini altýna mount edilir.
root # mount [san_disk_adý]      /pgdata
	mount iþleminden sonra aþaðýdaki komut ile postgresql data yapýsý oluþturulur.
root # service postgresql initdb
	daha sonra data dizini altýndaki pg_hba.conf ve postgresql.conf gerekli þekilde düzenlenerek disk umount edilir.
root # umount /pgdata

7 -  Her iki sunucuda crontab a ntp senkronizasyonu için  aþaðýdaki satýr eklenir.
root # crontab -e
1 * * * * /usr/sbin/ntpdate [ntp_server_ip] > /dev/null

8 - openUP.tar.gz dosyasi master sunucuya kopyalanir ve aþaðýdaki komutla açýlýr.
root # tar -xvf openUP.tar.gz

oluþan openUP klasörü içerisindeki configBuild.py dosyasýnýn aþaðýdaki deðiþken parametreleri gerekli þekilde düzenlenir.


##################NODE SPECIAL PARAMETERS################
MASTER_NODE="[master_ip]"  # # degisebilir
SLAVE_NODE="[slave_ip]"   # degisebilir
##################SHARED PARAMETERS#################
SW_IP="[swicth_ip]"          #Networkte bagolunan switch 1 in ipsi  # degisebilir
VIRTUAL_IP="[ortak_ip]"     #Ortak ip 1 Service IP  # degisebilir
NETWORK_INT="bond0"  # degisebilir
DB_SERVICE_NAME="postgresql"  # degisebilir
DB_DATA="/pgdata/data/"  # degisebilir
DB_FILE="PG_VERSION"  # degisebilir
SAN_DISK_NAME="/dev/mapper/mpathg" # degisebilir
SAN_DISK_MOUNT_NAME="/pgdata/"  # degisebilir
MOUNT_CONTROL_FILE=SAN_DISK_MOUNT_NAME+"MOUNT_CONTROL"   #degismese iyi olur
HA_SERVICE="openUP"  #degismese iyi olur
SSH_USER="root"      #degismese iyi olur

9 - Master sunucuda aþaðýdaki komut kullanýlarak cluster yaziliminin kurulumu yapýlir.
root # python configBuild.py
	kurulum sorunsuz tamamlandýysa her iki sunucuda aþaðýdaki aþaðýdaki komut çalýþtýrýlarak cluster yazýlýmý baþlatýlýr.


root # Network konfigurasyonu gecerli. OK
root # SSH konfigurasyonu gecerli. OK
root # db service konfigurasyonu gecerli. OK
root # SAN disk konfigurasyonu gecerli. OK
root # uygulama dizinleri olusturuldu.(/etc/openUP) 
root # uygulama programi kopyalandi.(/etc/openUP/openUP.py)
root # servis dosyasi kopyalandi.(/etc/init.d/openUP)
root # config dosyalari olusturuldu.
root # config dosyalari kopyalandi.
root # openUP servis baslatma scripti rc.local e yazildi.
root # Cluster configurasyonu basariyla sonuclandi. OK (service openUP start)
root #  - service openUP start - komutunu calistirabilirsiniz.

root # service openUP start

------------------********************************-----------------

Yönetim :

Kurumlum Sonrasý Oluþan Üç temel Dosya ( Her iki sunucuda da )

Konfigürasyon Dosyasý 		: /etc/openUP/config.py 
Program Dosyasý	     		: /etc/openUP/openUP.py 
Service Dosyasý			: /etc/init.d/openUP

Diðer Dosyalar
Log dosyasý			: /var/log/openUP.log
Aktif node dosyasý		: /etc/openUP/ACTIVE
SAN disk Kontrol dosyasý	: /pgdata/MOUNT_CONTROL


Konfigurasyon dosyasý /etc/openUP/config.py


#-*- coding: utf-8 -*-
## Author			: Mustafa YAVUZ 
## E-mail			: myavuz@tubitak.gov.tr
## Version  			: 4.0
## Date				: 11.04.2013
## OS System 			: Redhat/Centos 5, Redhat/Centos 6
## DB System 			: Postgresql, MySQL, same type other opensource db
## System Requirement		: SAN storage, 2 server wiht linux OS(Redhat/Centos), sshd deamon, DB service file (like /etc/init.d/postgresql), program service file
## PARAMETERS
##################NODE SPECIAL PARAMETERS################
IS_MASTER=True ## 1 = True, 0 = False
LOCALE_NODE="10.1.1.11"  #Bu sunucu
REMOTE_NODE="10.1.1.12"   #Diger cluster  sunucusu
##################SHARED PARAMETERS#################
SW_IP="10.1.1.1"          #Networkte bagolunan switch 1 in ipsi
VIRTUAL_IP="10.1.1.13"     #Ortak ip 1 Service IP
NETWORK_INT="bond0"        #Kullanilan networke göre degisecek.
DB_SERVICE_NAME="postgresql"
DB_DATA="/pgdata/data/"
DB_FILE="PG_VERSION"
ACTIVE_FILE='/etc/openUP/ACTIVE'
LOG_FILE="/var/log/openUP.log"
RUN_FILE="/var/run/openUP.pid"
SAN_DISK_CONTROL=True
SAN_DISK_CONTROL_TIME=60   # SAN diskin ne kadar sure sonra devir alinabilecegi
SAN_DISK_NAME="/dev/mapper/mpathg" ##mount /dev/mapper/mpathg /pgdata/
SAN_DISK_MOUNT_NAME="/pgdata/"
MOUNT_CONTROL_FILE=SAN_DISK_MOUNT_NAME+"MOUNT_CONTROL"
HA_SERVICE="openUP"
SSH_USER="root"
## PARAMETERS





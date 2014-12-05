#-*- coding: utf-8 -*-
## Author				: Mustafa YAVUZ 
## E-mail				: mustafa.yavuz@tubitak.gov.tr
## Version  			: 4.0.2
## Date					: 27.02.2014
## OS System 			: Redhat/Centos 5, Redhat/Centos 6
## DB System 			: Postgresql, MySQL, same type other opensource db
## System Requirement	: SAN storage, 2 server wiht linux OS(Redhat/Centos), sshd deamon, DB service file (like /etc/init.d/postgresql), program service file
## PARAMETERS
from time import *
import os
import sys
import commands
from time import *
##################NODE SPECIAL PARAMETERS################
MASTER_NODE="10.1.1.11"  #Bu sunucu
SLAVE_NODE="10.1.1.12" 
#MY_NODE="1"
##################SHARED PARAMETERS#################
SW_IP="10.1.1.1"          #Networkte bagolunan switch 1 in ipsi
VIRTUAL_IP="10.1.1.13"     #Ortak ip 1 Service IP
NETWORK_INT="bond0"        #Bagtcagdcayc.
DB_SERVICE_NAME="postgresql"
DB_DATA="/pgdata/data/"
DB_FILE="PG_VERSION"
SAN_DISK_NAME="/dev/mapper/mpathg" ##mount /dev/mapper/mpathg /pgdata/
SAN_DISK_MOUNT_NAME="/pgdata/"
MOUNT_CONTROL_FILE=SAN_DISK_MOUNT_NAME+"MOUNT_CONTROL"
HA_SERVICE="openUP"
SSH_USER="root"
## PARAMETERS
############################## GENERAL FUNCTION ###########################
def makeConfigFile():
	writeFileContinue("configLocal.py","#-*- coding: utf-8 -*-")
	writeFileContinue("configLocal.py","## Author				: Mustafa YAVUZ ")
	writeFileContinue("configLocal.py","## E-mail				: mustafa.yavuz@tubitak.gov.tr")
	writeFileContinue("configLocal.py","## Version  			: 4.0.2")
	writeFileContinue("configLocal.py","## Date					: 27.02.2014")
	writeFileContinue("configLocal.py","## OS System 			: Redhat/Centos 5, Redhat/Centos 6")
	writeFileContinue("configLocal.py","## DB System 			: Postgresql, MySQL, same type other opensource db")
	writeFileContinue("configLocal.py","## System Requirement	: SAN storage, 2 server wiht linux OS(Redhat/Centos), sshd deamon, DB service file (like /etc/init.d/postgresql), program service file")
	writeFileContinue("configLocal.py","## PARAMETERS")
	writeFileContinue("configLocal.py","##################NODE SPECIAL PARAMETERS################")
	writeFileContinue("configRemote.py","#-*- coding: utf-8 -*-")
	writeFileContinue("configRemote.py","## Author				: Mustafa YAVUZ ")
	writeFileContinue("configRemote.py","## E-mail				: mustafa.yavuz@tubitak.gov.tr")
	writeFileContinue("configRemote.py","## Version  			: 4.0.2")
	writeFileContinue("configRemote.py","## Date					: 27.02.2014")
	writeFileContinue("configRemote.py","## OS System 			: Redhat/Centos 5, Redhat/Centos 6")
	writeFileContinue("configRemote.py","## DB System 			: Postgresql, MySQL, same type other opensource db")
	writeFileContinue("configRemote.py","## System Requirement	: SAN storage, 2 server wiht linux OS(Redhat/Centos), sshd deamon, DB service file (like /etc/init.d/postgresql), program service file")
	writeFileContinue("configRemote.py","## PARAMETERS")
	writeFileContinue("configRemote.py","##################NODE SPECIAL PARAMETERS################")
	if(nodeControl()=='M'):
		writeFileContinue("configLocal.py", "IS_MASTER=True")
		writeFileContinue("configLocal.py", "LOCALE_NODE='"+MASTER_NODE+"'")
		writeFileContinue("configLocal.py", "REMOTE_NODE='"+SLAVE_NODE+"'")
		writeFileContinue("configRemote.py", "IS_MASTER=False")
		writeFileContinue("configRemote.py", "LOCALE_NODE='"+SLAVE_NODE+"'")
		writeFileContinue("configRemote.py", "REMOTE_NODE='"+MASTER_NODE+"'")
	elif(nodeControl()=='Y'):
		writeFileContinue("configLocal.py", "IS_MASTER=False")
		writeFileContinue("configLocal.py", "LOCALE_NODE='"+SLAVE_NODE+"'")
		writeFileContinue("configLocal.py", "REMOTE_NODE='"+MASTER_NODE+"'")	
		writeFileContinue("configRemote.py", "IS_MASTER=True")
		writeFileContinue("configRemote.py", "LOCALE_NODE='"+MASTER_NODE+"'")
		writeFileContinue("configRemote.py", "REMOTE_NODE='"+SLAVE_NODE+"'")		
	writeFileContinue("configLocal.py","##################SHARED PARAMETERS#################")
	writeFileContinue("configLocal.py", "SW_IP='"+SW_IP+"'")
	writeFileContinue("configLocal.py", "VIRTUAL_IP='"+VIRTUAL_IP+"'")
	writeFileContinue("configLocal.py", "NETWORK_INT='"+NETWORK_INT+"'")
	writeFileContinue("configLocal.py", "DB_SERVICE_NAME='"+DB_SERVICE_NAME+"'")
	writeFileContinue("configLocal.py", "DB_DATA='"+DB_DATA+"'")
	writeFileContinue("configLocal.py", "DB_FILE='"+DB_FILE+"'")
	writeFileContinue("configLocal.py", "ACTIVE_FILE='/etc/openUP/ACTIVE'")
	writeFileContinue("configLocal.py", "LOG_FILE='/var/log/openUP.log'")
	writeFileContinue("configLocal.py", "RUN_FILE='/var/run/openUP.pid'")
	writeFileContinue("configLocal.py", "SAN_DISK_CONTROL=True")
	writeFileContinue("configLocal.py", "SAN_DISK_CONTROL_TIME=60")
	writeFileContinue("configLocal.py", "SAN_DISK_NAME='"+SAN_DISK_NAME+"'")
	writeFileContinue("configLocal.py", "SAN_DISK_MOUNT_NAME='"+SAN_DISK_MOUNT_NAME+"'")
	writeFileContinue("configLocal.py", "MOUNT_CONTROL_FILE='"+SAN_DISK_MOUNT_NAME+"MOUNT_CONTROL'")
	writeFileContinue("configLocal.py", "HA_SERVICE='openUP'")						
	writeFileContinue("configLocal.py", "SSH_USER='"+SSH_USER+"'")
	writeFileContinue("configRemote.py","##################SHARED PARAMETERS#################")
	writeFileContinue("configRemote.py", "SW_IP='"+SW_IP+"'")
	writeFileContinue("configRemote.py", "VIRTUAL_IP='"+VIRTUAL_IP+"'")
	writeFileContinue("configRemote.py", "NETWORK_INT='"+NETWORK_INT+"'")
	writeFileContinue("configRemote.py", "DB_SERVICE_NAME='"+DB_SERVICE_NAME+"'")
	writeFileContinue("configRemote.py", "DB_DATA='"+DB_DATA+"'")
	writeFileContinue("configRemote.py", "DB_FILE='"+DB_FILE+"'")
	writeFileContinue("configRemote.py", "ACTIVE_FILE='/etc/openUP/ACTIVE'")
	writeFileContinue("configRemote.py", "LOG_FILE='/var/log/openUP.log'")
	writeFileContinue("configRemote.py", "RUN_FILE='/var/run/openUP.pid'")
	writeFileContinue("configRemote.py", "SAN_DISK_CONTROL=True")
	writeFileContinue("configRemote.py", "SAN_DISK_CONTROL_TIME=60")
	writeFileContinue("configRemote.py", "SAN_DISK_NAME='"+SAN_DISK_NAME+"'")
	writeFileContinue("configRemote.py", "SAN_DISK_MOUNT_NAME='"+SAN_DISK_MOUNT_NAME+"'")
	writeFileContinue("configRemote.py", "MOUNT_CONTROL_FILE='"+SAN_DISK_MOUNT_NAME+"MOUNT_CONTROL'")
	writeFileContinue("configRemote.py", "HA_SERVICE='openUP'")						
	writeFileContinue("configRemote.py", "SSH_USER='"+SSH_USER+"'")	
def nodeControl():
	output_mline=commands.getoutput('ifconfig | grep '+MASTER_NODE)
	output_sline=commands.getoutput('ifconfig | grep '+SLAVE_NODE)
	if(len(output_mline)>0 and len(output_sline)==0):
		return 'M'
	elif(len(output_mline)==0 and len(output_sline)>0):		
		return 'S'
	else:
		return 'E'  ## Error
def strf_time():
	return strftime('%Y%m%d%H%M%S')	
def removeFile(fileName):
	try:
		os.remove(fileName)
	except:
		print 'Dosya silinirken hata olustu'
def writeFileFirst(file, file_content):
	try:
		fp=open(file,'w')
		fp.write(file_content)
		fp.close()
	except :
		print 'Dosyaya yazilirkenn hata olustu'	
def writeFileContinue(file, file_content):
	try:
		fp=open(file,'ab')
		fp.write(file_content+'\n')
		fp.close()
	except :
		print 'Dosyaya ayazilirken hata olustu'
############################## HA FUNCTIONS ##################
def db_control(): # 0 servis calisiyor. --768 kapali
	db_yerel_durum=os.system("/sbin/service "+DB_SERVICE_NAME+" status  > /dev/null")
	return db_yerel_durum
def db_stop(): # 0 servis calisiyor.
	db_state=db_control()
	if(db_state==0):
		os.system("/sbin/service "+DB_SERVICE_NAME+" stop ")
def remote_ssh_state(R_NODE): # 0 servis calisiyor.
	ssh_state=os.system("ssh -q "+SSH_USER+"@"+R_NODE+" exit > /dev/null")
	return ssh_state
def ssh_state(): # 0 servis calisiyor.
	ssh_state=os.system("service sshd status > /dev/null")
	if(str(ssh_state)!='0'):
		os.system("service sshd start")
	return ssh_state
def ping_sw(): ## 0 pingleniyor 256 pinglenmiyor
	ping_state=os.system('/bin/ping '+SW_IP+' -c 4 > /dev/null')
	return ping_state
def ping_ip(targetIP): ## 0 pingleniyor 256 pinglenmiyor
	ping_state=os.system('/bin/ping '+targetIP+' -c 4 > /dev/null')
	return ping_state	
def hasVirtual_ip(): ## varsa 0 doner yoksa 256 doner
      virtual_ip_state=os.system('/sbin/ifconfig | grep '+VIRTUAL_IP+' > /dev/null')
      return virtual_ip_state

def requirementIPControl():
	print "system netwrok gereksinimleri kontrol ediliyor..."
	durum=True
	if(ping_sw()==0):
		print "Sunucu switch e eribiliyor. OK"
	else:
		print "Sunucu switch e erisemiyor.Lutfen switch i kontrol ediniz. ERROR!!!"
		durum=False
	if(ping_ip(MASTER_NODE)==0):
		print "Sunucu MASTER_NODE a eribiliyor. OK"
	else:
		print "Sunucu MASTER_NODE a erisemiyor.Lutfen MASTER_NODE u kontrol ediniz. ERROR!!!"
		durum=False
	if(ping_ip(SLAVE_NODE)==0):
		print "Sunucu SLAVE_NODE a eribiliyor. OK"
	else:
		print "Sunucu SLAVE_NODE a erisemiyor.Lutfen SLAVE_NODE u kontrol ediniz. ERROR!!!"
		durum=False
	if(ping_ip(VIRTUAL_IP)!=0):
		print "ortak ip bosta. OK"
	else:
		print "ortak ip baska sunucu tarafindan kullaniliyor. ERROR!!!"
		durum=False
	return durum
	
def requirementSSHControl(R_NODE):
	print "sshd ayarlari kontrol ediliyor..."
	durum=True
	if(os.path.exists("/etc/init.d/sshd")):
		print "sshd servisi kurulu. OK"
		ssh_state()  ## ssh servisi calismiyorsa baslatilir.
		print " Dikkat!!! ssh baglantisinda parola sormamasi gerekiyor."
		if(remote_ssh_state(R_NODE)==0):
			print " Uzak sunucuda ssh servisi calisiyor. OK"
##			remote_chkconfig=os.system('/usr/bin/ssh '+SSH_USER+'@'+REMOTE_NODE+' -C "/sbin/chkconfig sshd on" > /dev/null')
		else:
			print " Uzak sunucuda ssh servisi calismiyor. ERROR!!!"
			durum=False
	else:
		print "sshd servisi kurulu degil. ERROR!!!"
		durum=False
	return durum
	
def requirementDBServiceControl(R_NODE):
	print "db servisleri kontrol ediliyor..."
	durum=True
	if(os.path.exists("/etc/init.d/"+DB_SERVICE_NAME)):
		print DB_SERVICE_NAME+" servisi kurulu. OK"
		db_stop()
		os.system("/sbin/chkconfig "+DB_SERVICE_NAME+" off > /dev/null")
		serviceFile_state=os.system('/usr/bin/ssh '+SSH_USER+'@'+R_NODE+' -C "/bin/ls /etc/init.d/'+DB_SERVICE_NAME+'"') # 0 mount durumda 512 erisemiyor.
		if(serviceFile_state==0):
			os.system('/usr/bin/ssh '+SSH_USER+'@'+R_NODE+' -C "/sbin/chkconfig '+DB_SERVICE_NAME+' off > /dev/null"') # 0 mount durumda 512 erisemiyor.
		else:
			DB_SERVICE_NAME+" servisi  uzak sunucuda kurulu degil. ERROR!!!"
			durum=False
	else:
		print DB_SERVICE_NAME+" servisi kurulu degil. ERROR!!!"
		durum=False
	return durum
def requirementSANControl(R_NODE):
	print "SAN disk kontrol ediliyor..."
	durum=True
	if(os.path.exists(SAN_DISK_MOUNT_NAME)):
		print SAN_DISK_MOUNT_NAME+" dizini mevcut. OK"
		serviceFile_state=os.system('/usr/bin/ssh '+SSH_USER+'@'+R_NODE+' -C "/bin/ls '+SAN_DISK_MOUNT_NAME+' > /dev/null"') # 0 mount durumda 512 erisemiyor.
		if(serviceFile_state==0):
			print SAN_DISK_MOUNT_NAME+" dizini mevcut. OK"
			fdisk_l_state=commands.getoutput('fdisk -l | grep '+SAN_DISK_NAME)
			if(len(fdisk_l_state)>0):
				print SAN_DISK_MOUNT_NAME+" mount dizini mevcut. OK"
				fdisk_r_state=commands.getoutput('/usr/bin/ssh '+SSH_USER+'@'+R_NODE+' -C "fdisk -l | grep '+SAN_DISK_NAME+'"') # 0 mount durumda 512 erisemiyor.
				if(len(fdisk_r_state)>0):
					print SAN_DISK_MOUNT_NAME+" uzak sunucu mount dizini mevcut. OK"
					os.system("mount "+SAN_DISK_NAME+" "+SAN_DISK_MOUNT_NAME)
					writeFileFirst(MOUNT_CONTROL_FILE, MASTER_NODE+" "+strf_time())
					os.system("umount "+SAN_DISK_MOUNT_NAME)
					print MOUNT_CONTROL_FILE+" dosyasina mount bilgisi yazildi"
				else:
					print SAN_DISK_NAME+" uzak sunucu mount dizini mevcut degil. ERROR!!!"
					durum=False					
			else:
				print SAN_DISK_NAME+" sunucu mount dizini mevcut degil. ERROR!!!"
				durum=False				
		else:
			print SAN_DISK_MOUNT_NAME+" dizini  uzak sunucuda mevcut degil. ERROR!!!"
			durum=False
	else:
		print DB_SERVICE_NAME+" mount disk yeri bulunmuyor. ERROR!!!"
		durum=False
	return durum
		
	
	
############################## HA PROCESS ##########################
def build_control(): ## Ana fonksiyon
	Rem_NODE=SLAVE_NODE
	if(nodeControl()=='M'):
		Rem_NODE=SLAVE_NODE
	elif(nodeControl()=='S'):
		Rem_NODE=MASTER_NODE
	else:
		print "Gecersiz konfigurasyon !!!!"
		exit(0)
	if(requirementIPControl()):
		print "Network konfigurasyonu gecerli. OK"
		if(requirementSSHControl(Rem_NODE)):
			print "SSH konfigurasyonu gecerli. OK"
			if(requirementDBServiceControl(Rem_NODE)):
				print "db service konfigurasyonu gecerli. OK"
				if(requirementSANControl(Rem_NODE)):
					print "SAN disk konfigurasyonu gecerli. OK"
					os.system("mkdir -p /etc/openUP")
					os.system('/usr/bin/ssh '+SSH_USER+'@'+Rem_NODE+' -C "mkdir -p /etc/openUP"')
					print " uygulama dizinleri olusturuldu.(/etc/openUP)"
					os.system("cp source/openUP.py /etc/openUP/")
					os.system('scp  source/openUP.py '+SSH_USER+'@'+Rem_NODE+':/etc/openUP/')
					print " uygulama programi kopyalandi.(/etc/openUP/openUP.py)"
					os.system("cp source/openUP /etc/init.d/")
					os.system('scp  source/openUP '+SSH_USER+'@'+Rem_NODE+':/etc/init.d/')
					print " servis dosyasi kopyalandi.(/etc/init.d/openUP)"
					makeConfigFile()
					print "config dosyalari olusturuldu."
					os.system("cp configLocal.py /etc/openUP/config.py")
					os.system('scp  configRemote.py '+SSH_USER+'@'+Rem_NODE+':/etc/openUP/config.py')					
					print "config dosyalari kopyalandi."
					writeFileContinue("/etc/rc.local","service openUP start")
					os.system('ssh '+SSH_USER+'@'+Rem_NODE+' -C "echo \"service openUP start\" >> /etc/rc.local"')
					print "openUP servis baslatma scripti rc.local e yazildi."
					print "Cluster configurasyonu basariyla sonuclandi. OK (service openUP start)"
					print " - service openUP start - komutunu calistirabilirsiniz."
					os.remove("configLocal.py")
					os.remove("configRemote.py")
				else:
					print "Lutfen san disk ayarlarini kontrol ediniz. ERROR!!!"
			else:
				print "Lutfen db servis ayarlarini kontrol ediniz. ERROR!!!"
		else:
			print "Lutfen ssh ayarlarini kontrol ediniz. ERROR!!!"
	else:
		print "Lutfen IP ayarlarini kontrol ediniz. ERROR!!!"		
def main():
	build_control()
main()

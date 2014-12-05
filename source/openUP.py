#-*- coding: utf-8 -*-
## Author				: Mustafa YAVUZ 
## E-mail				: mustafa.yavuz@tubitak.gov.tr
## Version  			: 4.0.2
## Date					: 27.02.2014
## OS System 			: Redhat/Centos 5, Redhat/Centos 6
## DB System 			: Postgresql, MySQL, same type other opensource db
## System Requirement	: SAN storage, 2 server wiht linux OS(Redhat/Centos), sshd deamon, DB service file (like /etc/init.d/postgresql), program service file
from time import *
import os
import sys
import commands
from time import *
from config import *
############################## GENERAL FUNCTION ###########################
def read_file(file_name):
	if(os.path.exists(file_name)):
		fl=open(file_name,"r")
		file_content=fl.readline()
		fl.close()
		return file_content
	else:
		write_log("dosya bulunamadi.")
		return 'HATA'				
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
		print 'Dosyaya file_contentlirken hata olustu'
def writeFileContinue(file, file_content):
	try:
		fp=open(file,'ab')
		fp.write(file_content+'\n')
		fp.close()
	except :
		print 'Dosyaya ayazilirken hata olustu'
def get_datetime():
	my_year=str(localtime()[0])
	my_mounth=str(localtime()[1])
	my_day=str(localtime()[2])
	my_hour=str(localtime()[3])
	my_min=str(localtime()[4])
	my_sec=str(localtime()[5])
	day=str(localtime()[2])
	return my_year+"."+my_mounth+"."+my_day+" "+my_hour+":"+my_min+":"+my_sec	
def strf_time():
	return strftime('%Y%m%d%H%M%S')	
def write_log(log_content):
	log_content='* ('+get_datetime()+') ::: '+log_content
	writeFileContinue(LOG_FILE,log_content)
############################## HA FUNCTIONS ##################
def db_control(): # 0 servis calisiyor. --768 kapali
	db_yerel_durum=os.system("/sbin/service "+DB_SERVICE_NAME+" status  > /dev/null")
	return db_yerel_durum
def remote_db_control(): # 0 servis calisiyor. --768 kapali
	db_yerel_durum=os.system('/usr/bin/ssh '+SSH_USER+'@'+REMOTE_NODE+' -C "/sbin/service '+DB_SERVICE_NAME+' status" > /dev/null')
	return db_yerel_durum
def db_start(): # 0 servis calisiyor.
	db_state=db_control()
	if(db_state!=0):
		os.system("/sbin/service "+DB_SERVICE_NAME+" start ")
def db_stop(): # 0 servis calisiyor.
	db_state=db_control()
	if(db_state==0):
		os.system("/sbin/service "+DB_SERVICE_NAME+" stop ")
def remote_db_stop(): # 0 servis calisiyor.
	db_state=remote_db_control()
	if(db_state==0):
		os.system('/usr/bin/ssh '+SSH_USER+'@'+REMOTE_NODE+' -C "/sbin/service '+DB_SERVICE_NAME+' stop " > /dev/null')		
def mount_control(): ### ### TRUE var ,False bagli degil
	return os.path.isfile(DB_DATA+DB_FILE)
def remote_mount_control(): ### 0 mount durumda 512 erisemiyor.
	disk_state=os.system('/usr/bin/ssh '+SSH_USER+'@'+REMOTE_NODE+' -C "/bin/ls '+DB_DATA+DB_FILE+' > /dev/null"') # 0 mount durumda 512 erisemiyor.
	return disk_state
def disk_mount(): ## 0 ise basarili ,8192 basarisiz
	disk_state=os.system("mount "+SAN_DISK_NAME+" "+SAN_DISK_MOUNT_NAME)  ## 0 ise basarili ,8192 basarisiz
	return disk_state	
def disk_ro_mount(): ## 0 ise basarili ,8192 basarisiz
	disk_state=os.system("mount -o ro "+SAN_DISK_NAME+" "+SAN_DISK_MOUNT_NAME)  ## 0 ise basarili ,8192 basarisiz
	return disk_state	
def disk_umount():   ## 0 ise basarili ,8192 basarisiz
	disk_state=os.system("umount -l "+SAN_DISK_MOUNT_NAME)  ## 0 ise basarili ,8192 basarisiz
	return disk_state
def remote_disk_umount():
	disk_state=os.system('/usr/bin/ssh '+SSH_USER+'@'+REMOTE_NODE+' -C "/bin/umount '+SAN_DISK_MOUNT_NAME+'" > /dev/null')  ## 0 ise basarili ,8192 basarisiz
	return disk_state
def remote_disk_control():
	disk_state=os.system('/usr/bin/ssh '+SSH_USER+'@'+REMOTE_NODE+' -C "ls '+DB_DATA+DB_FILE+'" > /dev/null')  ## 0 ise basarili ,8192 basarisiz
	return disk_state
def isSan_disk_free():
	try:
		if(mount_control()==0):
			m_state=disk_ro_mount()
			if(m_state==0):
				file_text=read_file(MOUNT_CONTROL_FILE)
				um_state=disk_umount()
				if(um_state==0):
					file_text_array= file_text.split(' ')
					if(LOCALE_NODE==file_text_array[0]):  ## zaten en son aktif sunucu benim
						return True
					else:                        ## en son diger sunucu aktifmis.
						write_log("node: "+ file_text_array[0])
						write_log("date: "+ file_text_array[1])
						time_now=strf_time()
						time_result=int(time_now)-int(file_text_array[1])
						if(time_result>SAN_DISK_CONTROL_TIME):  ##  kontrol suresi kadar beklendi
							write_log("Gecen sure (sn.): "+str(time_result))
							return True
						else:
							return False
				else:
					return False
			else:
				return False
		else:
			return False
	except :
		write_log("isSan_disk_free() beklenmeyen HATA!!!")
		return False
def resource_stop(): # 0 servis calisiyor.
	db_stop()
	disk_umount()
	virtual_ip_down()
	removeFile(ACTIVE_FILE)
	ACTIVE_FLAG=0
	write_log("Kaynaklar serbes birakildi.")
def resource_start(): # 0 servis calisiyor.
	disk_mount()
	db_start()
	virtual_ip_up()
	virtual_ip_isMine_say()
	writeFileFirst(ACTIVE_FILE,str(get_datetime()))
	ACTIVE_FLAG=1
	write_log(" Kaynaklar acildi")
def remote_ssh_state(): # 0 servis calisiyor.
	ssh_state=os.system("ssh -q "+SSH_USER+"@"+REMOTE_NODE+" exit > /dev/null")
	return ssh_state
def ssh_state(): # 0 servis calisiyor.
	ssh_state=os.system("service sshd status > /dev/null")
	if(str(ssh_state)!='0'):
		os.system("service sshd start")
	return ssh_state
def remote_service_state(): # 0 servis calisiyor. 
	remote_ha_state=os.system('ssh -q '+SSH_USER+'@'+REMOTE_NODE+' -C "service '+HA_SERVICE+' status" > /dev/null')
	return remote_ha_state
def ping_sw(): ## 0 pingleniyor 256 pinglenmiyor
	ping_state=os.system('/bin/ping '+SW_IP+' -c 4 > /dev/null')
	return ping_state
def ping_remote_ip(): ## 0 pingleniyor 256 pinglenmiyor
	ping_state=os.system('/bin/ping '+REMOTE_NODE+' -c 4 > /dev/null')
	return ping_state
def ping_virtual_ip(): ## 0 pingleniyor 256 pinglenmiyor
	ping_state=os.system('/bin/ping '+VIRTUAL_IP+' -c 4 > /dev/null')
	return ping_state
def hasVirtual_ip(): ## varsa 0 doner yoksa 256 doner
      virtual_ip_state=os.system('/sbin/ifconfig | grep '+VIRTUAL_IP+' > /dev/null')
      return virtual_ip_state
def virtual_ip_isMine_say():
	process_return=os.system("/sbin/arping -c 1 -I "+NETWORK_INT+" -A -q "+VIRTUAL_IP)
def virtual_ip_down():
	process_return=os.system("/sbin/ifconfig "+NETWORK_INT+":0 down")
def remote_virtual_ip_down():
	process_return=os.system('/usr/bin/ssh '+SSH_USER+'@'+REMOTE_NODE+' -C "/sbin/ifconfig '+NETWORK_INT+':0 down"')	
def virtual_ip_up(): ## varsa 0 donerse basarili.
	virtual_ip_state=os.system("/sbin/ifconfig "+NETWORK_INT+" add "+VIRTUAL_IP+"  > /dev/null")
	vip_state=int(virtual_ip_state)
	if (vip_state==0):
		write_log("ortak ipler atandi:)")
	else:
		write_log("!!!!!!!!!!!!!! ortak ipler atanamadi !!!!!!!!!!!!!!")
	return vip_state
############################## HA PROCESS ##########################
def service_control(param): ## Ana fonksiyon
	ACTIVE_FLAG=0
	if(param=='start'):
		write_log("openUP servisi baslatildi.")
		print "openUP servisi baslatildi."
		os.system("/bin/sh /root/.bash_profile")
		removeFile(ACTIVE_FILE)
		writeFileFirst(RUN_FILE,str(os.getpid()))
#		sleep(10)
		while(1):
			sw_p=ping_sw()
			if(sw_p==0): ### switch e ulasildi.
				ssh_p=ssh_state()
				if(ssh_p==0):  ## sshd calisiyor
#					sleep(5)
					if(IS_MASTER): ##Sunucu master olarak atanmis					
						if(ACTIVE_FLAG==0):
							r_ip=ping_remote_ip()
							if(r_ip==0): ## diger sunucu pingleniyor
								r_ssh=remote_ssh_state()
								if(r_ssh==0): ## diger sunucuda ssh calisiyor.
									r_d_c=remote_disk_control()
									if(r_d_c!=0): ## remote da disk mount degil.
										if(isSan_disk_free()):  # disk bostami
											resource_start()
											ACTIVE_FLAG=1
											if(mount_control()):  ## disk mount durumda
												writeFileFirst(MOUNT_CONTROL_FILE,LOCALE_NODE+" "+strf_time())
										else:
											write_log("SAN disk hala kullaniliyor olabilir. Servislerin acilmasi ertelendi !!!")
									else:
										write_log("Uzak snucu ortak diske erisebiliyor. Servislerin acilmasi ertelendi !!!")
								else:## ## diger sunucu ssh cevabi vermiyor.
									sw_p=ping_sw()
									if(sw_p==0):
										if(isSan_disk_free()):  # disk bostami
											resource_start()
											ACTIVE_FLAG=1
											if(mount_control()):  ## disk mount durumda
												writeFileFirst(MOUNT_CONTROL_FILE,LOCALE_NODE+" "+strf_time())
										else:
											write_log("SAN disk hala kullaniliyor olabilir. Servislerin acilmasi ertelendi !!!")
							else:  ## diger sunucuya ulasamiyor.
								sw_p=ping_sw()
								if(sw_p==0):							
									write_log("diger sunucuya ulasilamiyor. Kaynaklar acilacak.")	
									if(isSan_disk_free()):  # disk bostami
										resource_start()
										ACTIVE_FLAG=1
										if(mount_control()):  ## disk mount durumda
											writeFileFirst(MOUNT_CONTROL_FILE,LOCALE_NODE+" "+strf_time())									
									else:
										write_log("SAN disk hala kullaniliyor olabilir. Servislerin acilmasi ertelendi !!!")						
						elif(ACTIVE_FLAG==1):
							if(mount_control()):  ## disk mount durumda
								writeFileFirst(MOUNT_CONTROL_FILE,LOCALE_NODE+" "+strf_time())
								sleep(5)
					else:  ##Sunucu slave olarak atanmis
#						sleep(5)
						r_ip=ping_remote_ip()
						if(r_ip==0): ## diger sunucu pingleniyor
							r_ssh=remote_ssh_state()
							if(r_ssh==0): ## diger sunucuda ssh calisiyor.
								r_s_state=remote_service_state()
								if(r_s_state==0): ## Diger sunucuda ha servisi ayakta..
									if(ACTIVE_FLAG==1):
										write_log("diger sunucu servisler aktif. Kaynaklar aciksa kapatilacak.")
										resource_stop()
										ACTIVE_FLAG=0
									sleep(10)
								else:
									sw_p=ping_sw()
									if(sw_p==0):									
										if(ACTIVE_FLAG==0):
											r_d_c=remote_disk_control()
											if(r_d_c!=0): ## remote da disk mount degil.
												if(isSan_disk_free()):
													write_log("Master da ha calismiyor. Slave devreye girecek !!!")
													resource_start()
													ACTIVE_FLAG=1
													if(mount_control()):  ## disk mount durumda
														writeFileFirst(MOUNT_CONTROL_FILE,LOCALE_NODE+" "+strf_time())
												else:
													write_log("SAN disk hala kullaniliyor olabilir. Servislerin acilmasi ertelendi !!!")																			
										elif(ACTIVE_FLAG==1):
											if(mount_control()):  ## disk mount durumda
												writeFileFirst(MOUNT_CONTROL_FILE,LOCALE_NODE+" "+strf_time())
									else:
										if(ACTIVE_FLAG==1):
											write_log("diger sunucu servisler aktif. Kaynaklar aciksa kapatilacak.")
											resource_stop()
											ACTIVE_FLAG=0
												
							else:  ## ## diger sunucu ssh cevabi vermiyor.
									sw_p=ping_sw()
									if(sw_p==0):
										if(ACTIVE_FLAG==0): ## sistem aktiv degil.
											if(isSan_disk_free()):
												write_log("Master da ssh calismiyor. Slave devreye girecek !!!")
												resource_start()
												ACTIVE_FLAG=1
												if(mount_control()):  ## disk mount durumda
													writeFileFirst(MOUNT_CONTROL_FILE,LOCALE_NODE+" "+strf_time())
											else:
												write_log("SAN disk hala kullaniliyor olabilir. Servislerin acilmasi ertelendi !!!")																								
										elif(ACTIVE_FLAG==1):
											if(mount_control()):  ## disk mount durumda
												writeFileFirst(MOUNT_CONTROL_FILE,LOCALE_NODE+" "+strf_time())
									else:
										if(ACTIVE_FLAG==1):
											write_log("diger sunucu servisler aktif. Kaynaklar aciksa kapatilacak.")
											resource_stop()
											ACTIVE_FLAG=0												
						else:    ## diger sunucuya ulasilamiyor
							r_ip=ping_remote_ip()
							sw_p=ping_sw()							
							if(sw_p==0 and r_ip!=0):
#								sleep(5)
#								r_ip=ping_remote_ip()
								if(ACTIVE_FLAG==0):
									if(isSan_disk_free()):  # disk bostami
										write_log("Master a ulasilamiyor. Slave devreye girecek !!!")
										resource_start()
										ACTIVE_FLAG=1
										if(mount_control()):  ## disk mount durumda
											writeFileFirst(MOUNT_CONTROL_FILE,LOCALE_NODE+" "+strf_time())										
									else:
										write_log("SAN disk hala kullaniliyor olabilir. Servislerin acilmasi ertelendi !!!")
								elif(ACTIVE_FLAG==1):
									if(mount_control()):  ## disk mount durumda
										writeFileFirst(MOUNT_CONTROL_FILE,LOCALE_NODE+" "+strf_time())
										sleep(5)
								
				else:
					if(ACTIVE_FLAG==1):
						write_log("sshd  calismiyor. Kaynaklar kapatilacak.")				
						resource_stop()
						ACTIVE_FLAG=0
					sleep(5)
					write_log("sshd servisi calismiyor.")
			else:
				if(ACTIVE_FLAG==1):
					write_log("sw koptu")
					write_log("Switch  e ulasilamiyor. Kaynaklar kapatilacak.")
					resource_stop()
					ACTIVE_FLAG=0
				sleep(5)
				write_log("switch baglantisi yok.")
	elif(param=='stop'):
		resource_stop()
		print 'openUP servisi sonlaniyor...'
		write_log('openUP servisi sonlaniyor...')
		pid=read_file(RUN_FILE)
		print "DOSYA ADI : "+RUN_FILE
		print "PID : "+pid
		if(pid!='HATA'):
			os.remove(RUN_FILE)
			if(os.path.isfile(ACTIVE_FILE)):
				os.remove(ACTIVE_FILE)
#			if(os.path.isfile(MOUNT_CONTROL_FILE)):
#				os.remove(MOUNT_CONTROL_FILE)				
			os.system("kill "+pid)
		else:
			write_log("proces id dosyasi bulunamadi.")
	else:
		print 'YANLIS PARAMETRE (start|stop)'
def main():
	try:
		service_control(sys.argv[1])
	except:
		write_log("!!! FATAL :: Sistemde beklenmeyen hata kaynaklar kapatilacak.")
		resource_stop()
		print 'openUP servisi sonlaniyor...'
		write_log('openUP servisi sonlaniyor...')
		pid=read_file(RUN_FILE)
		print "FILE ADI:: "+RUN_FILE
		print "PID:: "+pid
		if(pid!='HATA'):
			os.remove(RUN_FILE)
			if(os.path.isfile(ACTIVE_FILE)):
				os.remove(ACTIVE_FILE)
#			if(os.path.isfile(MOUNT_CONTROL_FILE)):
#				os.remove(MOUNT_CONTROL_FILE)	
			os.system("kill "+pid)
		else:
			write_log("proces id dosyasi bulunamadi.")		
main()

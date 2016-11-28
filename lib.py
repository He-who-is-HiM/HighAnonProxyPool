'''
Get:
Scrape new proxies from websites,
extract IP address and compare with existing ones, abandon the duplicated ips,
add these new proxies into the existing pool

Maintaince:
Check the connection for each existing proxies and delete the unavailable ones

'''
'''
ProxyPool Database:
	- Loop through proxies
	- Check their connection availability and anonymity.
	- Delete the proxy record if found unavailable or non-anonymous.
'''

'''
Next Step:
	- A daemon process to keep branched processes alive
	- Multiprocessing for purifying the proxy data within the database
	- More proxy scraping processes

'''

import os
import sqlite3
import socket
import requests

REQ_TIMEOUT = 1.5

class ProxyPool:
	def __init__(self,ProxyPoolDB):
		#Create the database if not exist
		self.ProxyPoolDB = ProxyPoolDB
		self.conn = sqlite3.connect(self.ProxyPoolDB, isolation_level=None)
		self.cursor = self.conn.cursor()
		self.TB_ProxyPool = "TB_ProxyPool"
		# self.cursor.execute("select SQLITE_VERSION()").fetchone()[0]
		self.cursor.execute("CREATE TABLE IF NOT EXISTS "+self.TB_ProxyPool+"(ip TEXT UNIQUE, port INTEGER, protocol TEXT)")

	def addProxy(self, IP, PORT, PROTOCOL):
		self.cursor.execute("INSERT OR IGNORE INTO " + self.TB_ProxyPool+"(ip, port, protocol) VALUES (?,?,?)", [IP,PORT,PROTOCOL])
	def checkIfProxyExist(self,IP):
		pass
	def showCurrentProxyCount(self):
		pass
	#Delete Proxy Data with no protocol provided
	def cleanNullProtocol(self):
		self.cursor.execute("DELETE FROM "+self.TB_ProxyPool+" WHERE protocol != ? and protocol != ?", ("HTTP","HTTPS"))
	#Delete Proxy Data with no connection
	def cleanNonWorking(self):
		for info in self.cursor.execute("SELECT * FROM "+self.TB_ProxyPool).fetchall():
			IP = info[0]
			PORT = str(info[1])
			PROTOCOL = info[2].lower()
			attempt = 0
			while True:
				print "Testing "+IP+":"+PORT
				#Attempt to connect for 4 times
				isAnonymous = self.testConnection(IP,PORT,PROTOCOL) or self.testConnection(IP,PORT,PROTOCOL) or self.testConnection(IP,PORT,PROTOCOL) or self.testConnection(IP,PORT,PROTOCOL)
				if isAnonymous == False:
					if self.testInternet() == True:
						#Not an Anonymous Proxy
						self.delRecord(IP)
						print IP+" is down or not anonymous\n"
						break
					else:
						#Internet is DOWN
						print "-"*10+" INTERNET IS DOWN "+"-"*10+"\n"
				else:
					#Is Anonymous Connection
					print " "*10+" --->>> ANONYMOUS <<<--- \n"
					break
	def testInternet(self):
		try:
			requests.get("http://google.com", timeout=REQ_TIMEOUT)
			return True
		except:
			return False
	
	#Test the connection and anonymity, return True if it is anonymous, otherwise return False
	def testConnection(self, IP, PORT, PROTOCOL):
		proxies = { PROTOCOL: IP+":"+PORT }
		try:
			OrigionalIP = requests.get("http://icanhazip.com", timeout=REQ_TIMEOUT).content
			MaskedIP = requests.get("http://icanhazip.com", timeout=REQ_TIMEOUT, proxies=proxies).content
			if OrigionalIP != MaskedIP:
				return True
			else:
				return False
			
		except:	
			return False 


	def delRecord(self, IP):
		self.cursor.execute("DELETE FROM "+self.TB_ProxyPool+" WHERE ip=?",(IP,))


# This file is part of Piper.
#
#    Piper is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Piper is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Piper.  If not, see <http://www.gnu.org/licenses/>.
#
# Piper Copyright (C) 2013  Christopher Cassano

import Image
import ImageDraw
import ImageFont
import qrcode
import sys
import sqlite3
from Adafruit_Thermal import *
from secretsharing.shamir import Secret
import random

def getRandPass(length):
	pw = ""
	with open("/home/pi/Printer/wordlist.txt") as f:
	    content = f.readlines()
	    for i in range(length):
		pw += content[random.randint(0, len(content))].strip().capitalize()
	return pw

def getQR(ttp, newSize):
	qr = qrcode.QRCode(
	    version=None,
	    error_correction=qrcode.constants.ERROR_CORRECT_M,
	    box_size=10,
	    border=0,
	)

	qr.add_data(ttp)
	qr.make(fit=True)

	qrImg = qr.make_image()

#resize the qr code to match our design
	qrImg = qrImg.resize(newSize, Image.NEAREST)

	return qrImg


def splitAndPrint(ttp, k, n):
	print "Thing to split: "+ttp
	#first, split it up
	secret = Secret.from_printable_ascii(ttp)
	shares = secret.split(int(k), int(n))
	
	#now convert to QR codes and print the shares
	print shares

	printer = Adafruit_Thermal("/dev/ttyAMA0", 19200, timeout=5)

	qrSize = (340, 340)
	ctr = 0
	
	qrImg = {}
	for shr in shares:
		print "Share: "+shr
		
		finalImg = Image.new("RGB", (384, 440), "white")
		finalImg.paste(getQR(shr, qrSize), (30, 55))

	 	qrImg[shr] = finalImg
	
	dividerLine = Image.new("RGB", (384, 6), "black")
	dividerLine.paste(Image.new("RGB", (384, 3), "white"), (0, 0))
	for shr in shares:
		printer.printImage(dividerLine, True)
		printer.println("This is a share in a "+k+" of "+n+"\nthreshold scheme")
		printer.println(shr)
		printer.printImage(qrImg[shr], True)
		printer.println(shr)
		printer.println("Shamir's Secret Sharing")
		printer.printImage(dividerLine, True)
		printer.feed(3)
		
	printer.setDefault() # Restore printer to defaults


def encodeQRAndPrint(ttp):
	qrSize = (340, 340)

	finalImg = Image.new("RGB", (384, 440), "white")
	finalImg.paste(getQR(ttp, qrSize), (30, 55))

	printer = Adafruit_Thermal("/dev/ttyAMA0", 19200, timeout=5)

	printer.printImage(finalImg, True)
	
	printer.feed(3)

	printer.setDefault() # Restore printer to defaults


def printHDMWalletSeed(headerText, seed, xpub):
	qrSize = (170,170)
	qrPad = 10

	finalImg = Image.new("RGB", (384, qrSize[1]), "white")
	finalImg.paste(getQR(seed, qrSize), (qrPad, 0))
	finalImg.paste(getQR(xpub, qrSize), (qrSize[0]+qrPad*2+14, 0))


	printer = Adafruit_Thermal("/dev/ttyAMA0", 19200, timeout=5)

	dividerLine = Image.new("RGB", (384, 6), "black")
	dividerLine.paste(Image.new("RGB", (384, 4), "white"), (0, 0))

	printer.printImage(dividerLine, True)
	printer.println(headerText)
	printer.println("Seed Mnemonic: "+seed+'\n')
	printer.println("xpub: "+xpub+'\n')
	printer.printImage(finalImg, True)
	printer.feed(1)
	printer.printImage(dividerLine, True)

	
	printer.feed(3)

	printer.setDefault() # Restore printer to defaults


def encodeQRAndPrintText(headerText, ttp):
	qrSize = (340, 340)

	finalImg = Image.new("RGB", (384, 440), "white")
	finalImg.paste(getQR(ttp, qrSize), (30, 55))

	printer = Adafruit_Thermal("/dev/ttyAMA0", 19200, timeout=5)

	dividerLine = Image.new("RGB", (384, 6), "black")
	dividerLine.paste(Image.new("RGB", (384, 3), "white"), (0, 0))

	printer.printImage(dividerLine, True)
	printer.println(headerText)
	printer.println(ttp)
	printer.printImage(finalImg, True)
	printer.println(ttp)
	printer.printImage(dividerLine, True)

	
	printer.feed(3)

	printer.setDefault() # Restore printer to defaults

def printText(ttp):

	printer = Adafruit_Thermal("/dev/ttyAMA0", 19200, timeout=5)


	printer.println(ttp)

	
	printer.feed(3)

	printer.setDefault() # Restore printer to defaults




def print_seed(seed):

	printer = Adafruit_Thermal("/dev/ttyAMA0", 19200, timeout=5)


	printer.println(seed)
	
	printer.feed(3)


	printer.setDefault() # Restore printer to defaults


def print_password(headerText, ttp):



	dividerLine = Image.new("RGB", (384, 6), "black")
	dividerLine.paste(Image.new("RGB", (384, 4), "white"), (0, 0))


#create the divider


	bottomDividerLineImg = Image.open("/home/pi/Printer/dividerline.bmp")
	font = ImageFont.truetype("/usr/share/fonts/ttf/swansea.ttf", 20)
	draw = ImageDraw.Draw(bottomDividerLineImg)
	
	rightMarkText = "Piperwallet.com"
	rightMarkSize = draw.textsize(rightMarkText, font=font)

	leftMarkOrigin = (10, 15)
	rightMarkOrigin = (384-rightMarkSize[0]-10, 15)
    
	draw.text(leftMarkOrigin, headerText, font=font, fill=(0,0,0))
	draw.text(rightMarkOrigin,rightMarkText, font=font, fill=(0,0,0))



	printer = Adafruit_Thermal("/dev/ttyAMA0", 19200, timeout=5)

	printer.printImage(dividerLine, True)
	printer.println("Password: ")
	printer.println(ttp)
	printer.printImage(bottomDividerLineImg, True)

	
	printer.feed(3)

	printer.setDefault() # Restore printer to defaults



def print_keypair(pubkey, privkey, leftBorderText, coinType):

#open the printer itself
	printer = Adafruit_Thermal("/dev/ttyAMA0", 19200, timeout=5)

#check the cointype to decide which background to use
	con = None
	try:
		con = sqlite3.connect('/home/pi/Printer/settings.db3')
		cur = con.cursor()
		cur.execute("SELECT bgfile FROM CoinFormats WHERE name=?;",(coinType,))
		row = cur.fetchone()
		finalImgName = row[0]
	except sqlite3.Error, e:
		print("Error %s:" % e.args[0])
		sys.exit(1)
	finally:
		if con:
			con.commit()
			con.close()
	printCoinName = (finalImgName == "blank")

	finalImgName += "-wallet"
#load a blank image of the paper wallet with no QR codes or keys on it which we will draw on
	if(len(privkey) > 51):
		finalImgName += "-enc"

	finalImgName += ".bmp"
	
	finalImgFolder = "/home/pi/Printer/Images/"
	finalImg = Image.open(finalImgFolder+finalImgName)



#---begin the public key qr code generation and drawing section---

#we begin the QR code creation process
#feel free to change the error correct level as you see fit
	qr = qrcode.QRCode(
	    version=None,
	    error_correction=qrcode.constants.ERROR_CORRECT_H,
	    box_size=10,
	    border=0,
	)

	qr.add_data(pubkey)
	qr.make(fit=True)

	pubkeyImg = qr.make_image()

#resize the qr code to match our design
	pubkeyImg = pubkeyImg.resize((175,175), Image.NEAREST)


	font = ImageFont.truetype("/usr/share/fonts/ttf/swansea.ttf", 60)
	draw = ImageDraw.Draw(finalImg)

	if(printCoinName):
		draw.text((45, 400), coinType, font=font, fill=(0,0,0))


	font = ImageFont.truetype("/usr/share/fonts/ttf/ubuntu-font-family-0.80/UbuntuMono-R.ttf", 20)
	startPos=(110,38)
	charDist=15
	lineHeight=23
	lastCharPos=0

	keyLength = len(pubkey)

	while(keyLength % 17 != 0):
		pubkey += " "
		keyLength = len(pubkey)




#draw 2 lines of 17 characters each.  keyLength always == 34 so keylength/17 == 2
	for x in range(0,keyLength/17):
		lastCharPos=0
		#print a line
		for y in range(0, 17):
			theChar = pubkey[(x*17)+y]
			charSize = draw.textsize(theChar, font=font)
			
			#if y is 0 then this is the first run of this loop, and we should use startPos[0] for the x coordinate instead of the lastCharPos
			if y == 0:
				draw.text((startPos[0],startPos[1]+(lineHeight*x)),theChar, font=font, fill=(0,0,0))
				lastCharPos = startPos[0]+charSize[0]+(charDist-charSize[0])
			else:
				draw.text((lastCharPos,startPos[1]+(lineHeight*x)),theChar, font=font, fill=(0,0,0))
				lastCharPos = lastCharPos + charSize[0] + (charDist-charSize[0])



#draw the QR code on the final image
	finalImg.paste(pubkeyImg, (150, 106))

#---end the public key qr code generation and drawing section---





#---begin the private key qr code generation and drawing section---

#we begin the QR code creation process
#feel free to change the error correct level as you see fit
	qr = qrcode.QRCode(
	    version=None,
	    error_correction=qrcode.constants.ERROR_CORRECT_H,
	    box_size=10,
	    border=0,
	)
	qr.add_data(privkey)
	qr.make(fit=True)

	privkeyImg = qr.make_image()

#resize the qr code to match our design
	privkeyImg = privkeyImg.resize((220,220), Image.NEAREST)

	#draw the QR code on the final image
	finalImg.paste(privkeyImg, (125, 560))


	startPos=(110,807)
	charDist=15
	lineHeight=23
	lastCharPos=0

	keyLength = len(privkey)

	while(keyLength % 17 != 0):
		privkey += " "
		keyLength = len(privkey)


#draw 2 lines of 17 characters each.  keyLength always == 34 so keylength/17 == 2
	for x in range(0,keyLength/17):
		lastCharPos=0
		#print a line
		for y in range(0, 17):
			theChar = privkey[(x*17)+y]
			charSize = draw.textsize(theChar, font=font)
			#print charSize
			if y == 0:
				draw.text((startPos[0],startPos[1]+(lineHeight*x)),theChar, font=font, fill=(0,0,0))
				lastCharPos = startPos[0]+charSize[0]+(charDist-charSize[0])
			else:
				draw.text((lastCharPos,startPos[1]+(lineHeight*x)),theChar, font=font, fill=(0,0,0))
				lastCharPos = lastCharPos + charSize[0] + (charDist-charSize[0])

#---end the private key qr code generation and drawing section---



#create the divider
	rightMarkText = "Piperwallet.com"


	font = ImageFont.truetype("/usr/share/fonts/ttf/swansea.ttf", 20)

	rightMarkSize = draw.textsize(rightMarkText, font=font)

	leftMarkOrigin = (10, 15)
	rightMarkOrigin = (384-rightMarkSize[0]-10, 15)

	dividerLineImg = Image.open("/home/pi/Printer/dividerline.bmp")
    
	draw = ImageDraw.Draw(dividerLineImg)    
	draw.text(leftMarkOrigin, leftBorderText, font=font, fill=(0,0,0))
	draw.text(rightMarkOrigin,rightMarkText, font=font, fill=(0,0,0))



	#strip whitespace from private key
	privkey = privkey.strip()
	
    	#do the actual printing
	printer.printImage(finalImg)
	if(len(privkey) <= 51):
		printer.printChar(privkey[:17]+"\n")
		printer.justify('R')
		printer.printChar(privkey[17:34]+"\n")
		printer.justify('L')
		printer.printChar(privkey[34:]+"\n")
	else:
		printer.println(privkey)

	#print the divider line
	printer.printImage(dividerLineImg)
	
	#print some blank space so we can get a clean tear of the paper
	printer.feed(3)





	printer.setDefault() # Restore printer to defaults
	
def genKeys(remPubKey, remPrivKey, password, coinType, remPW):

	#open serial number file which tracks the serial number
	snumfile = open('serialnumber.txt', 'r+')
	snum = snumfile.read()
	
	#update serial number
	snumfile.seek(0,0)
	snumfile.write(str(int(snum)+1))
	snumfile.close()



	#this actually generates the keys.  see the file genkeys.py or genkeys_forget.py
	import genkeys as btckeys

	btckeys.genKeys()
		
	import wallet_enc as WalletEnc
	#encrypt the keys if needed
	sqliteEncrypted = 0
	if(password != ""):
		privkey = WalletEnc.pw_encode(btckeys.pubkey, btckeys.privkey, password)
		sqliteEncrypted = 1
	else:
		privkey = btckeys.privkey
	
	
	rememberKeys = False
	sqlitePubKey = ""
	sqlitePrivKey = ""
	sqlitePW = ""
	strToWrite = ""
	if remPubKey:
		strToWrite = "\nPublic Key: "+btckeys.pubkey
		sqlitePubKey = btckeys.pubkey
		rememberKeys = True

	if remPrivKey:
		strToWrite = strToWrite + "\nPrivate Key: "+privkey
		sqlitePrivKey = privkey
		rememberKeys = True

	if remPW:
		strToWrite = strToWrite + "\nPassword: "+password
		sqlitePW = password
		rememberKeys = True



	if rememberKeys == True:


		#store it to the sqlite db
		con = None
		try:
			con = sqlite3.connect('/home/pi/Printer/keys.db3')
		        con.execute("INSERT INTO keys (serialnum, public, private, coinType, password, encrypted) VALUES (?,?,?,?,?,?)", (snum, sqlitePubKey, sqlitePrivKey, coinType, sqlitePW, sqliteEncrypted))
		except sqlite3.Error, e:
			print "Error %s:" % e.args[0]
			sys.exit(1)
		finally:
			if con:
				con.commit()
				con.close()
			
		
		#store it in a flat file on the sd card
		f = open("/boot/keys.txt", 'a+')
		strToWrite = strToWrite + "\nCoin Type: "+coinType
		strToWrite = "Serial Number: " + snum + strToWrite
		f.write(strToWrite);
		f.write("\n---------------------------------\n")
		f.close()


	leftMarkText = "Serial Number: "+snum
	return btckeys.pubkey, privkey, leftMarkText



def genAndPrintKeys(remPubKey, remPrivKey, numCopies, password, coinType, remPW):
	
	pubkey, privkey, leftMarkText = genKeys(remPubKey, remPrivKey, password, coinType, remPW)
	
	#do the actual printing
	for x in range(0, numCopies):
		#piper.print_keypair(pubkey, privkey, leftBorderText)
		print_keypair(pubkey, privkey, leftMarkText, coinType)
		




def genAndPrintKeysAndPass(remPubKey, remPrivKey, numCopies, password, coinType, remPW):

	pubkey, privkey, leftMarkText = genKeys(remPubKey, remPrivKey, password, coinType, remPW)
	
	#do the actual printing
	for x in range(0, numCopies):
		#piper.print_keypair(pubkey, privkey, leftBorderText)
		print_keypair(pubkey, privkey, leftMarkText, coinType)
		if password != "":
			print_password(leftMarkText, password)
		



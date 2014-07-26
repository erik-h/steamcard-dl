#!/usr/bin/env python

import urllib2
import sys
from bs4 import BeautifulSoup
import time
import imghdr
import os
import re

def downloadImage(gameName, imageName, url, fType):

	isBg = False

	imageName = imageName[:imageName.find("-")-1]

	#file_name = url.split('/')[-1]
	if fType == "card":
		file_name = "{0} - {1}{2}".format(gameName, imageName, url[url.rfind("."):])

	else: # fType == bg
		file_name = "{0} - {1}".format(gameName, imageName)
		isBg = True

	u = urllib2.urlopen(url)
	f = open(file_name, 'wb')
	meta = u.info()
	file_size = int(meta.getheaders("Content-Length")[0])
	print "Downloading: %s Bytes: %s" % (file_name, file_size)

	file_size_dl = 0
	block_sz = 8192
	while True:
		buffer = u.read(block_sz)
		if not buffer:
			break

		file_size_dl += len(buffer)
		f.write(buffer)
		status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
		status = status + chr(8)*(len(status)+1)
		print status,	
	

	f.close()

	if isBg:
		bgFileType = imghdr.what(file_name)
		os.rename(file_name, file_name + ".".format(bgFileType))


def main():

	BASEURL = "http://www.steamcardexchange.net/index.php?showcase"

	categoryURLList = ["-filter-ac", "-filter-df", "-filter-gi", "-filter-jl", "-filter-mo", "-filter-pr", "-filter-su", "-filter-vx", "-filter-yz", "-filter-09",]
	gamesDict = {}

	for filterURL in categoryURLList:

		page = urllib2.urlopen(BASEURL + filterURL)
		soup = BeautifulSoup(page.read())

		games = soup.findAll("div", attrs={"class":"showcase-game-item"})

		for game in games:	

			gameLink = game.select("a")[0]

			name = gameLink.find("img").get("alt")

			#print gameLink.get("href")	
			#print name

			gamesDict[name] = gameLink.get("href")

	for key in sorted(gamesDict.keys()):
		#print "{0}: {1}".format(key.encode("utf-8"), gamesDict[key].encode("utf-8"))
		page = urllib2.urlopen("http://www.steamcardexchange.net/" + gamesDict[key])
		soup = BeautifulSoup(page.read())

		cards = soup.findAll("div", {"class":"showcase-element-card"})

		hdBgrounds = soup.findAll("div", {"class":"showcase-element-background"})

		alreadyDoneCardLinks = []
		alreadyDoneBgLinks = []

		for card in cards:	
			# this part is ugly..I'll clean it up later
			try:
				hdImageLink = card.find("a", {"class":"card-image-link"}).get("href")
				hdImageName = card.findAll("a")[1].get("title")# hdImageName = card.find("span", {"class":"card-name"}).text
				if not hdImageLink in alreadyDoneCardLinks:
					downloadImage(key, hdImageName, hdImageLink, "card")
					alreadyDoneCardLinks.append(hdImageLink)
				#print "hdImageLink = {0}".format(hdImageLink)
				#print "hdImageName = {0}".format(hdImageName)
			except Exception as e:
				#print "card ERROR {0}".format(str(e))
				time.sleep(1)
				continue

		for hdBg in hdBgrounds:
			#print "DL A BACKGROUND:"
			try:
				hdBgLink = hdBg.find("a", {"class":"background-hd-link"}).get("href")
				hdBgName = hdBg.findAll("a")[2].get("title")# hdBgName = hdBg.find("span", {"class":"background-name"}).text
				if not hdBgLink in alreadyDoneBgLinks:
					downloadImage(key, hdBgName, hdBgLink, "bg")
					alreadyDoneBgLinks.append(hdBgLink)
			except Exception as e:
				#print "background ERROR: {0}".format(str(e))
				time.sleep(1)
				continue
	
	

	#print "Size of gamesDict = {0}".format(len(gamesDict))


if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print "\nStopping..."
		sys.exit(0)

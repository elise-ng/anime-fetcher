from xml.dom import minidom
from urllib.request import urlopen
import urllib.parse
import time
import os
import json

firstRun = False
def setup():
    firstRun = True
    print("Config not found")
    config["last_fetch"] = time.strftime("%Y-%m-%d %H:%M:%S %z")
    config["watch_list"] = []
    exitFlag = False
    while not exitFlag:
        inputStr = input("Enter search keywords (empty to exit): ")
        if inputStr != '':
            config["watch_list"].append(inputStr.strip().replace(" ","+"))
        else:
            exitFlag = True
    with open('config.json',"w+") as configFile:
        json.dump(config, configFile, ensure_ascii=False)
        print("Config saved")
try:
    with open("config.json","r") as configFile:
        try:
            config = json.load(configFile)
        except Exception as e:
            config = {}
            setup()
except Exception as e:
    config = {}
    setup()

newItemList = []
if input("Add item to list? [No]:").lower() in ['y','yes']:
    exitFlag = False
    while not exitFlag:
        inputStr = input("Enter search keywords (empty to exit): ")
        if inputStr != '':
            newItemList.append(inputStr.strip().replace(" ","+"))
        else:
            exitFlag = True

print("Last Update:",config["last_fetch"])
print("Searching for:")
for target in config["watch_list"]:
    print(target.replace("+"," "))
for target in newItemList:
    print("(new)",target.replace("+"," "))
titleList = []
magnetList = []
for query in config["watch_list"]:
    targetURL = "http://share.dmhy.org/topics/rss/rss.xml?keyword=" + urllib.parse.quote(query.encode('utf-8')).replace("%2B","+")
    with urlopen(targetURL) as response:
        xmlDoc = minidom.parseString(response.read().decode('utf-8'))
    itemList = xmlDoc.getElementsByTagName('rss')[0].getElementsByTagName('item')
    for item in itemList:
        if firstRun or time.strptime(item.getElementsByTagName('pubDate')[0].firstChild.nodeValue,"%a, %d %b %Y %H:%M:%S %z") > time.strptime(config["last_fetch"],"%Y-%m-%d %H:%M:%S %z"):
            titleList.append(item.getElementsByTagName('title')[0].firstChild.nodeValue)
            magnetList.append(item.getElementsByTagName('enclosure')[0].attributes['url'].value)

for query in newItemList:
    targetURL = "http://share.dmhy.org/topics/rss/rss.xml?keyword=" + urllib.parse.quote(query.encode('utf-8')).replace("%2B","+")
    with urlopen(targetURL) as response:
        xmlDoc = minidom.parseString(response.read().decode('utf-8'))
    itemList = xmlDoc.getElementsByTagName('rss')[0].getElementsByTagName('item')
    for item in itemList:
        titleList.append(item.getElementsByTagName('title')[0].firstChild.nodeValue)
        magnetList.append(item.getElementsByTagName('enclosure')[0].attributes['url'].value)

config["last_fetch"] = time.strftime("%Y-%m-%d %H:%M:%S %z")
for newItem in newItemList:
    config["watch_list"].append(newItem)
with open('config.json',"w") as configFile:
    json.dump(config, configFile, ensure_ascii=False)
if len(magnetList) > 0:
    print("New episodes found:")
    for title in titleList:
        print(title)
    if not input("Begin download? [Yes]:").lower() in ['n','no']:
        for magnet in magnetList:
            os.system("open "+magnet)
else:
    print("No new episode found.")

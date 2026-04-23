import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement

# Creating the xml tree from scratch

root = Element("rss")
tree = ET.ElementTree(root)
channel = ET.SubElement(root, "channel")
chantitle = ET.SubElement(channel, "title")
chantitle.text = "Anthropic Research blog"
chanlink = ET.SubElement(channel, "link")
chanlink.text = "https://www.anthropic.com/research"
chandescription = ET.SubElement(channel, "description")
chandescription.text = "The Anthropic Research blog"

# Extract the Anthropic research page

r = requests.get("https://anthropic.com/research")
soup = BeautifulSoup(r.text, features="html.parser")
table = soup.find("ul", class_="PublicationList-module-scss-module__KxYrHG__list")
if table is None:
    print("Ereur, la table est vide")
    exit(1)
for row in table.find_all("a"):
    item = ET.SubElement(channel, "item")
    time = row.find("time").string
    pubDatetag = ET.SubElement(item, "pubDate")
    pubDatetag.text = time
    category = row.find("span").string
    categorytag = ET.SubElement(item, "category")
    categorytag.text = category
    link = row.get("href")
    linktag = ET.SubElement(item, "link")
    linktag.text = "https://www.anthropic.com" + link
    title = row.find(
        "span", class_="PublicationList-module-scss-module__KxYrHG__title body-3"
    ).string
    titletag = ET.SubElement(item, "title")
    titletag.text = title

# Writing to the xml file

tree.write(
    "/Users/pierredecobert/Library/Application Support/nom/Anthropic/anthropic.xml",
    encoding="utf-8",
    xml_declaration=True,
)

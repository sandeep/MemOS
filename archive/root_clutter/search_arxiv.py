import urllib.request
import xml.etree.ElementTree as ET

url = "http://export.arxiv.org/api/query?search_query=all:%22knowledge+graph%22+AND+all:%22LLM%22+AND+all:triples&start=0&max_results=5"
response = urllib.request.urlopen(url)
xml_data = response.read()

root = ET.fromstring(xml_data)
ns = {'atom': 'http://www.w3.org/2005/Atom'}
for entry in root.findall('atom:entry', ns):
    title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
    summary = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')
    print(f"TITLE: {title}")
    print(f"SUMMARY: {summary[:300]}...\n")

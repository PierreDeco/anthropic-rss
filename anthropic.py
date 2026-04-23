import logging
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement

import requests
from bs4 import BeautifulSoup

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

ANTHROPIC_BASE_URL = os.environ.get("ANTHROPIC_BASE_URL", "https://www.anthropic.com")
RESEARCH_PATH = os.environ.get("RESEARCH_PATH", "/research")
RSS_TITLE = os.environ.get("RSS_TITLE", "Anthropic Research blog")
RSS_DESCRIPTION = os.environ.get("RSS_DESCRIPTION", "The Anthropic Research blog")
OUTPUT_FILE = os.environ.get(
    "OUTPUT_FILE",
    str(Path.home() / "Library/Application Support/nom/Anthropic/anthropic.xml"),
)
REQUEST_TIMEOUT = int(os.environ.get("REQUEST_TIMEOUT", "30"))
CSS_LIST_CLASS = os.environ.get(
    "CSS_LIST_CLASS", "PublicationList-module-scss-module__KxYrHG__list"
)
CSS_TITLE_CLASS = os.environ.get(
    "CSS_TITLE_CLASS", "PublicationList-module-scss-module__KxYrHG__title body-3"
)


def build_rss_feed():
    root = Element("rss")
    tree = ET.ElementTree(root)
    channel = SubElement(root, "channel")
    SubElement(channel, "title").text = RSS_TITLE
    SubElement(channel, "link").text = f"{ANTHROPIC_BASE_URL}{RESEARCH_PATH}"
    SubElement(channel, "description").text = RSS_DESCRIPTION

    research_url = f"{ANTHROPIC_BASE_URL.rstrip('/')}{RESEARCH_PATH}"
    logger.info("Fetching %s", research_url)
    try:
        response = requests.get(research_url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.error("Failed to fetch research page: %s", exc)
        sys.exit(1)

    soup = BeautifulSoup(response.text, features="html.parser")
    table = soup.find("ul", class_=CSS_LIST_CLASS)
    if table is None:
        logger.error("RSS list element not found — the page structure may have changed (CSS_LIST_CLASS=%s)", CSS_LIST_CLASS)
        sys.exit(1)

    for row in table.find_all("a"):
        item = SubElement(channel, "item")
        time_el = row.find("time")
        SubElement(item, "pubDate").text = time_el.string if time_el else ""
        span = row.find("span")
        SubElement(item, "category").text = span.string if span else ""
        link = row.get("href", "")
        SubElement(item, "link").text = f"{ANTHROPIC_BASE_URL}{link}"
        title_span = row.find("span", class_=CSS_TITLE_CLASS)
        SubElement(item, "title").text = title_span.string if title_span else ""

    output_path = Path(OUTPUT_FILE)
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        tree.write(str(output_path), encoding="utf-8", xml_declaration=True)
    except OSError as exc:
        logger.error("Failed to write RSS feed to %s: %s", output_path, exc)
        sys.exit(1)

    logger.info("RSS feed written to %s (%d items)", output_path, len(table.find_all("a")))


if __name__ == "__main__":
    build_rss_feed()

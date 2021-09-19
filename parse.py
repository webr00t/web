#!/usr/bin/env python3

import requests
import sys
import gzip
import ujson as json
import base64
import os
import re
import csv

try:
    url = sys.argv[1]
except:
    print("Missing URL as argument")
    sys.exit(1)

ts = url.split('/')[-1].split('-')[0]

if not os.path.exists(ts):
    os.mkdir(ts)
def to_ascii(data):
    if isinstance(data, str):
        return data.encode("ascii", errors="ignore")
    elif isinstance(data, bytes):
        return data.decode("ascii", errors="ignore")

server_vers = []
host_server = []
OUTFILE = "outfile.csv"
def write_to_csv(row):
    with open(OUTFILE, 'a+') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(row)
    csvfile.close()

server_re = re.compile('Server: (?P<server>.+?)\r?\n', flags=re.IGNORECASE)
def get_server(html):
    match_obj = server_re.search(html)
    if match_obj is not None:
        match_obj = match_obj.group('server').strip()
    return match_obj

lines = 0

resp = requests.get(url, stream=True)
decompressed = gzip.GzipFile(fileobj=resp.raw)
for line in decompressed:
    tmp_lst = []
    entry = json.loads(line.decode())
    #decoded = base64.b64decode(entry['data'])
    decoded = to_ascii(base64.b64decode(entry["data"]))
    server_header_name = get_server(decoded)
    lines += 1
    if lines % 10000 == 0:
        print("%10d lines" % lines)
    if server_header_name is not None:
        tmp_lst.append(str(entry["host"]))
        tmp_lst.append(server_header_name)
        server_vers.append(server_header_name)
        host_server.append(tmp_lst)
        write_to_csv(tmp_lst)


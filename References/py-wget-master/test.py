#!/usr/bin/python
import requests,sys
from optparse import OptionParser

url = sys.argv[1]
headers = {
	'Range': 'bytes=0-20'
}

r = requests.head(url, headers = headers, proxies = {
		'http': 'http://127.0.0.1:8080/'
	})
print r.headers
#!/usr/bin/env python
#encoding=utf-8
import json
from urlparse import parse_qs
from wsgiref.simple_server import make_server
import requests
from datetime import datetime
import time


def main():
    while True:
        math = []
        urls = ["https://mainnet.infura.io/v3/dd70b311da9a4147b5974c8698dec90b", "http://127.0.0.1:18759", "http://10.66.178.171:18759", "http://172.17.67.187:18759"]
        data = {"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1}
        for url in urls:
            res = requests.post(url, json=data)
            result = res.json()
            height = int(result.get("result", "0"), base=16)
            math.append(height)
        print 50*"*", math
        time.sleep(1)

def application(environ, start_response):
    start_response('200 OK', [('Content-Type', 'application/json')])
    rt = main()
    result = {
        "success": 1,
        "data": rt
    }
    return json.dumps(result)


if __name__ == "__main__":
    # port = 18760
    # httpd = make_server("0.0.0.0", port, application)
    # httpd.serve_forever()
    main()


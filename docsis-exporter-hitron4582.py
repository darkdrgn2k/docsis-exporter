#!/usr/bin/python3
# Hitron CODA 4582 Modem
import pycurl
import json
import os
from io import BytesIO
from urllib.parse import urlparse, parse_qs

host_url = "https://192.168.100.1"
PASSWORD="cusadmin"

# Settings
PASSWORD = os.environ["PASSWORD"]
SERVER_ADDRESS = ('', 8000)

import sys

if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")

import http.server
if sys.version_info[1] < 7:
    # Can't use threaded HTTP server, which is new in 3.7
    server_class = http.server.HTTPServer
else:
    server_class = http.server.ThreadingHTTPServer
from http.server import BaseHTTPRequestHandler

class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path != "/metrics":
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(getData().encode())
#        self.wfile.close()
        

def curlGet(url,post):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, host_url + url)
    c.setopt(pycurl.TIMEOUT, 10)

    #c.setopt(pycurl.FOLLOWLOCATION, 1)
    if post != "":
        c.setopt(pycurl.POSTFIELDS, post)
    c.setopt(pycurl.COOKIEJAR, '/tmp/cookies')
    c.setopt(pycurl.COOKIEFILE, '/tmp/cookies')
    c.setopt(pycurl.WRITEDATA, buffer)
    c.setopt(pycurl.SSL_VERIFYPEER, 0);
    c.setopt(pycurl.SSL_VERIFYHOST, 0);

    c.perform()
    c.close()
    body = buffer.getvalue()
    return body

def getData():
    # Login
    body = curlGet("/1/Device/Users/Login",'model={"username":"cusadmin","password":"' + PASSWORD + '"}')
    res = json.loads(body)

    strRes = ""
    if res["result"] == "success":
        body = curlGet("/1/Device/CM/DsInfo","")
        ds = json.loads(body)
        if ds["errMsg"] == "":
            for freq in ds["Freq_List"]:
                d = '{portId="' + freq["portId"] + '", modulation="' + freq["modulation"] + '", channelId="' + freq["channelId"] + '", frequency="' + freq["frequency"] + '"}'
                strength = freq["signalStrength"]
                if strength != "-":
                   strRes += "cable_ds_signalStrength" + d + " " + strength + "\n"
                strRes += "cable_ds_snr" + d + " " + freq["snr"] + "\n"
                strRes += "cable_ds_octets" + d + " " + freq["dsoctets"] + "\n"
                strRes += "cable_ds_correcteds" + d + " " + freq["correcteds"] + "\n"
                strRes += "cable_ds_uncorrect" + d + " " + freq["uncorrect"] + "\n"
        body = curlGet("/1/Device/CM/UsInfo","")
        us = json.loads(body)
        if us["errMsg"] == "":
            for freq in us["Freq_List"]:
                d = '{portId="' + freq["portId"] + '", modulation="' + freq["modulationType"] + '", channelId="' + freq["channelId"] + '", frequency="' + freq["frequency"] + '"}'
                strength = freq["signalStrength"]
                if strength != "-":
                    strRes += "cable_us_signalStrength" + d + " " + strength + "\n"
                strRes += "cable_us_bandwidth" + d + " " + freq["bandwidth"] + "\n"
        return strRes

SERVER_ADDRESS = ('', 8000)
def main():
    httpd = server_class(SERVER_ADDRESS, HTTPRequestHandler)
    httpd.serve_forever()

if __name__ == "__main__":
    main()

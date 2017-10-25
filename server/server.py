#!/usr/bin/env python
"""
Very simple HTTP server in python.
Usage::
    ./dummy-web-server.py [<port>]
Send a GET request::
    curl http://localhost
Send a HEAD request::
    curl -I http://localhost
Send a POST request::
    curl -d "foo=bar&bin=baz" http://localhost
"""
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import BaseHTTPServer, SimpleHTTPServer
import ssl

import os
import urllib
import time
from multiprocessing import Pool
import threading
import operator

download_pool = []
database = dict()


def download_audio(args):
    urllib.urlretrieve(*args)

def proccess_download_pool(path):
    t = threading.currentThread()
    
    global download_pool
    
    while getattr(t, "do_run", True):
        if len(download_pool) == 0:
            time.sleep(5)
            continue

        download_backup = download_pool[:]
        pool = Pool(processes=10)
        res = pool.map_async(
            download_audio,
            [(url, os.path.join(path, str(audio_id)+'.mp3')) for audio_id, url in download_backup]
        )
        res.get()
        pool.close()
        pool.join()

        download_pool = filter(lambda d: d not in download_backup, download_pool)


class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write("trololo")

    def do_HEAD(self):
        self._set_headers()
        
    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        print post_data # <-- Print post data
        
        audio_id, artist, title, url = post_data.split('\t')
        user_id = audio_id.split('_')[0]

        if user_id not in database:
            database[user_id] = dict()
        audio = {'id': audio_id, 'artist': artist, 'title': title, 'url': url}
        if audio_id not in database[user_id] or database[user_id][audio_id] != audio:
            print "{} need to be download!".format(audio_id)
            download_pool.append((audio_id, url))
            database[user_id][audio_id] = audio 
        else:
            print "{} has already been downloaded!".format(audio_id)
        
        self._set_headers()


def run(server_class=HTTPServer, handler_class=S, port=86):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting httpd...at port ', port
    t1 = threading.Thread(target=proccess_download_pool, args=('/mnt/hdd/music_map_project/data_mp3', ))
    try:
        t1.start()
        httpd.serve_forever()
    finally:
        t1.do_run = False
        t1.join()


if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
#!/usr/bin/env python3
"""
LAZPOOL Local Server v1.3
==========================
Serves the app on port 3000.
Proxies Home Assistant API calls on port 3001, passing through
the Authorization header sent by the browser — no config file needed.

All setup is done in the LAZPOOL UI:
  Settings -> Home Assistant -> enter IP + token -> Save
  Settings -> Access & Hosting -> Local Serve (default)

The token you enter in the app is stored in browser localStorage,
sent in each request header, forwarded by this proxy to HA.
Export your config in the app to back everything up.

Usage:
    start.bat          (Windows - recommended)
    python3 server.py  (any OS)

Access at: http://localhost:3000  or  http://YOUR-LAN-IP:3000
"""

import http.server
import socketserver
import urllib.request
import urllib.error
import json
import threading
import os
import sys
import socket

APP_PORT   = 3000
PROXY_PORT = 3001
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


class ProxyHandler(http.server.BaseHTTPRequestHandler):
    """
    CORS proxy - forwards browser requests to Home Assistant.

    Request path: /proxy/HAHOST:PORT/api/...
    The browser encodes the full HA target in the path so the proxy
    knows where to forward with no config file needed.

    Example:
      Browser:  GET http://localhost:3001/proxy/10.0.0.51:8123/api/states
      Proxy:    GET http://10.0.0.51:8123/api/states
      Auth header passed through unchanged from the browser.
    """

    def log_message(self, fmt, *args):
        print(f"[PROXY] {self.command} {self.path[:80]}")

    def _cors(self, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._cors(200)

    def _forward(self, method):
        raw = self.path.lstrip('/')
        if raw.startswith('proxy/'):
            raw = raw[len('proxy/'):]

        if not raw:
            self._cors(400)
            self.wfile.write(b'{"error":"Missing target path"}')
            return

        target = f'http://{raw}'
        print(f"[PROXY] -> {target[:90]}")

        auth = self.headers.get('Authorization', '')
        content_type = self.headers.get('Content-Type', 'application/json')

        body = None
        length = int(self.headers.get('Content-Length', 0))
        if length > 0:
            body = self.rfile.read(length)

        fwd_headers = {'Content-Type': content_type}
        if auth:
            fwd_headers['Authorization'] = auth

        try:
            req = urllib.request.Request(target, data=body, headers=fwd_headers, method=method)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = resp.read()
                self._cors(resp.status)
                self.wfile.write(data)
        except urllib.error.HTTPError as e:
            data = e.read()
            self._cors(e.code)
            self.wfile.write(data)
            print(f"[PROXY] HA returned {e.code}: {data[:120]}")
        except Exception as e:
            self._cors(502)
            self.wfile.write(json.dumps({'error': str(e)}).encode())
            print(f"[PROXY] Error: {e}")

    def do_GET(self):  self._forward('GET')
    def do_POST(self): self._forward('POST')


class AppHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=SCRIPT_DIR, **kwargs)

    def log_message(self, fmt, *args):
        pass  # silent

    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return 'localhost'


def start_proxy():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(('', PROXY_PORT), ProxyHandler) as srv:
        srv.serve_forever()


def start_app():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(('', APP_PORT), AppHandler) as srv:
        srv.serve_forever()


if __name__ == '__main__':
    ip = get_local_ip()
    print('=' * 54)
    print('  LAZPOOL v1.3 - Local Server')
    print('=' * 54)
    print(f'  App:   http://localhost:{APP_PORT}')
    print(f'  App:   http://{ip}:{APP_PORT}  <- bookmark this on your phone')
    print(f'  Proxy: http://localhost:{PROXY_PORT}  (internal only)')
    print()
    print('  No config file needed.')
    print('  Enter your HA IP + token in the app Settings.')
    print('  Ctrl+C to stop.')
    print('=' * 54)

    proxy_thread = threading.Thread(target=start_proxy, daemon=True)
    proxy_thread.start()

    try:
        start_app()
    except KeyboardInterrupt:
        print('\n  Stopped.')
        sys.exit(0)

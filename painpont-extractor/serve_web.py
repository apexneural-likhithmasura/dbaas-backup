#!/usr/bin/env python3
"""
Simple web server to serve the index.html file
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

PORT = 8080
DIRECTORY = Path(__file__).parent

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def main():
    os.chdir(DIRECTORY)
    
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        print("=" * 60)
        print("🌐 Topics API Web Interface")
        print("=" * 60)
        print(f"📄 Serving HTML at: http://localhost:{PORT}")
        print(f"📁 Directory: {DIRECTORY}")
        print("=" * 60)
        print("📋 Available URLs:")
        print(f"   • Web Interface: http://localhost:{PORT}")
        print(f"   • API Docs: http://localhost:8000/docs")
        print(f"   • API Health: http://localhost:8000/health")
        print("=" * 60)
        print("🎯 The web page will automatically:")
        print("   • Load top 6 topics for 15 years by default")
        print("   • Display topic name, growth, and description")
        print("   • Allow switching between 2, 10, and 15 years")
        print("   • Auto-refresh every 5 minutes")
        print("=" * 60)
        print("Press Ctrl+C to stop the web server")
        print("=" * 60)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Web server stopped.")
            httpd.shutdown()

if __name__ == "__main__":
    main()

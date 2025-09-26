"""Simple HTTP server for the frontend"""
import http.server
import socketserver
import os

# Change to the directory containing the HTML file
os.chdir(r'D:\Claude\Endeavor_1_2\ercot_explorer')

PORT = 8080

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Server running at http://localhost:{PORT}/")
    print(f"Open http://localhost:{PORT}/frontend_simple.html in your browser")
    httpd.serve_forever()
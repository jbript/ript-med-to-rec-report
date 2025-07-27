from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        response = {
            "service": "RIPT Med to Rec Report API",
            "status": "active",
            "message": "Your cannabis reporting API is working!"
        }
        
        self.wfile.write(json.dumps(response).encode())

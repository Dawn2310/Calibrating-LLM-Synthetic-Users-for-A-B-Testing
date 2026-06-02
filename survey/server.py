import http.server
import socketserver
import json
import os

PORT = 8000
DATA_FILE = "responses.jsonl"
SURVEY_DIR = os.path.dirname(os.path.abspath(__file__))

# Change working directory so it serves index.html and saves to the right folder
os.chdir(SURVEY_DIR)

class SurveyHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/submit':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                # Parse to ensure it's valid JSON
                data = json.loads(post_data.decode('utf-8'))
                
                # Append to file
                with open(DATA_FILE, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(data) + '\n')
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"status":"ok"}')
            except Exception as e:
                print(f"Error saving data: {e}")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"status":"error"}')
        else:
            self.send_error(404, "Not Found")

print(f"Starting survey server at http://localhost:{PORT}")
print(f"Responses will be saved to survey/{DATA_FILE}")
print("Press Ctrl+C to stop.")

with socketserver.TCPServer(("", PORT), SurveyHandler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")

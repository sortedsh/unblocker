from flask import Flask, request, Response
import requests
import urllib3

app = Flask(__name__)

# Disable SSL warnings (because we're using verify=False)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

@app.route('/')
def home():
    return '''
    <h2>Python Web Unblocker (SSL Ignored)</h2>
    <form action="/proxy" method="get">
        <input type="text" name="url" placeholder="https://example.com" style="width: 400px; padding: 5px;" />
        <input type="submit" value="Go" style="padding: 5px;" />
    </form>
    '''

@app.route('/proxy')
def proxy():
    target_url = request.args.get('url')
    if not target_url:
        return 'No URL provided.'

    try:
        headers = {
            'User-Agent': request.headers.get('User-Agent', 'Mozilla/5.0')
        }

        # INSECURE: Bypass SSL verification (this is what fixes the error you're getting)
        response = requests.get(target_url, headers=headers, verify=False)

        return Response(response.content, content_type=response.headers.get('Content-Type', 'text/html'))

    except Exception as e:
        return f'<p>Error accessing <strong>{target_url}</strong>:</p><pre>{str(e)}</pre>'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
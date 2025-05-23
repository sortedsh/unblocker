from flask import Flask, request, Response
import requests
from bs4 import BeautifulSoup
import urllib3
import traceback
from urllib.parse import urljoin, quote

app = Flask(__name__)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Website Unblocker</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: linear-gradient(to right, #2c3e50, #3498db);
            color: #fff;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
        }}
        .container {{
            background-color: rgba(0, 0, 0, 0.4);
            padding: 30px 40px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            text-align: center;
        }}
        h2 {{
            margin-bottom: 20px;
        }}
        input[type="text"] {{
            width: 400px;
            padding: 10px;
            font-size: 16px;
            border: none;
            border-radius: 5px;
            margin-bottom: 15px;
        }}
        input[type="submit"] {{
            padding: 10px 20px;
            font-size: 16px;
            background-color: #27ae60;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.3s;
        }}
        input[type="submit"]:hover {{
            background-color: #2ecc71;
        }}
        .error {{
            background-color: rgba(255, 0, 0, 0.2);
            padding: 10px;
            border-radius: 5px;
            color: #ffdddd;
            margin-top: 20px;
            max-width: 700px;
            overflow-wrap: break-word;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h2>🌐 Website Unblocker</h2>
        <form action="/proxy" method="get">
            <input type="text" name="url" placeholder="https://example.com" required />
            <br>
            <input type="submit" value="Go" />
        </form>
        {error}
    </div>
</body>
</html>
'''

def rewrite_html(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')

    # Tags and their attributes to rewrite
    tags_attrs = {
        'a': 'href',
        'img': 'src',
        'script': 'src',
        'link': 'href',
        'iframe': 'src',
    }

    for tag_name, attr in tags_attrs.items():
        for tag in soup.find_all(tag_name):
            if tag.has_attr(attr):
                try:
                    raw_url = tag[attr]
                    if raw_url.startswith('javascript:'):
                        continue
                    full_url = urljoin(base_url, raw_url)
                    tag[attr] = f"/proxy?url={quote(full_url)}"
                except Exception as e:
                    print(f"Error rewriting tag <{tag_name}>: {e}")

    # Rewrite form actions
    for form in soup.find_all('form'):
        if form.has_attr('action'):
            try:
                full_url = urljoin(base_url, form['action'])
                form['action'] = f"/proxy?url={quote(full_url)}"
            except Exception as e:
                print(f"Error rewriting form action: {e}")

    return str(soup)

@app.route('/')
def home():
    return HTML_TEMPLATE.format(error='')

@app.route('/proxy')
def proxy():
    target_url = request.args.get('url')
    if not target_url:
        return HTML_TEMPLATE.format(error='<div class="error">⚠️ No URL provided.</div>')

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(target_url, headers=headers, verify=False)
        content_type = response.headers.get('Content-Type', '')

        if 'text/html' in content_type:
            rewritten_html = rewrite_html(response.text, target_url)
            return Response(rewritten_html, content_type='text/html')
        else:
            return Response(response.content, content_type=content_type)

    except Exception as e:
        traceback.print_exc()
        error_message = f'<div class="error">❌ Error accessing <strong>{target_url}</strong>:<br><pre>{str(e)}</pre></div>'
        return HTML_TEMPLATE.format(error=error_message)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

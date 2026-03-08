from flask import Flask, request, Response
import cloudscraper

app = Flask(__name__)

# Cloudflare bypass karne wala scraper (Asli Chrome browser ka bhes)
scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'darwin', 'desktop': True})

# Aapka Premium Token
MY_TOKEN = '1jF9U0UInXafq4EZlapcEy4QkQizJ99uL'

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
    target_url = f"https://flingster.com/{path}"
    
    try:
        # Flingster se page maangna using Cloudscraper
        resp = scraper.get(target_url, params=request.args)
        
        # Agar HTML page hai, toh apna Token inject karo
        if 'text/html' in resp.headers.get('Content-Type', ''):
            injection_script = f'''
            <script>
                document.cookie = "Member={MY_TOKEN}; path=/; domain=.flingster.com; max-age=31536000";
                window.localStorage.setItem('Member', '{MY_TOKEN}');
            </script>
            '''
            modified_content = resp.text.replace('<head>', f'<head>{injection_script}')
            return Response(modified_content, resp.status_code, content_type=resp.headers['Content-Type'])
        
        # CSS/JS files ke liye headers pass karna
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        
        return Response(resp.content, resp.status_code, headers)
        
    except Exception as e:
        return f"Error connecting to Flingster: {e}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
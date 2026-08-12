import requests
import time
import re
import base64
from urllib.parse import urlparse, parse_qs
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def _d(s):
    return base64.b64decode(s).decode('utf-8')

def get_real_link(proxy_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Connection": "keep-alive"
    }
    try:
        response = requests.get(proxy_url, headers=headers, allow_redirects=False, verify=False, timeout=5)
        
        if response.status_code in [301, 302, 303, 307, 308]:
            redirect_url = response.headers.get('Location')
            
            if redirect_url:
                parsed_url = urlparse(redirect_url)
                query_params = parse_qs(parsed_url.query)
                final_url = ""
                
                if 'url' in query_params and query_params['url'][0]:
                    final_url = query_params['url'][0]
                
                if 'referer' in query_params and query_params['referer'][0] and final_url:
                    final_url += f"|Referer={query_params['referer'][0]}"
                
                if final_url:
                    return final_url
                return redirect_url
                
    except Exception:
        pass
        
    return None

def main():
    timestamp = int(time.time() * 1000)
    u1 = _d('aHR0cHM6Ly9wbGF5bGlzdC5lbW9uc2E0LndvcmtlcnMuZGV2L3BsYXlsaXN0Lm0zdQ==') + f"?t={timestamp}"
    o1 = _d('aHR0cHM6Ly9vYmlyYW10dmxpdmUucGFnZXMuZGV2')
    r1 = _d('aHR0cHM6Ly9vYmlyYW10dmxpdmUucGFnZXMuZGV2Lw==')
    k1 = _d('Y3JpY2hkcHJveHk=')
    k2 = _d('d29ya2Vycy5kZXY=')
    
    headers = {
        "Origin": o1,
        "Referer": r1,
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(u1, headers=headers, verify=False, timeout=15)
        
        if response.status_code == 200 and response.text:
            lines = response.text.split('\n')
            modified_playlist = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if line.startswith('#EXTINF:'):
                    line = re.sub(r'group-title="[^"]*"\s*', '', line, flags=re.IGNORECASE)
                    line = re.sub(r'^(#EXTINF:[^,]+)(.*)$', r'\1 group-title="MY BC"\2', line, flags=re.IGNORECASE)
                    
                elif line.startswith('http'):
                    if k1 in line or k2 in line:
                        real_link = get_real_link(line)
                        if real_link:
                            line = real_link
                        else:
                            if '|' not in line:
                                line += f"|Origin={o1}&Referer={r1}"
                    else:
                        if '|' not in line:
                            line += f"|Origin={o1}&Referer={r1}"
                
                modified_playlist.append(line)
            
            output_filename = "ovaga.m3u"
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(modified_playlist))
                
    except Exception:
        pass

if __name__ == "__main__":
    main()

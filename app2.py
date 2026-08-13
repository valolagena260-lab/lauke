import requests
import json
import re
from datetime import datetime
import urllib.parse

# M3U ফাইলের লিংক
m3u_url = "https://raw.githubusercontent.com/sm-monirulislam/SM-IPTV/refs/heads/main/akash_go.m3u"

try:
    response = requests.get(m3u_url)
    response.raise_for_status()
    lines = response.text.splitlines()
except Exception as e:
    print(f"Error fetching M3U: {e}")
    exit()

channels = []
current_channel = {}

for line in lines:
    line = line.strip()
    if not line:
        continue
        
    if line.startswith("#EXTINF"):
        # লোগো (logo) বের করা
        logo_match = re.search(r'tvg-logo="(.*?)"', line)
        current_channel['logo'] = logo_match.group(1) if logo_match else ""
        
        # ক্যাটাগরি (category_name) বের করা
        group_match = re.search(r'group-title="(.*?)"', line)
        current_channel['category_name'] = group_match.group(1) if group_match else ""
        
        # চ্যানেলের নাম (name) বের করা
        name_parts = line.split(',')
        current_channel['name'] = name_parts[-1].strip() if len(name_parts) > 1 else ""
        
    elif line.startswith("#EXTHTTP"):
        # কুকি (cookie) বের করা
        try:
            json_str = line.replace("#EXTHTTP:", "").strip()
            http_data = json.loads(json_str)
            current_channel['cookie'] = http_data.get('cookie', '')
        except:
            current_channel['cookie'] = ""
            
    elif not line.startswith("#"):
        # চ্যানেলের লিংক এবং Host বের করা
        current_channel['link'] = line
        
        try:
            # লিংক থেকে স্বয়ংক্রিয়ভাবে Host ডোমেইন বের করার জন্য
            parsed_url = urllib.parse.urlparse(line)
            host = parsed_url.netloc
        except:
            host = ""
        
        # চ্যানেলের ডেটা আপনার দেওয়া নির্দিষ্ট ফরম্যাটে সাজানো
        channel_data = {
            "category_name": current_channel.get('category_name', ''),
            "name": current_channel.get('name', ''),
            "link": current_channel.get('link', ''),
            "headers": {
                "Host": host,
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
                "client-api-header": "null",
                "accept-encoding": "gzip",
                "cookie": current_channel.get('cookie', '')
            },
            "logo": current_channel.get('logo', '')
        }
        
        channels.append(channel_data)
        current_channel = {} # পরের চ্যানেলের জন্য ক্লিয়ার করা

# বর্তমান সময় (Last_update এর জন্য)
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ফাইনাল JSON স্ট্রাকচার (Akal, Moga এবং অন্যান্য ইনফরমেশন সহ)
final_json = {
    "status": "success",
    "name": "Akal",
    "owner": "Moga",
    "channels_amount": len(channels),
    "Last_update": current_time,
    "response": channels
}

# akal.json ফাইলে সেভ করা
with open('akal.json', 'w', encoding='utf-8') as f:
    json.dump(final_json, f, indent=4, ensure_ascii=False)

print(f"Successfully generated akal.json with {len(channels)} channels.")

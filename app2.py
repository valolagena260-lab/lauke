import requests
import json
import re

# Source M3U URL provided by you
M3U_URL = "https://raw.githubusercontent.com/sm-monirulislam/SM-IPTV/refs/heads/main/akash_go.m3u"
# Output file name
OUTPUT_FILE = "akal.json"

def convert_m3u_to_json():
    print(f"Fetching data from {M3U_URL}...")
    
    try:
        response = requests.get(M3U_URL)
        response.raise_for_status()  # Check if the download was successful
        lines = response.text.splitlines()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the M3U file: {e}")
        return

    channels = []
    current_channel = {}

    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue

        if line.startswith("#EXTINF"):
            # 1. Extract Logo
            logo_match = re.search(r'tvg-logo="([^"]+)"', line)
            current_channel['logo'] = logo_match.group(1) if logo_match else ""

            # 2. Extract Category (group-title)
            group_match = re.search(r'group-title="([^"]+)"', line)
            current_channel['category'] = group_match.group(1) if group_match else "LIVE"

            # 3. Extract Name (String after the last comma)
            if ',' in line:
                current_channel['name'] = line.split(',')[-1].strip()
            else:
                current_channel['name'] = "Unknown Channel"

        elif line.startswith("#EXTHTTP:"):
            json_str = line.replace("#EXTHTTP:", "").strip()
            try:
                # Parse the JSON string to dictionary
                http_data = json.loads(json_str)
                if 'cookie' in http_data:
                    current_channel['cookie'] = http_data['cookie']
            except json.JSONDecodeError:
                current_channel['cookie'] = ""
                print(f"Warning: Could not parse JSON from line: {line}")

        elif not line.startswith("#"):
            # If line doesn't start with '#', it's the stream link
            current_channel['link'] = line
            
            # Default user agent as requested in your example
            current_channel['user_agent'] = "okhttp/4.11.0"
            
            # Formatting the final dictionary structure to match your requirement
            channel_data = {
                "category": current_channel.get("category", "LIVE"),
                "name": current_channel.get("name", "Unknown"),
                "link": current_channel.get("link", ""),
                "logo": current_channel.get("logo", ""),
                "cookie": current_channel.get("cookie", ""),
                "user_agent": current_channel.get("user_agent", "")
            }
            
            # Add to main list
            channels.append(channel_data)
            
            # Reset current channel dictionary for the next iteration
            current_channel = {}

    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            # Using indent=2 for nice formatting and ensure_ascii=False for Bengali/special characters
            json.dump(channels, f, indent=2, ensure_ascii=False)
        print(f"✅ Successfully converted {len(channels)} channels and saved to '{OUTPUT_FILE}'.")
    except IOError as e:
        print(f"Error saving to JSON file: {e}")

if __name__ == "__main__":
    convert_m3u_to_json()

import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

BLOGGER_API_KEY = os.environ.get("BLOGGER_API_KEY")
BLOG_ID = os.environ.get("BLOG_ID")

# Free Open-Source Indian EPG Data Source
EPG_URL = "https://raw.githubusercontent.com/iptv-org/epg/master/providers/iptv-epg.com.xml"

def fetch_and_parse_epg():
    response = requests.get(EPG_URL)
    root = ET.fromstring(response.content)
    
    # HTML Layout for TV Guide
    html = """
    <style>
        .tv-card { background: #f9f9f9; border-radius: 8px; padding: 15px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); font-family: Arial, sans-serif; }
        .channel-title { color: #e50914; border-bottom: 2px solid #e50914; padding-bottom: 5px; font-size: 20px; }
        .show-item { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px dashed #ccc; }
        .show-time { font-weight: bold; color: #333; }
        .show-name { color: #555; }
    </style>
    <h2>📺 आज का संपूर्ण टीवी गाइड (Today's TV Schedule)</h2>
    <p><i>यह पेज रोज़ स्वतः अपडेट होता है।</i></p>
    """
    
    # Extracting Top Indian Channels
    channels = {}
    for elem in root.findall('channel'):
        ch_id = elem.get('id')
        display_name = elem.find('display-name').text if elem.find('display-name') is not None else ch_id
        channels[ch_id] = display_name

    programmes = {}
    for prog in root.findall('programme'):
        ch_id = prog.get('channel')
        if ch_id in channels:
            title = prog.find('title').text if prog.find('title') is not None else "Unknown Show"
            start = prog.get('start')
            
            # Format time HH:MM
            time_str = start[8:10] + ":" + start[10:12] if len(start) >= 12 else "00:00"
            
            if ch_id not in programmes:
                programmes[ch_id] = []
            programmes[ch_id].append({'time': time_str, 'title': title})

    for ch_id, shows in programmes.items():
        if len(shows) > 0:
            html += f'<div class="tv-card"><h3 class="channel-title">{channels[ch_id]}</h3>'
            for show in shows[:10]: # Top 10 shows per channel
                html += f'<div class="show-item"><span class="show-time">⏰ {show["time"]}</span><span class="show-name">{show["title"]}</span></div>'
            html += '</div>'
            
    return html

def post_to_blogger(content):
    today = datetime.now().strftime('%d %B %Y')
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/?key={BLOGGER_API_KEY}"
    
    payload = {
        "kind": "blogger#post",
        "title": f"आज का टीवी शेड्यूल ({today}) - All Channels TV Guide",
        "content": content
    }
    
    res = requests.post(url, json=payload)
    if res.status_code == 200:
        print("Post published successfully!")
    else:
        print("Error posting:", res.text)

if __name__ == "__main__":
    html_data = fetch_and_parse_epg()
    post_to_blogger(html_data)
  

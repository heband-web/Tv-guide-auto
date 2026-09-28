import os
import requests
from datetime import datetime

BLOGGER_API_KEY = os.environ.get("BLOGGER_API_KEY")
BLOG_ID = os.environ.get("BLOG_ID")

# Reliable Indian TV Schedule API (TVMaze IN Feeds)
SCHEDULE_URL = "https://api.tvmaze.com/schedule?country=IN"

def fetch_tv_schedule():
    res = requests.get(SCHEDULE_URL)
    shows = res.json() if res.status_code == 200 else []
    
    html = """
    <style>
        .tv-card { background: #ffffff; border: 1px solid #e0e0e0; border-radius: 10px; padding: 15px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); font-family: sans-serif; }
        .channel-name { font-size: 18px; color: #d32f2f; font-weight: bold; border-bottom: 2px solid #d32f2f; padding-bottom: 5px; margin-bottom: 10px; }
        .show-row { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #f0f0f0; }
        .show-time { color: #1976d2; font-weight: bold; }
        .show-title { color: #333; font-weight: 500; }
    </style>
    <h2>📺 आज का प्रमुख टीवी शेड्यूल (Today's Live TV Guide)</h2>
    <p><i>यह सूची हर दिन अपने-आप अपडेट होती है।</i></p>
    """
    
    if not shows:
        html += "<p>आज का शेड्यूल उपलब्ध कराने में असमर्थ। कृपया बाद में प्रयास करें।</p>"
        return html

    # Channel Grouping
    channel_data = {}
    for item in shows:
        ch_name = item.get('embedded', {}).get('show', {}).get('network', {}).get('name', 'General Channel')
        show_name = item.get('name', 'Special Broadcast')
        airtime = item.get('airtime', '00:00')
        
        if ch_name not in channel_data:
            channel_data[ch_name] = []
        channel_data[ch_name].append({'time': airtime, 'title': show_name})

    for channel, show_list in channel_data.items():
        html += f'<div class="tv-card"><div class="channel-name">📺 {channel}</div>'
        for show in show_list[:8]: # Top 8 shows
            html += f'<div class="show-row"><span class="show-time">⏰ {show["time"]}</span><span class="show-title">{show["title"]}</span></div>'
        html += '</div>'
        
    return html

def post_to_blogger(content):
    today = datetime.now().strftime('%d %B %Y')
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/?key={BLOGGER_API_KEY}"
    
    payload = {
        "kind": "blogger#post",
        "title": f"आज का लाइव टीवी गाइड ({today}) - Daily TV Shows",
        "content": content
    }
    
    res = requests.post(url, json=payload)
    if res.status_code == 200:
        print("Successfully Posted to Blogger!")
    else:
        print("Error from Blogger API:", res.text)

if __name__ == "__main__":
    content = fetch_tv_schedule()
    post_to_blogger(content)
    

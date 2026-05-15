import requests
from datetime import datetime

URL = "http://120.76.248.139/udp/txiptv_chlist_zdy.php?deviceId=5b59b24e74886da42d969c7c6e09729b&ip=39.164.164.132:9901"

def fetch_channels():
    try:
        headers = {"User-Agent":"Mozilla/5.0"}
        resp = requests.get(URL, headers=headers, timeout=15)
        resp.raise_for_status()
        lines = resp.text.strip().splitlines()
        channels = []
        for line in lines:
            line = line.strip()
            if "," in line:
                name, url = line.split(",", 1)
                channels.append((name.strip(), url.strip()))
        return channels
    except Exception as e:
        print("抓取失败：", e)
        return []

def save_file(channels):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("live.txt", "w", encoding="utf-8") as f:
        f.write(f"# 更新时间：{now}\n")
        for name, url in channels:
            f.write(f"{name},{url}\n")
    with open("live.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        f.write(f"# 更新时间：{now}\n")
        for name, url in channels:
            f.write(f"#EXTINF:-1,{name}\n{url}\n")
    print(f"已生成文件，共 {len(channels)} 条")

if __name__ == "__main__":
    ch = fetch_channels()
    save_file(ch)

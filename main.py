import requests
from datetime import datetime

# 你的源地址
URL = "http://120.76.248.139/udp/txiptv_chlist_zdy.php?deviceId=5b59b24e74886da42d969c7c6e09729b&ip=39.164.164.132:9901"

def fetch_channels():
    try:
        headers = {"User-Agent":"Mozilla/5.0"}
        resp = requests.get(URL, headers=headers, timeout=15)
        resp.raise_for_status()
        # 清理 <br> 多余符号
        raw = resp.text.replace("<br>", "").strip()
        lines = raw.splitlines()
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
    # 生成干净 TXT：带分组头 iptv,#genre#
    with open("live.txt", "w", encoding="utf-8") as f:
        f.write("iptv,#genre#\n")
        for name, url in channels:
            f.write(f"{name},{url}\n")

    # 生成标准干净 M3U
    with open("live.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for name, url in channels:
            f.write(f"#EXTINF:-1,{name}\n{url}\n")

    print(f"✅ 已清理垃圾符号，生成干净列表共 {len(channels)} 条")

if __name__ == "__main__":
    ch = fetch_channels()
    save_file(ch)

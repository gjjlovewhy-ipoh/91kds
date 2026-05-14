import requests
import time
from datetime import datetime

# ========== 配置区 可自行修改 ==========
# 目标抓取地址
FETCH_URL = "http://120.76.248.139/udp/txiptv_chlist_zdy.php?deviceId=5b59b24e74886da42d969c7c6e09729b&ip=39.164.164.132:9901"
# 链接检测超时秒数
CHECK_TIMEOUT = 3
# 最大检测并发间隔
SLEEP_SEC = 0.3
# =====================================

def fetch_raw_list():
    """抓取原始网页内容"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "http://120.76.248.139/"
        }
        res = requests.get(FETCH_URL, headers=headers, timeout=15)
        res.raise_for_status()
        return res.text.strip()
    except Exception as e:
        print(f"❌ 抓取源地址失败：{e}")
        return ""

def parse_channel(raw_text):
    """解析 名称,链接 格式，去重"""
    channel_dict = {}
    lines = raw_text.splitlines()
    for line in lines:
        line = line.strip()
        if not line or "," not in line:
            continue
        parts = line.split(",", 1)
        if len(parts) != 2:
            continue
        name, url = parts[0].strip(), parts[1].strip()
        if not name or not url:
            continue
        # 按链接去重，同链接只保留第一个
        if url not in channel_dict:
            channel_dict[url] = name
    # 转回列表
    return [(v, k) for k, v in channel_dict.items()]

def is_valid_url(url):
    """检测链接是否有效"""
    try:
        res = requests.head(url, timeout=CHECK_TIMEOUT, allow_redirects=True)
        return res.status_code < 400
    except:
        try:
            requests.get(url, timeout=CHECK_TIMEOUT, stream=True)
            return True
        except:
            return False

def filter_invalid(channels):
    """过滤失效链接"""
    valid = []
    print(f"\n开始检测有效性，共 {len(channels)} 个频道...")
    for name, url in channels:
        if is_valid_url(url):
            valid.append((name, url))
            print(f"✅ 有效：{name}")
        else:
            print(f"❌ 失效：{name}")
        time.sleep(SLEEP_SEC)
    return valid

def save_txt(channels):
    with open("live.txt", "w", encoding="utf-8") as f:
        f.write("# 自动更新IPTV源  更新时间：" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        for name, url in channels:
            f.write(f"{name},{url}\n")
    print(f"\n📄 TXT 文件已生成，有效频道数：{len(channels)}")

def save_m3u(channels):
    with open("live.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        f.write(f"# 更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        for name, url in channels:
            f.write(f"#EXTINF:-1,{name}\n{url}\n")
    print(f"📺 M3U 文件已生成")

if __name__ == "__main__":
    print(f"===== 开始执行抓取任务 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} =====")
    raw = fetch_raw_list()
    if not raw:
        exit(1)
    # 解析+去重
    ch_list = parse_channel(raw)
    if not ch_list:
        print("未解析到任何频道")
        exit(0)
    # 过滤失效
    valid_list = filter_invalid(ch_list)
    # 保存文件
    save_txt(valid_list)
    save_m3u(valid_list)
    print("===== 任务执行完成 =====")

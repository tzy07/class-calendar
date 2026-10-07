import requests
import re
from icalendar import Calendar, Event
from datetime import datetime

# ========== 配置区 ==========
ORIGIN_URL = "https://all.czimt.edu.cn/cal/1426207754139848704"
OUTPUT_FILE = "fixed.ics"

# 节次 → (开始时分,结束时分)
time_map = {
    "1-2": ("08:20", "09:45"),
    "1-4": ("08:20", "11:25"),
    "3-4": ("10:00", "11:25"),
    "5": ("13:00", "13:40"),
    "5-6": ("13:00", "14:25"),
    "5-8": ("13:00", "16:05"),
    "7-8": ("14:40", "16:05"),
    "9-10": ("18:00", "19:25"),
}
# ===========================

resp = requests.get(ORIGIN_URL)
raw_text = resp.text

# 正则：删除所有 DTSTART: 后面无内容的整行（兼容 \n / \r\n）
raw_text = re.sub(r"DTSTART:\s*$", "", raw_text, flags=re.MULTILINE)

cal = Calendar.from_ical(raw_text)

for event in cal.walk("VEVENT"):
    desc = event.get("DESCRIPTION", "")
    # 匹配节次
    for seg in time_map.keys():
        if f"上课节次：{seg} 节" in desc:
            start_str, end_str = time_map[seg]
            old_start:datetime = event["DTSTART"].dt
            date_str = old_start.strftime("%Y%m%d")
            new_dtstart = datetime.strptime(f"{date_str}{start_str.replace(':','')}", "%Y%m%d%H%M")
            new_dtend = datetime.strptime(f"{date_str}{end_str.replace(':','')}", "%Y%m%d%H%M")
            event["DTSTART"].dt = new_dtstart
            event["DTEND"].dt = new_dtend
            break

# 保存新ics
with open(OUTPUT_FILE, "wb") as f:
    f.write(cal.to_ical())
print(f"✅ 已生成修正后的课表：{OUTPUT_FILE}")

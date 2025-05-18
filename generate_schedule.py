#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from datetime import date, timedelta

# ———————— 配置区域 ————————
BASE_URL       = "https://sportandrec.auckland.ac.nz"
SCHEDULE_URL   = BASE_URL + "/facility/GetSchedule"
API_URL        = BASE_URL + "/Facility/GetScheduleCustomAppointments"
FACILITY_LABEL = "Recreation Centre > Sports halls > Sports Hall 1"
# ————————————————————————

# 1️⃣ 解析 facilityId
html = requests.get(SCHEDULE_URL).text
soup = BeautifulSoup(html, "lxml")
select = soup.find("select", id="SelectedFacility")
if not select:
    raise RuntimeError("❌ 找不到下拉菜单 <select id='SelectedFacility'>")
facility_id = None
for opt in select.find_all("option"):
    if opt.text.strip() == FACILITY_LABEL:
        facility_id = opt["value"]
        break
if not facility_id:
    raise RuntimeError(f"❌ 未找到选项 “{FACILITY_LABEL}”")

# 2️⃣ 计算本周的周日和下个周日
today = date.today()
days_since_sun = (today.weekday() + 1) % 7
sunday = today - timedelta(days=days_since_sun)
next_sunday = sunday + timedelta(days=7)
start_ts = sunday.strftime("%Y-%m-%dT00:00:00")
end_ts   = next_sunday.strftime("%Y-%m-%dT00:00:00")

# 3️⃣ 拉取 JSON 活动数据
resp = requests.get(API_URL, params={
    "selectedId": facility_id,
    "start": start_ts,
    "end":   end_ts,
})
resp.raise_for_status()
events = resp.json()

# 4️⃣ 筛出 Badminton Drop-In
badminton = [
    e for e in events
    if e.get("title","").startswith("Member Drop-In: Badminton")
]

# 5️⃣ 打印 & 写入 schedule.md
week_range = f"{sunday:%b %d, %Y} – {(next_sunday - timedelta(days=1)):%b %d, %Y}"
print(f"\n🎾 Weekly Badminton Schedule ({week_range}):\n")
print(f"📍 Location: Sport Hall 1")
print(f"📅 Week: {week_range}\n")

if not badminton:
    print("⚠️ 本周没有找到 Member Drop-In: Badminton 时段。\n")
else:
    for e in badminton:
        dt_str, time_str = e["start"].split("T")
        weekday = date.fromisoformat(dt_str).strftime("%A")
        start_t = time_str[:5]
        end_t   = e["end"].split("T")[1][:5]
        print(f"- **{weekday}**: {start_t} – {end_t}")
    print()

# 🚨 新增提醒
print("📣 别忘了带上你的学生卡（Student ID）才能入场喔！\n")

# 写 markdown 文件
with open("schedule.md","w",encoding="utf-8") as md:
    md.write(f"# 🎾 Member Drop-In: Badminton Sessions\n")
    md.write(f"**Week:** {week_range}\n\n")
    if not badminton:
        md.write("- ⚠️ 本周没有找到 Member Drop-In: Badminton 时段。\n")
    else:
        for e in badminton:
            dt_str, time_str = e["start"].split("T")
            weekday = date.fromisoformat(dt_str).strftime("%A")
            start_t = time_str[:5]
            end_t   = e["end"].split("T")[1][:5]
            md.write(f"- **{weekday}**: {start_t} – {end_t}\n")
    md.write("\n📣 别忘了带上你的学生卡（Student ID）才能入场喔！\n")

print("✅ schedule.md 已生成！")

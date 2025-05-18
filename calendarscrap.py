from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import date
import time

# 设置 Chrome 浏览器参数（静音无头）
options = Options()
options.add_argument("--headless")
options.add_argument("--log-level=3")
options.add_experimental_option("excludeSwitches", ["enable-logging"])
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# 打开大学日历页面
driver.get("https://sportandrec.auckland.ac.nz/facility/GetSchedule")
try:
    wait = WebDriverWait(driver, 15)
    dropdown = wait.until(EC.presence_of_element_located((By.ID, "SelectedFacility")))
    select = Select(dropdown)
    select.select_by_visible_text("Recreation Centre > Sports halls > Sports Hall 1")
    print("✅ Selected: Sport Hall 1")
    time.sleep(5)
except Exception as e:
    print("❌ Dropdown selection failed:", e)
    driver.quit()
    exit()

# 抓取 badminton 时段
badminton_sessions = []
try:
    event_divs = driver.find_elements(By.CLASS_NAME, "fc-event")
    for div in event_divs:
        text = div.text.strip().replace('\n', ' | ')
        if "Member Drop-In: Badminton" in text:
            badminton_sessions.append(text)
except Exception as e:
    print("❌ Failed to extract events:", e)

driver.quit()

# 格式化输出为 Markdown 文件
today = date.today()
filename = "schedule.md"

print("\n📢 Weekly Badminton Schedule:\n")

with open(filename, "w", encoding="utf-8") as f:
    if not badminton_sessions:
        msg = "⚠️ No badminton sessions found for this week.\n"
        print(msg)
        f.write(msg)
    else:
        header = f"# 🎾 This Week's Member Drop-In: Badminton Sessions\n"
        subhead = f"📅 Date: {today.strftime('%B %d, %Y')}\n"
        location = "📍 Location: Sport Hall 1\n\n"
        times_header = "## 🗓️ Times:\n"
        outro = "\n📣 Remember to bring your student ID to enter.\n"

        # 打印并写入头部
        print(header + subhead + location + times_header)
        f.write(header + subhead + location + times_header)

        # 写入每个时间段
        for session in badminton_sessions:
            time_line = f"- {session.split('|')[0].strip()}\n"
            print(time_line.strip())
            f.write(time_line)

        # 打印结尾
        print(outro.strip())
        f.write(outro)

print(f"\n✅ Schedule written to `{filename}`")

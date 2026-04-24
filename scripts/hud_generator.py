import os
import json
import re
import urllib.request

# 配置你的技术栈 (Weapon Mounts)
TECH_STACK = ["LINUX", "DOCKER", "KALI", "REACT"]

def get_github_stats(username, token):
    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                contributionCount
                date
              }
            }
          }
        }
      }
    }
    """
    url = "https://api.github.com/graphql"
    # 使用 urllib 原生请求头
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "Bismarck423-HUD-Telemetry"
    }
    # 构造请求数据
    data = json.dumps({'query': query, 'variables': {'login': username}}).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.URLError as e:
        print(f"[-] HTTP Request failed: {e}")
        raise

def calculate_streak(weeks):
    # 将包含每天数据的嵌套列表展平
    days = [day for week in weeks for day in week['contributionDays']]
    
    # 倒序排列，从今天开始往回算
    days.reverse()
    
    streak = 0
    for i, day in enumerate(days):
        count = day['contributionCount']
        if count > 0:
            streak += 1
        elif count == 0:
            if i == 0:
                # 容错：如果今天是 0，继续检查昨天。因为今天还没过完，Streak 不算断。
                continue
            else:
                # 如果过去的某一天是 0，说明 Streak 断了，停止计算
                break
    return streak

def generate_svg(stats):
    try:
        calendar = stats['data']['user']['contributionsCollection']['contributionCalendar']
        total_commits = calendar['totalContributions']
        streak_days = calculate_streak(calendar['weeks'])
    except KeyError:
        total_commits = 0
        streak_days = 0
        print("[-] Could not parse contribution data.")
        
    act_level = "HIGH" if total_commits > 100 else "STABLE"
    
    with open("assets/tactical-hud.svg", "r", encoding="utf-8") as f:
        content = f.read()
    
    # 正则表达式替换动态数据，兼容首次替换和后续更新
    content = re.sub(r'SPD: MACH 2.4|ACT: [A-Z]+', f'ACT: {act_level}', content)
    content = re.sub(r'CMT: [\d,]+ BLKS', f'CMT: {total_commits} BLKS', content)
    content = re.sub(r'STRK: \d+ DAYS', f'STRK: {streak_days} DAYS', content)
    
    content = re.sub(r'PYTHON', TECH_STACK[0], content)
    content = re.sub(r'GO_LANG', TECH_STACK[1], content)
    content = re.sub(r'C_PLUS_PLUS', TECH_STACK[2], content)
    
    with open("assets/tactical-hud.svg", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    token = os.getenv("GITHUB_TOKEN")
    username = "bismarck423"
    if token:
        try:
            print("[*] Initializing telemetry with native urllib (Zero Dependencies)...")
            data = get_github_stats(username, token)
            generate_svg(data)
            print("[+] HUD Telemetry updated with real-time streak data.")
        except Exception as e:
            print(f"[-] Error: {e}")
    else:
        print("[-] GITHUB_TOKEN environment variable not found.")

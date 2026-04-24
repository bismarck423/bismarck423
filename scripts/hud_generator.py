import os
import requests
import re

# 配置你的技术栈 (Weapon Mounts)
TECH_STACK = ["LINUX", "DOCKER", "KALI", "REACT"]

def get_github_stats(username, token):
    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
          }
        }
      }
    }
    """
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post("https://api.github.com/graphql", json={'query': query, 'variables': {'login': username}}, headers=headers)
    return response.json()

def generate_svg(stats):
    try:
        total_commits = stats['data']['user']['contributionsCollection']['contributionCalendar']['totalContributions']
    except KeyError:
        total_commits = 0
        print("[-] Could not parse contribution data.")
        
    act_level = "HIGH" if total_commits > 100 else "STABLE"
    
    with open("assets/tactical-hud.svg", "r", encoding="utf-8") as f:
        content = f.read()
    
    # 实时数据替换
    content = re.sub(r'SPD: MACH 2.4', f'ACT: {act_level}', content)
    content = re.sub(r'CMT: 1,024 BLKS', f'CMT: {total_commits} BLKS', content)
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
            data = get_github_stats(username, token)
            generate_svg(data)
            print("[+] HUD Telemetry updated with real-time data.")
        except Exception as e:
            print(f"[-] Error: {e}")
    else:
        print("[-] GITHUB_TOKEN environment variable not found. Action may fail if run locally without token.")

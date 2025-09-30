# process_rules.py

import requests
import datetime
import time
import os

# --- 配置区 ---

# 1. 黑名单规则源
block_source_urls = [
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/SpywareFilter/sections/tracking_domains.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/MobileFilter/sections/adservers.txt",
    "https://raw.githubusercontent.com/damengzhu/banad/main/jiekouAD.txt",
    "https://raw.githubusercontent.com/privacy-protection-tools/anti-AD/master/anti-ad-adguard.txt",
    "https://raw.githubusercontent.com/xinggsf/Adblock-Plus-Rule/master/rule.txt",
    "https://raw.githubusercontent.com/o0HalfLife0o/list/master/ad-pc.txt",
    "https://raw.githubusercontent.com/Cats-Team/AdRules/main/adblock_plus.txt",
    "https://raw.githubusercontent.com/217heidai/adblockfilters/main/rules/adblockdnslite.txt", 
    "https://raw.githubusercontent.com/217heidai/adblockfilters/main/rules/adblockfilterslite.txt",
    "https://raw.githubusercontent.com/rentianyu/Ad-set-hosts/master/adguard",
    "https://raw.githubusercontent.com/8680/GOODBYEADS/master/data/rules/dns.txt",
    "https://raw.githubusercontent.com/lingeringsound/10007_auto/master/reward",
    "https://raw.githubusercontent.com/TG-Twilight/AWAvenue-Ads-Rule/main/AWAvenue-Ads-Rule.txt",
    "https://raw.githubusercontent.com/Menghuibanxian/AdguardHome/refs/heads/main/Black.txt"
]

# 2. 白名单规则源
white_source_urls = [
    "https://raw.githubusercontent.com/privacy-protection-tools/anti-AD/master/anti-ad-white-list.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/SpywareFilter/sections/exception_domains.txt",
    "https://raw.githubusercontent.com/8680/GOODBYEADS/master/data/rules/allow.txt",
    "https://file-git.trli.club/file-hosts/allow/Domains",
    "https://github.com/Potterli20/file/releases/download/github-hosts/allow.txt",
    "https://github.com/Potterli20/file/releases/download/github-hosts/ad-edge-hosts.txt",
    "https://raw.githubusercontent.com/Menghuibanxian/AdguardHome/refs/heads/main/White.txt"
]

# 3. 输出文件路径
block_output_file = "adguard-rules.txt"
white_output_file = "adguard-whitelist.txt"
readme_file = "README.md"

# --- 脚本区 ---

def download_file(url: str):
    """下载指定URL的内容"""
    try:
        print(f"  正在下载: {url.split('/')[-1]}")
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"  下载失败: {url}, 错误: {e}")
        return None

def process_line(line: str) -> str:
    """清洗单行规则，提取域名"""
    line = line.strip()
    if not line or line.startswith(('!', '#', '/', '[', '@')):
        return ""
    line = line.replace("||", "").replace("^", "").replace("@@", "")
    if '$' in line:
        line = line.split('$')[0]
    if line.startswith(('*.')):
        line = line[2:]
    if line.startswith('.'):
        line = line[1:]
    if line.startswith(('0.0.0.0 ', '127.0.0.1 ')):
        line = line.split(' ')[1]
    if '.' not in line or ' ' in line or '<' in line:
        return ""
    if line in ["localhost", "127.0.0.1", "0.0.0.0"]:
        return ""
    return line.strip()

def process_urls_to_dict(urls: list) -> dict:
    """下载并处理URL列表，返回一个 {规则: 来源} 的字典"""
    rules_dict = {}
    for url in urls:
        content = download_file(url)
        if content:
            lines = content.splitlines()
            count = 0
            # 使用来源域名作为标识
            source_identifier = url.split('/')[2] 
            for line in lines:
                processed_line = process_line(line)
                # "先到先得"原则去重，如果规则已存在，则不更新来源
                if processed_line and processed_line not in rules_dict:
                    rules_dict[processed_line] = source_identifier
                    count += 1
            print(f"  从 {source_identifier} 添加了 {count} 条新规则。")
        time.sleep(1)
    return rules_dict
    
def write_rules_to_file(filename: str, rules_dict: dict, title: str, description: str):
    """将规则字典写入文件，并添加来源注释"""
    print(f"\n正在将规则写入到 {filename}...")
    sorted_rules = sorted(rules_dict.keys())
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            now_cst = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
            f.write(f"! Title: {title}\n")
            f.write(f"! Description: {description}\n")
            f.write(f"! Version: {now_cst.strftime('%Y%m%d%H%M%S')}\n")
            f.write(f"! Last Updated: {now_cst.strftime('%Y-%m-%d %H:%M:%S CST')}\n")
            f.write(f"! Total Rules: {len(sorted_rules)}\n")
            f.write("!\n")
            
            for rule in sorted_rules:
                source = rules_dict[rule]
                f.write(f"{rule} # From: {source}\n")
        print(f"文件 {filename} 写入成功！")
    except IOError as e:
        print(f"写入文件失败: {filename}, 错误: {e}")

def update_readme(block_rules_dict: dict, white_rules_dict: dict):
    """生成并更新 README.md 文件"""
    print(f"\n正在更新 {readme_file}...")
    repo_name = os.environ.get("GITHUB_REPOSITORY", "your_username/your_repo")
    raw_url_base = f"https://raw.githubusercontent.com/{repo_name}/main"
    
    now_cst = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    
    # 构建黑名单来源列表的Markdown文本
    block_sources_md = "\n".join([f"- `{url}`" for url in block_source_urls])
    
    # 构建白名单来源列表的Markdown文本
    white_sources_md = "\n".join([f"- `{url}`" for url in white_source_urls])

    readme_content = f"""# 自动更新的 AdGuard Home 规则

本项目通过 GitHub Actions 自动合并、去重多个来源的 AdGuard Home 规则，并排除白名单。

**最后更新时间: {now_cst.strftime('%Y-%m-%d %H:%M:%S CST')}**

- **最终黑名单规则数**: {len(block_rules_dict)}
- **最终白名单规则数**: {len(white_rules_dict)}

---

## 订阅链接

### 拦截规则 (Blocklist)

适用于 AdGuard Home 的 DNS 封锁清单。

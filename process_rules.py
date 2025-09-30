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
    
def update_readme(block_rules_dict: dict, white_rules_dict: dict):
    """生成并更新 README.md 文件"""
    print(f"\n正在更新 {readme_file}...")
    repo_name = os.environ.get("GITHUB_REPOSITORY", "your_username/your_repo")
    raw_url_base = f"https://raw.githubusercontent.com/{repo_name}/main"
    
    now_cst = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    
    # 构建黑名单和白名单来源的Markdown文本
    block_sources_md = "\n".join([f"- `{url}`" for url in block_source_urls])
    white_sources_md = "\n".join([f"- `{url}`" for url in white_source_urls])

    # === 关键修复：将 Markdown 代码块的符号定义为变量 ===
    code_fence = "```"

    readme_content = f"""# 自动更新的 AdGuard Home 规则

本项目通过 GitHub Actions 自动合并、去重多个来源的 AdGuard Home 规则，并排除白名单。

**最后更新时间: {now_cst.strftime('%Y-%m-%d %H:%M:%S CST')}**

- **最终黑名单规则数**: {len(block_rules_dict)}
- **最终白名单规则数**: {len(white_rules_dict)}

---

## 订阅链接

### 拦截规则 (Blocklist)

适用于 AdGuard Home 的 DNS 封锁清单。

{code_fence}
{raw_url_base}/{block_output_file}
{code_fence}

### 允许规则 (Whitelist)

如果您需要，可以将其添加到 AdGuard Home 的 DNS 允许列表。

{code_fence}
{raw_url_base}/{white_output_file}
{code_fence}

---

## 规则来源

### 黑名单来源 (Blocklist Sources)

{block_sources_md}

### 白名单来源 (Whitelist Sources)

{white_sources_md}

---

---

由 [GitHub Actions](https://github.com/features/actions) 自动构建。
"""
    try:
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print(f"{readme_file} 更新成功！")
    except IOError as e:
        print(f"写入 {readme_file} 失败: {e}")

def main():
    print("--- 开始处理白名单 ---")
    white_rules_dict = process_urls_to_dict(white_source_urls)
    
    print("\n--- 开始处理黑名单 ---")
    block_rules_dict = process_urls_to_dict(block_source_urls)
    
    print("\n--- 最终处理 ---")
    initial_block_count = len(block_rules_dict)
    print(f"合并后黑名单共: {initial_block_count} 条")
    print(f"合并后白名单共: {len(white_rules_dict)} 条")
    
    # 从黑名单中移除白名单中的域名
    # 创建一个新的字典，只包含不在白名单中的键
    final_block_rules_dict = {
        rule: source 
        for rule, source in block_rules_dict.items() 
        if rule not in white_rules_dict
    }

    final_block_count = len(final_block_rules_dict)
    removed_count = initial_block_count - final_block_count
    
    print(f"从黑名单中移除了 {removed_count} 条白名单规则。")
    print(f"最终生效黑名单共: {final_block_count} 条。")
    
    # 写入文件
    write_rules_to_file(
        block_output_file, 
        final_block_rules_dict, 
        "AdGuard Custom Blocklist", 
        "自动合并、去重并排除白名单的广告拦截规则"
    )
    write_rules_to_file(
        white_output_file, 
        white_rules_dict, 
        "AdGuard Custom Whitelist", 
        "自动合并和去重的白名单规则"
    )

    # 更新 README.md
    update_readme(final_block_rules_dict, white_rules_dict)

if __name__ == "__main__":
    main()

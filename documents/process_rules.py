# process_rules.py

import requests
import datetime
import time
import os

# --- 配置区 ---

# ✨ 新增：定义脚本和项目根目录的路径
# 这让脚本无论在哪里运行都能正确找到文件
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)

# 1. 黑名单规则源 (网络)
block_source_urls = {
"秋风的规则":"https://raw.githubusercontent.com/TG-Twilight/AWAvenue-Ads-Rule/main/AWAvenue-Ads-Rule.txt",
"GitHub加速":"https://raw.githubusercontent.com/521xueweihan/GitHub520/refs/heads/main/hosts",
"广告规则":"https://raw.githubusercontent.com/huantian233/HT-AD/main/AD.txt",
"DD自用":"https://raw.githubusercontent.com/afwfv/DD-AD/main/rule/DD-AD.txt",
"消失DD":"https://raw.githubusercontent.com/afwfv/DD-AD/main/rule/dns.txt",
"大萌主":"https://raw.githubusercontent.com/damengzhu/banad/main/jiekouAD.txt",
"逆向涉猎":"https://raw.githubusercontent.com/790953214/qy-Ads-Rule/main/black.txt",
"下个ID见":"https://raw.githubusercontent.com/2Gardon/SM-Ad-FuckU-hosts/master/SMAdHosts",
"那个谁520":"https://raw.githubusercontent.com/qq5460168/666/master/rules.txt",
"1hosts":"https://raw.githubusercontent.com/badmojr/1Hosts/master/Lite/adblock.txt",
"茯苓的广告规则":"https://raw.githubusercontent.com/Kuroba-Sayuki/FuLing-AdRules/Master/FuLingRules/FuLingBlockList.txt",
"AdBlockDNSFilters1":"https://raw.githubusercontent.com/217heidai/adblockfilters/main/rules/adblockdnslite.txt",
"AdBlockDNSFilters2":"https://raw.githubusercontent.com/217heidai/adblockfilters/main/rules/adblockfilterslite.txt",
"Ad-set-hosts":"https://raw.githubusercontent.com/rentianyu/Ad-set-hosts/master/adguard",
"GOODBYEADS":"https://raw.githubusercontent.com/8680/GOODBYEADS/master/data/rules/dns.txt",
"10007_auto":"https://raw.githubusercontent.com/lingeringsound/10007_auto/master/reward",
"AWAvenue-Ads-Rule":"https://raw.githubusercontent.com/TG-Twilight/AWAvenue-Ads-Rule/main/AWAvenue-Ads-Rule.txt",
"Menghuibanxian":"https://raw.githubusercontent.com/Menghuibanxian/AdguardHome/refs/heads/main/Black.txt"
}

# 2. 白名单规则源 (网络)
white_source_urls = {
    "茯苓允许列表  ": "https://raw.githubusercontent.com/Kuroba-Sayuki/FuLing-AdRules/Master/FuLingRules/FuLingAllowList.txt",
    "666         ": "https://raw.githubusercontent.com/qq5460168/666/master/allow.txt",
    "个人自用白名单": "https://raw.githubusercontent.com/qq5460168/dangchu/main/white.txt",
    "冷漠白名单   ": "https://file-git.trli.club/file-hosts/allow/Domains",
    "BlueSkyXN   ": "https://raw.githubusercontent.com/BlueSkyXN/AdGuardHomeRules/master/ok.txt",
    "GOODBYEADS   ": "https://raw.githubusercontent.com/8680/GOODBYEADS/master/data/rules/allow.txt",
    "冷漠白名单2   ": "https://github.com/Potterli20/file/releases/download/github-hosts/allow.txt",
    "冷漠白名单3   ": "https://github.com/Potterli20/file/releases/download/github-hosts/ad-edge-hosts.txt",
    "Menghuibanxian   ": "https://raw.githubusercontent.com/Menghuibanxian/AdguardHome/refs/heads/main/White.txt"
}

# ✨ 新增：自定义本地规则文件名 (需要与脚本放在同一个文件夹内)
custom_block_file = "my-blocklist.txt"
custom_white_file = "my-whitelist.txt"

# 3. 输出文件路径 (输出到项目的根目录)
block_output_file = os.path.join(root_dir, "Black.txt")
white_output_file = os.path.join(root_dir, "White.txt")
readme_file = os.path.join(root_dir, "README.md")

# --- 脚本区 ---

def download_file(url: str, friendly_name: str):
    """下载指定URL的内容"""
    try:
        print(f"  正在下载: {friendly_name}")
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"  下载失败: {url}, 错误: {e}")
        return None

def process_line(line: str) -> str:
    """清洗单行规则，提取域名"""
    line = line.strip()
    # 忽略空行和注释
    if not line or line.startswith(('!', '#', '/', '[', '@')):
        return ""
    # 移除AdGuard修饰符和语法
    line = line.replace("||", "").replace("^", "").replace("@@", "")
    if '$' in line:
        line = line.split('$')[0]
    # 移除通配符前缀
    if line.startswith(('*.')):
        line = line[2:]
    if line.startswith('.'):
        line = line[1:]
    # 处理hosts格式
    if line.startswith(('0.0.0.0 ', '127.0.0.1 ')):
        line = line.split(' ')[1]
    # 过滤无效规则
    if '.' not in line or ' ' in line or '<' in line:
        return ""
    # 过滤本地主机
    if line in ["localhost", "127.0.0.1", "0.0.0.0"]:
        return ""
    return line.strip()

def process_urls_to_dict(urls_dict: dict) -> dict:
    """下载并处理URL字典，返回一个 {规则: 来源名称} 的字典"""
    rules_dict = {}
    for name, url in urls_dict.items():
        content = download_file(url, name)
        if content:
            lines = content.splitlines()
            count = 0
            for line in lines:
                processed_line = process_line(line)
                if processed_line and processed_line not in rules_dict:
                    rules_dict[processed_line] = name
                    count += 1
            print(f"  从 {name} 添加了 {count} 条新规则。")
        time.sleep(1)
    return rules_dict

# ✨ 新增：处理本地文件的函数
def process_local_file(filename: str, source_name: str) -> dict:
    """读取并处理本地规则文件，如果文件不存在则跳过"""
    # 确定文件的绝对路径 (与脚本在同一目录)
    full_path = os.path.join(script_dir, filename)

    if not os.path.exists(full_path):
        print(f"\n  本地文件 {filename} 不存在，跳过。")
        return {}

    print(f"\n  正在处理本地文件: {filename}")
    rules_dict = {}
    count = 0
    with open(full_path, 'r', encoding='utf-8') as f:
        for line in f:
            processed_line = process_line(line)
            if processed_line and processed_line not in rules_dict:
                rules_dict[processed_line] = source_name
                count += 1
    print(f"  从 {filename} 添加了 {count} 条自定义规则。")
    return rules_dict
    
def write_rules_to_file(filename: str, rules_dict: dict, title: str, description: str, author: str):
    """将规则字典写入文件，并添加作者和更新时间等头信息"""
    print(f"\n正在将规则写入到 {os.path.basename(filename)}...")
    sorted_rules = sorted(rules_dict.keys())
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            beijing_tz = datetime.timezone(datetime.timedelta(hours=8))
            now_beijing = datetime.datetime.now(beijing_tz)

            f.write(f"! Title: {title}\n")
            f.write(f"! Description: {description}\n")
            f.write(f"! Author: {author}\n")
            f.write(f"! Version: {now_beijing.strftime('%Y%m%d%H%M%S')}\n")
            f.write(f"! Last Updated: {now_beijing.strftime('%Y-%m-%d %H:%M:%S')} (UTC+8)\n")
            f.write(f"! Total Rules: {len(sorted_rules)}\n")
            f.write("!\n")
            
            for rule in sorted_rules:
                source = rules_dict[rule]
                f.write(f"{rule} # From: {source}\n")
        print(f"文件 {os.path.basename(filename)} 写入成功！")
    except IOError as e:
        print(f"写入文件失败: {filename}, 错误: {e}")

def update_readme(block_rules_dict: dict, white_rules_dict: dict):
    """生成并更新 README.md 文件"""
    print(f"\n正在更新 {os.path.basename(readme_file)}...")
    repo_name = os.environ.get("GITHUB_REPOSITORY", "your_username/your_repo")
    raw_url_base = f"https://raw.githubusercontent.com/{repo_name}/main"
    
    beijing_tz = datetime.timezone(datetime.timedelta(hours=8))
    now_beijing = datetime.datetime.now(beijing_tz)
    
    # 将本地自定义源也加入显示列表
    all_block_sources = list(block_source_urls.keys())
    if os.path.exists(os.path.join(script_dir, custom_block_file)):
        all_block_sources.append("Custom Blocklist (本地)")
        
    all_white_sources = list(white_source_urls.keys())
    if os.path.exists(os.path.join(script_dir, custom_white_file)):
        all_white_sources.append("Custom Whitelist (本地)")

    block_sources_md = "\n".join([f"- {name}" for name in all_block_sources])
    white_sources_md = "\n".join([f"- {name}" for name in all_white_sources])
    
    code_fence = "```"

    readme_content = f"""# 自动更新的 AdGuard Home 规则
项目作者: zhuanshenlikaini

本项目通过 GitHub Actions 自动合并、去重多个来源的 AdGuard Home 规则，并排除白名单。

**最后更新时间: {now_beijing.strftime('%Y-%m-%d %H:%M:%S')} (UTC+8)**

- **最终黑名单规则数**: {len(block_rules_dict)}
- **最终白名单规则数**: {len(white_rules_dict)}

---

## 订阅链接

### 拦截规则 (Blocklist)

{code_fence}
{raw_url_base}/{os.path.basename(block_output_file)}
{code_fence}

### 允许规则 (Whitelist)

{code_fence}
{raw_url_base}/{os.path.basename(white_output_file)}
{code_fence}

---

## 规则来源

### 黑名单来源 (Blocklist Sources)
{block_sources_md}

### 白名单来源 (Whitelist Sources)
{white_sources_md}

---

由 [GitHub Actions](https://github.com/features/actions) 自动构建。
"""
    try:
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print(f"{os.path.basename(readme_file)} 更新成功！")
    except IOError as e:
        print(f"写入 {readme_file} 失败: {e}")

def main():
    """主执行函数"""
    print("--- 开始处理白名单 ---")
    white_rules_dict = process_urls_to_dict(white_source_urls)
    # ✨ 合并本地自定义白名单
    custom_white_rules = process_local_file(custom_white_file, "Custom Whitelist")
    white_rules_dict.update(custom_white_rules)
    
    print("\n--- 开始处理黑名单 ---")
    block_rules_dict = process_urls_to_dict(block_source_urls)
    # ✨ 合并本地自定义黑名单
    custom_block_rules = process_local_file(custom_block_file, "Custom Blocklist")
    block_rules_dict.update(custom_block_rules)
    
    print("\n--- 最终处理 ---")
    initial_block_count = len(block_rules_dict)
    print(f"合并后黑名单共: {initial_block_count} 条")
    print(f"合并后白名单共: {len(white_rules_dict)} 条")
    
    final_block_rules_dict = {
        rule: source 
        for rule, source in block_rules_dict.items() 
        if rule not in white_rules_dict
    }

    final_block_count = len(final_block_rules_dict)
    removed_count = initial_block_count - final_block_count
    
    print(f"从黑名单中移除了 {removed_count} 条白名单规则。")
    print(f"最终生效黑名单共: {final_block_count} 条。")
    
    write_rules_to_file(block_output_file, final_block_rules_dict, "AdGuard Custom Blocklist", "自动合并的广告拦截规则", "zhuanshenlikaini")
    write_rules_to_file(white_output_file, white_rules_dict, "AdGuard Custom Whitelist", "自动合并的白名单规则", "zhuanshenlikaini")
    
    update_readme(final_block_rules_dict, white_rules_dict)

if __name__ == "__main__":
    main()

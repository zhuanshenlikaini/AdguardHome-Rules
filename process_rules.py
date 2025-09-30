# process_rules.py

import requests
import datetime
import time

# --- 配置区 ---

# 1. 黑名单规则源 (将被合并和去重)
block_source_urls = [
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/SpywareFilter/sections/tracking_domains.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/MobileFilter/sections/adservers.txt",
    "https://raw.githubusercontent.com/damengzhu/banad/main/jiekouAD.txt",
    "https://raw.githubusercontent.com/privacy-protection-tools/anti-AD/master/anti-ad-adguard.txt",
    "https://raw.githubusercontent.com/xinggsf/Adblock-Plus-Rule/master/rule.txt",
    "https://raw.githubusercontent.com/o0HalfLife0o/list/master/ad-pc.txt"
]

# 2. 白名单规则源 (用于从黑名单中排除误杀的域名)
white_source_urls = [
    "https://raw.githubusercontent.com/privacy-protection-tools/anti-AD/master/anti-ad-white-list.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/SpywareFilter/sections/exception_domains.txt"
]

# 3. 输出文件路径
block_output_file = "adguard-rules.txt"
white_output_file = "adguard-whitelist.txt"

# --- 脚本区 ---

def download_file(url: str):
    """下载指定URL的内容"""
    try:
        print(f"正在下载: {url}")
        response = requests.get(url, timeout=60)
        response.raise_for_status()  # 如果请求失败则抛出异常
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"下载失败: {url}, 错误: {e}")
        return None

def process_line(line: str) -> str:
    """处理单行规则，清洗并提取域名"""
    line = line.strip()
    
    # 忽略注释、空行和特殊规则
    if not line or line.startswith(('!', '#', '/', '[', '@')):
        return ""
        
    # 去除 AdGuard 的修饰符，如 ||, ^, $ 等，只保留域名/IP
    line = line.replace("||", "").replace("^", "").replace("@@", "")
    if '$' in line:
        line = line.split('$')[0]
    
    # 去除域名前的通配符和点
    if line.startswith(('*.')):
        line = line[2:]
    if line.startswith('.'):
        line = line[1:]

    # 以IP地址开头的规则处理
    if line.startswith(('0.0.0.0 ', '127.0.0.1 ')):
        line = line.split(' ')[1]

    # 简单验证是否像域名（包含点，不含非法字符）
    if '.' not in line or ' ' in line or '<' in line:
        return ""

    # 去除常见无效条目
    if line in ["localhost", "127.0.0.1", "0.0.0.0"]:
        return ""
        
    return line.strip()

def process_urls_to_set(urls: list) -> set:
    """下载并处理URL列表，返回一个包含所有有效规则的集合"""
    rules_set = set()
    for url in urls:
        content = download_file(url)
        if content:
            lines = content.splitlines()
            count = 0
            for line in lines:
                processed_line = process_line(line)
                if processed_line:
                    rules_set.add(processed_line)
                    count += 1
            print(f"从 {url} 添加了 {count} 条有效规则。")
        time.sleep(1) # 友好请求，避免过快访问
    return rules_set
    
def write_rules_to_file(filename: str, rules_list: list, title: str, description: str):
    """将规则列表写入文件，并添加文件头"""
    print(f"\n正在将规则写入到 {filename}...")
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))) # UTC+8
            f.write(f"! Title: {title}\n")
            f.write(f"! Description: {description}\n")
            f.write(f"! Version: {now.strftime('%Y%m%d%H%M%S')}\n")
            f.write(f"! Last Updated: {now.strftime('%Y-%m-%d %H:%M:%S CST')}\n")
            f.write(f"! Total Rules: {len(rules_list)}\n")
            f.write("!\n")
            
            for rule in rules_list:
                f.write(f"{rule}\n")
        print(f"文件 {filename} 写入成功！")
    except IOError as e:
        print(f"写入文件失败: {filename}, 错误: {e}")

def main():
    print("--- 开始处理白名单 ---")
    unique_whitelist_rules = process_urls_to_set(white_source_urls)
    
    print("\n--- 开始处理黑名单 ---")
    unique_blocklist_rules = process_urls_to_set(block_source_urls)
    
    print("\n--- 最终处理 ---")
    initial_block_count = len(unique_blocklist_rules)
    print(f"合并后黑名单共: {initial_block_count} 条")
    print(f"合并后白名单共: {len(unique_whitelist_rules)} 条")
    
    # 从黑名单中移除白名单中的所有项目
    unique_blocklist_rules.difference_update(unique_whitelist_rules)
    
    final_block_count = len(unique_blocklist_rules)
    removed_count = initial_block_count - final_block_count
    
    print(f"从黑名单中移除了 {removed_count} 条白名单规则。")
    print(f"最终生效黑名单共: {final_block_count} 条。")
    
    # 排序并写入文件
    sorted_blocklist = sorted(list(unique_blocklist_rules))
    sorted_whitelist = sorted(list(unique_whitelist_rules))
    
    # 写入黑名单文件
    write_rules_to_file(
        block_output_file,
        sorted_blocklist,
        "AdGuard Custom Blocklist",
        "自动合并和去重的多源广告拦截规则 (已排除白名单)"
    )
    
    # 写入白名单文件
    write_rules_to_file(
        white_output_file,
        sorted_whitelist,
        "AdGuard Custom Whitelist",
        "自动合并和去重的多源白名单规则"
    )

if __name__ == "__main__":
    main()

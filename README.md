# 自动更新的 AdGuard Home 规则

本项目通过 GitHub Actions 自动合并、去重多个来源的 AdGuard Home 规则，并排除白名单。

**最后更新时间: 2025-09-30 22:00:53 CST**

- **最终黑名单规则数**: 478697
- **最终白名单规则数**: 1524

---

## 订阅链接

### 拦截规则 (Blocklist)

适用于 AdGuard Home 的 DNS 封锁清单。

```
https://raw.githubusercontent.com/zhuanshenlikaini/AdguardHome-Rules/main/Black.txt
```

### 允许规则 (Whitelist)

如果您需要，可以将其添加到 AdGuard Home 的 DNS 允许列表。

```
https://raw.githubusercontent.com/zhuanshenlikaini/AdguardHome-Rules/main/White.txt
```

---

## 规则来源

### 黑名单来源 (Blocklist Sources)

- `https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/SpywareFilter/sections/tracking_domains.txt`
- `https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/MobileFilter/sections/adservers.txt`
- `https://raw.githubusercontent.com/damengzhu/banad/main/jiekouAD.txt`
- `https://raw.githubusercontent.com/privacy-protection-tools/anti-AD/master/anti-ad-adguard.txt`
- `https://raw.githubusercontent.com/xinggsf/Adblock-Plus-Rule/master/rule.txt`
- `https://raw.githubusercontent.com/o0HalfLife0o/list/master/ad-pc.txt`
- `https://raw.githubusercontent.com/Cats-Team/AdRules/main/adblock_plus.txt`
- `https://raw.githubusercontent.com/217heidai/adblockfilters/main/rules/adblockdnslite.txt`
- `https://raw.githubusercontent.com/217heidai/adblockfilters/main/rules/adblockfilterslite.txt`
- `https://raw.githubusercontent.com/rentianyu/Ad-set-hosts/master/adguard`
- `https://raw.githubusercontent.com/8680/GOODBYEADS/master/data/rules/dns.txt`
- `https://raw.githubusercontent.com/lingeringsound/10007_auto/master/reward`
- `https://raw.githubusercontent.com/TG-Twilight/AWAvenue-Ads-Rule/main/AWAvenue-Ads-Rule.txt`
- `https://raw.githubusercontent.com/Menghuibanxian/AdguardHome/main/Black.txt`

### 白名单来源 (Whitelist Sources)

- `https://raw.githubusercontent.com/privacy-protection-tools/anti-AD/master/anti-ad-white-list.txt`
- `https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/SpywareFilter/sections/exception_domains.txt`
- `https://raw.githubusercontent.com/8680/GOODBYEADS/master/data/rules/allow.txt`
- `https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt`
- `https://raw.githubusercontent.com/Potterli20/file/main/allow.txt`
- `https://raw.githubusercontent.com/Menghuibanxian/AdguardHome/main/White.txt`

---

由 [GitHub Actions](https://github.com/features/actions) 自动构建。

# Emby-TMDB-Scraper 🎬

这是一个轻量级的 Emby/Jellyfin 中文刮削脚本，专门解决国内网络环境下元数据获取困难的问题。

## ✨ 主要功能
- **自动刮削**：遍历指定文件夹，自动匹配电影/剧集信息。
- **中文优先**：强制优先获取 TMDB 的中文标题和简介。
- **海报下载**：自动下载高清海报 (poster) 和背景图 (fanart)。
- **NFO 生成**：生成标准的 .nfo 文件，Emby/Jellyfin 完美识别。

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install requests

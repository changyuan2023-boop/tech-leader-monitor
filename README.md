# 演讲/采访监控器

自动监控技术领袖的演讲、采访、博文等内容，推送 Slack 通知，生成中文财经资讯。

## 功能特性

✅ **RSS 监控** — 自动抓取官方博客更新  
✅ **Google News RSS** — 发现演讲/采访提及  
✅ **Slack 通知** — 实时推送新内容  
⏳ **YouTube 监控** — 获取频道视频（Step 3）  
⏳ **内容过滤** — Claude Haiku 判断相关性（Step 4）  
⏳ **文章生成** — Claude Sonnet 生成中文财经资讯（Step 6）  

## 监控目标

- **Elon Musk**（马斯克）— xai.com, Tesla, SpaceX blogs
- **Jensen Huang**（黄仁勋）— NVIDIA blog
- **Warren Buffett**（巴菲特）— Berkshire Hathaway
- **Lisa Su**（苏姿丰）— AMD newsroom
- **Sam Altman**（奥特曼）— blog.samaltman.com, OpenAI
- **Jeff Bezos**（贝索斯）— Blue Origin

## 快速开始

### 1️⃣ 部署到 GitHub

详见 [SETUP.md](./SETUP.md)

### 2️⃣ 配置环境变量

GitHub Secrets 需要配置：
- `ANTHROPIC_API_KEY` — Claude API 密钥
- `SLACK_WEBHOOK_URL` — Slack Incoming Webhook
- `YOUTUBE_API_KEY` — YouTube API（可选，Step 3）

### 3️⃣ 本地测试

```bash
pip install -r requirements.txt

# 测试 RSS 和 Google News
python3 test_monitor.py

# 测试完整工作流
python3 test_full_monitor.py

# 测试 URL 去重
python3 test_dedup.py
```

## 系统架构

```
GitHub Actions Cron (每天 08:00, 20:00 UTC)
  ↓
[监控模块] RSS feeds + Google News RSS（并发获取）
  ↓
[分类过滤] Claude Haiku 判断是否一手发言
  ↓
[去重存储] URL hash 存于 seen_urls.json
  ↓
[Slack 通知] 推送新内容到 Slack 频道
  ↓ (用户点击"生成文章"按钮)
[workflow_dispatch] 手动触发 Generate 工作流
  ↓
[内容获取] trafilatura (web) + youtube-transcript-api (YouTube)
  ↓
[文章生成] Claude Sonnet 生成 2000-4000 字中文资讯
  ↓
[输出] Slack 推送草稿供人工审核
```

## 实现进度

| Step | 任务 | 状态 |
|------|------|------|
| 1 | 项目骨架 | ✅ 完成 |
| 2 | RSS + Google News + Slack | ✅ 完成 |
| 3 | YouTube 监控 | ⏳ 待做 |
| 4 | 相关性过滤优化 | ⏳ 待做 |
| 5 | 内容获取完善 | ⏳ 待做 |
| 6 | 文章生成实现 | ⏳ 待做 |
| 7 | 端到端测试 | ⏳ 待做 |

## 项目文件

```
演讲:采访监控器/
├── .github/workflows/
│   ├── monitor.yml              # Cron job（每天 2 次）
│   └── generate.yml             # 手动触发工作流
├── monitors/
│   ├── main.py                  # ✅ 监控入口（完整实现）
│   ├── rss_monitor.py           # ✅ RSS 监控（并发）
│   ├── google_news.py           # ✅ Google News 监控
│   └── youtube_monitor.py       # ⏳ YouTube 监控（stub）
├── fetchers/
│   ├── web_fetcher.py           # 网页内容提取
│   └── youtube_fetcher.py       # YouTube 字幕提取
├── generator/
│   ├── __init__.py
│   └── main.py                  # 生成工作流入口
├── config/
│   └── people.yaml              # 6 人物 + 来源配置
├── data/
│   └── seen_urls.json           # URL 去重（git tracked）
├── classifier.py                # Claude Haiku 分类
├── generator.py                 # Claude Sonnet 生成
├── notifier.py                  # Slack 通知（完整实现）
├── dedup.py                     # URL 去重逻辑
├── test_monitor.py              # RSS/Google News 测试
├── test_full_monitor.py         # 完整工作流测试
├── test_dedup.py                # 去重逻辑测试
├── test_slack.py                # Slack 通知测试
├── requirements.txt             # Python 依赖
├── README.md                    # 本文件
├── SETUP.md                     # 详细部署指南
└── .gitignore
```

## 关键特性

### ✅ 已实现（Step 2）

- **RSS feeds 并发抓取** — 线程池加速，支持 5 并发
- **Google News RSS** — 自动构建查询 URL，处理特殊字符
- **Slack Webhook 通知** — 美化的 Block Kit 格式，包含行动按钮
- **URL 去重** — SHA256 哈希存储，90 天滚动窗口
- **错误处理** — 自动跳过失败的源，记录详细日志

### ⏳ 待实现（Step 3+）

- YouTube Data API 集成（获取频道最新视频）
- Claude Haiku 相关性过滤（区分一手发言 vs 新闻提及）
- trafilatura 网页文本提取（处理付费墙和复杂布局）
- youtube-transcript-api 字幕获取（支持自动和手工字幕）
- Claude Sonnet 文章生成（2000-4000 字，风格参考）

## 已知限制

- **Twitter/X API** — 免费 API 不可用，通过 Google News RSS 间接覆盖
- **付费墙内容** — Bloomberg/WSJ 文章无法提取，Slack 通知标注为"需手动处理"
- **巴菲特内容稀少** — 正常现象，一年仅 3-5 次更新
- **YouTube 字幕质量** — 非英语或口音重的内容可能有误

## 成本估算

| 组件 | 成本 |
|------|------|
| 监控（Haiku） | ~0.02 USD/次 |
| 文章生成（Sonnet） | ~0.10-0.15 USD/篇 |
| YouTube API | 免费（10K 配额/月） |
| GitHub Actions | 免费（2K 分钟/月） |

## 许可证

MIT

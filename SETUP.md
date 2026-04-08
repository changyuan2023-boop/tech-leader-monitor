# 设置和部署指南

## 前置需求

- GitHub 账户和仓库
- Claude API 密钥（从 https://console.anthropic.com）
- Slack 工作区和权限（创建 Incoming Webhook）
- YouTube API 密钥（可选，用于 Step 3）

---

## 步骤 1：创建 Slack Incoming Webhook

### 1.1 在 Slack 创建应用

1. 访问 https://api.slack.com/apps
2. 点击 "Create New App"
3. 选择 "From scratch"
4. 输入应用名称（如 "Monitor Bot"）
5. 选择你的 Workspace

### 1.2 启用 Incoming Webhooks

1. 左侧菜单选择 "Incoming Webhooks"
2. 打开 "Activate Incoming Webhooks" 开关
3. 点击 "Add New Webhook to Workspace"
4. 选择通知要发送的频道（如 #alerts 或 #news）
5. 点击 "Allow"
6. 复制生成的 Webhook URL，形式如：
   ```
   https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
   ```

---

## 步骤 2：配置 GitHub Secrets

### 2.1 在 GitHub 仓库中添加 Secrets

1. 在 GitHub 仓库页面，点击 Settings
2. 左侧选择 "Secrets and variables" → "Actions"
3. 点击 "New repository secret"，添加以下三个密钥：

| Secret 名 | 值 | 来源 |
|-----------|-----|------|
| `ANTHROPIC_API_KEY` | 你的 Claude API 密钥 | https://console.anthropic.com/api/keys |
| `SLACK_WEBHOOK_URL` | Slack Incoming Webhook URL | 步骤 1.2 中复制的 URL |
| `YOUTUBE_API_KEY` | YouTube Data API v3 密钥 | https://console.cloud.google.com/apis/library/youtube.googleapis.com |

### 2.2 获取 Claude API 密钥

1. 访问 https://console.anthropic.com/api/keys
2. 点击 "Create Key"
3. 复制生成的密钥（仅显示一次）

### 2.3 获取 YouTube API 密钥（可选，Step 3 需要）

1. 访问 Google Cloud Console：https://console.cloud.google.com/
2. 创建新项目或选择现有项目
3. 启用 YouTube Data API v3
4. 创建 API 密钥（API & Services → Credentials → Create Credentials → API Key）

---

## 步骤 3：初始化 Git 仓库

```bash
cd "演讲:采访监控器"

# 初始化 Git（如果还没有）
git init

# 添加所有文件
git add .

# 创建首次提交
git commit -m "初始化：监控系统骨架和 RSS/Google News 监控

- 实现 RSS feeds 监控
- 实现 Google News RSS 监控
- Slack webhook 通知
- URL 去重存储
- GitHub Actions 工作流"

# 添加远程仓库（替换为你的仓库 URL）
git remote add origin https://github.com/you/repo.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

---

## 步骤 4：验证 GitHub Actions 工作流

### 4.1 检查工作流文件

1. 在 GitHub 仓库页面，点击 "Actions" 标签
2. 应该能看到 "Monitor Content" 和 "Generate Article" 两个工作流

### 4.2 手动触发 Monitor 工作流测试

1. 在 GitHub Actions 页面，选择 "Monitor Content"
2. 点击 "Run workflow" 按钮
3. 选择 "main" 分支
4. 点击 "Run workflow"
5. 等待执行完成（应该在 2-5 分钟内完成）
6. 查看日志检查是否有错误

### 4.3 检查 Slack 通知

- 如果执行成功，应该在你的 Slack 频道看到通知
- 通知包含：人物名字、内容类型、标题、链接和"生成文章"按钮

---

## 步骤 5：本地测试（可选）

### 5.1 安装依赖

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5.2 运行测试脚本

```bash
# 测试 RSS 和 Google News 监控
python3 test_monitor.py

# 测试完整工作流（使用 mock 的 Slack）
python3 test_full_monitor.py

# 测试 URL 去重
python3 test_dedup.py
```

### 5.3 测试 Slack 通知（需要设置 SLACK_WEBHOOK_URL）

```bash
export SLACK_WEBHOOK_URL="your-webhook-url"
python3 test_slack.py
```

---

## 步骤 6：配置 Cron 时间

编辑 `.github/workflows/monitor.yml`，修改 cron 表达式：

```yaml
on:
  schedule:
    - cron: '0 8 * * *'   # 你想要的第一次运行时间（UTC）
    - cron: '0 20 * * *'  # 你想要的第二次运行时间（UTC）
```

**时间转换：**
- UTC 08:00 = GMT+8 16:00（中国标准时间下午 4 点）
- UTC 20:00 = GMT+8 04:00+1（中国标准时间次日凌晨 4 点）

---

## 故障排查

### 监控任务失败

**日志位置：** GitHub Actions → 对应工作流 → 最新运行 → 查看详细日志

**常见问题：**

1. **Secrets 未正确设置**
   - 确认 ANTHROPIC_API_KEY、SLACK_WEBHOOK_URL 已在 GitHub Settings 中配置
   - Secret 名称必须完全匹配（区分大小写）

2. **RSS 源无效或超时**
   - 某些 RSS 源可能不稳定或被 blocked
   - 系统有超时和错误处理，会跳过失败的源

3. **Slack 通知未收到**
   - 检查 Webhook URL 是否正确
   - 确认频道是否存在且 Bot 有权限发送消息
   - 查看 GitHub Actions 日志中是否有 Slack 请求错误

4. **分类结果不符合预期**
   - Claude Haiku 有时可能错分
   - 此时只需人工审核 Slack 通知即可决定是否生成文章

### 生成工作流失败

1. 确认 URL 格式正确（应该是 web article 或 YouTube 链接）
2. 检查 ANTHROPIC_API_KEY 是否有足够的配额
3. 查看工作流日志中的 trafilatura 或 youtube-transcript-api 错误

---

## 下一步（Step 3+）

### Step 3：YouTube 监控
- 实现 `monitors/youtube_monitor.py`
- 添加 YouTube Data API 集成
- 获取频道最新视频

### Step 4：相关性过滤优化
- 改进 `classifier.py` 的 prompt
- 使用更多上下文进行分类

### Step 5：内容获取完善
- 改进 `web_fetcher.py` 的网页解析
- 优化 `youtube_fetcher.py` 的字幕处理

### Step 6：文章生成
- 实现完整的 `generator.py`
- 添加参考文章风格学习

### Step 7：端到端测试
- 用真实 URL 测试完整流程
- 验证生成的文章质量

---

## 数据安全说明

1. **见 URL 存储：** `data/seen_urls.json` 存储 URL 哈希（非明文），并 committed 到仓库
2. **API 密钥：** 仅存储在 GitHub Secrets，不会被 committed
3. **内容保留：** 监控日志在 GitHub Actions 中保留 90 天

---

## 成本估算

- **Claude API：** 监控阶段使用 Haiku（便宜），生成使用 Sonnet（较贵）
  - 每次监控：~0.02 USD（Haiku 分类 5-10 次）
  - 每篇文章：~0.10-0.15 USD（Sonnet 生成）
- **YouTube API：** 每月 10,000 配额免费
- **GitHub Actions：** 免费账户每月 2,000 分钟，足够运行

---

## 许可证

MIT

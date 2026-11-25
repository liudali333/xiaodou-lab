# 小豆邀请码雷达

页面计划地址：https://liudali333.github.io/xiaodou-lab/invite-radar/ （需启用 GitHub Pages 并成功部署）。

## 功能

使用 X 官方 Recent Search API 搜索最近 24 小时公开帖子，每次最多返回 20 条，不分页。识别明确标注的小豆邀请码，排除常见求码及出售话术、去重、链接原帖。不保证实际码格式正确或有效，不自动兑换。仅展示最近一次扫描快照，不长期积累历史。代码匹配可能误识别；请核对原帖分享意愿及状态。

## 启用

1. 在 X Developer Portal（https://developer.x.com/）创建项目及应用，确认当前 API 计划包含 Recent Search、允许你的使用方式及公开展示内容，核对计费和开发者协议。取得 Bearer Token。
2. GitHub 仓库 Settings → Secrets and variables → Actions → Secrets → New repository secret，名称 X_BEARER_TOKEN，值为令牌。切勿写入仓库或 HTML。
3. 同一页面 Variables → New repository variable，名称 ENABLE_X_RADAR，值 true。未开启变量不会调用 API。
4. Settings → Pages → Build and deployment → Source 选择 GitHub Actions。
5. Actions → Invite Radar and Pages → Run workflow。查看执行状态及部署页面链接。开启后每小时第 17 分钟计划扫描；实际运行可能延迟。关闭变量即停止扫描（仍可能发布空快照）。

每次只发出一个 API 请求，计划每日约 24 次（另加手动运行），并不保证免费。API 返回 401/403/429 时检查令牌、套餐权限、额度和速率限制，不采用绕过机制。不要高频手动运行。普通 push 重新发布初始空快照，不调用 X；下一次成功定时或手动扫描恢复最新候选。页面刷新仅重新读取静态数据。

代码：scripts/invite_radar.py；页面：site/invite-radar/index.html；工作流：.github/workflows/invite-radar.yml。

当前未完成实际 X 授权及 Pages 部署验证。请遵守 X 开发者协议及小豆邀请码规则；如禁止公开转载候选码，应停用本功能。

## 无 API 的人工收录

编辑 `site/invite-radar/manual.json`，在 `items` 中添加对象，例如：

```json
{"items":[{"code":"ABC123","post_id":"1234567890123456789","created_at":"2026-11-25T00:00:00Z"}]}
```

示例是占位数据，请勿作为真实邀请码发布。`post_id` 是公开 X 原帖链接中 `/status/` 后的数字；时间使用原帖时间（UTC）。先核对原帖确有主动公开分享意愿；不要提交凭证、私人消息、求码或售卖内容。删除记录即可撤下。页面按邀请码不区分大小写去重，人工记录优先；不会验证或兑换。提交到 main 后 Pages 工作流会部署，人工数据不依赖 API，也不会被扫描覆盖。列表数量包含人工记录；扫描帖子数与最后更新时间仅代表扫描快照。

## 社区公开快照

Pages 构建时读取 [社区抓码站公开数据](https://good1uck.github.io/xiaodou-codes/codes.json)，提取邀请码、原帖 ID 和时间，与人工和可选 X API 结果合并去重。社区快照计划每 5 分钟更新一次，GitHub 调度可能延迟。页面打开期间每分钟尝试直接读取来源，失败则显示发布快照；页面刷新不触发 X API 采集。来源站更新不代表码有效，回复数也不能证明已使用。读取失败时本次部署使用仓库中的空快照，页面仍可使用其他来源。该数据由第三方维护，可能中断、延迟或撤下。项目不获取 X 登录信息、不绕过限制、不自动兑换。

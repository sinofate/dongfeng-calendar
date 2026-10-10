# 东风日历（原型）

> 目标：**跟别人约了事，转头就忘——不再发生。**
> 一句话记下约定 → 多级提醒 → 未确认置顶 → 事后跟进。手机优先、中文优先，纯前端、数据只存在本机 `localStorage`。

## 运行

```bash
cd /workspace/dongfeng-calendar
python3 -m http.server 8765        # 或：npx serve .
# 浏览器打开 http://127.0.0.1:8765/index.html  （手机访问请用电脑局域网 IP）
```
直接双击 `index.html` 也能用，但**系统通知需要 http://localhost 或 https**。
文件：`index.html`（页面）· `style.css` · `core.js`（解析/重复/冲突/提醒/ICS，可在 node 测试）· `app.js`（界面）· `tests/`（测试 + 截图）。

---

## 一、选型调研（事实 / 推断 分开写）

调研日期：2026-10-10。App Store 数据来自 Apple 公开的 iTunes Search/Lookup API（美区），评分会随时间变动。

### 事实：App Store（美区）评分

| App | 评分 | 评分数 | 价格 | 备注 |
|---|---|---|---|---|
| 苹果日历（系统自带，Apple） | 4.85 | 1,514,717 | 免费 | 预装；评分数含大量系统用户 |
| TickTick | 4.86 | 46,302 | 免费+内购 | 待办为主，带日历 |
| Things 3 | 4.82 | 27,999 | $9.99 | 纯待办/项目管理 |
| Todoist | 4.80 | 129,663 | 免费+内购 | 待办为主 |
| Structured | 4.79 | 167,323 | 免费+内购 | 竖向时间线日计划 |
| Notion Calendar | 4.74 | 7,614 | 免费 | 偏工作/Notion 用户 |
| Google Calendar | 4.53 | 132,273 | 免费 | 跨平台、协作 |
| Sunsama | 4.50 | 510 | 免费+订阅 | 样本少 |
| **Fantastical** | **4.22** | 24,506 | 免费+内购（Premium $56.99/年、$6.99/月） | **App Store“编辑精选 Editors' Choice”**；4+；当前版本 4.2.2（2026-10-01 更新） |
| Amie | 3.39 | 128 | 免费 | 样本很少 |

来源：
- 评分接口：`https://itunes.apple.com/search?term=...&entity=software&country=us`、`https://itunes.apple.com/lookup?id=718043190&country=us`
- Fantastical 商店页：https://apps.apple.com/us/app/fantastical-calendar/id718043190
- Structured：https://apps.apple.com/us/app/structured-daily-planner-todo/id1499198946 · Google Calendar：https://apps.apple.com/us/app/google-calendar-get-organized/id909319292 · Notion Calendar：https://apps.apple.com/us/app/notion-calendar/id1607562761 · Things 3：https://apps.apple.com/us/app/things-3/id904237743 · TickTick：https://apps.apple.com/us/app/ticktick-to-do-list-calendar/id626144601 · Todoist：https://apps.apple.com/us/app/todoist-to-do-list-calendar/id572688855 · Apple 日历：https://apps.apple.com/us/app/calendar/id1108185179

### 事实：评测与编辑推荐
- **App Store 编辑精选**：Fantastical 商店页显示 Editors' Choice（上表其他 App 我没有在抓取到的页面里核对该徽章，**未查到不代表没有**）。
- **Zapier（2025-11 更新）《The 6 best calendar apps in 2026》**：Fantastical 获“最佳设计”，作者称其为自己每天使用的日历；同时列了 Google Calendar（免费团队）、Outlook、Apple Calendar（Apple 用户免费首选）、Morgen（AI）。https://zapier.com/blog/best-calendar-apps/
- **The Verge**：多篇但**较旧**——2012 年 iPhone 版评测称其是“iPhone 上最容易用、最快创建事件的日历”（https://www.theverge.com/2012/11/29/3703778/fantastical-for-iphone）；2013 年 Fantastical 2 称日历+待办融合，“如果要替换 iPhone 自带日历，它是最佳选择”（https://www.theverge.com/2013/10/30/5044174/fantastical-2-iphone-calendar-app-reminders）；2020 年报道转订阅制（https://www.theverge.com/2020/1/29/21109700/fantastical-flexibits-subscription-service-premium-price-apple）。
- **PCMag**：只查到较旧的 Mac 版评测 Fantastical 2（https://www.pcmag.com/reviews/fantastical-2-for-mac），**没有查到当前 iPhone 版结论**。
- **Wirecutter**：**没有查到**可引用的当期日历 App 评测。
- 其他第三方博客（观点参考，部分是竞品/厂商自己的博客，可能有倾向）：The Sunrise Digest 称 Fantastical 是 2026 年 Apple 平台最佳日历（https://thesunrisedigest.com/focus/fantastical-review-2026/）；Temporal / Composed 的榜单则把 Apple 日历、Structured、Notion Calendar 各自列为某类最佳，说明**没有跨场景的唯一赢家**（https://temporal.day/blog/best-calendar-app-iphone-2026 、https://staycomposed.app/best/best-calendar-app-iphone-2026/）。

### 推断与结论：推荐 Fantastical 作为“克隆对象”
**这里不是“评分最高”，而是“最适合解决你的痛点”**——纯看商店评分，Fantastical（4.22）反而低于苹果日历/TickTick/Structured（多半因为订阅价格与高级功能付费墙，评论里常见；这是推断，我没有逐条统计差评）。但按你的标准“快速记录约定 + 可靠提醒 + 日历/任务融合 + 跟进”：

| 标准 | 依据（事实，来自商店页/评测） |
|---|---|
| 一句话快速记录 | 自然语言解析是其招牌：“Lunch with Casey at noon at Park Place”自动拆出标题/时间/地点/人（Zapier）；商店页列出的本地化语言为英/法/德/意/日/西/葡（**未列中文**，所以中文解析是东风日历自己补的）、重复事件表达如“third Thursday of every month”；2025-09 起接入 Apple Intelligence 解析复杂句子 |
| 可靠提醒 | 默认提醒、多个提醒、紧急提醒、出发时间提醒（travel time）、Apple Watch、小组件（商店页） |
| 日历与任务融合 | 事件与有日期的任务同列在主列表，一个开关切换“事件/任务”（商店页） |
| 跟进/人 | 受邀人自动补全、邀请回应、会面提案 Proposals（商店页）——但**没有“约后记一笔 / 按人看历史”**，这是你的差异化机会（推断） |

备选：想要“免费、零学习”选苹果日历；想要“竖向时间线规划一天”选 Structured。它们都不如 Fantastical 的“一句话记约定”贴近你的痛点。
**唯一推荐：Fantastical。** 克隆范围是功能与体验层面，**不使用其名称、图标、商标和素材**，视觉与命名均为原创（东风日历：青碧 + 朱砂、纸张底色、三道“风线”Logo）。

---

## 二、功能拆解（Fantastical → 东风日历）

| Fantastical 的做法 | 东风日历 | 状态 |
|---|---|---|
| 自然语言输入框，实时预览解析结果 | 底部常驻“一句话记约定”，输入时实时显示 日期/时间/人/地点/重复/状态/冲突 | ✅ |
| 日/周/月视图（另有季/年） | 日/周/月（日、周为 24 小时网格，重叠事件分栏；月视图点格子看当天） | ✅（无季/年） |
| 事件与任务同列 | “待办”与约定同在日程/简报；待办可勾选 | ✅ |
| 多个提醒、默认提醒 | 每条可选 提前1天/2小时/1小时/15分钟/准时；设置里可改默认（默认 1天+2小时+15分钟） | ✅ |
| 重复事件 | 每天/工作日/每周/每两周/每月/每年，可设截止；删除“仅此次/整个系列” | ✅ |
| 暗色主题 | 跟随系统 / 浅色 / 深色 | ✅ |
| 模板、日历集、天气、Zoom、Openings | 不做 | ⛔ |
| **（新增，针对“约了就忘”）** | | |
| — | **“约了谁”字段** + 人物页：按人看即将到来/历史约定与跟进备注，一键“＋约 TA” | ✅ |
| — | **今日/明日简报首页**：未确认的约定置顶，其后是待跟进、今日、明日 | ✅ |
| — | **确认状态** 待确认 / 已确认 / 已改期；改时间会自动标“已改期”；提醒弹窗里可直接“已确认” | ✅ |
| — | **冲突检测**：输入时预览、保存时、简报/视图里红框标注 | ✅ |
| — | **约后记一笔**：约定结束后弹提醒 + 简报卡片，记结论和要跟进的事，写入人物历史 | ✅ |
| — | **导出 .ics**（含 VALARM 提醒、RRULE、EXDATE、待办 VTODO）；JSON 备份/导入 | ✅ |

### 自然语言能解析什么（`core.js` 的 `parse`）
- 日期：今天/明天/后天/大后天、今晚/明早、周X/星期X/礼拜X、下周三/本周五/下下周一、10月20日、10/20、2026-10-20、3天后/两周后/下个月5号、15号；英文 tomorrow / next Wed / in 3 days / 11/3。
- 时间：下午3点、晚上8点半、15:30、十点、3点15分、中午/上午等时段词、3pm、2:30pm、noon。**无时段的 1–6 点按下午处理（启发式），7–11 点按原样。**
- 时长：1小时、半小时、一个半小时、90分钟、2h。
- 重复：每天/每周一/每个工作日/每两周/每月15号/每年；英文 every Monday。
- 人：和/跟/与/同/约/拜访 + 姓名（支持“、”多人，如“和小李、小王聚餐”）；英文 with Jack。
- 地点：在X / @X / at X。
- 待办：以“提醒我/记得/待办/任务”开头或含“提醒我”；状态词：待确认 / 已确认。
- 例：`周三下午3点和蒋宇飞喝咖啡在国贸星巴克` → 10月14日 15:00 · 👤蒋宇飞 · 📍国贸星巴克 · 待确认。

---

## 三、已验证 / 未验证

**已验证（本机 headless Chrome + node，脚本在 `tests/`）**
- `tests/parse.test.js`：20 条中英文句子解析断言全部通过（另有 8 条人工查看输出）（固定“现在”为 2026-10-10 周六 22:30）。
- `tests/e2e.js`（Playwright + 系统 Chrome，390×844 手机视口、HK 时区、虚拟时钟）**43 项全部通过**：一句话记约定字段、实时预览、冲突警告、简报置顶、确认、改期自动标记、日/周/月视图渲染、重复事件展开与“仅删除此次”、待办勾选、提醒（创建时已过期的提醒静默、提前2小时/稍后10分钟/提前15分钟触发、页内横幅、`Notification` 调用、弹窗内确认）、约后记一笔 → 人物页显示备注、“约 TA”、手动新建、深色模式、.ics 导出内容、刷新后 localStorage 保留、清空/示例数据、全程无 JS 报错。截图在 `tests/screenshots/`。
- 运行测试：`cd tests && npm i && node parse.test.js && node e2e.js`（需要本机有 `/usr/bin/google-chrome`，服务先起在 8765 端口）。

**未验证 / 已知局限**
- 真机 iPhone Safari：未测。**iOS 网页的系统通知只有“添加到主屏幕（PWA）”后才可能工作，且 Web 通知在后台/关闭页面时不可靠**——这是 Web 原型的根本局限，页面不打开就不会提醒。真正“可靠提醒”需要原生（见第四节）。
- 系统通知只用桩（stub）验证了调用，未在真实桌面/手机浏览器里看到系统弹窗；“提醒声”用 WebAudio，浏览器可能要求先有用户交互才出声，未验证。
- 导入 .ics 到苹果/谷歌日历：只检查了文件内容，未实际导入测试；时间为“浮动时间”（无时区），在不同时区设备上按本地时间显示。
- 解析器是规则/正则，不是 AI：姓名靠“动词停止词”判断，**会有误判**（例如人名里含“学/会”等字、地点里含“吃/喝/开”等字）；解析不对时点输入框旁的＋进编辑页手改。每月“31号”等不存在的日期当月跳过。
- 不含多设备同步、账号、联系人、地图、语音输入。无障碍（VoiceOver）未专门测试。
- 编辑重复事件只能改整个系列（不能改“仅此次”）；重复事件的确认状态/跟进是系列级（跟进备注按日期分开存）。

---

## 四、做成原生 iOS（SwiftUI）的路线

1. **数据层**：用 **EventKit** 读写系统日历/提醒事项（EKEvent/EKReminder），让约定自动出现在苹果日历、Apple Watch 和 Siri 里；自有字段（人物、确认状态、跟进备注、提醒档位）存 **SwiftData**，通过 `EKEvent.eventIdentifier` 关联；iCloud（CloudKit）同步。
2. **提醒（最关键）**：`UNUserNotificationCenter` 本地通知，每个约定预排 1天/2小时/15分钟三条；通知带操作按钮“已确认 / 10分钟后再提醒 / 改期”（`UNNotificationAction`）；重要约定用 **Time Sensitive** 级别；事件结束时排一条“约后记一笔”。修改/删除时重排。可选：用 `AlarmKit`（iOS 26）做“像闹钟一样会响”的强提醒（需核对当时 API）。
3. **一句话记录**：先用 `NSDataDetector`（日期/地点）+ 移植 `core.js` 的规则解析（中英）；再用 **Apple Intelligence / Foundation Models**（iOS 26，设备支持时）做结构化抽取（标题/人/时间/地点），失败回退规则解析；加语音输入 `Speech` 框架；联系人用 `Contacts` 自动补全“约了谁”。
4. **界面**：`TabView`（简报 / 日 / 周 / 月 / 人物）+ 底部常驻输入栏；日/周视图用 `ScrollView` + `LazyVStack` 自绘时间网格；月视图 `LazyVGrid`；深色模式原生支持。
5. **系统入口**：WidgetKit（今日简报 + 待确认数）、锁屏小组件、Live Activity（即将开始的约定倒计时）、App Intents/Siri 快捷指令（“记一个约定”）、Share Extension（从微信/信息里选中文字→一键记约定）。
6. **里程碑**：M1 数据层 + 一句话记录 + 三档本地通知（1–2 周）→ M2 简报/人物/冲突/确认状态（1–2 周）→ M3 约后跟进 + 小组件 + Siri（1–2 周）→ M4 CloudKit 同步 + TestFlight 内测。
7. **代码复用**：`core.js` 里的解析、重复展开、冲突、ICS 逻辑和 `tests/` 里的用例可直接作为 Swift 单元测试的规格。

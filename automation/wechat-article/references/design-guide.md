# 微信公众号设计指南

> 本文件提供视觉设计的具体规范，包括配色、组件、字体、间距等。
>
> **核心规则参见**：[rules.md](rules.md)

---

## 设计原则

### 移动端优先
- 最大宽度：677px（微信标准）
- 正文：16px，行高 1.5
- 所有文本添加 `word-break: break-word`
- **无需首行缩进**，现代网文用换行分段即可

### 视觉丰富原则（2025 升级版）

> 详细规则参见 [rules.md](rules.md#去ai味核心规则)

**设计目标**：让文章像"人"写的，但视觉效果更丰富、更吸引人

**核心原则**：
- ✅ **小标题必须加 emoji**：增强视觉吸引力，根据内容选择合适的图标
- ✅ **对比必用表格**：有对比数据时优先用表格，不要用纯文本列举
- ✅ **数据必用图表**：有百分比、趋势等数据时用图表展示（进度条、柱状图）
- ✅ **适当用 SVG 装饰**：用 SVG 图标、装饰线丰富页面，但不过度
- ✅ **颜色可以丰富**：每篇文章选择 2-3 种主色调，根据内容自然搭配
- ❌ **禁止紫蓝渐变**：避免 #6a5acd → #1e90ff 等常见 AI 风格渐变
- ❌ **避免过度装饰**：装饰为内容服务，不喧宾夺主

**变化节奏**：
- 长短段落交替
- 表格和图表穿插其中
- 适当留白，不要填得太满

---

## 配色方案（丰富多彩，自然搭配）

### 基础色（通用）

| 用途 | 颜色 | 说明 |
|------|------|------|
| 主标题 | `#222` | 最深，最醒目 |
| 副标题 | `#333` | 深灰 |
| 正文 | `#333` / `#444` | 主要内容 |
| 辅助文字 | `#555` / `#666` | 次要信息 |
| 引用文字 | `#555` | 斜体，强调 |
| 边框 | `#ddd` / `#eee` | 分隔线、引用框 |

### 丰富的强调色（按需使用）

| 颜色 | HEX | 适用场景 | 搭配建议 |
|------|-----|----------|----------|
| **红色系** | `#e74c3c` / `#ff6b6b` | 重要提示、错误、危险警告 | 搭配浅红背景 `#ffebee` |
| **蓝色系** | `#3498db` / `#5dade2` | 信息提示、链接、理性分析 | 搭配浅蓝背景 `#e3f2fd` |
| **绿色系** | `#2ecc71` / `#4caf50` | 成功、正面信息、环保主题 | 搭配浅绿背景 `#e8f5e9` |
| **橙色系** | `#f39c12` / `#ff9800` | 注意事项、警示、活力 | 搭配浅橙背景 `#fff3e0` |
| **紫色系** | `#9b59b6` / `#ba68c8` | 创意、高端、艺术主题 | 搭配浅紫背景 `#f3e5f5` |
| **青色系** | `#1abc9c` / `#26c6da` | 科技、清新、现代感 | 搭配浅青背景 `#e0f7fa` |
| **黄色系** | `#f1c40f` / `#ffd54f` | 强调、提醒、温暖 | 搭配浅黄背景 `#fffde7` |
| **粉色系** | `#e91e63` / `#ec407a` | 时尚、温馨、女性主题 | 搭配浅粉背景 `#fce4ec` |

**颜色使用原则**：
- ✅ 每篇文章选择 2-3 种主色调，保持协调
- ✅ 根据内容主题选择合适的配色
- ✅ 可以使用多种颜色丰富视觉效果
- ❌ **避免紫蓝渐变**（#6a5acd → #1e90ff 等常见 AI 风格）
- ❌ 避免纯黑纯白的强烈对比
- ❌ 避免超过 4 种主色（会显得杂乱）

### 渐变色使用（可选）

**允许的渐变方向**：
```css
/* 自然的单色渐变（推荐） */
background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);  /* 橙色系 */
background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);  /* 绿色系 */
background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);  /* 红色系 */

/* 相近色渐变（适度使用） */
background: linear-gradient(135deg, #f39c12 0%, #e74c3c 100%);  /* 橙红渐变 */
background: linear-gradient(135deg, #3498db 0%, #2ecc71 100%);  /* 蓝绿渐变 */
```

**禁止的渐变**：
- ❌ 紫蓝渐变：`#6a5acd → #1e90ff`
- ❌ 粉紫渐变：`#ff69b4 → #9b59b6`
- ❌ 跨度太大的渐变（如红到绿）

**注意**：不强制使用任何配色，根据主题灵活选择。渐变建议少用，主要用于标题背景或特殊强调区域。

---

## 组件样式（适度丰富）

> **重要**：组件总数≤8个，允许表格+图表组合，但大部分内容自然流动

### 标题

```html
<!-- 文章标题（H1，可选添加 emoji） -->
<h1 style="font-size:22px;font-weight:700;color:#222;margin:0 0 20px;line-height:1.4;word-break:break-word;">
  <span style="display:block;">文章标题</span>
</h1>

<!-- 章节标题（H2，建议添加 emoji） -->
<h2 style="font-size:18px;font-weight:700;color:#222;margin:30px 0 12px;line-height:1.4;">
  <span style="display:block;">📌 章节标题</span>
</h2>

<!-- 小节标题（H3，推荐添加 emoji） -->
<h3 style="font-size:17px;font-weight:600;color:#222;margin:24px 0 10px;line-height:1.4;">
  <span style="display:block;">💡 小节标题</span>
</h3>

<!-- 小节标题（H4，可以添加 emoji） -->
<h4 style="font-size:16px;font-weight:600;color:#333;margin:20px 0 8px;line-height:1.4;">
  <span style="display:block;">✨ 更小的标题</span>
</h4>
```

**Emoji 使用建议**：
- ✅ **每个小标题建议添加合适的 emoji**，增强视觉吸引力
- ✅ 根据内容选择相关的 emoji（如数据用 📊，技巧用 💡，重点用 ⭐）
- ✅ 保持 emoji 风格统一（全部使用彩色或全部使用单色）
- ❌ 避免使用不相关或过于花哨的 emoji
- ❌ 避免在同一个标题中使用多个 emoji

**常用 Emoji 参考**：
| 类别 | Emoji | 适用场景 |
|------|-------|----------|
| **提示** | 💡 ⚡ 🔍 🎯 | 技巧、要点、重点 |
| **数据** | 📊 📈 📉 💹 | 数据分析、趋势 |
| **成功** | ✅ ✨ 🎉 🏆 | 成功案例、好结果 |
| **警告** | ⚠️ ❌ 🚫 ⛔ | 注意事项、错误 |
| **技术** | 💻 ⚙️ 🔧 🛠️ | 技术教程、工具 |
| **时间** | ⏰ 📅 ⏳ 🕐 | 时间相关、进度 |
| **重点** | ⭐ 🌟 💎 🔥 | 核心内容、热点 |
| **步骤** | 1️⃣ 2️⃣ 3️⃣ 📝 | 流程步骤、清单 |

### 段落

```html
<!-- 重要：span 使用 display:block 来避免首行缩进 -->
<!-- 使用 div 而非 section，避免微信默认样式影响 -->
<div style="font-size:16px;color:#333;line-height:1.5;margin:3px 0;word-break:break-word;">
  <span style="display:block;">正文内容...</span>
</div>
```

### 引用框（少量使用）

```html
<!-- 简单引用框 -->
<div style="border-left:3px solid #ddd;padding-left:16px;margin:20px 0;">
  <section style="margin:0;color:#555;font-size:15px;font-style:italic;line-height:1.6;">
    <span style="display:block;">"引用内容"</span>
  </section>
</div>
```

### 强调框（极少使用）

```html
<!-- 重要信息框（一篇文章最多1-2次） -->
<div style="background:#f5f5f5;padding:12px 16px;border-radius:4px;margin:16px 0;">
  <section style="margin:0;color:#222;font-size:15px;line-height:1.6;">
    <span style="display:block;"><strong>重要</strong>：这里是最重要的信息</span>
  </section>
</div>
```

### 分隔线（偶尔使用）

```html
<div style="height:1px;background:#eee;margin:30px 0;"></div>
```

### 图片

```html
<div style="text-align:center;margin:20px 0;">
  <img src="URL" alt="描述" style="max-width:100%;height:auto;display:block;border-radius:8px;" />
</div>
```

### 表格（适合对比数据）

**重要**：有对比信息时，优先使用表格呈现，让数据更清晰。

```html
<!-- 基础表格（推荐） -->
<table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:15px;">
  <thead>
    <tr style="background:#f5f5f5;">
      <th style="padding:10px;text-align:left;border:1px solid #ddd;font-weight:600;color:#222;">列标题1</th>
      <th style="padding:10px;text-align:left;border:1px solid #ddd;font-weight:600;color:#222;">列标题2</th>
      <th style="padding:10px;text-align:left;border:1px solid #ddd;font-weight:600;color:#222;">列标题3</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="padding:10px;border:1px solid #ddd;color:#333;">数据1</td>
      <td style="padding:10px;border:1px solid #ddd;color:#333;">数据2</td>
      <td style="padding:10px;border:1px solid #ddd;color:#333;">数据3</td>
    </tr>
    <tr style="background:#fafafa;">
      <td style="padding:10px;border:1px solid #ddd;color:#333;">数据4</td>
      <td style="padding:10px;border:1px solid #ddd;color:#333;">数据5</td>
      <td style="padding:10px;border:1px solid #ddd;color:#333;">数据6</td>
    </tr>
  </tbody>
</table>

<!-- 彩色强调表格（带颜色区分） -->
<table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:15px;">
  <thead>
    <tr>
      <th style="padding:10px;text-align:left;background:#3498db;color:#fff;font-weight:600;">方案A</th>
      <th style="padding:10px;text-align:left;background:#2ecc71;color:#fff;font-weight:600;">方案B</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="padding:10px;border:1px solid #ddd;color:#333;">优点：...</td>
      <td style="padding:10px;border:1px solid #ddd;color:#333;">优点：...</td>
    </tr>
    <tr style="background:#fafafa;">
      <td style="padding:10px;border:1px solid #ddd;color:#333;">缺点：...</td>
      <td style="padding:10px;border:1px solid #ddd;color:#333;">缺点：...</td>
    </tr>
  </tbody>
</table>

<!-- 对比卡片式表格（适合 2 列对比） -->
<div style="display:flex;margin:16px 0;gap:10px;">
  <div style="flex:1;padding:16px;background:#e3f2fd;border-left:4px solid #3498db;">
    <div style="font-weight:600;color:#222;margin-bottom:8px;">✅ 推荐做法</div>
    <div style="color:#333;font-size:15px;line-height:1.6;">说明内容...</div>
  </div>
  <div style="flex:1;padding:16px;background:#ffebee;border-left:4px solid #e74c3c;">
    <div style="font-weight:600;color:#222;margin-bottom:8px;">❌ 避免做法</div>
    <div style="color:#333;font-size:15px;line-height:1.6;">说明内容...</div>
  </div>
</div>
```

**表格使用原则**：
- ✅ 有对比数据时优先使用表格
- ✅ 数据多时使用基础表格（清晰为主）
- ✅ 需要强调时使用彩色表格（2-3 种颜色）
- ✅ 简单对比用卡片式（如优缺点对比）

### 数据图表（使用 SVG）

**进度条**：
```html
<!-- 百分比进度条 -->
<div style="margin:16px 0;">
  <div style="color:#666;font-size:14px;margin-bottom:6px;">完成度：75%</div>
  <div style="width:100%;height:20px;background:#f0f0f0;border-radius:10px;overflow:hidden;">
    <div style="width:75%;height:100%;background:linear-gradient(90deg,#3498db,#2ecc71);border-radius:10px;"></div>
  </div>
</div>

<!-- 多段进度条（对比多个数据） -->
<div style="margin:16px 0;">
  <div style="margin-bottom:12px;">
    <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
      <span style="color:#333;font-size:14px;">产品 A</span>
      <span style="color:#3498db;font-size:14px;font-weight:600;">85%</span>
    </div>
    <div style="width:100%;height:12px;background:#f0f0f0;border-radius:6px;overflow:hidden;">
      <div style="width:85%;height:100%;background:#3498db;border-radius:6px;"></div>
    </div>
  </div>
  <div style="margin-bottom:12px;">
    <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
      <span style="color:#333;font-size:14px;">产品 B</span>
      <span style="color:#2ecc71;font-size:14px;font-weight:600;">70%</span>
    </div>
    <div style="width:100%;height:12px;background:#f0f0f0;border-radius:6px;overflow:hidden;">
      <div style="width:70%;height:100%;background:#2ecc71;border-radius:6px;"></div>
    </div>
  </div>
</div>
```

**对比柱状图（使用 SVG）**：
```html
<div style="margin:20px 0;">
  <svg viewBox="0 0 400 200" style="max-width:100%;height:auto;">
    <!-- 背景网格线 -->
    <line x1="50" y1="20" x2="50" y2="160" stroke="#ddd" stroke-width="1"/>
    <line x1="50" y1="160" x2="380" y2="160" stroke="#ddd" stroke-width="2"/>

    <!-- 柱状图 1 -->
    <rect x="80" y="60" width="60" height="100" fill="#3498db" rx="4"/>
    <text x="110" y="50" text-anchor="middle" font-size="14" fill="#333" font-weight="600">85%</text>
    <text x="110" y="180" text-anchor="middle" font-size="12" fill="#666">产品 A</text>

    <!-- 柱状图 2 -->
    <rect x="180" y="90" width="60" height="70" fill="#2ecc71" rx="4"/>
    <text x="210" y="80" text-anchor="middle" font-size="14" fill="#333" font-weight="600">70%</text>
    <text x="210" y="180" text-anchor="middle" font-size="12" fill="#666">产品 B</text>

    <!-- 柱状图 3 -->
    <rect x="280" y="110" width="60" height="50" fill="#f39c12" rx="4"/>
    <text x="310" y="100" text-anchor="middle" font-size="14" fill="#333" font-weight="600">50%</text>
    <text x="310" y="180" text-anchor="middle" font-size="12" fill="#666">产品 C</text>
  </svg>
</div>
```

**趋势线图（使用 SVG）**：
```html
<div style="margin:20px 0;">
  <svg viewBox="0 0 400 150" style="max-width:100%;height:auto;">
    <!-- 坐标轴 -->
    <line x1="40" y1="120" x2="380" y2="120" stroke="#ddd" stroke-width="2"/>
    <line x1="40" y1="20" x2="40" y2="120" stroke="#ddd" stroke-width="2"/>

    <!-- 趋势线 -->
    <polyline points="40,100 120,80 200,60 280,40 360,30"
              fill="none" stroke="#3498db" stroke-width="3" stroke-linecap="round"/>

    <!-- 数据点 -->
    <circle cx="40" cy="100" r="5" fill="#3498db"/>
    <circle cx="120" cy="80" r="5" fill="#3498db"/>
    <circle cx="200" cy="60" r="5" fill="#3498db"/>
    <circle cx="280" cy="40" r="5" fill="#3498db"/>
    <circle cx="360" cy="30" r="5" fill="#3498db"/>

    <!-- 标签 -->
    <text x="40" y="140" text-anchor="middle" font-size="11" fill="#666">Q1</text>
    <text x="120" y="140" text-anchor="middle" font-size="11" fill="#666">Q2</text>
    <text x="200" y="140" text-anchor="middle" font-size="11" fill="#666">Q3</text>
    <text x="280" y="140" text-anchor="middle" font-size="11" fill="#666">Q4</text>
  </svg>
</div>
```

### SVG 图标和装饰

**常用图标**：
```html
<!-- 对勾图标 -->
<svg width="20" height="20" viewBox="0 0 24 24" fill="none" style="vertical-align:middle;margin-right:6px;">
  <path d="M20 6L9 17L4 12" stroke="#2ecc71" stroke-width="2" stroke-linecap="round"/>
</svg>

<!-- 错误图标 -->
<svg width="20" height="20" viewBox="0 0 24 24" fill="none" style="vertical-align:middle;margin-right:6px;">
  <path d="M18 6L6 18M6 6L18 18" stroke="#e74c3c" stroke-width="2" stroke-linecap="round"/>
</svg>

<!-- 信息图标 -->
<svg width="20" height="20" viewBox="0 0 24 24" fill="none" style="vertical-align:middle;margin-right:6px;">
  <circle cx="12" cy="12" r="10" stroke="#3498db" stroke-width="2"/>
  <path d="M12 8V12M12 16H12.01" stroke="#3498db" stroke-width="2" stroke-linecap="round"/>
</svg>

<!-- 箭头图标 -->
<svg width="20" height="20" viewBox="0 0 24 24" fill="none" style="vertical-align:middle;margin-right:6px;">
  <path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="#f39c12" stroke-width="2" stroke-linecap="round"/>
</svg>
```

**装饰性分隔线**：
```html
<!-- 波浪分隔线 -->
<div style="margin:30px 0;text-align:center;">
  <svg width="100%" height="20" viewBox="0 0 400 20" preserveAspectRatio="none">
    <path d="M0,10 Q50,5 100,10 T200,10 T300,10 T400,10"
          stroke="#ddd" stroke-width="2" fill="none"/>
  </svg>
</div>

<!-- 点状分隔线 -->
<div style="margin:30px 0;text-align:center;">
  <svg width="100" height="10">
    <circle cx="20" cy="5" r="3" fill="#ccc"/>
    <circle cx="50" cy="5" r="3" fill="#ccc"/>
    <circle cx="80" cy="5" r="3" fill="#ccc"/>
  </svg>
</div>

<!-- 渐变色装饰条 -->
<div style="height:4px;background:linear-gradient(90deg,#3498db,#2ecc71,#f39c12);margin:25px 0;border-radius:2px;"></div>
```

**SVG 使用原则**：
- ✅ 用 SVG 创建图表（柱状图、折线图、进度条）
- ✅ 用 SVG 图标增强视觉效果
- ✅ 用 SVG 装饰丰富页面（分隔线、装饰元素）
- ✅ 保持 SVG 简洁，避免过于复杂
- ❌ 不要过度使用，保持整体简洁

---

## 字体规范

| 元素 | 字号 | 字重 | 颜色 | 行高 |
|------|------|------|------|------|
| 文章标题 (H1) | 22px | 700 | #222 | 1.4 |
| 章节标题 (H2) | 18px | 700 | #222 | 1.4 |
| 小节标题 (H3) | 17px | 600 | #222 | 1.4 |
| 正文 (P) | 16px | 400 | #333 | 1.5 |
| 辅助文字 | 15px | 400 | #555 | 1.6 |
| 注释 | 14px | 400 | #666 | 1.5 |

**字体栈**（使用系统默认，不指定）：
- 微信会使用系统字体
- 不需要在 CSS 中指定 font-family
- 系统会自动选择最合适的中文字体

---

## 间距规范

| 位置 | 间距 | 说明 |
|------|------|------|
| 容器内边距 | `24px 20px` | 主容器的上下和左右内边距 |
| 文章标题下方 | `20px` | H1 标题的 margin-bottom |
| 章节之间 | `30px` | H2 标题的 margin-top |
| 段落之间 | `3px` | 段落的 margin 上下（移动端优化） |
| 组件上下 | `20px` | 引用框、图片等组件的 margin |
| 段落首行 | **0** | 不使用 text-indent，现代风格 |

---

## 移动端兼容

### 防止溢出

```html
<!-- 容器设置 -->
<section style="max-width:677px;margin:0 auto;background:#fff;">
  <div style="padding:24px 20px;">
    <!-- 内容 -->
  </div>
</section>

<!-- 文本防止溢出（段落使用 div，不用 p 以避免首行缩进） -->
<div style="word-break:break-word;">...</div>

<!-- 表格防止溢出 -->
<table style="table-layout:fixed;width:100%;">
  <td style="word-break:break-word;">...</td>
</table>
```

### 图片适配

```html
<img
  src="URL"
  alt="描述"
  style="max-width:100%;height:auto;display:block;border-radius:8px;"
/>
```

**说明**：
- `max-width:100%` - 图片宽度不超过容器
- `height:auto` - 保持宽高比
- `display:block` - 消除图片底部空隙
- `border-radius:8px` - 可选圆角

---

## 完整HTML模板

参见：[templates/natural-template.html](../templates/natural-template.html)

**模板特点**：
- 无 Hero 区，直接进入内容
- 无蓝字渐变，使用纯色
- 无紫蓝渐变背景
- emoji 适度使用（≤15个，H2/H3 建议添加）
- 组件适度丰富（≤8个，允许表格+图表）
- 颜色丰富协调（2-3 种主色调）
- 所有样式内联
- 使用 span 包裹文本防止首行缩进

---

## 常用组件速查表

| 组件 | 使用频率 | 关键样式 | 说明 |
|------|----------|----------|------|
| **标题 (H1)** | 每篇1个 | `font-size:22px;font-weight:700;color:#222` | 可选添加 emoji |
| **章节标题 (H2)** | 按需使用 | `font-size:18px;font-weight:700;color:#222` | **建议添加 emoji** |
| **小节标题 (H3)** | 按需使用 | `font-size:17px;font-weight:600;color:#222` | **推荐添加 emoji** |
| **段落 (DIV)** | 大量使用 | `font-size:16px;color:#333;line-height:1.5` | 主要内容 |
| **表格** | 对比数据时使用 | `border-collapse:collapse;font-size:15px` | **有对比优先用表格** |
| **数据图表 (SVG)** | 展示数据时使用 | 进度条、柱状图、折线图 | **适当使用丰富页面** |
| **引用框** | 少量使用（≤3） | `border-left:3px solid #ddd;padding-left:16px` | 强调引用 |
| **SVG 图标** | 适度使用 | 对勾、错误、信息、箭头 | 增强视觉效果 |
| **图片** | 仅相关图 | `max-width:100%;height:auto;display:block` | 参考文章原图优先 |
| **分隔线** | 偶尔使用 | `height:1px;background:#eee` 或 SVG | 可用 SVG 装饰 |

**重要原则**：
- ✅ **小标题必须添加 emoji**（H2、H3 级别）
- ✅ **有对比数据必须用表格**（不要用纯文本列举）
- ✅ **有百分比/趋势数据用图表**（进度条、柱状图）
- ✅ **适当用 SVG 丰富页面**（图标、装饰、图表）
- ✅ **颜色可以丰富**（2-3 种主色调）
- ❌ **禁止紫蓝渐变**（常见 AI 风格）

---

## 内容组织建议

### 开头
- 直接进入主题
- 用数据、问题、故事吸引
- 不需要 Hero 区
- 可以用彩色引用框突出核心观点

### 中间
- 长短段落交替
- **小标题必须添加 emoji**（H2、H3 级别）
- **有对比数据必须用表格**（不要纯文本列举）
- **有百分比/趋势用图表**（进度条、柱状图、折线图）
- 偶尔用引用框强调重点
- 具体数据而非"很多"
- **适当用 SVG 图标和装饰**丰富视觉效果
- **使用 2-3 种主色调**让页面更生动

### 结尾
- 可自然结束
- 不需要固定套路
- 根据内容决定是否总结
- 可以用彩色卡片总结要点

### 视觉丰富度检查清单
- [ ] 每个小标题是否添加了合适的 emoji？
- [ ] 有对比信息是否使用了表格？
- [ ] 有数据是否使用了图表展示？
- [ ] 是否使用了 2-3 种主色调？
- [ ] 是否适当添加了 SVG 图标或装饰？
- [ ] 是否避免了紫蓝渐变？
- [ ] 整体视觉是否丰富但不杂乱？

---

## 微信编辑器问题处理

### 首行缩进问题

**问题**：即使 HTML 中没有 `text-indent`，微信编辑器仍可能自动添加首行缩进。

**预防措施**：
```html
<!-- 使用 span 包裹所有文本内容，设置 display:block 防止首行缩进 -->
<!-- 段落容器使用 div 而非 section，避免微信默认样式影响 -->
<div style="font-size:16px;color:#333;line-height:1.5;margin:3px 0;">
  <span style="display:block;">文本内容</span>
</div>
```

**清除方法**（在微信后台）：
1. 全选内容（Ctrl+A）
2. 点击"清除格式"或"移除格式"
3. 或手动设置：格式 → 段落 → 首行缩进 → 0

---

## 更多参考

- **核心规则**：[rules.md](rules.md) - 去AI味规则、微信CSS限制、检查清单
- **内容创作**：[content-guide.md](content-guide.md) - 文章结构、写作技巧、数据收集
- **HTML模板**：[templates/natural-template.html](../templates/natural-template.html) - 完整示例

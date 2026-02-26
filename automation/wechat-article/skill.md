---
name: wechat-article
description: 创建自然风格的微信公众号文章。去AI味、无套路排版，根据内容自然组织结构。自动生成封面图并上传到草稿箱。用于创建和发布微信公众号文章时使用。
---

# 微信公众号文章写作技能

## 核心工作流程

1. **初步收集** → 搜索参考文章，建立基础认知
2. **了解需求** → 确定文章类型和主题
3. **选择模板** → 根据文章类型选择对应结构
4. **创作草稿** → 基于收集的数据，按照模板组织内容
5. **自我审查** → 检查内容深度、数据支撑、逻辑完整性
6. **二次收集** → 针对发现的问题，深入挖掘补充数据
7. **完善内容** → 整合二次收集的深度信息，优化文章
8. **质量评分** → 使用评分体系评估文章质量（≥70分可发布）
9. **视觉设计** → 应用配色、图标、组件
10. **图片处理** → 优先使用参考文章的原图，没有图片时生成封面
11. **生成HTML** → 基于模板生成最终HTML
12. **自动上传** → 自动生成封面图并上传到草稿箱，失败时重试3次

**重要说明**：
- 本技能会**自动完成**所有步骤（包括封面生成和草稿上传）
- 封面图使用魔搭社区 API 生成
- 上传失败时自动重试 3 次（超时或错误）
- 生成的文章自动保存到：项目根目录 `output/article.html`
- 上传成功后在草稿箱中查看

---

## 快速参考

### 核心规则
- **去AI味规则**：[references/rules.md](references/rules.md#去ai味核心规则)
- **微信CSS限制**：[references/rules.md](references/rules.md#微信公众号css限制)
- **检查清单**：[references/rules.md](references/rules.md#微信兼容性检查清单)

### 内容创作
- **文章类型和结构**：[references/content-guide.md](references/content-guide.md#文章类型与结构参考)
- **写作技巧**：[references/content-guide.md](references/content-guide.md#内容创作技巧)
- **数据收集**：[references/content-guide.md](references/content-guide.md#数据收集和引用原则)

### 视觉设计
- **配色方案**：[references/design-guide.md](references/design-guide.md#配色方案)
- **组件样式**：[references/design-guide.md](references/design-guide.md#组件样式)
- **HTML模板**：[templates/natural-template.html](templates/natural-template.html)

---

## 多轮数据收集机制（确保深度）

### 第 1 轮：快速广度收集
**目标**：建立对主题的整体认知

- 搜索关键词的 3-5 种变体
- 阅读至少 5-10 篇相关文章
- 记录核心观点、关键数据、典型案例
- 建立信息框架和逻辑结构

**产出**：文章草稿框架

### 第 2 轮：针对性深度挖掘
**目标**：填补草稿中的信息缺口

**触发条件（满足任一即启动）：**
- 某个观点缺少数据支撑
- 某个案例描述过于笼统
- 某个逻辑链条缺少中间环节
- 某个结论缺少来源背书

**收集策略**：[详见 content-guide.md](references/content-guide.md#二次收集的搜索策略)

---

## 文章质量评分体系

### 评分标准（总分 100）

#### 一、内容质量（50 分）

| 评分项 | 分值 | 评分标准 |
|-------|-----|---------|
| **数据支撑** | 15分 | 核心观点有数据支撑（10-15分）<br>部分观点有数据（5-9分）<br>缺少数据支撑（0-4分） |
| **案例丰富** | 12分 | 有多个具体案例（9-12分）<br>有1-2个案例（5-8分）<br>无案例或笼统描述（0-4分） |
| **深度分析** | 15分 | 有深入分析和洞察（11-15分）<br>有一定分析（6-10分）<br>停留在表面（0-5分） |
| **逻辑完整** | 8分 | 逻辑严密、链条完整（6-8分）<br>逻辑基本通顺（3-5分）<br>有明显跳跃或断层（0-2分） |

#### 二、信息质量（30 分）

| 评分项 | 分值 | 评分标准 |
|-------|-----|---------|
| **时效性** | 10分 | 信息最新（6个月内）（8-10分）<br>信息较新（1年内）（5-7分）<br>信息陈旧（0-4分） |
| **权威性** | 10分 | 有权威来源背书（8-10分）<br>来源较可靠（5-7分）<br>来源不可靠（0-4分） |
| **准确性** | 10分 | 信息准确无误（8-10分）<br>基本准确但有疑点（5-7分）<br>存在明显错误（0-4分） |

#### 三、可读性（20 分）

| 评分项 | 分值 | 评分标准 |
|-------|-----|---------|
| **结构清晰** | 8分 | 结构清晰、层次分明（6-8分）<br>结构基本清晰（3-5分）<br>结构混乱（0-2分） |
| **语言流畅** | 7分 | 语言流畅、表达准确（5-7分）<br>语言基本通顺（3-4分）<br>表达困难或有语病（0-2分） |
| **排版美观** | 5分 | 排版精美、组件丰富（4-5分）<br>排版整洁（2-3分）<br>排版简陋（0-1分） |

### 评分判定

| 总分 | 等级 | 处理方式 |
|-----|------|---------|
| 85-100 | 优秀 | 直接输出 ✅ |
| 70-84 | 良好 | 小幅优化后输出 |
| 60-69 | 及格 | 需要针对性修改 |
| **60 以下** | **不及格** | **必须重写** |

### 不及格的处理（低于 60 分）

当评分低于 60 分时，必须：

1. **列出主要问题**（按重要性排序）
2. **给出修改建议**（具体可执行）
3. **询问用户意见**：
   - "评分 XX 分，存在以下问题：[问题列表]"
   - "建议：[修改方案]"
   - "是否按照建议重新生成？或者您有其他要求？"

---

## 图片处理策略

### 图片来源优先级

**配图策略**：
1. **优先使用参考文章内的原图** - 从参考文章中提取相关图片
2. **参考文章没有图片时** - 文章内不使用配图，只生成封面图

**封面图策略**：
1. **优先从参考文章中选取** - 选择参考文章中最合适的图片作为封面
2. **参考文章没有图片时** - 使用 AI 生成封面图

### AI 生成图片（无需 MCP）

本项目包含内置图片生成脚本 `scripts/generate_image.py`，直接调用魔搭社区 API。

#### 前置要求

Python 3 和 `requests` 库：
```bash
pip install requests
```

#### 配置 API Key

设置环境变量 `MODELSCOPE_API_KEY`（从魔搭社区获取）：

**Windows (PowerShell):**
```powershell
$env:MODELSCOPE_API_KEY="your-api-key-here"
```

**Windows (CMD):**
```cmd
set MODELSCOPE_API_KEY=your-api-key-here
```

**永久设置（推荐）：**
- 在系统环境变量中添加 `MODELSCOPE_API_KEY`
- 或在用户目录创建 `.env` 文件

#### 使用方式

**通过 Bash 工具调用：**
```bash
cd .claude/skills/wechat-article/scripts
python generate_image.py "a cute cat playing in sunlight" --size 1024x1024 --steps 30
```

**支持的参数：**
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--model` | 模型名称 | Qwen/Qwen-Image |
| `--size` | 图片尺寸（如 1024x1024） | 1024x1024 |
| `--steps` | 采样步数（1-100） | - |
| `--guidance` | 引导系数（1.5-20） | - |
| `--seed` | 随机种子 | - |
| `--negative` | 负向提示词 | - |

### 图片生成提示词模板

#### 封面图提示词公式

```
"[风格前缀], [主体内容], [构图描述], [光影效果], [色彩描述], --ar 16:9 --quality 2"
```

**按文章类型的封面图模板（2024 流行风格）：**

```python
# 技术教程类 - 简约现代风格
"Clean flat illustration of {topic}, minimalist style, "
"soft gradient background, pastel color palette, "
"simple geometric shapes, modern tech icons, "
"white space for breathing room, organized layout, "
"friendly and approachable, professional quality"

# 行业分析类 - 数据可视化风格
"Modern infographic illustration, {topic} data concept, "
"clean line charts and growth curves, soft color gradients, "
"minimalist data visualization, organized information layout, "
"white or light gray background, accent colors for highlights, "
"professional business style, clear visual hierarchy"

# 生活随笔类 - 温暖插画风格
"Warm hand-drawn illustration style, {topic} scene, "
"soft pastel colors, cozy and inviting atmosphere, "
"gentle watercolor texture, natural lighting effect, "
"simple composition with negative space, "
"emotional and peaceful, artistic quality"
```

**通用封面图负向提示词：**
```
"low quality, blurry, distorted, text, watermark, signature, "
"ugly, deformed, cartoon, sketch, grayscale, "
"oversaturated, bad composition, cropped, out of frame, "
"multiple subjects, messy background"
```

#### 封面图生成参数建议

```bash
python generate_image.py "{prompt}" \
  --model Tongyi-MAI/Z-Image-Turbo \
  --size 1024x576 \
  --steps 30 \
  --guidance 7.5 \
  --negative "low quality, blurry, distorted, text, watermark"
```

---

## 上传到微信公众号

本项目包含内置微信 API 脚本 `scripts/wechat.py`，直接调用微信公众号 API。

### 配置微信 API

获取微信公众号的 **AppID** 和 **AppSecret**：
- 登录微信公众平台：https://mp.weixin.qq.com
- 开发 -> 基本配置 -> 开发者ID(AppID) 和 开发者密码(AppSecret)

**设置环境变量（推荐）：**

**Windows (PowerShell):**
```powershell
$env:WECHAT_APP_ID="your-app-id"
$env:WECHAT_APP_SECRET="your-app-secret"
```

**Windows (CMD):**
```cmd
set WECHAT_APP_ID=your-app-id
set WECHAT_APP_SECRET=your-app-secret
```

### 微信 API 功能

**通过 Bash 工具调用：**

```bash
cd .claude/skills/wechat-article/scripts
```

#### 1. 上传图片
```bash
python wechat.py upload_image "image.jpg" --app-id wx123 --app-secret secret123
```

支持三种图片来源：
- 本地文件路径：`C:\images\photo.jpg`
- HTTP URL：`https://example.com/image.jpg`
- Base64 Data URL：`data:image/jpeg;base64,/9j/4AAQ...`

#### 2. 创建草稿
```bash
# 从文件读取（推荐，避免中文乱码）
python wechat.py create_draft "文章标题" "placeholder" "media_id" \
  --content-file "content.html" \
  --app-id wx123 --app-secret secret123
```

#### 3. 发布文章
```bash
python wechat.py publish "media_id" --app-id wx123 --app-secret secret123
```

### 创建草稿参数
```python
{
  "title": "文章标题（吸引人，60字内，不能含emoji和特殊字符）",
  "author": "作者名（可选）",
  "content": "HTML内容",
  "thumb_media_id": "封面图MediaID",
  "digest": "摘要（120字内，提炼核心价值）",
  "content_source_url": "原文链接（可选）",
  "need_open_comment": "1",  # 0不打开，1打开
  "only_fans_can_comment": "0"  # 0所有人，1仅粉丝
}
```

### 摘要撰写原则
- 提炼文章核心价值
- 包含数字或数据
- 制造好奇心或紧迫感
- 120字以内

**摘要公式**：`[痛点/好奇心] + [核心价值] + [数据/案例支撑]`

**详细指南**：[references/content-guide.md#摘要撰写原则](references/content-guide.md#摘要撰写原则)

---

## 完整工作流程示例（从创作到发布）

### 自动化全流程

当你说"帮我写一篇关于XX的微信文章"时，本技能会**自动完成**以下所有步骤：

1. **收集数据** - 搜索相关文章，收集真实可靠的信息和数据
2. 了解你的需求
3. 选择合适的文章模板
4. 基于收集的数据创作内容
5. **质量评分** - 使用评分体系评估文章质量（≥70分可发布）
6. 应用视觉设计
7. 处理图片（优先使用参考文章原图）
8. 生成最终的 HTML 文件
9. **生成封面图** - 使用魔搭社区 API 自动生成（参考文章无图时）
10. **上传草稿** - 自动上传到微信公众号草稿箱，失败时重试 3 次

**数据收集说明**：
- 会主动搜索和阅读多篇参考文章
- 提取真实的数据、案例、观点
- 记录参考文章来源，确保信息可靠
- 尽可能多地收集相关信息

**图片处理说明**：
- 优先从参考文章中提取相关图片
- 记录图片的原始来源 URL
- 参考文章无图时，文章内不使用配图
- 封面图优先选用参考文章中最合适的图片

**自动上传说明**：
- 封面图使用 `scripts/generate_image.py` 生成（魔搭社区 API）
- 草稿上传使用 `scripts/auto_upload.py`
- 失败时自动重试 3 次（超时 30 秒/次）
- 需要配置环境变量：`WECHAT_APP_ID`、`WECHAT_APP_SECRET`、`MODELSCOPE_API_KEY`

**生成的文件会保存到**：项目根目录 `output/`（相对于当前工作目录）

---

### 前置配置

#### 1. 微信公众号配置

获取微信公众号的 **AppID** 和 **AppSecret**：
- 登录微信公众平台：https://mp.weixin.qq.com
- 开发 -> 基本配置 -> 开发者ID(AppID) 和 开发者密码(AppSecret)

**设置环境变量（推荐）：**

**Windows (PowerShell):**
```powershell
$env:WECHAT_APP_ID="your-app-id"
$env:WECHAT_APP_SECRET="your-app-secret"
```

**永久设置（推荐）：**
- 在系统环境变量中添加 `WECHAT_APP_ID` 和 `WECHAT_APP_SECRET`

#### 2. 魔搭社区配置（图片生成）

**设置环境变量：**

**Windows (PowerShell):**
```powershell
$env:MODELSCOPE_API_KEY="your-api-key-here"
```

---

### 上传过程详解

脚本会自动完成以下步骤：

1. ✅ **生成封面图**（如需要）
   - 使用魔搭社区 API 生成
   - 尺寸：1024x576（16:9）
   - 失败时重试 3 次

2. ✅ **上传封面图**
   - 获取微信 media_id
   - 失败时重试 3 次

3. ✅ **读取 HTML 文件**
   - 从 `output/article.html` 读取

4. ✅ **创建草稿**
   - 上传到微信公众号草稿箱
   - 失败时重试 3 次

**输出示例**：

```
📝 正在上传文章: 文章标题

📸 步骤 1/4: 生成封面图...
✅ 封面图生成成功!
   文件: output/cover.jpg

📤 步骤 2/4: 上传封面图...
✅ 封面图上传成功!
   Media ID: 1234567890

📄 步骤 3/4: 读取文章内容...
✅ 已读取 15234 个字符

📝 步骤 4/4: 创建草稿...
✅ 草稿创建成功!
   Media ID: 9876543210

==================================================
🎉 上传完成!
==================================================

封面图 Media ID: 1234567890
草稿 Media ID: 9876543210

你可以在微信公众号后台的草稿箱中查看这篇文章。
```

---

**📝 上传完成后的重要提醒**：

微信公众号编辑器会强制给段落添加首行缩进。这是**平台限制**，无法通过 HTML/CSS 避免。

**原因**：
- 微信编辑器会忽略所有 `text-indent` 相关样式
- 对所有段落标签（`<p>`、`<div>`、`<section>`）自动应用默认格式
- 所有第三方工具都会遇到这个问题

**解决方案（二选一）**：

**方案 1：手动清除（如果需要无缩进）**
1. 打开草稿编辑器
2. 全选文章内容（Ctrl+A）
3. 点击"清除格式"或"移除格式"按钮
4. 或手动设置：格式 → 段落 → 首行缩进 → 设置为 0

**方案 2：接受这个样式（推荐）**
- 首行缩进是传统中文排版的标准格式
- 对阅读体验影响不大
- 可以保留这个样式

---

## 常见问题

**详细 FAQ 参见**：[references/rules.md#常见问题](references/rules.md#常见问题)

**快速链接**：
- 为什么段落有首行缩进？→ [查看解决方案](references/rules.md#q-为什么文章上传到微信后段落有首行缩进)
- 为什么样式错乱？→ [查看解决方案](references/rules.md#q-为什么网页预览正常但微信中样式错乱)
- 渐变背景不显示？→ [查看解决方案](references/rules.md#q-为什么我的渐变背景在微信中没有显示)

---

## 参考文件

- **核心规则**：[references/rules.md](references/rules.md) - 去AI味规则、微信CSS限制、检查清单
- **内容创作**：[references/content-guide.md](references/content-guide.md) - 文章结构、写作技巧、数据收集
- **视觉设计**：[references/design-guide.md](references/design-guide.md) - 配色、组件、字体、间距
- **HTML模板**：[templates/natural-template.html](templates/natural-template.html) - 完整示例

---

## 技术文档

- **工作流程总结**：[FLOW_SUMMARY.md](FLOW_SUMMARY.md)
- **环境配置指南**：[SETUP.md](SETUP.md)
- **Nginx 代理配置**：[NGINX_PROXY.md](NGINX_PROXY.md)
- **问题排查指南**：[NGINX_TROUBLESHOOTING.md](NGINX_TROUBLESHOOTING.md)

---

**总结**：
- ✅ 本技能：**全自动流程** - 收集数据 → 创作文章 → 质量评分 → 生成封面 → 上传草稿
- ✅ 你只需要：配置环境变量，然后说"帮我写一篇关于XX的文章"

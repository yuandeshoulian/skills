# wechat-article Skill 配置指南

## 概述

`wechat-article` 是一个专门用于创建和发布微信公众号文章的技能。它集成了：
- 移动端适配的 HTML 模板
- 暖色系配色方案
- 图片生成功能（魔搭社区）
- 微信公众号 API 调用

**完全独立**：无需配置任何 MCP 服务器，所有功能通过 Python 脚本直接调用 API。

---

## 环境要求

- Python 3.7+
- 依赖库：`requests`

```bash
pip install requests
```

---

## API Key 配置

本技能需要配置两个 API Key：

### 1. 魔搭社区 API Key（图片生成）

用于 AI 生成图片。

#### 获取方式

1. 访问 [魔搭社区](https://www.modelscope.cn/)
2. 登录账号
3. 进入个人中心
4. 获取 **SDK Token**（格式：`ms-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`）

#### 配置方法

**临时设置（当前会话有效）：**

```powershell
# Windows PowerShell
$env:MODELSCOPE_API_KEY="ms-your-api-key-here"

# Windows CMD
set MODELSCOPE_API_KEY=ms-your-api-key-here

# Linux/Mac
export MODELSCOPE_API_KEY="ms-your-api-key-here"
```

**永久设置（推荐）：**

1. **Windows 系统环境变量：**
   - 右键"此电脑" -> 属性 -> 高级系统设置
   - 环境变量 -> 新建用户变量
   - 变量名：`MODELSCOPE_API_KEY`
   - 变量值：你的 API Key

2. **Linux/Mac（~/.bashrc 或 ~/.zshrc）：**
   ```bash
   echo 'export MODELSCOPE_API_KEY="ms-your-api-key-here"' >> ~/.bashrc
   source ~/.bashrc
   ```

---

### 2. 微信公众号 API Key

用于上传图片、创建草稿、发布文章。

#### 获取方式

1. 登录 [微信公众平台](https://mp.weixin.qq.com)
2. 开发 -> 基本配置
3. 记录以下信息：
   - **开发者ID(AppID)**：格式如 `wx1234567890abcdef`
   - **开发者密码(AppSecret)**：格式如 `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

#### 配置方法

**临时设置（当前会话有效）：**

```powershell
# Windows PowerShell
$env:WECHAT_APP_ID="wx1234567890abcdef"
$env:WECHAT_APP_SECRET="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Windows CMD
set WECHAT_APP_ID=wx1234567890abcdef
set WECHAT_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Linux/Mac
export WECHAT_APP_ID="wx1234567890abcdef"
export WECHAT_APP_SECRET="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

**永久设置（推荐）：**

1. **Windows 系统环境变量：**
   - 右键"此电脑" -> 属性 -> 高级系统设置
   - 环境变量 -> 新建用户变量
   - 添加 `WECHAT_APP_ID` 和 `WECHAT_APP_SECRET`

2. **Linux/Mac（~/.bashrc 或 ~/.zshrc）：**
   ```bash
   echo 'export WECHAT_APP_ID="wx1234567890abcdef"' >> ~/.bashrc
   echo 'export WECHAT_APP_SECRET="your-app-secret"' >> ~/.bashrc
   source ~/.bashrc
   ```

---

### 3. 代理服务器配置（可选）

如果你的服务器 IP 不在微信白名单中，或者没有固定 IP，可以使用代理服务器。

#### 获取代理服务器

你需要有一台有固定 IP 且在微信白名单中的服务器。可以使用 Nginx 配置反向代理将请求转发到微信 API。

#### 配置代理

**重要说明**：

代理 URL 的格式为：`http://your-domain.com/wechat/` 或 `https://your-domain.com/wechat/`

- **末尾必须有 `/`**
- **不需要手动添加 `/cgi-bin`**，Nginx 配置会自动处理路径映射

**临时设置（当前会话有效）：**

```powershell
# Windows PowerShell
$env:WECHAT_PROXY_URL="http://your-proxy-domain.com/wechat/"

# Windows CMD
set WECHAT_PROXY_URL=http://your-proxy-domain.com/wechat/

# Linux/Mac
export WECHAT_PROXY_URL="http://your-proxy-domain.com/wechat/"
```

**永久设置（推荐）：**

1. **Windows 系统环境变量：**
   - 右键"此电脑" -> 属性 -> 高级系统设置
   - 环境变量 -> 新建用户变量
   - 变量名：`WECHAT_PROXY_URL`
   - 变量值：你的代理服务器 URL（如 `http://your-proxy-domain.com/wechat/`）

2. **Linux/Mac（~/.bashrc 或 ~/.zshrc）：**
   ```bash
   echo 'export WECHAT_PROXY_URL="http://your-proxy-domain.com/wechat/"' >> ~/.bashrc
   source ~/.bashrc
   ```

**使用代理：**

配置代理后，所有微信 API 请求都会自动通过代理服务器转发：

```bash
python wechat.py upload_image "image.jpg"
# 会自动使用 WECHAT_PROXY_URL 环境变量中的代理
```

或者通过命令行参数指定：

```bash
python wechat.py upload_image "image.jpg" --proxy "http://your-proxy-domain.com/wechat/"
```

**代理工作原理**：

当你访问 `http://your-proxy-domain.com/wechat/token` 时：
- Nginx 会将 `/wechat/` 替换为 `/cgi-bin/`
- 实际代理到 `https://api.weixin.qq.com/cgi-bin/token`
- 不需要在客户端代码中手动添加 `/cgi-bin`

---

## 验证配置

配置完成后，可以通过以下命令验证：

```bash
cd E:\workspace\jasion\test-weixin\.claude\skills\wechat-article\scripts
```

### 验证魔搭 API Key

```bash
python generate_image.py "a cat" --api-key $env:MODELSCOPE_API_KEY
```

成功会返回图片 URL。

### 验证微信 API Key

```bash
python wechat.py upload_image "test.jpg" --app-id $env:WECHAT_APP_ID --app-secret $env:WECHAT_APP_SECRET
```

成功会返回包含 `media_id` 的 JSON。

---

## 完整工作流程示例

### 步骤 1：生成封面图

```bash
cd E:\workspace\jasion\test-weixin\.claude\skills\wechat-article\scripts

# 生成图片
IMAGE_URL=$(python generate_image.py "a cute cat playing in sunlight" --api-key "ms-your-key")

# 上传图片到微信
MEDIA_ID=$(python wechat.py upload_image "$IMAGE_URL" --app-id "wx123" --app-secret "secret123" | jq -r '.media_id')
```

### 步骤 2：创建文章 HTML

使用 skill 提供的模板创建文章内容（详见 skill.md）

### 步骤 3：创建草稿

```bash
python wechat.py create_draft "我的文章标题" "$HTML_CONTENT" "$MEDIA_ID" \
  --app-id "wx123" \
  --app-secret "secret123" \
  --author "我的名字" \
  --digest "这是一篇关于..." \
  --open-comment 1
```

### 步骤 4：发布文章

```bash
python wechat.py publish "$MEDIA_ID" --app-id "wx123" --app-secret "secret123"
```

---

## 常见问题

### Q: 如何确认 API Key 配置成功？

**A:** 运行以下命令检查：

```powershell
# Windows PowerShell
echo $env:MODELSCOPE_API_KEY
echo $env:WECHAT_APP_ID
echo $env:WECHAT_APP_SECRET

# Linux/Mac
echo $MODELSCOPE_API_KEY
echo $WECHAT_APP_ID
echo $WECHAT_APP_SECRET
```

### Q: 为什么图片生成失败？

**A:** 检查以下几点：
1. API Key 格式是否正确（以 `ms-` 开头）
2. 网络连接是否正常
3. 账户是否有余额

### Q: 为什么微信 API 调用失败？

**A:** 常见原因：
1. AppID 或 AppSecret 不正确
2. IP 地址未加入白名单（需要在微信公众平台配置）
3. API 调用频率超限

### Q: 我没有固定 IP，如何调用微信 API？

**A:** 你可以使用代理服务器：

1. 找一台有固定 IP 且在微信白名单中的服务器
2. 按照 `NGINX_PROXY.md` 配置 Nginx 反向代理
3. 设置 `WECHAT_PROXY_URL` 环境变量或使用 `--proxy` 参数

示例：
```bash
# 使用环境变量
export WECHAT_PROXY_URL="http://your-proxy.com/wechat/"
python wechat.py upload_image "image.jpg"

# 或使用命令行参数
python wechat.py upload_image "image.jpg" --proxy "http://your-proxy.com/wechat/"
```

**注意**：
- 代理 URL 末尾必须有 `/`
- Nginx 会自动处理 `/wechat/` 到 `/cgi-bin/` 的路径映射
- 不需要在客户端代码中手动添加 `/cgi-bin`

### Q: 如何同时配置多个公众号？

**A:** 使用命令行参数指定不同的 AppID/AppSecret：

```bash
# 公众号 A
python wechat.py create_draft "标题" "内容" "media_id" --app-id "wxaaa" --app-secret "secreta"

# 公众号 B
python wechat.py create_draft "标题" "内容" "media_id" --app-id "wxbbb" --app-secret "secretb"
```

---

## 安全建议

1. **不要将 API Key 提交到 Git 仓库**
2. **定期轮换 API Key**
3. **为不同环境使用不同的 Key**
4. **限制 API Key 的权限范围**

---

## 文件结构

```
.wechat-article/
├── skill.md                    # 主文档
├── references/
│   ├── style-guide.md         # 配色方案
│   └── article-patterns.md    # 文章模板
└── scripts/
    ├── generate_image.py      # 图片生成脚本
    └── wechat.py               # 微信 API 脚本
```

---

## 更新日志

### v1.0.0 (2024-11-11)
- 初始版本
- 支持 5 种文章类型
- 内置微信兼容 HTML 模板
- 集成图片生成功能
- 集成微信 API 功能

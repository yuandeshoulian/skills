# AI 视频生成器快速开始指南

## 📦 安装

### 1. 安装 Python 依赖

```bash
cd skills/creative-writing/ai-video-generator
pip install -r requirements.txt
```

### 2. 安装 FFmpeg

**Windows**:
1. 下载：https://ffmpeg.org/download.html
2. 解压到 `C:\ffmpeg`
3. 添加到 PATH：`C:\ffmpeg\bin`

**Mac**:
```bash
brew install ffmpeg
```

**Linux**:
```bash
sudo apt install ffmpeg
```

### 3. 配置 API 密钥

#### 方式1：环境变量（推荐）

创建 `.env` 文件：
```bash
# .env（不要提交到 Git！）
VOLCANO_API_KEY=your_volcano_api_key_here
ALIYUN_API_KEY=your_aliyun_api_key_here
```

#### 方式2：配置文件

复制配置模板：
```bash
cp config.template.yaml config.yaml
```

编辑 `config.yaml`，填入 API Key。

---

## 🚀 使用方法

### 方法1：完整流程（命令行）

```bash
python scripts/generate_video.py \
  --project "王者归来" \
  --episode 1 \
  --script "../short-drama/output/王者归来/episode-001.md" \
  --storyboard "../storyboard-director/output/王者归来/storyboard-episode-001.md"
```

**参数说明**：
- `--project`: 项目名称
- `--episode`: 集数
- `--script`: 剧本路径
- `--storyboard`: 分镜脚本路径
- `--config`: 配置文件路径（可选，默认 config.yaml）

### 方法2：Python 脚本

```python
from scripts.generate_video import VideoGenerator

# 初始化
generator = VideoGenerator("config.yaml")

# 生成视频
generator.generate_full_episode(
    project_name="王者归来",
    episode_number=1,
    script_path="path/to/script.md",
    storyboard_path="path/to/storyboard.md"
)
```

### 方法3：API 调用

**✨ 支持两套完整的 API**：
- **火山引擎/字节跳动**：文生图、参考生图、图生视频
- **阿里云**：文生图、参考生图、图生视频

只需在配置文件中切换 `provider`，无需修改代码！

```python
from scripts.api_client import APIClient

# 初始化客户端（自动根据配置选择火山或阿里云）
client = APIClient("config.yaml")

# 1. 生成角色形象（文生图）
client.generate_character_image(
    prompt="male, 28 years old, business elite, ...",
    save_path="output/character.png"
)

# 2. 生成关键帧（使用参考图，保持角色一致性）
client.generate_keyframe_with_reference(
    prompt="same character, in hotel lobby, ...",
    reference_image_path="output/character.png",  # 参考图
    save_path="output/keyframe.png"
)

# 3. 生成视频（图生视频）
client.generate_video(
    keyframe_path="output/keyframe.png",
    prompt="camera slowly pushes in",
    duration=5,
    save_path="output/video.mp4"
)
```

**切换服务商**：

```yaml
# 使用火山引擎
text_to_image:
  provider: "volcano"

# 或使用阿里云
text_to_image:
  provider: "aliyun"
```

---

## ⚙️ 配置模型

### 使用不同的模型

编辑 `config.yaml`:

```yaml
image_to_video:
  # 切换模型（只需改一行！）
  model: "seaweed-2.0"  # 或 "seaweed-1.0", "runway-gen3", 等

  capabilities:
    max_duration: 12  # 根据模型调整时长
```

### 添加新模型

在 `config.yaml` 的 `alternative_models` 中添加：

```yaml
alternative_models:
  - name: "seaweed-3.0"  # 新模型
    provider: "volcano"
    max_duration: 30  # ✨ 支持 30 秒！
    has_audio: true
    has_voice: true
    cost_per_second: 2.5
    quality: 5
```

然后切换：
```yaml
model: "seaweed-3.0"
```

---

## 💰 成本优化

### 启用缓存（推荐）

```yaml
cost:
  optimization:
    enable_caching: true  # ✅ 复用角色和场景图片
```

### 使用低成本模型

```yaml
image_to_video:
  model: "seaweed-1.0"  # 1元/秒（质量略低）

cost:
  optimization:
    use_low_cost_model: true
```

### 减少镜头数量

在分镜脚本中减少镜头数量（例如从 45 个减到 30 个）。

---

## 📊 生成流程

```
第1步：角色设计
  └─> 生成 15 张角色图（5角色 × 3角度）
  └─> 耗时：约 15 分钟

第2步：场景生成
  └─> 生成 3 张场景图
  └─> 耗时：约 5 分钟

第3步：关键帧绘制
  └─> 生成 45 张关键帧（使用角色参考图）
  └─> 耗时：约 10 分钟

第4步：视频生成 ⚡
  └─> 生成 45 个视频片段（每个 2-3 秒）
  └─> 耗时：约 60-90 分钟

第5步：视频合成
  └─> 使用 FFmpeg 合并所有片段
  └─> 耗时：约 10 分钟

总耗时：约 100-130 分钟
总成本：约 200 元/集（可优化到 70-150 元）
```

---

## 📁 输出结构

```
output/ai-video/王者归来/
├── characters/           # 角色形象（可复用）
│   ├── 林宇-正面.png
│   ├── 林宇-侧面.png
│   └── ...
├── scenes/              # 场景图片（可复用）
│   ├── 豪华酒店大堂-晚上.png
│   └── ...
├── keyframes/           # 关键帧
│   └── episode-001/
│       ├── S1-1.png
│       └── ...
├── videos/              # 视频片段
│   └── episode-001/
│       ├── S1-1.mp4
│       └── ...
└── final/               # 最终视频 ⭐
    └── episode-001.mp4
```

---

## ❓ 常见问题

### Q1: API 调用失败？

**检查**：
- API Key 是否正确？
- 网络是否通畅？
- API 额度是否充足？

**调试**：
```yaml
debug:
  enabled: true
  log_level: "DEBUG"
```

### Q2: FFmpeg 找不到？

**检查安装**：
```bash
ffmpeg -version
```

**如果没安装**：
- Windows: 下载并添加到 PATH
- Mac: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

### Q3: 成本太高？

**优化方案**：
1. 启用缓存（角色和场景复用）
2. 使用低成本模型（seaweed-1.0）
3. 减少镜头数量
4. 固定镜头不生成视频，用静态图代替

### Q4: 生成太慢？

**加速方案**：
```yaml
concurrency:
  max_parallel_images: 10  # 增加并发数
  max_parallel_videos: 3
```

---

## 🔗 相关文档

- [模型配置指南](references/model-config.md)
- [角色一致性技术](references/character-consistency.md)
- [提示词模板](prompts/character-prompts.md)

---

## 📞 获取帮助

遇到问题？
1. 查看日志：`logs/ai-video-generator.log`
2. 开启调试模式（config.yaml 中设置 `debug.enabled: true`）
3. 检查 API 响应

---

**开始创作你的 AI 短剧吧！🎬**

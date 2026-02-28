# 模型配置文件

本文档定义 AI 视频生成器的可配置模型参数。

---

## 配置文件格式

### config.yaml

```yaml
# AI 视频生成器配置文件
# 版本: 1.0.0

# ===== 模型配置 =====

# 文生图模型
text_to_image:
  provider: "volcano"  # volcano | aliyun | openai
  model: "doubaao-ai"  # 具体模型名称
  api_key: "${VOLCANO_API_KEY}"  # 从环境变量读取
  api_endpoint: "https://ark.cn-beijing.volces.com/api/v3"

  # 默认参数
  default_params:
    width: 768
    height: 1365  # 9:16 竖屏比例
    num_inference_steps: 50
    guidance_scale: 7.5
    negative_prompt: "worst quality, low quality, blurry, ..."

# 图生图模型（角色一致性）
image_to_image:
  provider: "volcano"
  model: "controlnet-openpose"
  api_key: "${VOLCANO_API_KEY}"

  # IP-Adapter 配置
  ip_adapter:
    enabled: true
    model: "ip-adapter-plus"
    default_weight: 0.75  # 参考图权重 0-1

  # LoRA 配置
  lora:
    enabled: true
    default_weight: 0.8
    models_dir: "./lora_models"  # LoRA 模型存放目录

# 图生视频模型
image_to_video:
  provider: "volcano"  # volcano | aliyun | runway
  model: "seaweed-2.0"  # 默认模型
  api_key: "${VOLCANO_API_KEY}"

  # 模型能力配置
  capabilities:
    max_duration: 12  # 最大时长（秒）可配置
    has_audio: true   # 是否支持音频生成
    has_voice: true   # 是否支持配音生成
    vertical_support: true  # 是否支持竖屏

  # 可选模型列表（按推荐度排序）
  alternative_models:
    - name: "seaweed-2.0"
      provider: "volcano"
      max_duration: 12
      has_audio: true
      has_voice: true
      cost_per_second: 2.0
      quality: 5  # 1-5 星

    - name: "seaweed-1.0"
      provider: "volcano"
      max_duration: 8
      has_audio: false
      has_voice: false
      cost_per_second: 1.0
      quality: 4

    - name: "runway-gen3"
      provider: "runway"
      max_duration: 16
      has_audio: false
      has_voice: false
      cost_per_second: 3.0
      quality: 5

    - name: "aliyun-video-gen"
      provider: "aliyun"
      max_duration: 10
      has_audio: true
      has_voice: false
      cost_per_second: 1.5
      quality: 4

  # 默认参数
  default_params:
    fps: 24
    motion_strength: 0.7  # 运动强度 0-1
    aspect_ratio: "9:16"  # 竖屏
    seed: -1  # -1 表示随机

# 音效和配音
audio:
  # TTS（配音）
  tts:
    provider: "volcano"
    model: "volcano-tts-v1"
    api_key: "${VOLCANO_API_KEY}"

    # 角色音色配置
    voice_mapping:
      男主角: "male-young-confident"
      女主角: "female-young-sweet"
      反派: "male-mature-cold"
      配角: "neutral"

  # 音效生成
  sound_effects:
    provider: "elevenlabs"  # elevenlabs | freesound
    api_key: "${ELEVENLABS_API_KEY}"
    library_path: "./sound_effects"  # 本地音效库

# ===== 生成策略配置 =====

generation:
  # 视频分段策略
  segmentation:
    strategy: "by_shot"  # by_shot | by_scene | fixed_duration
    max_segment_duration: 12  # 最大分段时长（秒）
    overlap_frames: 2  # 分段重叠帧数（用于平滑过渡）

  # 并发控制
  concurrency:
    max_parallel_images: 5  # 最多同时生成 5 张图
    max_parallel_videos: 2  # 最多同时生成 2 个视频

  # 重试策略
  retry:
    max_attempts: 3
    retry_delay: 5  # 秒

  # 质量控制
  quality_control:
    enable_validation: true
    min_quality_score: 75  # 最低质量分数
    auto_regenerate: true  # 低于分数自动重新生成

# ===== 成本控制配置 =====

cost:
  # 预算限制
  budget:
    max_per_episode: 300  # 单集最大预算（元）
    alert_threshold: 0.8  # 达到 80% 预算时警告

  # 成本优化
  optimization:
    enable_caching: true  # 启用缓存（角色和场景图片复用）
    compress_keyframes: false  # 不压缩关键帧（保证质量）
    use_low_cost_model: false  # 不使用低成本模型

  # 成本估算
  pricing:
    text_to_image: 0.3  # 元/张
    image_to_image: 0.5  # 元/张
    image_to_video: 2.0  # 元/秒
    tts: 0.3  # 元/分钟
    sound_effects: 0.1  # 元/次

# ===== 输出配置 =====

output:
  # 目录结构
  directories:
    base: "./output/ai-video"
    characters: "{base}/{project}/characters"
    scenes: "{base}/{project}/scenes"
    keyframes: "{base}/{project}/keyframes/{episode}"
    videos: "{base}/{project}/videos/{episode}"
    final: "{base}/{project}/final"

  # 文件命名
  naming:
    character: "{name}-{angle}.png"
    scene: "{location}-{time}.png"
    keyframe: "S{scene}-{shot}_{description}.png"
    video_segment: "S{scene}-{shot}.mp4"
    final_video: "episode-{number:03d}.mp4"

  # 视频格式
  video:
    codec: "h264"
    bitrate: "8M"
    audio_codec: "aac"
    audio_bitrate: "192k"

# ===== 提示词配置 =====

prompts:
  # 全局质量标签
  global_quality_tags: "masterpiece, best quality, ultra-detailed, 8k, photorealistic"

  # 全局负面提示词
  global_negative_prompt: "(worst quality, low quality:1.4), lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, jpeg artifacts, signature, watermark, username, blurry, multiple people, deformed"

  # 竖屏标签
  vertical_tags: "vertical composition, 9:16 aspect ratio, portrait orientation"

  # 风格标签
  style_tags:
    realistic: "photorealistic, realistic, cinematic lighting"
    semi_realistic: "semi-realistic, high quality render"
    anime: "anime style, cel shading"

# ===== 调试配置 =====

debug:
  enabled: false
  save_intermediate: false  # 保存中间结果
  log_level: "INFO"  # DEBUG | INFO | WARNING | ERROR
  log_file: "./logs/ai-video-generator.log"
```

---

## 配置说明

### 模型可配置性

#### 为什么需要可配置？

1. **模型快速迭代**：Seaweed 2.0 → 3.0 → 4.0...
2. **时长限制变化**：12秒 → 30秒 → 无限制
3. **多模型选择**：不同模型适合不同场景
4. **成本优化**：根据预算选择模型

#### 如何配置新模型？

**添加新的图生视频模型**：
```yaml
image_to_video:
  # 当前使用的模型
  model: "seaweed-3.0"  # 改为新模型

  # 模型能力更新
  capabilities:
    max_duration: 30  # 新模型支持 30 秒
    has_audio: true
    has_voice: true

  # 添加到可选模型列表
  alternative_models:
    - name: "seaweed-3.0"
      provider: "volcano"
      max_duration: 30  # 更长！
      cost_per_second: 2.5
      quality: 5
```

### 时长配置

#### 可配置时长的好处

**适应不同模型**：
```yaml
# Seaweed 2.0
max_duration: 12

# Seaweed 3.0
max_duration: 30

# 未来模型
max_duration: 60
```

**适应不同需求**：
```yaml
# 预算充足
max_segment_duration: 30  # 更长片段，更少拼接

# 预算有限
max_segment_duration: 8   # 更短片段，降低成本
```

---

## 使用配置文件

### 加载配置

```python
import yaml

# 加载配置
with open("config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# 读取模型配置
video_model = config["image_to_video"]["model"]
max_duration = config["image_to_video"]["capabilities"]["max_duration"]

print(f"使用模型: {video_model}")
print(f"最大时长: {max_duration}秒")
```

### 动态切换模型

```python
def select_video_model(budget, quality_requirement):
    """根据预算和质量要求选择最佳模型"""
    models = config["image_to_video"]["alternative_models"]

    # 筛选符合预算的模型
    affordable_models = [
        m for m in models
        if m["cost_per_second"] * max_duration <= budget
    ]

    # 筛选符合质量要求的模型
    qualified_models = [
        m for m in affordable_models
        if m["quality"] >= quality_requirement
    ]

    # 选择质量最高的
    best_model = max(qualified_models, key=lambda m: m["quality"])

    return best_model

# 使用
model = select_video_model(budget=50, quality_requirement=4)
print(f"选择模型: {model['name']}")
print(f"最大时长: {model['max_duration']}秒")
```

### 根据模型调整分段策略

```python
def calculate_segments(total_duration, model_config):
    """根据模型能力计算视频分段"""
    max_seg_duration = model_config["max_duration"]

    num_segments = math.ceil(total_duration / max_seg_duration)
    segment_duration = total_duration / num_segments

    return {
        "num_segments": num_segments,
        "segment_duration": segment_duration,
        "model_max": max_seg_duration
    }

# 示例：90秒视频
video_duration = 90  # 秒

# Seaweed 2.0: 最大 12 秒
model_2 = {"max_duration": 12}
segments_2 = calculate_segments(video_duration, model_2)
print(f"Seaweed 2.0: {segments_2['num_segments']} 段")
# 输出: 8 段（90/12 = 7.5，向上取整为 8）

# Seaweed 3.0: 最大 30 秒
model_3 = {"max_duration": 30}
segments_3 = calculate_segments(video_duration, model_3)
print(f"Seaweed 3.0: {segments_3['num_segments']} 段")
# 输出: 3 段（90/30 = 3）

# 好处：段数更少，拼接更自然，成本更低
```

---

## 环境变量配置

### .env 文件

```bash
# .env 文件（不要提交到 Git）

# 火山引擎
VOLCANO_API_KEY=your_volcano_api_key_here
VOLCANO_ENDPOINT=https://ark.cn-beijing.volces.com/api/v3

# 阿里云
ALIYUN_API_KEY=your_aliyun_api_key_here
ALIYUN_ENDPOINT=https://dashscope.aliyuncs.com/api/v1

# ElevenLabs（音效）
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Runway（可选）
RUNWAY_API_KEY=your_runway_api_key_here
```

### 加载环境变量

```python
from dotenv import load_dotenv
import os

# 加载 .env 文件
load_dotenv()

# 读取 API Key
volcano_key = os.getenv("VOLCANO_API_KEY")
aliyun_key = os.getenv("ALIYUN_API_KEY")

# 使用
api_client = VolcanoClient(api_key=volcano_key)
```

---

## 配置文件模板

### 最小配置（快速开始）

```yaml
# config.minimal.yaml
image_to_video:
  provider: "volcano"
  model: "seaweed-2.0"
  api_key: "${VOLCANO_API_KEY}"
  capabilities:
    max_duration: 12
```

### 完整配置（生产环境）

使用上面完整的 config.yaml

### 开发配置（调试）

```yaml
# config.dev.yaml
debug:
  enabled: true
  save_intermediate: true
  log_level: "DEBUG"

cost:
  optimization:
    enable_caching: true
    use_low_cost_model: true  # 开发时使用低成本模型
```

---

## 配置最佳实践

### 实践1：版本管理

```
config/
├── config.yaml           # 默认配置
├── config.prod.yaml      # 生产环境
├── config.dev.yaml       # 开发环境
└── config.test.yaml      # 测试环境
```

### 实践2：配置验证

```python
def validate_config(config):
    """验证配置文件的有效性"""
    required_keys = [
        "image_to_video.model",
        "image_to_video.capabilities.max_duration"
    ]

    for key in required_keys:
        if not get_nested_value(config, key):
            raise ValueError(f"配置缺失: {key}")

    # 验证时长设置合理
    max_duration = config["image_to_video"]["capabilities"]["max_duration"]
    if max_duration < 1 or max_duration > 300:
        raise ValueError(f"max_duration 必须在 1-300 秒之间: {max_duration}")

    print("✅ 配置验证通过")
```

### 实践3：配置热更新

```python
class ConfigManager:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self):
        with open(self.config_path, "r") as f:
            return yaml.safe_load(f)

    def reload(self):
        """重新加载配置（无需重启）"""
        self.config = self.load_config()
        print("✅ 配置已重新加载")

    def get(self, key):
        return get_nested_value(self.config, key)

# 使用
config_manager = ConfigManager("config.yaml")
max_duration = config_manager.get("image_to_video.capabilities.max_duration")

# 修改配置文件后
config_manager.reload()  # 重新加载，无需重启程序
```

---

**灵活配置，适应未来！**

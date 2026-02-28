# API 服务商对比指南

## 概述

本工具支持**两套完整的 API**，可根据需求灵活选择：

- **火山引擎/字节跳动**：Seaweed 2.0 视频生成，支持音频和配音
- **阿里云**：通义万相图像生成，VideoComposer 视频生成

两套 API 都支持：
1. **文生图**（Text-to-Image）
2. **参考生图**（Image-to-Image with Reference）：保持角色一致性
3. **图生视频**（Image-to-Video）或**首尾帧生视频**

---

## 一、火山引擎/字节跳动

### 1.1 文生图 API

**模型**：豆包 AI 绘画 / Doubao AI

**接口**：`/text-to-image`

**特点**：
- 支持高质量图像生成
- 支持负面提示词
- 可调节推理步数和引导系数

**请求示例**：
```python
client = VolcanoEngineClient(api_key, endpoint)
image_data = client.text_to_image(
    prompt="male, 28 years old, business elite, sharp eyes",
    negative_prompt="blurry, low quality, deformed",
    width=768,
    height=1365,
    num_inference_steps=50,
    guidance_scale=7.5
)
```

### 1.2 参考生图 API（IP-Adapter）

**模型**：IP-Adapter Plus

**接口**：`/image-to-image`

**特点**：
- ✅ **保持角色一致性的最佳方案**
- 支持参考图权重调节（0-1）
- 生成图片时保留参考图的角色特征

**请求示例**：
```python
image_data = client.image_to_image_with_reference(
    prompt="same character, in hotel lobby, confident posture",
    reference_image_path="character-front.png",
    reference_weight=0.75,  # 权重越高，越接近参考图
    width=768,
    height=1365
)
```

**权重调节建议**：
- `0.5-0.6`：参考图影响较小，生成图更自由
- `0.7-0.8`：✅ **推荐**，角色一致性好，场景灵活
- `0.85-1.0`：角色高度一致，但场景变化受限

### 1.3 图生视频 API（Seaweed 2.0）

**模型**：Seaweed 2.0

**接口**：`/image-to-video`（异步任务）

**特点**：
- ✅ **支持音频生成**
- ✅ **支持配音生成**
- 最大时长：**12 秒**
- 支持运动强度调节
- 竖屏友好（9:16）

**请求示例**：
```python
# 提交任务
task_id = client.image_to_video(
    image_path="keyframe.png",
    prompt="camera slowly pushes in, character stands still",
    duration=5,  # 秒
    motion_strength=0.7,
    fps=24
)

# 轮询结果
video_data = client.get_video_result(task_id, max_wait=300)
```

**运动提示词建议**：
- 固定镜头：`static shot, minimal movement`
- 推镜：`camera slowly pushes in, zoom in`
- 拉镜：`camera pulls out, zoom out`
- 跟镜：`camera follows subject, tracking shot`

---

## 二、阿里云

### 2.1 文生图 API（通义万相）

**模型**：Wanx-v1

**接口**：`/services/aigc/text2image/image-synthesis`

**特点**：
- 阿里云自研模型
- 支持负面提示词
- 尺寸格式：`宽*高`（如 `768*1365`）

**请求示例**：
```python
client = AliyunClient(api_key, endpoint)
image_data = client.text_to_image(
    prompt="male, 28 years old, business elite",
    negative_prompt="blurry, deformed",
    width=768,
    height=1365
)
```

### 2.2 参考生图 API（图像编辑）

**模型**：Wanx-v1 Image Editing

**接口**：`/services/aigc/image2image/image-synthesis`

**特点**：
- 使用 `strength` 参数控制（与火山引擎的 `reference_weight` 相反）
- `strength=0.2` 约等于 `reference_weight=0.8`
- 保持角色一致性

**请求示例**：
```python
image_data = client.image_to_image_with_reference(
    prompt="same character, in hotel lobby",
    reference_image_path="character.png",
    reference_weight=0.75,  # 自动转换为 strength=0.25
    width=768,
    height=1365
)
```

### 2.3 图生视频 API（VideoComposer）

**模型**：VideoComposer-v1

**接口**：`/services/aigc/image2video/video-synthesis`（异步任务）

**特点**：
- 最大时长：**10 秒**（比 Seaweed 2.0 短）
- ❌ 不支持音频生成（需要后期配音）
- 支持运动强度调节

**请求示例**：
```python
# 提交任务
task_id = client.image_to_video(
    image_path="keyframe.png",
    prompt="camera slowly pushes in",
    duration=5,
    motion_strength=0.7,
    fps=24
)

# 轮询结果
video_data = client.get_video_result(task_id, max_wait=300)
```

---

## 三、服务商对比

| 功能 | 火山引擎/字节 | 阿里云 | 推荐 |
|------|---------------|--------|------|
| **文生图** | ✅ 豆包 AI | ✅ 通义万相 | 两者都优秀 |
| **参考生图** | ✅ IP-Adapter | ✅ 图像编辑 | 火山引擎（IP-Adapter更强） |
| **图生视频** | ✅ Seaweed 2.0 | ✅ VideoComposer | 火山引擎（12秒 + 音频） |
| **最大时长** | 12 秒 | 10 秒 | 火山引擎 |
| **音频生成** | ✅ 支持 | ❌ 不支持 | 火山引擎 |
| **配音生成** | ✅ 支持 | ❌ 不支持 | 火山引擎 |
| **角色一致性** | ⭐⭐⭐⭐⭐ IP-Adapter | ⭐⭐⭐⭐ Image Editing | 火山引擎 |
| **成本** | 中等 | 中等 | 相当 |
| **稳定性** | 高 | 高 | 相当 |

---

## 四、使用建议

### 4.1 推荐方案 ✅

**短剧视频生成：优先使用火山引擎**

原因：
- Seaweed 2.0 支持 **12 秒时长**（比阿里云多 2 秒）
- **自动生成音频和配音**，省去后期配音成本
- IP-Adapter **角色一致性更好**

**配置示例**：
```yaml
text_to_image:
  provider: "volcano"

image_to_image:
  provider: "volcano"

image_to_video:
  provider: "volcano"
  model: "seaweed-2.0"
```

### 4.2 备用方案

**阿里云作为备用**：
- 当火山引擎 API 不可用时切换
- 需要后期配音和音效（成本更高）

**配置示例**：
```yaml
text_to_image:
  provider: "aliyun"

image_to_image:
  provider: "aliyun"

image_to_video:
  provider: "aliyun"
  model: "videocomposer-v1"
```

### 4.3 混合方案

**根据任务类型选择不同服务商**：

```yaml
# 图片生成：使用阿里云（假设更便宜）
text_to_image:
  provider: "aliyun"

image_to_image:
  provider: "aliyun"

# 视频生成：使用火山引擎（质量更好）
image_to_video:
  provider: "volcano"
  model: "seaweed-2.0"
```

---

## 五、代码使用示例

### 5.1 自动选择服务商

使用 `APIClient` 自动根据配置选择：

```python
from scripts.api_client import APIClient

# 自动读取 config.yaml 中的 provider 配置
client = APIClient("config.yaml")

# 以下调用会自动使用配置的服务商
client.generate_character_image(prompt="...", save_path="...")
client.generate_keyframe_with_reference(prompt="...", reference_image_path="...", save_path="...")
client.generate_video(keyframe_path="...", prompt="...", save_path="...")
```

### 5.2 直接使用特定服务商

如果想显式使用某个服务商：

```python
from scripts.api_client import VolcanoEngineClient, AliyunClient

# 显式使用火山引擎
volcano_client = VolcanoEngineClient(
    api_key="your_volcano_key",
    endpoint="https://ark.cn-beijing.volces.com/api/v3"
)
image_data = volcano_client.text_to_image(prompt="...")

# 显式使用阿里云
aliyun_client = AliyunClient(
    api_key="your_aliyun_key",
    endpoint="https://dashscope.aliyuncs.com/api/v1"
)
image_data = aliyun_client.text_to_image(prompt="...")
```

---

## 六、常见问题

### Q1: 如何快速切换服务商？

只需修改 `config.yaml` 中的 `provider`，无需修改代码：

```yaml
# 切换为火山引擎
image_to_video:
  provider: "volcano"

# 切换为阿里云
image_to_video:
  provider: "aliyun"
```

### Q2: 两个服务商可以同时使用吗？

可以！示例：

```yaml
# 图片生成用阿里云
text_to_image:
  provider: "aliyun"

# 视频生成用火山引擎
image_to_video:
  provider: "volcano"
```

### Q3: 如果火山引擎达到配额限制怎么办？

立即切换到阿里云：

```bash
# 修改 config.yaml
sed -i 's/provider: "volcano"/provider: "aliyun"/g' config.yaml

# 重新运行生成脚本
python scripts/generate_video.py --project "王者归来" --episode 1
```

### Q4: 哪个服务商的角色一致性更好？

**火山引擎的 IP-Adapter 更强**。

如果角色一致性是首要需求，推荐使用火山引擎的参考生图功能。

### Q5: 未来会支持更多服务商吗？

会！当前架构设计支持轻松添加新服务商：

1. 在 `api_client.py` 中添加新的客户端类（如 `RunwayClient`）
2. 在 `config.yaml` 的 `api_keys` 中添加配置
3. 在 `APIClient._get_client()` 中注册新服务商

无需修改业务逻辑代码！

---

## 七、API 端点参考

### 火山引擎

**基础 URL**：`https://ark.cn-beijing.volces.com/api/v3`

**端点列表**：
- 文生图：`POST /text-to-image`
- 图生图：`POST /image-to-image`
- 图生视频：`POST /image-to-video`
- 查询任务：`GET /tasks/{task_id}`

**认证方式**：
```
Authorization: Bearer YOUR_VOLCANO_API_KEY
```

### 阿里云

**基础 URL**：`https://dashscope.aliyuncs.com/api/v1`

**端点列表**：
- 文生图：`POST /services/aigc/text2image/image-synthesis`
- 图生图：`POST /services/aigc/image2image/image-synthesis`
- 图生视频：`POST /services/aigc/image2video/video-synthesis`
- 查询任务：`GET /services/aigc/tasks/{task_id}`

**认证方式**：
```
Authorization: Bearer YOUR_ALIYUN_API_KEY
```

---

## 八、总结

✅ **两套 API 都已完整实现**：
- 火山引擎/字节跳动：文生图、参考生图、图生视频
- 阿里云：文生图、参考生图、图生视频

✅ **推荐方案**：
- 短剧生成：**优先火山引擎**（12秒 + 音频 + IP-Adapter）
- 阿里云作为备用或混合使用

✅ **无缝切换**：
- 只需修改 `config.yaml` 的 `provider`
- 无需修改业务代码

---

**开始使用吧！🚀**

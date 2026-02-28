# 角色一致性技术

本文档介绍如何在不同镜头中保持角色外貌一致性的技术方法。

---

## 角色一致性的重要性

### 问题

**AI 生成的角色容易出现不一致**：
- 同一角色在不同镜头中外貌不同
- 面部特征变化
- 发型和服装不一致
- 风格不统一

**影响**：
- 观众困惑（这是同一个人吗？）
- 破坏沉浸感
- 降低专业度

### 目标

**保持角色的核心特征一致**：
- 面部特征：眼睛、鼻子、嘴巴、脸型
- 发型和发色
- 服装和配饰
- 整体风格

---

## 技术方案

### 方案1：IP-Adapter（推荐）⭐⭐⭐⭐⭐

**原理**：使用参考图引导生成，保持外貌一致

#### 工作流程

```
步骤1：生成角色标准参考图
    ↓
步骤2：后续生成时传入参考图
    ↓
步骤3：AI 根据参考图保持外貌一致
```

#### 实现方法

**生成标准参考图**：
```python
# 第一次生成角色（正面、高质量）
prompt = "masterpiece, 8k, male, 28 years old, business elite, ..."
reference_image = generate_image(prompt)

# 保存为参考图
save_reference(reference_image, "林宇-参考图.png")
```

**使用参考图生成后续图片**：
```python
# 后续生成时传入参考图
prompt = "same character, different angle, side view, ..."
new_image = generate_image_with_reference(
    prompt=prompt,
    reference_image="林宇-参考图.png",
    reference_weight=0.7  # 参考图权重 0-1
)
```

#### 参数调整

| 参数 | 范围 | 说明 |
|------|------|------|
| **reference_weight** | 0-1 | 参考图影响权重 |
| 0.5-0.6 | 中等 | 保持外貌但允许较大变化 |
| 0.7-0.8 | 高 | 严格保持外貌（推荐）|
| 0.9-1.0 | 极高 | 几乎完全复制（可能过于死板）|

#### 优势
- ✅ 简单易用，无需训练
- ✅ 一致性高
- ✅ 灵活性好，可调整不同姿势和角度
- ✅ 成本低

#### 劣势
- ⚠️ 依赖首次生成的质量
- ⚠️ 极端角度可能有偏差

---

### 方案2：LoRA 模型训练 ⭐⭐⭐⭐

**原理**：训练角色专属的 LoRA 模型，固化角色特征

#### 工作流程

```
步骤1：准备训练数据（15-30张角色图）
    ↓
步骤2：训练 LoRA 模型（1-3小时）
    ↓
步骤3：使用 LoRA 生成所有后续图片
    ↓
步骤4：角色外貌高度一致
```

#### 训练数据准备

**数量要求**：
- 最少：10 张
- 推荐：20-30 张
- 最多：50 张

**角度覆盖**：
- 正面：5-8 张
- 侧面（左右）：各 3-5 张
- 45度角：各 2-3 张
- 背面：2-3 张

**姿势覆盖**：
- 站立：5-8 张
- 坐姿：3-5 张
- 行走：2-3 张
- 其他动作：2-3 张

**表情覆盖**：
- 中性：10 张
- 微笑：5 张
- 严肃：3 张
- 其他：2 张

#### 训练步骤

**1. 生成训练数据**：
```python
# 使用不同提示词生成角色多角度图片
angles = ["front view", "side view", "45 degree angle", "back view"]
poses = ["standing", "sitting", "walking"]
expressions = ["neutral", "smiling", "serious"]

for angle in angles:
    for pose in poses:
        for expression in expressions:
            prompt = f"{base_character_prompt}, {angle}, {pose}, {expression}"
            image = generate_image(prompt)
            save_training_image(image)
```

**2. 训练 LoRA**：
```bash
# 使用 Kohya_ss 或类似工具训练
python train_lora.py \
    --pretrained_model="base_model.safetensors" \
    --train_data_dir="./training_images" \
    --output_dir="./lora_output" \
    --resolution=768 \
    --train_batch_size=1 \
    --learning_rate=1e-4 \
    --max_train_steps=1500
```

**3. 使用 LoRA 生成**：
```python
# 加载 LoRA 模型生成图片
prompt = "character in different scene, new pose, ..."
image = generate_image_with_lora(
    prompt=prompt,
    lora_path="林宇_LoRA.safetensors",
    lora_weight=0.8
)
```

#### 参数调整

| 参数 | 范围 | 说明 |
|------|------|------|
| **lora_weight** | 0-1 | LoRA 影响权重 |
| 0.6-0.7 | 中等 | 保持特征但允许变化 |
| 0.8-0.9 | 高 | 严格保持特征（推荐）|
| 1.0 | 极高 | 完全锁定特征 |

#### 优势
- ✅ 一致性极高
- ✅ 可生成任何角度和姿势
- ✅ 长期使用成本低

#### 劣势
- ❌ 需要训练时间（1-3小时）
- ❌ 需要训练数据准备
- ❌ 前期成本较高

---

### 方案3：固定提示词 ⭐⭐⭐

**原理**：使用完全相同的角色描述提示词

#### 方法

**核心关键词保持不变**：
```
固定部分（必须相同）：
- 基本信息：male, 28 years old, business elite
- 面部特征：angular face, sharp eyes, high nose bridge
- 发型：short black hair slicked back
- 服装：navy blue suit, white shirt

可变部分（可以调整）：
- 角度：front view, side view, back view
- 姿势：standing, sitting, walking
- 表情：neutral, smiling, serious
```

#### 示例

**正面图提示词**：
```
masterpiece, 8k, photorealistic,
male, 28 years old, business elite,
angular face, sharp eyes, high nose bridge, thin lips,
short black hair slicked back,
wearing navy blue suit, white shirt,
front view, standing, confident expression
```

**侧面图提示词**：
```
masterpiece, 8k, photorealistic,
male, 28 years old, business elite,              ← 相同
angular face, sharp eyes, high nose bridge, thin lips,  ← 相同
short black hair slicked back,                    ← 相同
wearing navy blue suit, white shirt,              ← 相同
side view, standing, thoughtful expression        ← 不同（角度和表情）
```

#### 优势
- ✅ 最简单，无需额外技术
- ✅ 无额外成本

#### 劣势
- ❌ 一致性较低
- ❌ 容易出现偏差
- ❌ 需要多次重新生成

---

## 方案对比

| 方案 | 一致性 | 易用性 | 成本 | 推荐度 |
|------|-------|--------|------|--------|
| **IP-Adapter** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 低 | ⭐⭐⭐⭐⭐ 最推荐 |
| **LoRA 训练** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 中 | ⭐⭐⭐⭐ 适合长期项目 |
| **固定提示词** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 低 | ⭐⭐⭐ 适合快速测试 |

---

## 实战流程

### 推荐工作流：IP-Adapter + 固定提示词

#### 步骤1：生成标准参考图

**生成多角度参考图**：
```python
angles = [
    ("front", "front view, facing camera"),
    ("side", "side view, profile"),
    ("45deg", "45 degree angle view"),
    ("full", "full body shot")
]

base_prompt = """
masterpiece, best quality, ultra-detailed, 8k, photorealistic,
male, 28 years old, handsome business elite,
angular face, sharp eyes, high nose bridge, thin lips, fair skin,
short black hair slicked back,
athletic build,
wearing tailored navy blue suit, white shirt, black tie,
confident expression, cold aura,
cinematic lighting, studio lighting,
vertical composition, 9:16 aspect ratio
"""

for name, angle_desc in angles:
    full_prompt = f"{base_prompt}, {angle_desc}"
    image = generate_image(full_prompt)
    save_image(image, f"林宇-{name}.png")
```

#### 步骤2：验证参考图质量

**检查要点**：
- [ ] 面部特征清晰？
- [ ] 发型准确？
- [ ] 服装正确？
- [ ] 整体风格统一？
- [ ] 竖屏构图合适？

**不满意则重新生成**

#### 步骤3：使用参考图生成关键帧

**对于每个镜头**：
```python
# 读取参考图
reference_image = load_image("林宇-正面.png")

# 生成关键帧（使用参考图）
keyframe_prompt = """
same character as reference,
in luxury hotel lobby,
standing near entrance,
looking confident,
maintaining same facial features,
cinematic lighting, realistic
"""

keyframe = generate_image_with_reference(
    prompt=keyframe_prompt,
    reference_image=reference_image,
    reference_weight=0.75,
    negative_prompt="different person, changed appearance, ..."
)
```

#### 步骤4：质量检查

**对比参考图和生成图**：
- 面部特征是否一致？
- 发型是否一致？
- 整体感觉是否像同一人？

**不一致的处理**：
- 调高 reference_weight（0.8-0.9）
- 在提示词中强调"same character"
- 重新生成

---

## 常见问题和解决方案

### 问题1：角色外貌有偏差

**原因**：参考图权重太低

**解决**：
```python
# 增加参考图权重
reference_weight = 0.8  # 从 0.7 提升到 0.8

# 或在提示词中强调
prompt += ", exactly same face as reference, same person, identical features"
```

### 问题2：角色风格不统一

**原因**：不同镜头使用了不同的风格描述

**解决**：
```python
# 固定风格关键词
style_keywords = "photorealistic, cinematic lighting, realistic"

# 所有镜头都使用相同的风格关键词
prompt = f"{character_desc}, {scene_desc}, {style_keywords}"
```

### 问题3：侧面或背面不像同一人

**原因**：只用了正面参考图

**解决**：
```python
# 根据角度选择合适的参考图
if angle == "side":
    reference_image = "林宇-侧面.png"
elif angle == "back":
    reference_image = "林宇-背面.png"
else:
    reference_image = "林宇-正面.png"
```

### 问题4：服装不一致

**原因**：提示词中服装描述不同

**解决**：
```python
# 固定服装描述
clothing_desc = "wearing navy blue suit, white shirt, black tie"

# 所有镜头都使用相同的服装描述
prompt = f"{character_desc}, {clothing_desc}, {angle_desc}"
```

---

## 批量生成检查流程

### 生成前检查清单

- [ ] 准备好标准参考图（多角度）？
- [ ] 提示词中核心关键词固定？
- [ ] reference_weight 设置合适（0.7-0.8）？
- [ ] 风格关键词统一？
- [ ] 服装描述一致？

### 生成后检查清单

- [ ] 对比所有生成图，外貌是否一致？
- [ ] 面部特征是否统一？
- [ ] 发型是否一致？
- [ ] 服装是否一致？
- [ ] 整体风格是否统一？

### 不一致时的处理

**方案A：重新生成**（推荐）
```python
# 调整参数重新生成
reference_weight += 0.1
regenerate_image()
```

**方案B：后期修复**
```python
# 使用 Photoshop 或 AI 修复工具
# 将不一致的部分调整为与参考图一致
```

---

## API 支持情况

### 火山引擎

**支持 IP-Adapter**：✅
- DoubaoAI：支持参考图
- API 参数：`reference_image`, `reference_strength`

**支持 LoRA**：✅
- 可上传自定义 LoRA
- API 参数：`lora_path`, `lora_weight`

### 阿里云

**支持参考图**：✅
- 通义万相：支持参考图模式
- API 参数：`ref_img`, `ref_mode`

**支持 LoRA**：⚠️ 部分支持
- 需要联系客服开通

---

## 最佳实践

### 实践1：建立角色资产库

**结构**：
```
characters/
├── 林宇/
│   ├── reference-front.png    # 正面参考图
│   ├── reference-side.png     # 侧面参考图
│   ├── reference-full.png     # 全身参考图
│   └── lora-model.safetensors # LoRA 模型（可选）
├── 张雪/
│   ├── reference-front.png
│   └── ...
└── ...
```

### 实践2：版本管理

**记录每个角色的提示词版本**：
```json
{
  "character": "林宇",
  "version": "v1.0",
  "base_prompt": "male, 28 years old, business elite, ...",
  "reference_images": {
    "front": "reference-front-v1.png",
    "side": "reference-side-v1.png"
  },
  "lora_model": "lora-v1.safetensors",
  "settings": {
    "reference_weight": 0.75
  }
}
```

### 实践3：质量控制流程

```
生成 → 检查一致性 → 不一致 → 调整参数 → 重新生成
              ↓ 一致
           通过 → 保存并用于后续生成
```

---

**保持角色一致性，提升视频专业度！**

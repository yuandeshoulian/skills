# 角色提示词模板

本文档提供专业的角色生成提示词模板，用于生成一致性高的角色形象。

---

## 提示词结构

### 标准提示词格式

```
[质量标签] [角色基本信息] [外貌细节] [服装] [姿势/角度] [风格] [技术参数] [负面提示词]
```

---

## 质量标签（必需）

**作用**：提升图片质量

**推荐标签**：
```
masterpiece, best quality, ultra-detailed, 8k, photorealistic
```

**中文**：
```
杰作，最佳质量，超高细节，8K，照片级真实感
```

---

## 角色基本信息

### 模板

```
[性别] [年龄] [职业/身份] character
```

### 示例

**示例1：都市精英**
```
male, 28 years old, business elite character
男性，28岁，商业精英角色
```

**示例2：霸道总裁**
```
male, 30s, handsome CEO character
男性，30多岁，英俊的CEO角色
```

**示例3：独立女性**
```
female, mid-20s, independent designer character
女性，20多岁，独立设计师角色
```

---

## 外貌细节

### 面部特征

**模板**：
```
[脸型] face, [眼睛特征] eyes, [鼻子特征] nose, [嘴唇特征] lips, [皮肤特征] skin
```

**常用描述**：

#### 脸型
- oval face（鹅蛋脸）
- angular face（棱角分明）
- round face（圆脸）
- sharp jawline（清晰的下颌线）

#### 眼睛
- sharp eyes（锐利的眼神）
- deep-set eyes（深邃的眼睛）
- gentle eyes（温柔的眼睛）
- cold eyes（冷漠的眼神）

#### 其他
- high nose bridge（高鼻梁）
- thin lips（薄唇）
- fair skin（白皙皮肤）
- wheat-colored skin（小麦色皮肤）

### 发型

**模板**：
```
[长度] [颜色] [风格] hair
```

**常用描述**：
- short black hair（短黑发）
- medium-length brown hair（中长棕发）
- long straight hair（长直发）
- slicked-back hair（背头）
- wavy hair（波浪卷发）

### 身材

**模板**：
```
[身高] [体型] build
```

**常用描述**：
- tall（高个子）
- athletic build（运动型身材）
- slim figure（苗条身材）
- muscular physique（肌肉发达）

---

## 服装

### 模板

```
wearing [服装类型] [颜色] [风格]
```

### 常用服装

#### 正式商务
```
wearing a tailored black suit, white shirt, black tie
穿着定制黑色西装，白衬衫，黑领带
```

#### 休闲风格
```
wearing a casual white t-shirt and jeans
穿着休闲白色T恤和牛仔裤
```

#### 晚礼服
```
wearing an elegant red evening gown
穿着优雅的红色晚礼服
```

---

## 姿势和角度

### 三个必需角度

#### 1. 正面（Portrait/Front View）

**用途**：主要角色展示，对话场景

**提示词**：
```
front view, facing camera, portrait shot, looking at camera
正面视角，面对镜头，肖像拍摄，看向镜头
```

#### 2. 侧面（Side View/Profile）

**用途**：展示轮廓，思考场景

**提示词**：
```
side view, profile shot, looking to the side
侧面视角，侧脸拍摄，看向一侧
```

#### 3. 全身（Full Body）

**用途**：展示整体形象，动作场景

**提示词**：
```
full body shot, standing pose, whole body visible
全身拍摄，站立姿势，全身可见
```

### 其他姿势

#### 特写（Close-up）
```
close-up shot, face focus, upper body
特写镜头，面部焦点，上半身
```

#### 动作姿势
```
walking pose（行走姿势）
sitting pose（坐姿）
leaning against wall（靠墙站立）
hands in pockets（手插口袋）
arms crossed（双臂交叉）
```

---

## 风格和氛围

### 风格选择

#### 写实风格（推荐）
```
photorealistic, realistic, lifelike, cinematic lighting
照片级真实，现实主义，如同真实，电影级打光
```

#### 半写实风格
```
semi-realistic, slightly stylized, high quality render
半写实，略微风格化，高质量渲染
```

#### 二次元风格
```
anime style, manga style, cel shading
动漫风格，漫画风格，赛璐珞着色
```

### 氛围和情绪

#### 冷酷精英
```
cold atmosphere, professional aura, confident expression
冷酷氛围，专业气场，自信表情
```

#### 温和亲切
```
warm atmosphere, gentle expression, friendly vibe
温暖氛围，温和表情，亲切感觉
```

---

## 技术参数

### 竖屏参数（重要）

```
vertical composition, 9:16 aspect ratio, portrait orientation
竖屏构图，9:16宽高比，纵向方向
```

### 画质参数

```
8k resolution, ultra high definition, sharp focus, high detail
8K分辨率，超高清，清晰对焦，高细节
```

### 光照参数

```
studio lighting, soft lighting, natural light, rim light
影棚灯光，柔和灯光，自然光，轮廓光
```

---

## 负面提示词（Negative Prompt）

**作用**：避免生成不想要的元素

### 通用负面提示词

```
(worst quality, low quality:1.4), lowres, bad anatomy, bad hands, text, error,
missing fingers, extra digit, fewer digits, cropped, jpeg artifacts, signature,
watermark, username, blurry, multiple people, crowd
```

**中文**：
```
最差质量，低质量，低分辨率，错误的解剖结构，错误的手，文字，错误，
缺失手指，多余手指，裁剪，JPEG伪影，签名，水印，用户名，模糊，多人，人群
```

### 针对性负面提示词

#### 避免多人
```
multiple people, crowd, group shot
多人，人群，集体照
```

#### 避免变形
```
deformed, distorted, disfigured, mutation
变形，扭曲，损毁，突变
```

#### 避免低质量
```
blurry, pixelated, low resolution, compressed
模糊，像素化，低分辨率，压缩
```

---

## 完整示例

### 示例1：都市逆袭男主角

**角色信息**：
- 姓名：林宇
- 年龄：28岁
- 身份：重生归来的商业精英
- 性格：冷静、睿智、腹黑

#### 正面提示词（英文）

```
masterpiece, best quality, ultra-detailed, 8k, photorealistic,

male, 28 years old, handsome business elite character,
angular face, sharp eyes, deep-set eyes, high nose bridge, thin lips, fair skin,
short black hair slicked back,
tall, athletic build,

wearing a tailored navy blue suit, white shirt, black tie, luxury watch,

front view, facing camera, portrait shot, upper body,
confident expression, slight smirk, cold aura,

photorealistic, realistic, cinematic lighting, studio lighting, rim light,
vertical composition, 9:16 aspect ratio, portrait orientation,
8k resolution, sharp focus, high detail,

professional photography, business portrait, elegant, sophisticated
```

#### 正面提示词（中文）

```
杰作，最佳质量，超高细节，8K，照片级真实感，

男性，28岁，英俊的商业精英角色，
棱角分明的脸，锐利的眼神，深邃的眼睛，高鼻梁，薄唇，白皙皮肤，
短黑发背头，
高个子，运动型身材，

穿着定制海军蓝西装，白衬衫，黑领带，豪华手表，

正面视角，面对镜头，肖像拍摄，上半身，
自信的表情，淡淡的笑容，冷酷的气场，

照片级真实，现实主义，电影级打光，影棚灯光，轮廓光，
竖屏构图，9:16宽高比，纵向方向，
8K分辨率，清晰对焦，高细节，

专业摄影，商业肖像，优雅，精致
```

#### 负面提示词

```
(worst quality, low quality:1.4), lowres, bad anatomy, bad hands, text, error,
missing fingers, extra digit, fewer digits, cropped, jpeg artifacts, signature,
watermark, username, blurry, multiple people, crowd, deformed, distorted,
cartoonish, unrealistic, anime
```

---

### 示例2：霸总甜宠男主角

**角色信息**：
- 年龄：32岁
- 身份：霸道总裁
- 性格：霸道、深情、宠溺

#### 正面提示词（英文）

```
masterpiece, best quality, ultra-detailed, 8k, photorealistic,

male, early 30s, extremely handsome CEO character,
sharp angular face, deep penetrating eyes, strong jawline, perfect facial features,
short dark hair with texture, styled elegantly,
tall muscular build, broad shoulders,

wearing a luxury black three-piece suit, crisp white shirt, silver cufflinks,
expensive black leather shoes, platinum watch,

front view, facing camera, upper body portrait,
intense gaze, domineering yet gentle expression, slight smile,
powerful aura, charismatic presence,

photorealistic, cinematic lighting, dramatic lighting, rim light, soft shadows,
vertical composition, 9:16 aspect ratio, portrait orientation,
8k resolution, ultra sharp focus, extreme detail,

luxury business portrait, high-end fashion photography, sophisticated, elegant
```

#### 正面提示词（中文）

```
杰作，最佳质量，超高细节，8K，照片级真实感，

男性，30出头，极其英俊的CEO角色，
锐利棱角分明的脸，深邃犀利的眼神，强壮的下颌线，完美的面部特征，
短黑发有质感，优雅定型，
高大肌肉发达的身材，宽肩，

穿着奢华的黑色三件套西装，洁白衬衫，银色袖扣，
昂贵的黑色皮鞋，铂金手表，

正面视角，面对镜头，上半身肖像，
强烈的凝视，霸道而温柔的表情，微笑，
强大的气场，魅力十足的存在感，

照片级真实，电影级打光，戏剧性灯光，轮廓光，柔和阴影，
竖屏构图，9:16宽高比，纵向方向，
8K分辨率，超清晰对焦，极致细节，

奢华商业肖像，高端时尚摄影，精致，优雅
```

---

### 示例3：独立女主角

**角色信息**：
- 姓名：苏婉
- 年龄：25岁
- 身份：独立设计师
- 性格：独立、坚强、聪慧

#### 正面提示词（英文）

```
masterpiece, best quality, ultra-detailed, 8k, photorealistic,

female, mid-20s, beautiful independent designer character,
oval face, bright intelligent eyes, delicate features, gentle smile,
long straight black hair, elegant hairstyle,
slim figure, graceful posture,

wearing a stylish white blouse, black pencil skirt, minimal jewelry,
professional yet fashionable,

front view, facing camera, upper body portrait,
confident yet approachable expression, warm smile, intelligent gaze,
independent aura, elegant demeanor,

photorealistic, soft natural lighting, window light, gentle shadows,
vertical composition, 9:16 aspect ratio, portrait orientation,
8k resolution, sharp focus, high detail,

professional portrait photography, fashion photography, modern, elegant
```

#### 正面提示词（中文）

```
杰作，最佳质量，超高细节，8K，照片级真实感，

女性，25岁左右，美丽的独立设计师角色，
鹅蛋脸，明亮聪慧的眼睛，精致的五官，温柔的笑容，
长直黑发，优雅的发型，
苗条身材，优雅姿态，

穿着时尚的白色衬衫，黑色铅笔裙，简约首饰，
专业又时尚，

正面视角，面对镜头，上半身肖像，
自信而亲和的表情，温暖的笑容，聪慧的目光，
独立的气场，优雅的风度，

照片级真实，柔和自然光，窗户光，柔和阴影，
竖屏构图，9:16宽高比，纵向方向，
8K分辨率，清晰对焦，高细节，

专业肖像摄影，时尚摄影，现代，优雅
```

---

## 提示词优化技巧

### 技巧1：权重控制

**语法**：
```
(keyword:weight)
```

**示例**：
```
(photorealistic:1.3) - 强调真实感
(sharp eyes:1.2) - 强调锐利的眼神
(blurry:0.8) - 降低模糊的可能性
```

### 技巧2：多语言混合

**建议**：英文 + 中文混合，提升理解准确度

**示例**：
```
sharp eyes, 锐利的眼神
business elite, 商业精英
```

### 技巧3：细节递进

**从粗到细**：
```
1. 基本信息：male, 28 years old
2. 外貌特征：angular face, sharp eyes
3. 服装细节：navy blue suit, white shirt
4. 氛围情绪：confident expression, cold aura
```

### 技巧4：参考真人

**方法**：可以参考明星或模特

**示例**：
```
in the style of [明星名], similar to [模特名]
注意：避免直接使用真人姓名，容易被拒绝
改用"类似风格"的描述
```

---

## 角色一致性技巧

### 方法1：使用 IP-Adapter

**原理**：将首次生成的角色图作为参考图

**步骤**：
1. 生成角色正面图
2. 后续所有图片都传入这张参考图
3. 保持角色外貌一致

### 方法2：使用 LoRA

**原理**：训练角色专属 LoRA 模型

**步骤**：
1. 生成 10-20 张角色图（不同角度和姿势）
2. 训练 LoRA 模型
3. 后续生成时使用该 LoRA

**优势**：一致性最高
**劣势**：需要训练时间和成本

### 方法3：固定提示词

**原理**：使用完全相同的提示词

**注意**：
- 核心关键词必须相同
- 可以调整姿势和角度
- 不要改变外貌和服装描述

---

## 检查清单

在生成角色前，使用此清单检查提示词：

### 必需元素

- [ ] 包含质量标签？
- [ ] 包含基本信息（性别、年龄、身份）？
- [ ] 包含外貌细节？
- [ ] 包含服装描述？
- [ ] 包含姿势和角度？
- [ ] 包含风格和氛围？
- [ ] 包含技术参数？
- [ ] 包含负面提示词？

### 竖屏适配

- [ ] 包含 `vertical composition` 或 `9:16 aspect ratio`？
- [ ] 包含 `portrait orientation`？

### 一致性保证

- [ ] 核心关键词明确？
- [ ] 外貌描述详细？
- [ ] 服装描述清晰？

---

**用专业的提示词，生成高质量的角色形象！**

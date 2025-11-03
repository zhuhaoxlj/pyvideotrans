# Whisper 字幕错误检测工具 - 快速开始指南

## 🚀 5分钟快速上手

### 第一步：安装依赖（1分钟）

```bash
# macOS/Linux
pip install PySide6 openai httpx

# Windows
pip install PySide6 openai httpx
```

### 第二步：启动工具（10秒）

```bash
# macOS/Linux
./run_whisper_error_checker.sh

# 或直接运行
python whisper_error_checker.py

# Windows
run_whisper_error_checker.bat
```

### 第三步：基础配置（2分钟）

#### 推荐配置1：使用 DeepSeek（便宜好用）

1. 注册账号：https://platform.deepseek.com/
2. 获取API Key：https://platform.deepseek.com/api_keys
3. 在工具中选择：
   - Provider: `DeepSeek`
   - API Key: `粘贴你的key`
   - Model: `deepseek-chat`

**费用参考**：约 ￥1 可处理 1000+ 条字幕

#### 推荐配置2：使用 SiliconFlow（免费额度）

1. 注册账号：https://siliconflow.cn/
2. 获取API Key：https://siliconflow.cn/account/ak
3. 在工具中选择：
   - Provider: `SiliconFlow`
   - API Key: `粘贴你的key`
   - Model: `Qwen/Qwen2.5-7B-Instruct`

**免费额度**：新用户有免费tokens

#### 推荐配置3：使用 OpenAI（效果最好）

1. 获取API Key：https://platform.openai.com/api-keys
2. 在工具中选择：
   - Provider: `OpenAI`
   - API Key: `粘贴你的key`
   - Model: `gpt-4o-mini`

**费用参考**：约 $0.1 可处理 500+ 条字幕

### 第四步：分析字幕（1分钟）

1. **拖入字幕文件**：将 `.srt` 文件拖到界面上
2. **点击"🚀 开始分析"**
3. 等待分析完成
4. 查看结果并导出

## 📋 使用示例

### 示例1：分析你提供的字幕

你的字幕文件：`videoplayback (1)_word_based.srt`

```bash
# 启动工具
python whisper_error_checker.py

# 在界面上：
# 1. 拖入 "videoplayback (1)_word_based.srt"
# 2. 配置 DeepSeek API
# 3. 点击"开始分析"
# 4. 等待结果
# 5. 导出修正后的字幕
```

### 预期结果

工具会检测类似这样的错误：

```
原文: "anti-vision"
可能修正: "anti-vision" (正确)

原文: "mad scientist"
可能修正: "mad scientist" (正确)

原文: "there"
可能修正: "they're" (如果上下文是 they are)
```

## ⚙️ 常用配置

### 小文件（<100条字幕）
- Batch Size: `50`
- Temperature: `0.7`
- Max Tokens: `4096`

### 中等文件（100-500条）
- Batch Size: `30`
- Temperature: `0.7`
- Max Tokens: `4096`

### 大文件（>500条）
- Batch Size: `20`
- Temperature: `0.6`
- Max Tokens: `8192`

## 💡 常见问题

### Q1: 如何知道我的字幕有多少条？
打开 `.srt` 文件，最后一个数字就是字幕条数。

### Q2: 处理要多久？
- DeepSeek: 约 1-2秒/批次（30条）
- OpenAI gpt-4o-mini: 约 2-3秒/批次
- 总时间 = (字幕总数 / Batch Size) × 单批时间

### Q3: 费用大概多少？
- **DeepSeek**: 100条字幕约 ￥0.1
- **OpenAI gpt-4o-mini**: 100条字幕约 $0.02
- **SiliconFlow**: 免费额度内可处理数千条

### Q4: 如果检测不到错误怎么办？
1. 降低Temperature (试试 0.5)
2. 在Prompt中更明确要求
3. 尝试"激进模式"Prompt（见 `whisper_checker_prompts.json`）

### Q5: 如何减少误报？
1. 提高Temperature (试试 0.8-0.9)
2. 使用"保守模式"Prompt
3. 在Prompt中明确说明不要修改某些类型的内容

## 🎯 针对你的字幕的建议

你的字幕是关于个人成长/自我提升的内容，建议：

1. **使用教育类Prompt**：
```
你是教育内容字幕校对专家，重点关注：
1. 自我提升术语（vision, anti-vision, entropy等）
2. 心理学概念
3. 励志类表达的准确性
4. 保持口语化表达风格

不要过度修正口语化表达，保持演讲者的风格。
```

2. **配置参数**：
   - Temperature: `0.6` (稍保守，避免改变演讲风格)
   - Batch Size: `30`
   - Model: `deepseek-chat` 或 `gpt-4o-mini`

3. **重点检查**：
   - 专业术语（vision, anti-vision, entropy, chaos, order等）
   - 同音词（there/their/they're）
   - 人称代词的一致性

## 📊 效果预览

处理后你会看到：

**左侧（错误列表）**：
```
发现 5 处可能的错误:

1. 字幕 [15]
   原文: "your"
   修正: "you're"
   原因: 应为"you are"的缩写

2. 字幕 [42]
   原文: "effect"
   修正: "affect"
   原因: 此处应使用动词"影响"
...
```

**右侧（对比视图）**：
高亮显示所有修改的地方，方便对比

## 🔥 进阶技巧

### 技巧1：使用预设Prompt模板

```bash
# 加载预设Prompt
# 工具会自动读取 whisper_checker_prompts.json
# 你可以复制对应的prompt到界面
```

### 技巧2：自定义领域词汇表

在Prompt中添加：
```
请特别注意以下专业术语，确保正确识别：
- anti-vision: 反愿景
- entropy: 熵（混乱度）
- mad scientist: 疯狂科学家
- transmute: 转化
...
```

### 技巧3：分阶段处理

1. 第一轮：保守模式，只修正明显错误
2. 第二轮：针对第一轮结果，使用激进模式
3. 人工复核，选择性应用修正

## 📝 完整工作流程

```
1. 准备字幕
   ↓
2. 启动工具
   ↓
3. 配置LLM (DeepSeek推荐)
   ↓
4. 加载字幕文件
   ↓
5. 选择/编写Prompt
   ↓
6. 测试连接
   ↓
7. 开始分析
   ↓
8. 查看结果
   ↓
9. 人工复核
   ↓
10. 导出修正后的字幕
   ↓
11. 与原字幕对比验证
```

## 🎓 最佳实践

1. **先小批量测试**：用前50条字幕测试效果
2. **保留原始文件**：不要覆盖原字幕
3. **人工复核**：不要盲目应用所有修改
4. **迭代优化**：根据结果调整Prompt和参数
5. **记录配置**：找到好用的配置后记录下来

---

**开始使用吧！** 🚀

如有问题，查看详细文档：`WHISPER_ERROR_CHECKER_README.md`


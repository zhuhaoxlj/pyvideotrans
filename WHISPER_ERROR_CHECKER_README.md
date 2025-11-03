# Whisper 字幕错误检测工具

## 🎯 功能简介

这是一个基于LLM的智能工具，用于分析和修正Whisper语音识别生成的字幕中可能存在的识别错误。

### 主要功能

1. **智能错误检测**：使用LLM分析字幕文本，根据上下文语义找出可能的识别错误
2. **可视化对比**：高亮显示原文和修正后的文本差异
3. **批量处理**：自动分批处理大量字幕，避免超出LLM token限制
4. **多LLM支持**：支持OpenAI、DeepSeek、SiliconFlow等多个LLM提供商
5. **自定义Prompt**：可以自定义分析提示词，针对特定领域优化
6. **导出功能**：导出修正后的字幕文件和错误报告

## 📋 使用场景

Whisper在语音识别时可能出现的错误：

- **同音词混淆**：their/there/they're, your/you're, its/it's
- **专有名词错误**：人名、地名、品牌名识别错误
- **技术术语错误**：行业专业术语识别不准确
- **语法不通顺**：识别出的句子语法不正确
- **上下文不连贯**：局部识别正确但整体语义不通

## 🚀 快速开始

### 1. 安装依赖

```bash
# 使用 uv (推荐)
uv pip install PySide6 openai httpx

# 或使用 pip
pip install PySide6 openai httpx
```

### 2. 启动工具

```bash
# 方式1: 使用 uv
uv run python whisper_error_checker.py

# 方式2: 使用 python
python whisper_error_checker.py
```

### 3. 使用步骤

#### 步骤1：加载字幕文件

- **方式A**：直接拖拽 `.srt` 字幕文件到文件选择区域
- **方式B**：点击"选择文件"按钮选择字幕文件

#### 步骤2：配置LLM

1. **选择Provider**：
   - **OpenAI**（推荐 gpt-4o-mini，性价比高）
   - **DeepSeek**（国内可用，价格便宜）
   - **SiliconFlow**（国内可用，免费额度）
   - **Custom**（自定义API）

2. **输入API Key**：
   - OpenAI: https://platform.openai.com/api-keys
   - DeepSeek: https://platform.deepseek.com/api_keys
   - SiliconFlow: https://siliconflow.cn/account/ak

3. **选择模型**：
   - OpenAI: `gpt-4o-mini` (推荐)
   - DeepSeek: `deepseek-chat` (推荐)
   - SiliconFlow: `Qwen/Qwen2.5-7B-Instruct`

4. **配置参数**（可选）：
   - **Temperature**: 0.7（建议0.5-0.8，越低越保守）
   - **Max Tokens**: 4096（根据字幕长度调整）
   - **Batch Size**: 30（每批处理的字幕条数，可根据模型调整）
   - **JSON Mode**: 勾选以确保返回JSON格式
   - **Proxy**: 如需代理，填写如 `http://127.0.0.1:7890`

5. **测试连接**：
   - 点击"测试 LLM 连接"确保配置正确

#### 步骤3：编写/调整Prompt

工具已提供默认Prompt，你可以根据需要自定义：

```
你是一个专业的字幕校对助手，专门分析Whisper语音识别可能出现的错误。

请注意以下常见的Whisper识别错误类型：
1. 同音词混淆（如：their/there/they're, your/you're, its/it's）
2. 专有名词识别错误（人名、地名、品牌名）
3. 技术术语或行业术语错误
4. 语法不通顺的地方
5. 上下文语义不连贯

请基于上下文语义分析，只标注那些明显可能是识别错误的地方。
不要过度修正，保持原文风格。
```

**针对特定领域的Prompt示例**：

- **技术视频**：
```
你是技术视频字幕校对专家。重点关注：
1. 编程语言名称和关键字
2. 技术术语和缩写
3. 框架和库名称
4. 命令行指令
```

- **医学视频**：
```
你是医学字幕校对专家。重点关注：
1. 医学术语和疾病名称
2. 药物名称
3. 解剖学术语
4. 医疗程序名称
```

#### 步骤4：执行分析

1. 点击"🚀 开始分析"按钮
2. 等待处理完成（处理时间取决于字幕数量和LLM速度）
3. 查看结果

#### 步骤5：查看结果

**左侧窗口**：显示所有检测到的错误列表
```
发现 3 处可能的错误:

1. 字幕 [5]
   原文: there
   修正: they're
   原因: 根据上下文应该是"they are"的缩写

2. 字幕 [12]
   原文: LLM
   修正: LLM
   原因: ...
```

**右侧窗口**：高亮显示修正后的字幕（黄色背景表示修改）

#### 步骤6：导出结果

- **导出修正后的字幕**：生成应用了所有修正的新字幕文件
- **导出错误报告**：生成详细的错误报告文本文件

## 💡 使用技巧

### 1. Batch Size 设置建议

- **小文件（<100条字幕）**：Batch Size = 50
- **中等文件（100-500条）**：Batch Size = 30
- **大文件（>500条）**：Batch Size = 20

### 2. Temperature 参数调整

- **保守修正（0.3-0.5）**：只修正明显错误，适合准确率高的字幕
- **平衡修正（0.6-0.8）**：默认设置，平衡准确性和覆盖率
- **激进修正（0.9-1.0）**：可能会有更多建议，需要人工复核

### 3. 提高检测准确率

1. **提供上下文**：在Prompt中说明视频主题/领域
2. **添加专业术语列表**：在Prompt中列出关键术语
3. **分段处理**：对于超长字幕，可以分段处理后合并

### 4. 成本优化

- **使用更小的模型**：gpt-4o-mini 比 gpt-4o 便宜90%
- **增大Batch Size**：减少API调用次数
- **使用国内模型**：DeepSeek、SiliconFlow价格更低

## 🔧 高级配置

### 自定义API端点

如果你有自己的LLM API服务：

1. 选择 Provider = "Custom"
2. 输入自定义API URL（必须兼容OpenAI格式）
3. 输入API Key
4. 手动输入模型名称

### 代理设置

如果需要通过代理访问API：

- HTTP代理：`http://127.0.0.1:7890`
- HTTPS代理：`https://127.0.0.1:7890`
- SOCKS5代理：`socks5://127.0.0.1:7890`

### 批处理脚本

如果需要批量处理多个字幕文件，可以修改代码添加批处理功能，或使用命令行参数。

## 📊 返回格式说明

LLM返回的JSON格式：

```json
{
  "corrections": [
    {
      "subtitle_index": 5,
      "original": "there",
      "corrected": "they're",
      "reason": "根据上下文'they are going'应该使用缩写they're"
    },
    {
      "subtitle_index": 12,
      "original": "OpenAI GPT",
      "corrected": "OpenAI GPT-4",
      "reason": "完整模型名称应为GPT-4"
    }
  ]
}
```

## ⚠️ 注意事项

1. **API费用**：使用OpenAI等服务会产生费用，建议先小批量测试
2. **网络连接**：需要稳定的网络连接访问LLM API
3. **人工复核**：LLM的修正建议需要人工审核，不要盲目应用所有修改
4. **隐私保护**：字幕内容会发送到LLM服务商，注意隐私保护
5. **准确率限制**：LLM可能产生误判，建议作为辅助工具使用

## 🐛 故障排除

### 问题1：连接测试失败

- 检查API Key是否正确
- 检查API URL是否正确
- 检查网络连接
- 检查是否需要代理

### 问题2：返回结果为空

- 增加Temperature参数
- 调整Prompt，使其更明确
- 检查字幕文件是否正确加载

### 问题3：处理速度慢

- 减小Batch Size
- 使用速度更快的模型（如gpt-4o-mini）
- 检查网络速度

### 问题4：JSON解析错误

- 确保勾选"JSON Mode"
- 在Prompt中明确要求返回JSON格式
- 尝试使用支持JSON mode的模型

## 📝 开发说明

### 项目结构

```
whisper_error_checker.py
├── SubtitleBlock          # 字幕块数据类
├── SubtitleParser         # SRT解析器
├── LLMWorker             # LLM处理线程
└── WhisperErrorCheckerGUI # 主界面
```

### 扩展功能建议

1. 支持更多字幕格式（ASS, VTT等）
2. 添加批处理模式
3. 添加命令行界面
4. 支持本地LLM（Ollama等）
5. 添加字幕时间轴调整功能
6. 集成更多LLM服务商

## 📄 许可证

本工具基于 pyvideotrans 项目，遵循相同的开源许可证。

## 🙏 致谢

- 基于 [pyvideotrans](https://github.com/jianchang512/pyvideotrans) 项目
- 使用 OpenAI API
- 使用 PySide6 GUI框架

---

**祝使用愉快！如有问题欢迎反馈。**


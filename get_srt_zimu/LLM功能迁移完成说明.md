# LLM 智能字幕分割功能迁移完成说明

## 概述

已成功将 `llm_split.py` 及其完整的 LLM 智能字幕分割功能从主项目迁移到 `get_srt_zimu/` 独立项目中。

## 迁移内容

### 1. 核心处理器更新

**文件：** `get_srt_zimu/utils/llm_processor.py`

**新增功能：**
- ✅ **从视频生成新字幕**：使用 Faster-Whisper 进行语音识别 + LLM 智能断句
- ✅ **重新分割现有字幕（带视频）**：使用 Whisper 获取词级时间戳 + 原始字幕文本 + LLM 优化
- ✅ **重新分割现有字幕（仅SRT）**：纯 LLM 重新分割，无需视频
- ✅ **缓存机制**：自动缓存 Whisper 识别结果，避免重复处理
- ✅ **规则引擎回退**：当 LLM 失败时自动使用规则引擎
- ✅ **流式输出**：实时显示 LLM 响应内容
- ✅ **多种 LLM 提供商**：支持 SiliconFlow、OpenAI、Claude、DeepSeek
- ✅ **增强的文本匹配算法**：处理 Whisper 缺失词、插值估算
- ✅ **时间戳验证和调整**：自动修复时间戳冲突

**主要方法：**
```python
class LLMProcessor(QThread):
    - process_srt_only()              # 模式1：仅重新分割现有字幕
    - process_new_transcription()     # 模式2：从视频生成新字幕
    - process_with_video_and_srt()    # 模式3：视频+字幕重新分割
    - transcribe_with_whisper()       # Whisper 语音识别
    - llm_smart_split()               # LLM 智能断句（词级时间戳）
    - llm_split_simple()              # LLM 简单分割（无词级时间戳）
    - fallback_split()                # 规则引擎回退
    - get_cache_key() / save_cache() / load_cache()  # 缓存管理
```

### 2. UI 界面更新

**文件：** `get_srt_zimu/ui/split_view.py`

**新增界面元素：**
- 🎥 **视频/音频文件选择**：用于生成新字幕或获取词级时间戳
- ☑️ **使用现有字幕复选框**：可选择是否使用现有字幕
- 📁 **字幕文件选择**：选择 SRT 文件进行重新分割
- 🎤 **Whisper 设置组**：
  - 识别语言选择（支持 auto-detect）
  - 模型大小选择（tiny/base/small/medium/large/large-v3/large-v3-turbo）
  - 计算设备选择（CPU/CUDA/MPS）
- 🤖 **LLM 配置组**（保持原有）
- 📄 **处理日志**：实时显示处理进度和 LLM 响应

**支持的处理模式：**
1. **仅选择视频**：从视频生成新字幕（Whisper + LLM）
2. **仅选择字幕**：重新分割现有字幕（纯 LLM）
3. **视频 + 字幕**：使用视频的词级时间戳重新分割字幕（Whisper + LLM）

### 3. 依赖项更新

**文件：** `requirements.txt` 和 `pyproject.toml`

**新增依赖：**
```txt
faster-whisper>=0.10.0  # Faster-Whisper 语音识别
requests>=2.31.0        # HTTP 请求（LLM API 调用）
```

## 使用指南

### 方式 1：从视频生成新字幕

1. 点击「📂 选择视频/音频」选择视频文件
2. 配置 Whisper 设置（语言、模型、设备）
3. 配置 LLM 设置（提供商、API Key、模型）
4. 点击「✨ 开始处理」

### 方式 2：重新分割现有字幕（仅 LLM）

1. 勾选「使用现有字幕进行重新分割」
2. 点击「📂 选择 SRT 文件」选择字幕文件
3. 配置 LLM 设置
4. 点击「✨ 开始处理」

### 方式 3：视频 + 字幕重新分割（最精确）

1. 点击「📂 选择视频/音频」选择视频文件
2. 勾选「使用现有字幕进行重新分割」
3. 点击「📂 选择 SRT 文件」选择字幕文件
4. 配置 Whisper 和 LLM 设置
5. 点击「✨ 开始处理」

## 技术特性

### 缓存机制

- **位置：** `~/Videos/pyvideotrans/get_srt_zimu/whisper_cache/`
- **格式：** `.pkl` 文件（pickle 序列化）
- **内容：** 词级时间戳、检测语言、时间戳
- **缓存键：** 视频文件 SHA256 哈希（如果有字幕文件，则包含字幕文件哈希）

### 输出文件

- **位置：** `~/Videos/pyvideotrans/get_srt_zimu/output/`
- **命名规则：**
  - 从视频生成：`{视频文件名}_llm_smart.srt`
  - 重新分割（带视频）：`{视频文件名}_llm_resplit.srt`
  - 重新分割（仅SRT）：`{字幕文件名}_llm_split.srt`

### LLM 流式输出

- 实时显示 LLM 生成的内容
- 支持所有主流 LLM 提供商的流式 API
- 自动处理不同提供商的响应格式

### 错误处理

- LLM 失败时自动回退到规则引擎
- Faster-Whisper 不支持 MPS 时自动回退到 CPU
- 自动修复时间戳冲突和重叠
- 详细的错误日志输出

## 配置文件

### API Key 存储

**位置：** `~/Videos/pyvideotrans/get_srt_zimu/.env`

**格式：**
```env
SILICONFLOW_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
CLAUDE_API_KEY=your_key_here
DEEPSEEK_API_KEY=your_key_here
```

- 自动根据选择的提供商加载对应的 API Key
- 输入 API Key 后自动保存到 .env 文件
- 支持多个提供商的 API Key 同时存储

## 安装依赖

在 `get_srt_zimu/` 目录下运行：

```bash
# 使用 pip
pip install -r requirements.txt

# 或使用 uv
uv pip install -r requirements.txt
```

## 运行方式

### 独立运行

在 `get_srt_zimu/` 目录下：

```bash
# 使用 Python
python main.py

# 或使用 uv
uv run python main.py
```

### 在主项目中运行

在主项目根目录：

```bash
python llm_split.py
```

## 与原始功能的对比

| 功能 | 原始 llm_split.py | 迁移后 get_srt_zimu | 状态 |
|------|-------------------|---------------------|------|
| 从视频生成字幕 | ✅ | ✅ | ✅ 完整迁移 |
| 重新分割现有字幕 | ✅ | ✅ | ✅ 完整迁移 |
| 视频+字幕重新分割 | ✅ | ✅ | ✅ 完整迁移 |
| 缓存机制 | ✅ | ✅ | ✅ 完整迁移 |
| 规则引擎回退 | ✅ | ✅ | ✅ 完整迁移 |
| 流式输出 | ✅ | ✅ | ✅ 完整迁移 |
| 多 LLM 提供商 | ✅ | ✅ | ✅ 完整迁移 |
| GUI 界面 | ✅ | ✅ | ✅ 增强版 |
| 独立运行 | ❌ | ✅ | ✅ 新功能 |

## 文件结构

```
get_srt_zimu/
├── main.py                    # 主程序入口
├── requirements.txt           # 依赖项（已更新）
├── pyproject.toml            # 项目配置（已更新）
├── ui/
│   ├── split_view.py         # AI智能分割界面（已更新）
│   ├── main_window.py        # 主窗口
│   ├── home_view.py          # 首页
│   ├── process_view.py       # 处理视图
│   └── render_view.py        # 渲染视图
└── utils/
    ├── llm_processor.py      # LLM处理器（已更新）
    ├── whisper_processor.py  # Whisper处理器
    ├── srt_utils.py          # SRT工具
    └── fcpxml_generator.py   # FCPXML生成器
```

## 测试建议

1. **测试模式 1**：选择一个短视频（< 1分钟），从视频生成新字幕
2. **测试模式 2**：选择一个现有的 SRT 文件，进行重新分割
3. **测试模式 3**：同时选择视频和字幕，进行高精度重新分割
4. **测试缓存**：重复处理同一个视频，验证缓存机制
5. **测试错误处理**：尝试使用无效的 API Key，验证错误处理
6. **测试流式输出**：观察 LLM 响应的实时显示

## 已知限制

1. **Faster-Whisper MPS 支持**：目前 faster-whisper 不支持 Apple Silicon 的 MPS 加速，会自动回退到 CPU
2. **模型下载**：首次使用时需要下载 Whisper 模型（可能需要几分钟）
3. **LLM API 调用**：需要稳定的网络连接和有效的 API Key

## 迁移完成清单

- [x] ✅ 更新 `llm_processor.py` - 添加完整的 LLM 功能
- [x] ✅ 更新 `split_view.py` - 添加视频输入、Whisper设置等
- [x] ✅ 更新 `requirements.txt` 和 `pyproject.toml` - 添加依赖
- [x] ✅ 创建迁移说明文档

## 总结

LLM 智能字幕分割功能已完整迁移到 `get_srt_zimu/` 独立项目中，功能完全保留，界面得到增强，现在可以作为独立工具使用，也可以集成到主项目中。

所有核心功能（Whisper 识别、LLM 断句、缓存机制、流式输出、多提供商支持）均已完整实现，并通过新的 UI 界面提供更好的用户体验。


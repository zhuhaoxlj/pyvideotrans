# 🎬 Get SRT Zimu - AI 字幕工具集

智能字幕生成、分割和渲染工具，基于 Whisper 和 LLM。

## 🌟 主要功能

### 1. 🎙️ 字幕生成
使用 OpenAI Whisper 从视频自动生成字幕，支持词级时间戳。

### 2. ✂️ 智能分割 ⭐
使用 LLM（大语言模型）对字幕进行智能断句优化，基于语义理解而非简单规则。

### 3. 🎥 视频渲染
将优化后的字幕烧录到视频中。

### 4. 🔍 缓存检查
可视化检查 Whisper 词级时间戳的准确性。

## 🚀 快速启动

### 主界面（所有功能）

```bash
# macOS/Linux
./run.sh

# Windows
run.bat

# 或直接运行
python main.py
```

### 独立启动 - LLM 智能分割 ⭐

**最常用功能，现在可以独立启动！**

```bash
# macOS/Linux
./run_llm_split.sh

# Windows
run_llm_split.bat

# 或直接运行
python llm_split.py
```

详细使用说明：[LLM_SPLIT_QUICK_START.md](./LLM_SPLIT_QUICK_START.md)

### 独立启动 - 缓存检查工具

```bash
python check_whisper_cache.py
```

## 📦 安装

### 方式 1：使用 uv（推荐）

```bash
cd get_srt_zimu
uv sync
```

### 方式 2：使用 pip

```bash
cd get_srt_zimu
pip install -r requirements.txt
```

## 📋 依赖

核心依赖：
- `PySide6` - 图形界面
- `openai-whisper` - 语音识别
- `torch` - 深度学习框架
- `pydub` - 音频处理
- `requests` - HTTP 请求（LLM API）

详见 [requirements.txt](./requirements.txt) 或 [pyproject.toml](./pyproject.toml)

## 🎯 使用场景

### 场景 1: 从零开始创建字幕

```
1. 使用「生成字幕」功能
   - 选择视频文件
   - Whisper 自动识别
   ↓
2. 使用「智能分割」功能（独立启动）
   - 选择生成的字幕
   - LLM 优化断句
   ↓
3. 使用「视频渲染」功能
   - 烧录字幕到视频
   ↓
完成！
```

### 场景 2: 优化现有字幕

```
1. 直接使用「智能分割」功能（独立启动）
   - 选择现有 SRT 文件
   - LLM 重新断句优化
   ↓
完成！
```

### 场景 3: 检查时间戳准确性

```
1. 使用「缓存检查工具」
   - 选择视频文件
   - 点击单词跳转播放
   - 验证时间戳准确性
   ↓
完成！
```

## 🔑 LLM API Key 配置

### 支持的提供商

| 提供商 | 推荐度 | 特点 |
|--------|--------|------|
| SiliconFlow | ★★★★★ | 国内快、价格低 |
| OpenAI | ★★★★☆ | 质量最高 |
| Claude | ★★★★☆ | 高质量、响应快 |
| DeepSeek | ★★★★☆ | 国产、价格低 |

### API Key 获取

- **SiliconFlow**: https://siliconflow.cn/ （推荐）
- **OpenAI**: https://platform.openai.com/api-keys
- **Claude**: https://console.anthropic.com/
- **DeepSeek**: https://platform.deepseek.com/

API Key 会自动保存到 `~/Videos/pyvideotrans/get_srt_zimu/.env`

## 📚 文档

### 快速指南
- [LLM 智能分割快速入门](./LLM_SPLIT_QUICK_START.md) ⭐
- [LLM 智能分割完整说明](./LLM智能分割使用说明.md)

### 技术文档
- [Whisper 迁移说明](./WHISPER_MIGRATION_OPENAI.md)
- [LLM 功能迁移说明](./README_LLM_MIGRATION.md)
- [Faster Whisper 迁移](./FASTER_WHISPER_MIGRATION.md)

### 功能说明
- [完整功能说明](./功能说明.md)
- [视频渲染使用说明](./视频渲染使用说明.md)
- [字幕处理工具说明](../docs/字幕处理工具说明.md)

## 🗂️ 项目结构

```
get_srt_zimu/
├── main.py                    # 主程序入口
├── llm_split.py              # LLM 分割独立启动 ⭐
├── check_whisper_cache.py    # 缓存检查工具
├── ui/                       # 用户界面
│   ├── main_window.py        # 主窗口
│   ├── home_view.py          # 生成字幕
│   ├── split_view.py         # 智能分割
│   ├── process_view.py       # 处理视图
│   └── render_view.py        # 视频渲染
├── utils/                    # 工具模块
│   ├── whisper_processor.py  # Whisper 处理器
│   ├── llm_processor.py      # LLM 处理器
│   ├── fcpxml_generator.py   # FCPXML 生成
│   ├── srt_utils.py          # SRT 工具
│   └── paths.py              # 路径配置
├── models/                   # Whisper 模型
├── resource/                 # 资源文件
└── docs/                     # 文档
```

## 🎨 特色功能

### 词级时间戳缓存
- ✅ Whisper 识别结果自动缓存
- ✅ 避免重复识别同一视频
- ✅ 大幅提升处理速度
- ✅ 可视化检查工具

### LLM 智能分割
- ✅ 基于语义理解的断句
- ✅ 流式输出，实时查看处理过程
- ✅ 精确的时间戳映射
- ✅ 支持多种 LLM 提供商

### 设备支持
- ✅ CPU：所有功能正常
- ✅ CUDA（NVIDIA GPU）：加速支持
- ⚠️ MPS（Apple Silicon）：词级时间戳需用 CPU

## 🔧 系统要求

- Python 3.9+
- macOS / Linux / Windows
- 推荐：16GB+ RAM

### 可选加速
- NVIDIA GPU + CUDA：Whisper 加速
- Apple Silicon：CPU 性能已很好

## 💡 使用技巧

### 技巧 1: 利用缓存加速
第一次处理视频时启用缓存，后续处理同一视频会快 10 倍以上！

### 技巧 2: 选择合适的 LLM
- 快速测试：SiliconFlow + Qwen2.5-7B
- 最终输出：OpenAI GPT-4o
- 大量处理：DeepSeek（性价比高）

### 技巧 3: 独立启动常用功能
不需要每次都打开主界面，直接运行：
```bash
./run_llm_split.sh  # 最常用的智能分割
```

### 技巧 4: 检查时间戳准确性
使用缓存检查工具，点击单词即可跳转播放验证。

## ❓ 常见问题

### Q: 为什么词级时间戳在 Apple Silicon 上用 CPU？
**A:** MPS 不支持 float64，而词级时间戳的 DTW 算法需要 float64。程序会自动使用 CPU 以确保功能正常。Apple Silicon 的 CPU 性能依然很好！

### Q: API Key 保存在哪里？
**A:** `~/Videos/pyvideotrans/get_srt_zimu/.env`

### Q: 如何选择 LLM 提供商？
**A:** 
- 国内用户：SiliconFlow（无需代理，速度快）
- 追求质量：OpenAI GPT-4
- 预算有限：DeepSeek

### Q: 处理速度慢怎么办？
**A:**
- 启用缓存：第二次处理会很快
- 使用 SiliconFlow：通常比 OpenAI 快
- 查看日志了解进度

## 🎉 致谢

本项目基于：
- [OpenAI Whisper](https://github.com/openai/whisper) - 强大的语音识别
- [pyvideotrans](https://github.com/jianchang512/pyvideotrans) - 参考实现

## 📄 许可证

MIT License

---

**开始你的 AI 字幕之旅！** 🚀

有问题？查看 [LLM_SPLIT_QUICK_START.md](./LLM_SPLIT_QUICK_START.md) 获取详细指南。


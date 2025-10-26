# 🚀 LLM智能字幕分割 - 独立启动模式

## 概述

现在你可以**独立启动**LLM智能字幕分割工具，无需启动整个应用！

## 快速开始

### 方式1：使用 uv（推荐）

```bash
cd /Users/mark/Downloads/pyvideotrans
uv run python llm_split.py
```

### 方式2：使用 python

```bash
cd /Users/mark/Downloads/pyvideotrans
python llm_split.py
```

### 方式3：直接运行（macOS/Linux）

```bash
cd /Users/mark/Downloads/pyvideotrans
./llm_split.py
```

## 功能特点

✅ **独立运行**：无需启动完整的视频翻译应用
✅ **快速启动**：3-5秒即可打开窗口
✅ **完整功能**：包含所有LLM智能断句功能
✅ **方便测试**：适合快速测试和调试

## 使用流程

### 1. 启动工具

```bash
uv run python llm_split.py
```

看到输出：
```
============================================================
🤖 LLM智能字幕分割工具
============================================================
工作目录: /Users/mark/Videos/pyvideotrans
输出目录: /Users/mark/Videos/pyvideotrans/SmartSplit
============================================================

正在启动LLM智能字幕分割窗口...
✅ 窗口已打开

使用说明：
1. 选择LLM提供商（推荐：SiliconFlow 或 OpenAI）
2. 输入API Key
3. 选择模型（如：Qwen/Qwen2.5-7B-Instruct 或 gpt-4o-mini）
4. 选择视频文件
5. 可选：勾选'使用现有字幕'并选择.srt文件
6. 点击'开始生成智能字幕'

💡 提示：
   - SiliconFlow: https://siliconflow.cn/ (国内推荐)
   - OpenAI: https://platform.openai.com/api-keys
============================================================
```

### 2. 配置LLM

在打开的窗口中：

**选项1：SiliconFlow（国内推荐）**
- LLM提供商：`SiliconFlow`
- API Key：你的 SiliconFlow API Key
- 模型：`Qwen/Qwen2.5-7B-Instruct`

**选项2：OpenAI**
- LLM提供商：`OpenAI`
- API Key：你的 OpenAI API Key
- 模型：`gpt-4o-mini`

### 3. 选择文件

- 点击"选择视频/音频"
- 选择你的视频文件

**可选：重新分割现有字幕**
- ✅ 勾选"使用现有字幕文件"
- 点击"选择字幕文件(.srt)"
- 选择下载的长句字幕文件

### 4. 开始生成

点击"🎬 开始生成智能字幕"

## 输出位置

生成的字幕文件保存在：
```
/Users/mark/Videos/pyvideotrans/SmartSplit/
```

文件命名：
- 新生成字幕：`视频名_llm_smart.srt`
- 重新分割字幕：`视频名_llm_resplit.srt`

## 与完整应用的区别

| 特性 | 独立模式 | 完整应用 |
|------|---------|---------|
| 启动速度 | ⚡ 快（3-5秒） | 慢（10-15秒） |
| 功能 | 仅LLM字幕分割 | 完整视频翻译功能 |
| 内存占用 | 💚 低 | 中等 |
| 适用场景 | 快速测试、专注字幕处理 | 完整视频制作流程 |

## 命令行参数（未来扩展）

```bash
# 未来可以支持命令行参数
uv run python llm_split.py --video video.mp4 --srt subtitle.srt --provider siliconflow --model Qwen/Qwen2.5-7B-Instruct
```

目前版本暂不支持命令行参数，需要通过GUI配置。

## 常见问题

### Q: 启动失败？

**A:** 确保已安装所有依赖：
```bash
uv pip install -r requirements.txt
```

### Q: 找不到模块？

**A:** 确保在项目根目录运行：
```bash
cd /Users/mark/Downloads/pyvideotrans
uv run python llm_split.py
```

### Q: API Key 保存吗？

**A:** 目前不保存，每次启动需要重新输入。可以在代码中硬编码或使用环境变量：
```bash
export SILICONFLOW_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
```

### Q: 可以不用GUI吗？

**A:** 目前需要GUI。如果需要纯命令行版本，可以参考 `regenerate_subtitles_smart.py`。

## 创建快捷方式

### macOS

创建应用快捷方式：

```bash
cat > ~/Desktop/LLM字幕分割.command << 'EOF'
#!/bin/bash
cd /Users/mark/Downloads/pyvideotrans
uv run python llm_split.py
EOF

chmod +x ~/Desktop/LLM字幕分割.command
```

双击桌面上的"LLM字幕分割.command"即可启动！

### Windows

创建快捷方式：

1. 右键桌面 → 新建 → 快捷方式
2. 目标：
   ```
   C:\Python\python.exe C:\path\to\pyvideotrans\llm_split.py
   ```
3. 名称：`LLM字幕分割`

### Linux

创建桌面文件：

```bash
cat > ~/.local/share/applications/llm-split.desktop << EOF
[Desktop Entry]
Type=Application
Name=LLM字幕分割
Exec=/usr/bin/python3 /path/to/pyvideotrans/llm_split.py
Icon=subtitle
Terminal=true
Categories=AudioVideo;
EOF
```

## 批量处理脚本

如果需要批量处理多个视频，可以创建脚本：

```bash
#!/bin/bash
# batch_llm_split.sh

videos=(
    "/path/to/video1.mp4"
    "/path/to/video2.mp4"
    "/path/to/video3.mp4"
)

for video in "${videos[@]}"; do
    echo "处理: $video"
    # 这里需要实现自动化调用
    # 目前需要手动处理每个视频
done
```

## 开发说明

如果你想修改脚本：

### 文件位置
- 主脚本：`llm_split.py`
- 核心逻辑：`videotrans/winform/fn_llm_split.py`
- UI界面：`videotrans/ui/llmsplit.py`

### 修改配置

编辑 `llm_split.py`：

```python
# 修改默认语言
config.defaulelang = 'en'  # 'zh' 或 'en'

# 修改工作目录
config.HOME_DIR = "/custom/path"
```

### 添加命令行参数

使用 argparse：

```python
import argparse

parser = argparse.ArgumentParser(description='LLM智能字幕分割')
parser.add_argument('--video', help='视频文件路径')
parser.add_argument('--srt', help='现有字幕文件路径')
parser.add_argument('--provider', help='LLM提供商', choices=['openai', 'siliconflow', 'deepseek'])
args = parser.parse_args()
```

## 相关文档

- **完整文档**：`docs/LLM_SMART_SPLIT.md`
- **快速指南**：`LLM_SPLIT_QUICK_START.md`
- **算法说明**：`docs/SMART_SPLIT_ALGORITHM.md`

## 技术支持

遇到问题？
1. 检查日志输出
2. 查看详细文档
3. 确认API Key有效
4. 检查网络连接

---

**享受独立快速的LLM字幕分割！** 🚀✨

## 更新日志

**v1.0.0** (2025-10-26)
- ✅ 初始版本
- ✅ 支持独立启动
- ✅ 完整GUI功能
- ✅ 支持所有LLM提供商

**未来计划**
- [ ] 命令行参数支持
- [ ] 批量处理模式
- [ ] 配置文件保存
- [ ] 进度条和日志文件
- [ ] 自动重试机制


# LLM 智能字幕分割 - 快速启动指南

## 🚀 独立启动

现在你可以直接启动 LLM 智能分割功能，无需打开主界面！

### macOS / Linux

```bash
cd /Users/mark/Downloads/pyvideotrans/get_srt_zimu
./run_llm_split.sh
```

或者直接运行：

```bash
python llm_split.py
```

### Windows

双击运行：
```
run_llm_split.bat
```

或者命令行：
```cmd
python llm_split.py
```

## 📋 两种使用方式

### 方式 1：仅重新分割现有字幕 ⭐推荐入门

这是最简单的方式，适合你已经有字幕文件的情况。

1. **选择字幕文件**
   - 点击 `📂 选择 SRT 文件`
   - 选择你的 `.srt` 字幕文件

2. **配置 LLM**
   - **选择提供商**：推荐 `SiliconFlow`
   - **输入 API Key**：从提供商网站获取
   - **选择模型**：推荐 `Qwen/Qwen2.5-7B-Instruct`

3. **开始处理**
   - 点击 `✨ 开始智能分割`
   - 等待处理完成

4. **查看结果**
   - 输出文件：`原文件名_llm_split.srt`
   - 位置：`~/Videos/pyvideotrans/get_srt_zimu/output/`

### 方式 2：从视频生成 + 智能分割

完整流程：先用 Whisper 识别，再用 LLM 优化。

1. **启用视频生成**
   - 勾选 `从视频生成字幕` ✅

2. **选择视频文件**
   - 点击 `📁 选择视频文件`
   - 选择你的视频文件（mp4, mkv, avi, mov）

3. **可选：使用现有字幕**
   - 勾选 `使用现有字幕` （可选）
   - 选择原字幕文件
   - 这样可以利用缓存，更快完成

4. **配置 Whisper**
   - **语言**：选择视频语言（如 English, Chinese Simplified）
   - **模型大小**：推荐 `large-v3-turbo`
   - **启用缓存**：建议勾选 ✅

5. **配置 LLM**
   - 同方式 1

6. **开始处理**
   - 点击 `✨ 开始智能分割`
   - 等待处理完成

7. **查看结果**
   - 输出文件：
     - 无原字幕：`原文件名_llm_smart.srt`
     - 有原字幕：`原文件名_llm_resplit.srt`
   - 位置：`~/Videos/pyvideotrans/get_srt_zimu/output/`

## 🔑 API Key 获取

### SiliconFlow ⭐推荐

**优势**：国内访问快，价格低廉

1. 访问：https://siliconflow.cn/
2. 注册并登录
3. 进入「API Keys」页面
4. 创建新的 API Key
5. 复制密钥

**推荐模型**：
- `Qwen/Qwen2.5-7B-Instruct` - 平衡性能和质量
- `Qwen/Qwen2.5-72B-Instruct` - 最高质量

### OpenAI

**优势**：质量最高，技术最成熟

1. 访问：https://platform.openai.com/api-keys
2. 创建 API Key
3. 注意：需要国际网络访问

**推荐模型**：
- `gpt-4o-mini` - 性价比高
- `gpt-4o` - 最高质量

### Claude (Anthropic)

**优势**：高质量，响应快

1. 访问：https://console.anthropic.com/
2. 申请 API 访问权限
3. 创建 API Key

**推荐模型**：
- `claude-3-5-sonnet-20241022`

### DeepSeek

**优势**：国产大模型，价格实惠

1. 访问：https://platform.deepseek.com/
2. 注册并创建 API Key

**推荐模型**：
- `deepseek-chat`

## 🎯 功能特性

### 智能断句
- ✅ 基于语义理解，而非简单规则
- ✅ 考虑自然的短语边界
- ✅ 保持句子完整性
- ✅ 优化阅读体验

### 流式输出
- ✅ 实时查看 LLM 处理过程
- ✅ 详细的处理日志
- ✅ 进度追踪

### 自动映射
- ✅ 精确保持时间戳同步
- ✅ 智能词级匹配
- ✅ 插值算法优化

### 缓存机制
- ✅ Whisper 词级时间戳缓存
- ✅ 避免重复识别
- ✅ 大幅提升处理速度

### API 管理
- ✅ 自动保存配置到 `.env`
- ✅ 多提供商独立配置
- ✅ 密码输入模式保护隐私

## 📊 性能参考

| 提供商 | 速度 | 价格 | 质量 | 国内访问 | 推荐度 |
|--------|------|------|------|----------|--------|
| SiliconFlow | ⚡⚡⚡ | 💰 | ⭐⭐⭐⭐ | ✅ | ★★★★★ |
| OpenAI GPT-4 | ⚡⚡ | 💰💰💰 | ⭐⭐⭐⭐⭐ | ❌ | ★★★★☆ |
| Claude | ⚡⚡ | 💰💰 | ⭐⭐⭐⭐⭐ | ❌ | ★★★★☆ |
| DeepSeek | ⚡⚡⚡ | 💰 | ⭐⭐⭐⭐ | ✅ | ★★★★☆ |

## 🗂️ 目录结构

```
~/Videos/pyvideotrans/get_srt_zimu/
├── output/                    # 输出文件
│   ├── *_llm_split.srt       # 重新分割的字幕
│   ├── *_llm_smart.srt       # 智能生成的字幕
│   └── *_llm_resplit.srt     # 基于原字幕重新分割
├── whisper_cache/             # Whisper 缓存
│   └── *.pkl                 # 词级时间戳缓存
└── .env                       # API Key 配置
```

## 🔍 配置文件

API Key 会自动保存到 `~/.env` 文件：

```env
SILICONFLOW_API_KEY=sk-xxx
OPENAI_API_KEY=sk-xxx
CLAUDE_API_KEY=sk-ant-xxx
DEEPSEEK_API_KEY=sk-xxx
```

## ❓ 常见问题

### Q1: API Key 保存在哪里？
**A:** 自动保存到：
- macOS/Linux: `~/Videos/pyvideotrans/get_srt_zimu/.env`
- Windows: `%USERPROFILE%\Videos\pyvideotrans\get_srt_zimu\.env`

### Q2: 如何选择最合适的 LLM？
**A:** 
- **国内用户**：推荐 SiliconFlow（速度快，价格低）
- **追求质量**：OpenAI GPT-4 或 Claude
- **预算有限**：DeepSeek 或 SiliconFlow

### Q3: 处理速度慢怎么办？
**A:**
- LLM 处理需要时间，特别是长字幕
- SiliconFlow 通常比 OpenAI 快
- 可以查看日志区域了解实时进度
- 如果是从视频生成，第一次会较慢（Whisper 识别），后续使用缓存会很快

### Q4: 时间戳不准确怎么办？
**A:**
- 系统使用词级时间戳精确映射
- 如果 LLM 返回的文本与原文差异较大，可能影响映射
- 可以尝试更换模型
- 确保原字幕或 Whisper 识别准确

### Q5: 支持哪些语言？
**A:**
- 支持 LLM 能理解的所有语言
- 中文、英文效果最好
- 其他语言取决于 LLM 的多语言能力

### Q6: 缓存有什么用？
**A:**
- Whisper 词级时间戳会被缓存
- 下次处理同一视频时无需重新识别
- 大幅提升处理速度
- 缓存基于文件内容的 SHA256 哈希

### Q7: 为什么选 SiliconFlow？
**A:**
- ✅ 国内访问无需代理，速度快
- ✅ 价格便宜（约为 OpenAI 的 1/10）
- ✅ 支持众多开源模型（Qwen 系列效果好）
- ✅ 稳定可靠

## 💡 使用技巧

### 技巧 1：利用缓存
如果你要多次优化同一视频的字幕：
1. 第一次：从视频生成，启用缓存
2. 后续：使用现有字幕，选择之前生成的字幕
3. 速度提升 10 倍以上！

### 技巧 2：选择合适的模型
- **快速测试**：SiliconFlow + Qwen2.5-7B
- **最终输出**：OpenAI GPT-4o 或 Claude
- **大量处理**：DeepSeek（价格低）

### 技巧 3：查看实时日志
- 日志区域会显示：
  - LLM 的流式输出（你能看到它"思考"）
  - 时间戳映射过程
  - 处理进度
- 出错时，日志能帮你快速定位问题

### 技巧 4：测试连接
- 输入 API Key 后，使用"测试连接"功能
- 确保配置正确再开始处理
- 避免浪费时间

## 🎬 完整工作流程

### 推荐流程：从视频到优化字幕

```
1. 使用主界面「生成字幕」功能
   - 用 Whisper 生成初始字幕
   - 启用词级时间戳缓存
   ↓
2. 使用独立 LLM 分割工具（本工具）
   - 选择步骤1生成的字幕
   - 或勾选"使用现有字幕"直接从视频处理
   - LLM 优化断句
   ↓
3. 使用主界面「视频渲染」功能
   - 将优化后的字幕烧录到视频
   ↓
4. 完成！🎉
```

## 📚 相关文档

- [完整功能说明](./LLM智能分割使用说明.md)
- [Whisper 迁移说明](./WHISPER_MIGRATION_OPENAI.md)
- [缓存检查工具](./check_whisper_cache.py)

## 🎉 开始使用

准备好了？让我们开始吧！

```bash
# macOS/Linux
./run_llm_split.sh

# 或直接运行
python llm_split.py
```

享受 AI 驱动的智能字幕优化体验！🚀


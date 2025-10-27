# 🚀 LLM智能字幕 - 5分钟快速上手

## 你遇到的问题

从网上下载的字幕：
```
❌ 每句超长（15-20秒）
❌ 渲染时显示3-5行
❌ 严重影响观感
```

使用纯规则引擎分割：
```
❌ "Thousands of people coming"          ← 在动词后断开
❌ "joyfully together to create a"       ← 在冠词后断开
❌ "mile-long, beautiful, playful"       ← 语义不完整
```

## 解决方案：LLM智能断句

使用AI理解语义，生成专业级字幕：
```
✅ "Thousands of people coming joyfully together"
✅ "to create a mile-long beautiful spectacle"
✅ "for themselves and their community"
```

## 快速开始（3步）

### 第1步：获取API Key (2分钟)

**推荐选项1：SiliconFlow（国内推荐）** ⭐

1. 访问：https://siliconflow.cn/
2. 注册/登录账号
3. 进入控制台 → API Keys
4. 创建并复制API Key

💰 **成本**：约 ¥0.002-0.005 / 10分钟视频（超便宜！）
✅ **优势**：国内访问快，无需科学上网

**推荐选项2：OpenAI（国际推荐）**

1. 访问：https://platform.openai.com/api-keys
2. 注册/登录账号
3. 点击 "Create new secret key"
4. 复制API Key：`sk-proj-xxxxx...`

💰 **成本**：约 $0.001-0.003 / 10分钟视频

**其他选项**：
- **DeepSeek**（国产便宜）：https://platform.deepseek.com/
- **Anthropic Claude**：https://console.anthropic.com/
- **免费本地模型**：使用 Ollama（需要好的GPU）

### 第2步：配置工具 (1分钟)

1. 打开 **"🤖 LLM智能字幕生成"** 工具

2. 配置LLM：
   - LLM提供商：`OpenAI` ✅
   - API Key：粘贴你的Key
   - 模型：`gpt-4o-mini` ✅（最便宜）
   - Base URL：留空

3. 选择视频/音频文件

4. **（重点）如果要重新分割下载的字幕**：
   - ✅ 勾选 "使用现有字幕文件"
   - 选择你下载的 .srt 文件

### 第3步：生成字幕 (2分钟+)

点击 **"🎬 开始生成智能字幕"**

处理流程：
```
1. Whisper识别语音 → 获取词级时间戳
2. LLM理解语义 → 智能断句
3. 生成最终字幕 → 保存到 SmartSplit 目录
```

完成！🎉

## 效果对比

### 原始下载的字幕
```
1
00:00:00,000 --> 00:00:20,317
Transcriber: Phương Tú Lê Reviewer: Maxime Sobrier Bringing people together these days is a feat. Thousands of people coming joyfully together to create a mile long, beautiful,

问题：一句话20秒，渲染时显示4-5行！
```

### LLM智能断句后
```
1
00:00:00,000 --> 00:00:03,500
Transcriber: Phương Tú Lê
Reviewer: Maxime Sobrier

2
00:00:03,500 --> 00:00:06,800
Bringing people together these days is a feat.

3
00:00:06,800 --> 00:00:10,500
Thousands of people coming joyfully together

4
00:00:10,500 --> 00:00:14,200
to create a mile-long beautiful spectacle

完美：每句3-5秒，渲染时显示1-2行！
```

## 常见问题

### Q: 为什么比规则引擎好？

**A:** 
- 规则引擎：机械地按时长/词数断开，不懂语义
- LLM：理解完整语义，像人一样断句

**示例**：
```
规则引擎："together to create a"     ← 在冠词后断开❌
LLM："together to create a beautiful spectacle" ← 完整短语✅
```

### Q: 成本如何？

**A:** 非常便宜！
- 10分钟视频 ≈ $0.001-0.003 (使用gpt-4o-mini)
- 1小时视频 ≈ $0.01-0.02
- 比一杯咖啡还便宜！

### Q: 可以完全免费吗？

**A:** 可以！使用本地模型：
```bash
# 安装 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 运行模型
ollama run llama3

# 配置
LLM提供商：Local
模型：llama3
Base URL：http://localhost:11434/api/generate
```

### Q: 处理时间多久？

**A:** 
- 5分钟视频 ≈ 2-3分钟处理
- 主要时间在Whisper识别（和不用LLM一样）
- LLM断句只增加 20-30秒

### Q: 支持哪些语言？

**A:** 所有Whisper支持的语言：
- 英文、中文、日文、韩文
- 西班牙语、法语、德语、俄语
- 等100+种语言

### Q: 如何选择模型？

**推荐配置**：

| 场景 | 提供商 | 模型 | 成本 |
|------|--------|------|------|
| 🏆 **最佳性价比** | OpenAI | gpt-4o-mini | ~$0.002/10分钟 |
| 💎 **最高质量** | Anthropic | claude-3-5-sonnet | ~$0.05/10分钟 |
| 💰 **最便宜** | DeepSeek | deepseek-chat | ~¥0.01/10分钟 |
| 🆓 **完全免费** | Local | llama3/qwen | $0 |

### Q: LLM会改变字幕文本吗？

**A:** 不会！
- 如果使用"现有字幕"模式，会尽量保留原文
- LLM只决定**在哪里断句**
- 时间戳来自Whisper的词级识别，非常精确

## 参数建议

### 标准配置（推荐）
```
语言：en (或根据实际)
Whisper模型：large-v3-turbo
最大持续时间：5秒
最大词数：15词
LLM提供商：OpenAI
LLM模型：gpt-4o-mini
```

### 快节奏视频
```
最大持续时间：3-4秒
最大词数：10-12词
```

### 慢节奏/教育视频
```
最大持续时间：6-7秒
最大词数：18-20词
```

## 两种使用模式

### 模式1：从视频生成新字幕
```
1. 选择视频文件
2. 不勾选"使用现有字幕"
3. 开始生成
→ 完全由AI生成字幕
```

### 模式2：重新分割下载的字幕（推荐）
```
1. 选择视频文件
2. ✅ 勾选"使用现有字幕"
3. 选择下载的.srt字幕文件
4. 开始生成
→ 保留准确文本，只重新断句
```

**推荐使用模式2**：
- 文本准确性更高（来自专业翻译）
- 只需要AI重新断句
- 效果最好

## 故障排除

### ❌ API Key错误
```
错误：401 Unauthorized
解决：检查API Key是否正确，确认有余额
```

### ❌ 网络连接失败
```
错误：Connection timeout
解决：
1. 检查网络连接
2. 使用Base URL配置代理
3. 或使用本地模型（免费）
```

### ❌ LLM返回格式错误
```
错误：LLM返回格式错误，回退到规则引擎
解决：使用更强的模型（如gpt-4o代替gpt-3.5）
```

## 下一步

1. ✅ **立即尝试**：用你手头的视频测试
2. 📖 **深入了解**：阅读 [LLM_SMART_SPLIT.md](docs/LLM_SMART_SPLIT.md)
3. ⚙️  **优化参数**：根据视频类型调整配置
4. 🚀 **批量处理**：处理更多视频

## 技术支持

遇到问题？
1. 查看详细文档：`docs/LLM_SMART_SPLIT.md`
2. 检查日志输出：工具会显示详细的处理日志
3. 尝试不同的LLM提供商和模型

---

**开始享受专业级AI字幕！** 🤖✨

**记住**：
- ✅ 使用 gpt-4o-mini（便宜且效果好）
- ✅ 对下载的字幕使用"现有字幕"模式
- ✅ 默认参数就很好，不需要过多调整


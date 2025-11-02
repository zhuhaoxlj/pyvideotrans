# 🎬 LLM 智能分割 - 实战演示

## 🚀 5 分钟快速上手

### 第一步：启动程序

```bash
cd /Users/mark/Downloads/pyvideotrans/get_srt_zimu
./run_llm_split.sh
```

或者直接：

```bash
python llm_split.py
```

### 第二步：选择文件

**场景 A：优化现有字幕**（最简单）

1. 点击 `📂 选择 SRT 文件`
2. 选择你的字幕文件，例如：
   ```
   /Users/mark/Videos/pyvideotrans/get_srt_zimu/output/666_word_based.srt
   ```

**场景 B：从视频生成**（完整流程）

1. 勾选 `从视频生成字幕` ✅
2. 点击 `📁 选择视频文件`
3. 选择视频，例如：
   ```
   /Users/mark/Downloads/666.mp4
   ```

### 第三步：配置 LLM

#### 推荐配置（SiliconFlow）

1. **提供商**：选择 `SiliconFlow`
2. **API Key**：
   - 访问：https://siliconflow.cn/
   - 注册并获取 API Key
   - 粘贴到输入框：`sk-xxxxxxxxxx`
3. **模型**：保持默认 `Qwen/Qwen2.5-7B-Instruct`

#### 测试连接（可选但推荐）

点击 `🔌 测试 LLM 连接` 按钮，确保配置正确。

### 第四步：开始处理

点击 `✨ 开始智能分割` 按钮！

### 第五步：查看结果

处理完成后：

1. 界面会弹出提示
2. 点击 `📂 打开输出文件夹` 查看结果
3. 输出文件位于：
   ```
   ~/Videos/pyvideotrans/get_srt_zimu/output/
   ```

## 📖 实战示例

### 示例 1：优化你刚生成的 666.mp4 字幕

假设你已经在主界面生成了 `666_word_based.srt`：

```bash
# 1. 启动 LLM 分割工具
./run_llm_split.sh

# 2. 在界面中：
点击 [📂 选择 SRT 文件]
选择：/Users/mark/Downloads/pyvideotrans/get_srt_zimu/resource/666_word_based.srt

# 3. 配置 LLM：
提供商：SiliconFlow
API Key：sk-your-key-here
模型：Qwen/Qwen2.5-7B-Instruct

# 4. 点击 [✨ 开始智能分割]

# 5. 等待处理...查看日志区域了解进度

# 6. 完成！
输出文件：~/Videos/pyvideotrans/get_srt_zimu/output/666_llm_split.srt
```

### 示例 2：从视频直接处理（利用缓存）

如果你之前生成过 666.mp4 的字幕（启用了缓存）：

```bash
# 1. 启动工具
./run_llm_split.sh

# 2. 在界面中：
勾选 [✅ 从视频生成字幕]
点击 [📁 选择视频文件]
选择：/Users/mark/Downloads/666.mp4

勾选 [✅ 使用现有字幕]
点击 [📂 选择原 SRT 字幕]
选择：/Users/mark/Downloads/pyvideotrans/get_srt_zimu/resource/666_word_based.srt

# 3. 配置 Whisper（会使用缓存，很快）：
语言：English
模型：large-v3-turbo
启用缓存：✅

# 4. 配置 LLM（同上）

# 5. 点击 [✨ 开始智能分割]

# 6. 完成！
输出文件：~/Videos/pyvideotrans/get_srt_zimu/output/666_llm_resplit.srt

# 注意：因为使用了缓存，Whisper 部分会秒级完成！
```

## 🎯 日志解读

处理过程中，你会在日志区域看到：

```
📂 Step 1: 加载字幕文件...
   ✓ 成功加载 123 条字幕
   ✓ 总时长: 05:23

🤖 Step 2: 调用 LLM 进行智能分割...
   提供商: siliconflow
   模型: Qwen/Qwen2.5-7B-Instruct
   
   ⏳ 正在等待 LLM 响应...
   
   🎤 LLM 流式输出:
   [这里会显示 LLM 的实时输出...]
   
🔄 Step 3: 映射时间戳...
   ✓ 成功映射 98 个分段
   ✓ 匹配率: 100.0%
   
💾 Step 4: 保存结果...
   ✓ 输出文件: /path/to/output.srt
   
✅ 全部完成！
```

## 💡 常见问题实战

### Q: 看到 "API Key 无效"？

```bash
# 检查清单：
1. API Key 是否正确复制（没有多余空格）
2. 提供商是否选对（SiliconFlow vs OpenAI）
3. 账户是否有余额
4. 使用 [🔌 测试 LLM 连接] 验证
```

### Q: 处理很慢？

```bash
# 正常情况：
- 第一次处理视频：较慢（Whisper 识别 + LLM 分割）
- 使用现有字幕：快速（仅 LLM 分割）
- 利用缓存：超快（秒级 + LLM 分割）

# 加速技巧：
1. 使用 SiliconFlow（比 OpenAI 快）
2. 启用 Whisper 缓存
3. 查看日志了解哪个步骤慢
```

### Q: 时间戳不准？

```bash
# 检查方法：
1. 使用缓存检查工具验证原始时间戳：
   python check_whisper_cache.py
   
2. 查看日志中的"匹配率"
   - 100%：完美
   - 95%+：很好
   - <90%：可能有问题

3. 尝试不同的 LLM 模型
```

## 🎬 完整工作流演示

### 场景：从视频到完美字幕

```bash
# ========================================
# 第 1 步：生成初始字幕（主界面）
# ========================================
1. 打开主界面：./run.sh
2. 选择视频：666.mp4
3. 配置：Large-v3-Turbo, English, 启用缓存 ✅
4. 生成字幕
   输出：666_word_based.srt

# ========================================
# 第 2 步：LLM 智能优化（独立工具）
# ========================================
1. 启动 LLM 工具：./run_llm_split.sh
2. 选择字幕：666_word_based.srt
3. 配置 LLM：SiliconFlow + Qwen2.5-7B
4. 开始分割
   输出：666_llm_split.srt

# ========================================
# 第 3 步：验证时间戳（可选）
# ========================================
1. 运行检查工具：python check_whisper_cache.py
2. 选择视频：666.mp4
3. 点击单词验证时间戳准确性

# ========================================
# 第 4 步：渲染到视频（主界面）
# ========================================
1. 打开主界面（如果已关闭）
2. 切换到"视频渲染"标签
3. 选择视频和优化后的字幕
4. 渲染
   输出：666_with_subtitles.mp4

# ========================================
# 完成！🎉
# ========================================
```

## 🔧 高级技巧

### 技巧 1：批量处理多个字幕

```bash
# 创建一个简单的批处理脚本
for srt in *.srt; do
  echo "处理: $srt"
  # 这里可以通过命令行参数传递
  # 或者手动逐个处理
done
```

### 技巧 2：对比不同 LLM 的效果

```bash
# 1. 用 SiliconFlow 处理一次
输出：666_llm_split_silicon.srt

# 2. 用 OpenAI 处理一次
输出：666_llm_split_openai.srt

# 3. 对比两个文件，选择更好的
```

### 技巧 3：保存 API Key 到环境变量

```bash
# 编辑 ~/.zshrc 或 ~/.bashrc
export SILICONFLOW_API_KEY="sk-your-key"
export OPENAI_API_KEY="sk-your-key"

# 程序会自动从环境变量读取
```

## 📊 性能参考

基于 666.mp4（约 1 分钟视频）：

| 步骤 | 时间 | 说明 |
|-----|------|------|
| Whisper 识别 | ~30-60秒 | 第一次 |
| Whisper（缓存） | <1秒 | 使用缓存 |
| LLM 分割 | ~10-30秒 | 取决于提供商 |
| 时间戳映射 | <1秒 | 自动完成 |

## 🎉 开始实战

准备好了吗？开始你的第一次智能分割：

```bash
cd /Users/mark/Downloads/pyvideotrans/get_srt_zimu
./run_llm_split.sh
```

跟着界面提示操作，享受 AI 驱动的智能字幕优化！🚀

---

**有问题？** 查看 [LLM_SPLIT_QUICK_START.md](./LLM_SPLIT_QUICK_START.md) 获取更多帮助。


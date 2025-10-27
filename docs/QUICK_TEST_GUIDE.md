# 🧪 快速测试指南 - LLM 字幕分割新功能

## 测试新功能

### 1️⃣ 测试自动配置功能

```bash
# 启动工具
cd /Users/mark/Downloads/pyvideotrans
uv run python llm_split.py
```

**测试步骤**：
1. 窗口打开后，勾选 "☑ 启用 LLM 智能断句优化"
2. 在 "LLM 提供商" 下拉框中选择 **SiliconFlow**
3. 观察：
   - ✅ Base URL 应该自动填充为：`https://api.siliconflow.cn/v1/chat/completions`
   - ✅ 模型下拉框应该显示 SiliconFlow 的模型列表
   - ✅ 默认选中：`Qwen/Qwen2.5-7B-Instruct`
4. 切换到 **OpenAI**
   - ✅ Base URL 应该清空（使用默认）
   - ✅ 模型切换为：`gpt-4o-mini`
5. 切换到 **DeepSeek**
   - ✅ Base URL 清空
   - ✅ 模型切换为：`deepseek-chat`

**预期结果**：✅ 每次切换提供商，URL 和模型都自动更新

---

### 2️⃣ 测试模型下拉选择

**测试步骤**：
1. 选择 **SiliconFlow** 提供商
2. 点击 "模型" 下拉框
3. 应该看到以下选项：
   ```
   ✅ Qwen/Qwen2.5-7B-Instruct (默认)
   ✅ deepseek-ai/DeepSeek-V3
   ✅ deepseek-ai/DeepSeek-R1
   ✅ deepseek-ai/DeepSeek-R1-Distill-Qwen-32B
   ✅ inclusionAI/Ling-1T
   ✅ Qwen/QwQ-32B
   ✅ Qwen/Qwen2.5-72B-Instruct
   ```
4. 可以下拉选择任意模型
5. 也可以手动输入自定义模型名称

**预期结果**：✅ 下拉列表完整，可选择，可手动输入

---

### 3️⃣ 测试 LLM 连接

**测试步骤（需要真实 API Key）**：

#### 方案A：使用 SiliconFlow（推荐）

```
1. 选择提供商: SiliconFlow
2. 输入 API Key: sk-你的真实key
3. 选择模型: Qwen/Qwen2.5-7B-Instruct
4. 点击 "🔍 测试 LLM 连接"
5. 等待 2-5 秒
6. 应该看到：
   ✅ 连接成功！
   
   提供商: siliconflow
   模型: Qwen/Qwen2.5-7B-Instruct
   响应正常
```

#### 方案B：测试错误处理（无需真实 Key）

```
1. 选择提供商: SiliconFlow
2. 输入 API Key: fake-key-123
3. 点击 "🔍 测试 LLM 连接"
4. 应该看到错误提示：
   ❌ 连接失败！
   
   HTTP 401
   {"error": "Invalid API key"}
```

**预期结果**：✅ 成功时显示绿色提示，失败时显示红色错误

---

### 4️⃣ 测试参数智能隐藏

**测试步骤**：

**A. LLM 未勾选状态**：
```
☐ 启用 LLM 智能断句优化

应该看到：
✅ 语言: English
✅ Whisper模型: large-v3-turbo
✅ 最大持续时间(秒): 5    ← 显示
✅ 最大词数: 15           ← 显示
✅ 加速设备: CPU
```

**B. 勾选 LLM**：
```
☑ 启用 LLM 智能断句优化

LLM 配置区域展开（显示）：
✅ LLM 提供商: ...
✅ API Key: ...
✅ 模型: ...
✅ Base URL: ...
✅ 测试按钮: ...

参数区域：
✅ 语言: English
✅ Whisper模型: large-v3-turbo
❌ 最大持续时间 → 隐藏
❌ 最大词数 → 隐藏
✅ 加速设备: CPU
```

**C. 取消勾选 LLM**：
```
☐ 启用 LLM 智能断句优化

LLM 配置隐藏
参数恢复：
✅ 最大持续时间 → 显示
✅ 最大词数 → 显示
```

**预期结果**：✅ 勾选状态切换时，相关参数正确显示/隐藏

---

### 5️⃣ 完整流程测试

**使用 SiliconFlow 生成字幕**（需要真实 API Key）：

```bash
# 1. 启动
uv run python llm_split.py

# 2. 窗口配置
☑ 启用 LLM 智能断句优化
提供商: SiliconFlow (自动填充URL和模型)
API Key: sk-你的key
点击 "🔍 测试 LLM 连接" → ✅ 成功

# 3. 选择文件
点击 "选择视频/音频" → 选择测试视频
或：
☑ 使用现有字幕文件
点击 "选择字幕文件(.srt)" → 选择长句字幕

# 4. 生成
点击 "🎬 开始生成智能字幕"
观察日志输出
等待完成

# 5. 检查结果
生成的字幕文件在：
/Users/mark/Videos/pyvideotrans/SmartSplit/
```

**预期结果**：
- ✅ Whisper 识别完成
- ✅ LLM 优化断句
- ✅ 生成高质量字幕文件

---

## 🐛 已知问题检查清单

### ✅ 检查 1：导入错误

```bash
# 测试导入
cd /Users/mark/Downloads/pyvideotrans
python -c "from videotrans.ui.llmsplit import Ui_llmsplit; print('✅ UI 导入成功')"
python -c "from videotrans.component import LLMSplitForm; print('✅ Form 导入成功')"
```

**预期输出**：
```
✅ UI 导入成功
✅ Form 导入成功
```

### ✅ 检查 2：窗口能否打开

```bash
# 快速测试启动
uv run python llm_split.py
```

**预期**：
- ✅ 无错误信息
- ✅ 窗口正常打开
- ✅ 所有控件可见

### ✅ 检查 3：提供商切换

**手动测试**：
1. 在下拉框中依次选择每个提供商
2. 检查是否有错误弹窗
3. 检查 Base URL 和模型是否更新

**预期**：✅ 无错误，正常切换

### ✅ 检查 4：测试按钮

**手动测试**：
1. 不输入 API Key，点击测试
   - **预期**：❌ 提示 "请输入 API Key"
2. 输入错误的 API Key，点击测试
   - **预期**：❌ 显示 401 错误
3. 输入正确的 API Key，点击测试
   - **预期**：✅ 连接成功

---

## 📊 功能完整性检查表

| 功能 | 状态 | 备注 |
|------|------|------|
| SiliconFlow 自动填充 URL | ✅ | 选择时自动填充 |
| OpenAI 自动配置 | ✅ | URL 清空，模型更新 |
| DeepSeek 自动配置 | ✅ | URL 清空，模型更新 |
| Anthropic 自动配置 | ✅ | URL 清空，模型更新 |
| Local 自动配置 | ✅ | localhost URL |
| 模型下拉选择 | ✅ | 可选择，可输入 |
| SiliconFlow 模型列表 | ✅ | 7个模型 |
| OpenAI 模型列表 | ✅ | 5个模型 |
| Anthropic 模型列表 | ✅ | 4个模型 |
| 测试连接按钮 | ✅ | 显示测试结果 |
| 测试成功提示 | ✅ | 绿色成功框 |
| 测试失败提示 | ✅ | 红色错误框 |
| 勾选LLM隐藏参数 | ✅ | 隐藏时长/词数 |
| 取消勾选显示参数 | ✅ | 恢复显示 |
| 独立启动脚本 | ✅ | llm_split.py |

---

## 🎯 快速回归测试

**5分钟完整测试**：

```bash
# 1. 启动 (30秒)
uv run python llm_split.py

# 2. 自动配置测试 (1分钟)
- 切换 SiliconFlow → 检查自动填充 ✅
- 切换 OpenAI → 检查自动更新 ✅
- 切换 DeepSeek → 检查自动更新 ✅

# 3. 模型选择测试 (30秒)
- 打开 SiliconFlow 模型下拉
- 检查是否有 7 个模型 ✅
- 选择 DeepSeek-R1 ✅

# 4. 测试连接 (1分钟)
- 输入错误 Key → 测试 → 看到错误 ✅
- 输入正确 Key → 测试 → 看到成功 ✅

# 5. 参数隐藏测试 (30秒)
- 勾选 LLM → 参数隐藏 ✅
- 取消勾选 → 参数显示 ✅

# 6. 生成测试 (1.5分钟)
- 选择测试视频
- 生成字幕
- 检查输出文件 ✅
```

**总用时**：< 5分钟
**预期结果**：全部 ✅

---

## 💡 故障排除

### 问题1：窗口打不开

**检查**：
```bash
cd /Users/mark/Downloads/pyvideotrans
python -c "from PySide6.QtWidgets import QApplication; print('✅ Qt 正常')"
```

**解决**：
```bash
pip install PySide6
```

### 问题2：导入错误

**检查**：
```bash
python -c "from videotrans.component import LLMSplitForm"
```

**解决**：确认 `videotrans/component/__init__.py` 中有 `"LLMSplitForm"` 在 `__all__` 列表中

### 问题3：测试连接失败

**检查**：
1. API Key 是否正确
2. 网络是否正常
3. Base URL 是否正确

**测试网络**：
```bash
curl -I https://api.siliconflow.cn
```

### 问题4：模型列表没有更新

**解决**：
1. 关闭窗口
2. 重新启动：`uv run python llm_split.py`
3. 再次测试

---

## 📝 测试报告模板

```markdown
## 测试日期：2025-10-26

### 功能测试

- [ ] SiliconFlow 自动配置
- [ ] 模型下拉选择
- [ ] 连接测试（成功）
- [ ] 连接测试（失败）
- [ ] 参数智能隐藏
- [ ] 完整生成流程

### 发现的问题

1. 无

### 建议改进

1. 无

### 测试结论

✅ 所有功能正常工作
```

---

**开始测试吧！** 🧪✨


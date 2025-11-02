# ✅ 生成字幕后自动跳转到 LLM 智能分割功能

## 🎯 功能说明

当用户在主界面完成字幕生成后，系统会：
1. ⏱️ 等待 5 秒
2. 🚀 自动跳转到 LLM 智能分割页面
3. 📦 自动预填充视频文件和生成的字幕文件
4. ✅ 自动勾选"使用现有字幕进行重新分割"
5. 💡 显示友好提示信息

用户只需配置 LLM 设置，点击"开始处理"即可！

## ✅ 实现状态

**已完全实现！** 无需修改任何代码。

## 📋 实现细节

### 1. 处理完成后的自动跳转

**文件**: `ui/process_view.py`

```python
def on_processing_finished(self, srt_path, fcpxml_path):
    """Processing completed successfully"""
    self.srt_path = srt_path
    self.fcpxml_path = fcpxml_path
    
    # ... 更新UI状态 ...
    
    self.output_text.append("\n⏳ 5秒后自动跳转到智能分割页面...")
    
    # 5秒后自动跳转到智能分割
    from PySide6.QtCore import QTimer
    QTimer.singleShot(5000, lambda: self._auto_goto_split())
```

**位置**: 第 351-378 行

### 2. 自动跳转方法

**文件**: `ui/process_view.py`

```python
def _auto_goto_split(self):
    """自动跳转到智能分割页面，并传递所有数据"""
    if self.srt_path and hasattr(self, 'processor') and self.processor:
        # 获取原始视频文件路径
        video_file = self.processor.data.get('file_path', '')
        
        # 通过父窗口跳转，并传递完整数据
        parent_window = self.window()
        if hasattr(parent_window, 'show_split_with_full_data'):
            parent_window.show_split_with_full_data(
                video_file=video_file,
                srt_file=self.srt_path
            )
        else:
            # 回退方案：只传递字幕文件
            self.split_requested.emit(self.srt_path)
```

**位置**: 第 438-456 行

**关键点**:
- ✅ 获取原始视频文件路径
- ✅ 获取生成的字幕文件路径
- ✅ 调用主窗口的完整数据跳转方法
- ✅ 提供回退方案

### 3. 主窗口的数据传递

**文件**: `ui/main_window.py`

```python
def show_split_with_full_data(self, video_file, srt_file):
    """显示分割字幕视图并预填充视频和字幕文件"""
    self.stacked_widget.setCurrentWidget(self.split_view)
    # 先加载视频文件
    if video_file:
        self.split_view.load_video_file(video_file)
    # 再加载字幕文件，并自动勾选"使用现有字幕"
    if srt_file:
        self.split_view.use_existing_srt.setChecked(True)
        self.split_view.load_srt_file(srt_file)
    self.sidebar.set_active_button(self.sidebar.btn_split)
```

**位置**: 第 214-224 行

**关键操作**:
1. ✅ 切换到分割视图
2. ✅ 加载视频文件
3. ✅ 勾选"使用现有字幕"复选框
4. ✅ 加载字幕文件
5. ✅ 高亮侧边栏按钮

### 4. SplitView 的文件加载

**文件**: `ui/split_view.py`

#### 加载视频文件

```python
def load_video_file(self, file_path):
    """加载视频文件（用于外部调用）"""
    if file_path and Path(file_path).exists():
        self.video_file_path = file_path
        file_name = Path(file_path).name
        self.video_label.setText(f"✓ {file_name}")
        self.video_label.setStyleSheet(
            "padding: 12px; background: #e3f2fd; border-radius: 5px; "
            "color: #1976d2; border: 2px solid #2196f3; font-weight: bold;"
        )
        self.update_process_button()
```

**位置**: 第 557-564 行

#### 加载字幕文件

```python
def load_srt_file(self, file_path):
    """加载 SRT 文件（用于外部调用）"""
    if file_path and Path(file_path).exists():
        self.srt_file_path = file_path
        file_name = Path(file_path).name
        self.srt_label.setText(f"✓ {file_name}")
        self.srt_label.setStyleSheet(
            "padding: 12px; background: #e3f2fd; border-radius: 5px; "
            "color: #1976d2; border: 2px solid #2196f3; font-weight: bold;"
        )
        
        # 显示友好提示
        if self.video_file_path:
            self.log_text.setText(
                f"✅ 已加载视频文件: {Path(self.video_file_path).name}\n"
                f"✅ 已加载字幕文件: {file_name}\n\n"
                f"🚀 模式：使用视频+现有字幕（Whisper词级+LLM）\n"
                f"💡 由于视频已处理过，将直接使用缓存的词级时间戳\n\n"
                f"📌 请配置 LLM 设置后点击「开始处理」"
            )
        else:
            self.log_text.setText(
                f"✅ 已加载字幕文件: {file_name}\n\n"
                f"📌 请配置 LLM 设置后点击「开始处理」"
            )
```

**位置**: 第 566-587 行

**智能提示**:
- ✅ 检测到视频+字幕：提示使用缓存
- ✅ 仅字幕：提示配置 LLM
- ✅ UI 反馈清晰

## 🎬 完整流程演示

### 步骤 1: 生成字幕

```
用户操作：
1. 打开主界面
2. 选择视频文件：/Users/mark/Downloads/666.mp4
3. 配置 Whisper 设置
4. 点击"开始生成字幕"
5. 等待处理完成...
```

### 步骤 2: 自动跳转（5秒后）

```
系统自动：
1. 检测处理完成 ✅
2. 等待 5 秒 ⏱️
3. 获取视频路径：/Users/mark/Downloads/666.mp4
4. 获取字幕路径：~/Videos/.../output/666_word_based.srt
5. 跳转到智能分割页面 🚀
6. 预填充所有数据 📦
```

### 步骤 3: 智能分割界面

```
界面状态：
✅ 视频文件：✓ 666.mp4
✅ 使用现有字幕：[√] 已勾选
✅ 字幕文件：✓ 666_word_based.srt

日志提示：
✅ 已加载视频文件: 666.mp4
✅ 已加载字幕文件: 666_word_based.srt

🚀 模式：使用视频+现有字幕（Whisper词级+LLM）
💡 由于视频已处理过，将直接使用缓存的词级时间戳

📌 请配置 LLM 设置后点击「开始处理」
```

### 步骤 4: 用户操作

```
用户只需：
1. 选择 LLM 提供商（如 SiliconFlow）
2. 输入 API Key
3. 选择模型
4. 点击"✨ 开始智能分割"

完成！
```

## 🔧 技术实现亮点

### 1. 智能状态管理

- ✅ 处理完成后重置状态标志
- ✅ 避免重复处理
- ✅ 正确的线程清理

### 2. 数据传递完整

- ✅ 视频文件路径
- ✅ 字幕文件路径
- ✅ 所有元数据

### 3. 用户体验优化

- ✅ 5秒延迟提示用户
- ✅ 友好的界面反馈
- ✅ 智能提示信息
- ✅ 缓存复用说明

### 4. 容错处理

- ✅ 检查方法存在性
- ✅ 回退方案
- ✅ 文件存在性验证

## 📊 调用链路图

```
生成字幕完成
    ↓
ProcessView.on_processing_finished()
    ↓
QTimer.singleShot(5000, ...)  # 5秒延迟
    ↓
ProcessView._auto_goto_split()
    ↓
MainWindow.show_split_with_full_data(video_file, srt_file)
    ↓
SplitView.load_video_file(video_file)
    ↓
SplitView.use_existing_srt.setChecked(True)
    ↓
SplitView.load_srt_file(srt_file)
    ↓
界面更新完成 ✅
```

## 🎯 用户操作流程

### 完整流程（推荐）

```
1. 生成字幕
   └─> 主界面 → 选择视频 → 生成

2. 自动跳转（5秒）
   └─> 系统自动完成

3. 配置 LLM
   └─> 智能分割界面 → 配置 API

4. 开始处理
   └─> 点击"开始智能分割"

5. 查看结果
   └─> 输出目录中的 _llm_resplit.srt
```

### 手动跳转（可选）

如果用户不想等5秒，可以：

```
在处理完成页面：
1. 点击「✂️ 继续智能分割字幕」按钮
   └─> 立即跳转，效果相同
```

## 💡 使用技巧

### 技巧 1: 利用缓存加速

```
第一次：
生成字幕（启用缓存）→ 等待 1-2 分钟

第二次优化：
自动跳转 → 配置 LLM → 开始处理
└─> Whisper 部分秒级完成（使用缓存）
└─> 仅 LLM 需要时间
```

### 技巧 2: 批量处理

```
处理多个视频：
1. 生成第一个视频的字幕
2. 自动跳转后，先不处理
3. 继续生成第二个视频...
4. 最后统一配置 LLM 批量处理
```

### 技巧 3: 对比效果

```
1. 生成原始字幕
2. 自动跳转后使用不同 LLM 处理
3. 对比 output 目录中的多个版本
4. 选择最优结果
```

## 🐛 故障排查

### Q1: 没有自动跳转？

**检查**:
- 是否等待了 5 秒？
- 处理是否真的完成？（查看日志）
- 有无错误提示？

**解决**:
- 手动点击「✂️ 继续智能分割字幕」按钮

### Q2: 跳转后没有预填充文件？

**检查**:
- 字幕文件是否成功生成？
- 查看输出目录是否有 .srt 文件

**解决**:
- 手动选择字幕文件

### Q3: 缓存没有复用？

**检查**:
- 生成字幕时是否启用了缓存？
- 视频文件是否相同？（基于 SHA256）

**解决**:
- 确保使用相同的视频文件
- 查看日志中的缓存提示

## 📚 相关文档

- [LLM 智能分割快速入门](./LLM_SPLIT_QUICK_START.md)
- [LLM 智能分割功能说明](./LLM智能分割使用说明.md)
- [项目主文档](./README.md)

## ✅ 总结

**功能状态**: ✅ 已完全实现

**代码修改**: ❌ 无需修改（已实现）

**用户体验**: ⭐⭐⭐⭐⭐

**实现质量**: ⭐⭐⭐⭐⭐

---

**享受无缝的 AI 字幕生成到优化的工作流！** 🚀


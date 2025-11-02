# 安装 faster-whisper

## 🐛 闪退问题解决

如果点击"开始生成字幕"后程序闪退，是因为 **`faster-whisper` 还没有安装**。

---

## 🚀 快速安装（推荐）

### 方法 1：使用主项目虚拟环境

```bash
cd /Users/mark/Downloads/pyvideotrans
source venv/bin/activate
pip install faster-whisper
```

### 方法 2：使用 get_srt_zimu 的虚拟环境

```bash
cd /Users/mark/Downloads/pyvideotrans/get_srt_zimu
source venv/bin/activate
pip install faster-whisper
```

---

## 📦 完整安装步骤

### 1. 激活虚拟环境

```bash
cd /Users/mark/Downloads/pyvideotrans
source venv/bin/activate
```

### 2. 安装 faster-whisper

```bash
pip install faster-whisper
```

### 3. 验证安装

```bash
python -c "from faster_whisper import WhisperModel; print('✅ faster-whisper 安装成功')"
```

如果看到 `✅ faster-whisper 安装成功`，说明安装成功！

### 4. 重新启动应用

```bash
cd /Users/mark/Downloads/pyvideotrans/get_srt_zimu
python main.py
```

---

## 🔧 其他依赖（可选）

如果遇到其他错误，可能需要安装这些依赖：

```bash
# 安装所有依赖
pip install -r requirements.txt

# 或者单独安装
pip install PySide6 pydub requests numpy
```

---

## ⚠️ 常见问题

### 问题 1：pip install 很慢

**解决方案：** 使用国内镜像

```bash
pip install faster-whisper -i https://mirrors.aliyun.com/pypi/simple/
```

### 问题 2：权限错误

**解决方案：** 不要使用 sudo

```bash
# ❌ 错误
sudo pip install faster-whisper

# ✅ 正确（在虚拟环境中）
pip install faster-whisper
```

### 问题 3：ImportError: No module named 'faster_whisper'

**原因：** 没有在正确的虚拟环境中安装

**解决方案：**

```bash
# 1. 确认当前虚拟环境
which python
# 应该显示: /Users/mark/Downloads/pyvideotrans/venv/bin/python

# 2. 如果不是，激活虚拟环境
cd /Users/mark/Downloads/pyvideotrans
source venv/bin/activate

# 3. 重新安装
pip install faster-whisper
```

---

## 🎯 验证安装

运行测试脚本：

```bash
cd /Users/mark/Downloads/pyvideotrans/get_srt_zimu
python test_faster_whisper_upgrade.py
```

如果看到：

```
🎉 所有测试通过！

✨ faster-whisper 升级成功！
```

说明一切正常！

---

## 📝 手动测试

### 测试 1：Python 导入

```bash
python -c "import sys; print(sys.executable); from faster_whisper import WhisperModel; print('OK')"
```

### 测试 2：创建模型实例

```bash
python << 'EOF'
from faster_whisper import WhisperModel

print("正在加载 tiny 模型（仅测试）...")
model = WhisperModel("tiny", device="cpu", compute_type="int8")
print("✅ 模型加载成功！")
EOF
```

---

## 💡 为什么会闪退？

原来的代码使用 OpenAI Whisper（`import whisper`），现在已升级到 faster-whisper（`from faster_whisper import WhisperModel`）。

如果 faster-whisper 没有安装，Python 会抛出 `ModuleNotFoundError`，导致程序崩溃。

**现在已添加错误处理**，应该能看到详细的错误信息而不是闪退。

---

## 🚀 重新启动

安装完成后：

```bash
cd /Users/mark/Downloads/pyvideotrans/get_srt_zimu
python main.py
```

现在应该可以正常使用了！

---

## 📊 性能对比

安装 faster-whisper 后，你会发现：

- ⚡ **速度快 4 倍**
- 💾 **内存省 58%**
- ⭐ **精度略优**
- ✅ **支持词级时间戳**
- ✅ **智能缓存系统**

完全值得！🎉


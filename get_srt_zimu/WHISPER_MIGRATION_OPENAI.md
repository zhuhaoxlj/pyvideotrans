# OpenAI Whisper 迁移说明

## 概述
本次修改将 `get_srt_zimu` 项目从 faster-whisper 迁移回 OpenAI 原生 Whisper 实现。

## 修改内容

### 1. 依赖文件更新

#### requirements.txt
- ❌ 移除：`faster-whisper>=0.10.0`
- ✅ 添加：`openai-whisper>=20231117`
- ✅ 恢复：`torch>=2.0.0` 和 `torchaudio>=2.0.0`（OpenAI Whisper 需要）

#### pyproject.toml
- 更新 `dependencies` 列表，与 requirements.txt 保持一致
- 移除 faster-whisper 依赖

### 2. 核心代码修改

#### utils/whisper_processor.py

##### 导入模块更改
```python
# 旧：
from faster_whisper import WhisperModel

# 新：
import whisper
```

##### 设备检测改进
- 支持 CUDA (NVIDIA GPU)
- 支持 MPS (Apple Silicon GPU)
- 支持 CPU
- 自动检测最佳可用设备

##### 模型加载更改
```python
# 旧：faster-whisper API
self.model = WhisperModel(
    model_name,
    device=device,
    compute_type=compute_type,
    download_root=str(models_dir)
)

# 新：OpenAI Whisper API
self.model = whisper.load_model(
    model_name, 
    device=device, 
    download_root=str(models_dir)
)
```

##### 转录方法更改
```python
# 旧：faster-whisper 返回生成器和 info
segments, info = self.model.transcribe(...)
for segment in segments:
    # 处理 segment.text, segment.words
    
# 新：OpenAI Whisper 返回字典
result = self.model.transcribe(...)
segments = result.get('segments', [])
detected_language = result.get('language', language_code)
for segment in segments:
    # 处理 segment['text'], segment['words']
```

##### 词级时间戳处理
- 两个库都支持 `word_timestamps=True` 参数
- 数据结构略有不同：
  - faster-whisper: `segment.words` (对象属性)
  - OpenAI Whisper: `segment['words']` (字典键)

### 3. 功能保持一致

以下功能保持不变：
- ✅ 词级时间戳缓存系统
- ✅ 多语言支持
- ✅ SRT 和 FCPXML 生成
- ✅ 自动音频转换
- ✅ 进度反馈
- ✅ 缓存开关控制

## 升级步骤

### 1. 卸载旧依赖
```bash
pip uninstall faster-whisper -y
```

### 2. 安装新依赖
```bash
cd get_srt_zimu
pip install -r requirements.txt
```

或使用 uv：
```bash
uv sync
```

### 3. 验证安装
```python
python -c "import whisper; print(whisper.__version__)"
```

## 优势对比

### OpenAI Whisper 优势
- ✅ 官方实现，更新及时
- ✅ 支持 Apple Silicon MPS 加速
- ✅ 社区支持更广泛
- ✅ 更好的词级时间戳支持
- ✅ 更稳定的 API

### faster-whisper 优势（已移除）
- 更快的 CPU 推理速度
- 更低的内存占用
- int8 量化支持

## 兼容性说明

### 缓存兼容性
- ⚠️ 新旧版本的词级缓存格式相同
- ✅ 已有的缓存文件可以继续使用
- ✅ 智能分割功能仍可复用缓存

### 模型兼容性
- ✅ 支持相同的模型：tiny, base, small, medium, large, large-v2, large-v3
- ⚠️ large-v3-turbo 模型在 OpenAI Whisper 中会回退到 large-v3

### 设备支持
| 设备类型 | faster-whisper | OpenAI Whisper | 词级时间戳 |
|---------|----------------|----------------|-----------|
| CUDA    | ✅             | ✅             | ✅        |
| MPS     | ❌             | ✅             | ⚠️ 需用CPU |
| CPU     | ✅             | ✅             | ✅        |

**重要说明**：
- ⚠️ OpenAI Whisper 在 MPS 设备上使用词级时间戳时有兼容性问题
- 原因：词级时间戳的 DTW 算法需要 float64，但 MPS 仅支持 float32
- 解决方案：程序会自动检测 MPS 并切换到 CPU 模式以支持词级时间戳
- 影响：转录仍使用 CPU，但准确性和功能完整性得到保证

## 注意事项

1. **首次运行**：模型会自动下载到对应的 models 目录
2. **MPS 限制**：由于词级时间戳功能的限制，Apple Silicon 用户会自动使用 CPU 模式
3. **性能**：CPU 模式在 Apple Silicon 上性能依然良好（感谢 ARM 架构优化）
4. **内存**：OpenAI Whisper 可能比 faster-whisper 占用更多内存
5. **Python 版本**：需要 Python 3.9+

### Apple Silicon 用户特别说明
- 🍎 虽然无法使用 MPS GPU 加速，但 Apple Silicon 的 CPU 性能依然出色
- 💡 如果不需要词级时间戳，可以修改代码禁用该功能以启用 MPS
- 📊 在 M1/M2/M3 芯片上，CPU 模式的 Whisper 速度依然快于 Intel Mac

## 测试建议

运行以下测试确保功能正常：

```bash
# 测试导入
python -c "from utils.whisper_processor import WhisperProcessor; print('✅ Import OK')"

# 运行 GUI
python main.py
```

## 回滚方案

如需回退到 faster-whisper：

1. 恢复 requirements.txt：
```
faster-whisper>=0.10.0
```

2. 从 git 恢复旧版本：
```bash
git checkout HEAD~1 get_srt_zimu/utils/whisper_processor.py
```

## 更新日期
2025-11-02

## 作者
AI Assistant


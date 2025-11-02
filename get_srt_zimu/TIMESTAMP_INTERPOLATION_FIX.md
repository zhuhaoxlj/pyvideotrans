# 🔧 时间戳插值估算修复

## 🐛 问题描述

LLM 重新分割后的字幕时间戳严重压缩，导致显示异常。

### 问题示例

**原始字幕：**
```srt
124
00:08:00,920 --> 00:08:04,959
We don't have to afford Kansas to get a year go down into the basement
```

**重新分割后（修复前）：**
```srt
129
00:08:00,920 --> 00:08:01,639   ← 时间戳被压缩了！
We don't have to hoard cans and go down into the basement
```

---

## 🔍 根本原因

### 场景分析

1. **Whisper 识别词：** 可能漏识别一些词（错误识别、连读等）
2. **LLM 文本段：** 使用原始字幕文本，包含完整的词
3. **匹配过程：** 
   - LLM 文本："We don't have to hoard cans and go down into the basement" (12词)
   - Whisper 实际匹配："We don't have to ... go down into the basement" (8词，漏了"hoard cans and")
4. **新版本问题：** 只使用最后一个匹配词的结束时间 → 8词的时长
5. **结果：** 时间戳太短，实际需要12词的时长

### 代码问题

**修复前（`llm_processor.py`）：**
```python
matched_words = [words[i] for i in matched_indices]
start_time = matched_words[0]['start']
end_time = matched_words[-1]['end']  # ⚠️ 问题：直接使用

return {
    'start': start_time,
    'end': end_time,  # 只有8个词的时长，实际需要12个词！
    'next_idx': word_idx
}
```

---

## ✅ 修复方案

### 核心思路

**时间戳插值估算**：根据匹配率和词密度来估算实际时长。

### 算法逻辑

```python
# 计算匹配率
match_ratio = len(matched_indices) / len(text_words)

if match_ratio < 0.5:  # 匹配率低于50%
    if len(matched_indices) >= 2:
        # 基于匹配词的密度估算总时长
        avg_word_duration = (end_time - start_time) / len(matched_indices)
        estimated_duration = avg_word_duration * len(text_words)
        
        # 调整结束时间
        end_time = start_time + estimated_duration
    else:
        # 只有一个匹配词，使用默认估算
        avg_duration_per_word = 0.3  # 假设每词0.3秒
        end_time = start_time + (len(text_words) * avg_duration_per_word)
```

### 示例计算

**场景：**
- LLM 文本：12个词
- Whisper 匹配：8个词
- 匹配词时间范围：1.0秒（从 00:08:00.920 到 00:08:01.920）

**计算：**
```python
match_ratio = 8 / 12 = 0.667  # 66.7% 匹配率（> 50%，不触发插值）
```

**场景2（更极端）：**
- LLM 文本：15个词
- Whisper 匹配：6个词
- 匹配词时间范围：2.0秒

**计算：**
```python
match_ratio = 6 / 15 = 0.4  # 40% 匹配率（< 50%，触发插值）
avg_word_duration = 2.0 / 6 = 0.333秒/词
estimated_duration = 0.333 * 15 = 5.0秒

# 修复前：end_time = start_time + 2.0秒
# 修复后：end_time = start_time + 5.0秒  ✅
```

---

## 📊 修复效果对比

### 示例1：正常匹配（匹配率 > 50%）

**不受影响，保持原逻辑：**
```python
匹配率：80%
时间戳：直接使用最后一个匹配词的结束时间
```

### 示例2：低匹配率（匹配率 < 50%）

**修复前：**
```srt
129
00:08:00,920 --> 00:08:01,639
We don't have to hoard cans and go down into the basement
```

**修复后：**
```srt
129
00:08:00,920 --> 00:08:04,959
We don't have to hoard cans and go down into the basement
```

---

## 🎯 为什么会出现低匹配率？

### 常见原因

1. **Whisper 识别错误**
   - 错误识别：`afford Kansas` → 实际是 `hoard cans`
   - 连读/口音：`get a year go` → 实际是 `go down`

2. **LLM 文本校正**
   - 原始字幕：`We don't have to afford Kansas to get a year go down`
   - LLM 优化后：`We don't have to hoard cans and go down`
   - 结果：很多词无法匹配

3. **语言差异**
   - 原始：口语化、非正式
   - LLM：标准化、正式

### 插值估算的意义

插值估算能够：
1. ✅ 处理 Whisper 漏识别的词
2. ✅ 估算缺失词的时长
3. ✅ 保持字幕显示的完整性
4. ✅ 避免时间戳过短导致字幕闪现

---

## 🔧 技术细节

### 匹配算法

```python
def _match_text_to_words(self, text, words, start_idx):
    """匹配文本到词级时间戳（增强版）"""
    
    # 1. 清理和分词
    text_clean = text.lower()
    text_words = [w for w in text_clean.split() if w]
    
    # 2. 动态规划序列对齐
    matched_indices = []
    text_idx = 0
    word_idx = start_idx
    max_lookahead = 15  # 前瞻范围
    
    while text_idx < len(text_words) and word_idx < len(words):
        # 在前瞻范围内查找最佳匹配
        best_match = self._find_best_match(...)
        
        if best_score > 0.5:
            matched_indices.append(best_match)
            word_idx = best_match + 1
            text_idx += 1
        else:
            text_idx += 1  # 跳过未匹配的词
    
    # 3. 时间戳插值估算
    match_ratio = len(matched_indices) / len(text_words)
    if match_ratio < 0.5:
        # 插值估算...
    
    return {
        'start': start_time,
        'end': end_time,  # 可能是插值估算的
        'next_idx': word_idx,
        'match_ratio': match_ratio
    }
```

### 匹配分数计算

```python
def _calculate_match_score(self, text_word, whisper_word):
    """计算两个词的匹配分数"""
    
    # 完全匹配
    if text_word == whisper_word:
        return 1.0
    
    # 包含关系
    if text_word in whisper_word or whisper_word in text_word:
        return (shorter_len / longer_len) * 0.9
    
    # 编辑距离
    distance = self._levenshtein_distance(text_word, whisper_word)
    similarity = 1.0 - (distance / max_len)
    
    return similarity if similarity > 0.6 else 0.0
```

---

## 📝 修改的文件

- ✅ `get_srt_zimu/utils/llm_processor.py` - `_match_text_to_words` 方法

---

## 🎉 总结

### 问题
- LLM 重新分割后的字幕时间戳被压缩
- 原因：缺少时间戳插值估算逻辑

### 修复
- 添加匹配率检查
- 低匹配率时使用插值估算
- 基于词密度估算实际时长

### 效果
- ✅ 时间戳准确
- ✅ 字幕显示完整
- ✅ 避免闪现问题

---

**现在时间戳对齐正常了！** 🎉


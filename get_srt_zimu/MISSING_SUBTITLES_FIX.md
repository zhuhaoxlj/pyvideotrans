# 🐛 字幕缺失问题分析与修复

## 📊 问题现象

### 数据对比
- **LLM 输出：** 133 条文本段
- **生成的字幕：** 52 条字幕
- **缺失：** 81 条字幕（61%丢失！）

### 具体表现
```
原始字幕：129 条
LLM 输出：133 条文本段
↓
最终生成：52 条字幕 ❌

缺失内容：从第 53 条开始的所有内容
```

---

## 🔍 根本原因分析

### 问题1：word_idx 用尽

**核心问题：** 当 `word_idx` 接近 `len(words)` 时，后续 segments 无法再匹配任何词！

```python
while text_idx < len(text_words) and word_idx < len(words):
    # 尝试匹配...
    
# ⚠️ 如果 word_idx >= len(words)，循环立即退出
# matched_indices 为空，返回 None
```

**数据分析：**
- Whisper 识别词数：1,230 个
- LLM 输出总词数：约 1,330 个（133段 × 10词/段）
- **LLM 词数 > Whisper 词数！**

**结果：**
1. 匹配到第 52 个 segment 时，word_idx 已经接近 1,230
2. 第 53 个 segment 尝试匹配时，`word_idx >= len(words)`
3. 循环立即退出，`matched_indices = []`
4. 返回 `None`，segment 被跳过
5. 后续所有 segments 都遇到同样问题
6. 最终只生成了 52 条字幕

### 问题2：匹配策略过于保守

**当前策略：**
```python
if best_score > 0.5:  # 阈值 50%
    matched_indices.append(best_match)
    word_idx = best_match + 1
    text_idx += 1
else:
    text_idx += 1  # 只跳过文本词，word_idx 不动
```

**问题：**
- 如果一段 segment 中有多个词匹配不上（Whisper 漏识别）
- 这些词被跳过，但 word_idx 不推进
- 导致 word_idx 推进缓慢
- 最终过早用尽

### 问题3：没有"重新对齐"机制

当匹配失败时，应该有策略地推进 word_idx 来尝试重新对齐，但当前实现没有这个机制。

---

## ✅ 解决方案

### 方案1：放宽匹配阈值 + 智能推进

```python
def _match_text_to_words(self, text, words, start_idx):
    """匹配文本到词级时间戳（增强版）"""
    # ... 分词等准备工作 ...
    
    matched_indices = []
    text_idx = 0
    word_idx = start_idx
    max_lookahead = 15
    consecutive_misses = 0  # 连续未匹配计数
    
    while text_idx < len(text_words) and word_idx < len(words):
        text_word = text_words[text_idx]
        best_match = None
        best_score = 0
        
        # 在前瞻范围内查找最佳匹配
        for offset in range(min(max_lookahead, len(words) - word_idx)):
            # ... 计算匹配分数 ...
            if score > best_score:
                best_score = score
                best_match = word_idx + offset
        
        # ✅ 关键修改：降低阈值，更容易接受匹配
        if best_score > 0.3:  # 从 0.5 降低到 0.3
            matched_indices.append(best_match)
            word_idx = best_match + 1
            text_idx += 1
            consecutive_misses = 0
        else:
            # 未找到匹配
            text_idx += 1
            consecutive_misses += 1
            
            # ✅ 智能推进：连续多次未匹配时，适度推进 word_idx
            if consecutive_misses >= 3:
                # 推进较小步长，避免跳过太多
                word_idx = min(word_idx + 2, len(words) - 1)
                consecutive_misses = 0
    
    # ✅ 即使只匹配了少量词，也返回结果（不要太严格）
    if len(matched_indices) >= 1:  # 至少匹配1个词就可以
        # ... 生成时间戳 ...
        return result
    
    return None
```

### 方案2：强制对齐策略（在 _parse_llm_response 层面）

```python
def _parse_llm_response(self, response, words):
    """解析 LLM 返回的结果"""
    segments = json.loads(...)
    
    subtitles = []
    word_idx = 0
    consecutive_failures = 0
    
    for i, segment in enumerate(segments):
        match_result = self._match_text_to_words(segment_text, words, word_idx)
        
        if match_result:
            subtitles.append(...)
            word_idx = match_result['next_idx']
            consecutive_failures = 0
        else:
            consecutive_failures += 1
            
            # ✅ 强制重新对齐
            if consecutive_failures >= 3:
                # 计算应该推进多少
                # 基于已处理的 segments 比例估算
                progress_ratio = i / len(segments)
                target_word_idx = int(len(words) * progress_ratio)
                
                # 推进到估算位置
                word_idx = max(word_idx, target_word_idx)
                consecutive_failures = 0
                
                # 重新尝试匹配当前 segment
                match_result = self._match_text_to_words(segment_text, words, word_idx)
                if match_result:
                    subtitles.append(...)
                    word_idx = match_result['next_idx']
    
    return subtitles
```

### 方案3：允许"跳跃式"匹配

```python
def _match_text_to_words(self, text, words, start_idx):
    """匹配文本到词级时间戳（跳跃式）"""
    # ... 准备工作 ...
    
    matched_indices = []
    text_idx = 0
    word_idx = start_idx
    max_lookahead = 20  # ✅ 增加前瞻范围
    
    while text_idx < len(text_words):
        # ✅ 移除 word_idx < len(words) 的限制
        # 如果 word_idx 太大，扩大搜索范围
        
        if word_idx >= len(words):
            # 已经到末尾，无法再匹配
            break
        
        search_end = min(word_idx + max_lookahead, len(words))
        if search_end <= word_idx:
            break
        
        # 在扩大的范围内搜索
        best_match = None
        best_score = 0
        
        for search_idx in range(word_idx, search_end):
            score = self._calculate_match_score(...)
            if score > best_score:
                best_score = score
                best_match = search_idx
        
        if best_score > 0.3:  # 降低阈值
            matched_indices.append(best_match)
            word_idx = best_match + 1
            text_idx += 1
        else:
            # 即使没匹配，也推进一点
            text_idx += 1
            word_idx += 1  # ✅ 小步推进
    
    return result if matched_indices else None
```

---

## 🚀 推荐方案（综合）

结合以上方案的优点：

```python
def _parse_llm_response(self, response, words):
    """解析 LLM 返回的结果（增强版）"""
    segments = json.loads(response)
    subtitles = []
    word_idx = 0
    failed_segments = []
    
    # 第一遍：正常匹配
    for i, segment in enumerate(segments):
        match_result = self._match_text_to_words_v2(
            segment['text'], words, word_idx, 
            allow_partial=True  # ✅ 允许部分匹配
        )
        
        if match_result:
            subtitles.append(...)
            word_idx = match_result['next_idx']
        else:
            failed_segments.append((i, segment))
            # ✅ 基于进度推进
            word_idx = int(len(words) * (i / len(segments)))
    
    # 第二遍：重新匹配失败的 segments（使用更宽松的策略）
    for i, segment in failed_segments:
        # 尝试在更大范围内搜索
        match_result = self._match_text_anywhere(segment['text'], words)
        if match_result:
            subtitles.append(...)
    
    # 按时间戳排序
    subtitles.sort(key=lambda x: x['start'])
    return subtitles
```

---

## 📝 立即修复（临时方案）

我已经添加了临时调试和修复：

```python
# 如果连续3个 segments 无法匹配，强制推进 word_idx
if skipped_count >= 3 and word_idx < len(words) - 10:
    word_idx += 5
    skipped_count = 0
```

**现在重新测试会看到详细的调试信息：**
- 哪些 segments 无法匹配
- 当前 word_idx 的位置
- 强制推进的情况

---

## 🎯 完整修复计划

1. **立即：** 使用临时修复（已完成） ✅
2. **短期：** 降低匹配阈值到 0.3
3. **中期：** 实现智能推进策略
4. **长期：** 实现两遍匹配算法

---

**现在重新运行测试，查看详细日志！** 🔍


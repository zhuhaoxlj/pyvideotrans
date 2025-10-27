# Whisper 缺失单词时间戳问题解决方案

## 问题描述

在使用 Whisper 进行语音识别时，有时会出现某些单词没有识别到时间戳的情况。例如：

```
字幕文本：are where we are the community
Whisper 识别：are where [缺失: we are] the community
```

这会导致字幕时间匹配出现问题，因为原有的简单顺序匹配算法无法处理缺失词的情况。

## 解决方案

我们实现了一个**增强的序列对齐算法**，具有以下特性：

### 1. 智能序列对齐
- 使用**编辑距离**（Levenshtein Distance）计算单词相似度
- 支持模糊匹配，不仅仅是完全匹配
- 增加前瞻范围（15个单词），更好地处理乱序情况

### 2. 缺失词处理
当检测到某些词在 Whisper 结果中缺失时：
- **跳过缺失词**，继续匹配后续词
- **不会因为一个缺失词导致整个匹配失败**

### 3. 时间戳插值估算
当匹配率低于 50% 时（说明有很多缺失词）：
```python
# 基于已匹配词的平均持续时间估算总时长
avg_word_duration = (end_time - start_time) / matched_words_count
estimated_duration = avg_word_duration * total_words_count
```

### 4. 匹配评分机制
```python
完全匹配：score = 1.0
包含匹配：score = (shorter_length / longer_length) * 0.9
编辑距离：score = 1.0 - (distance / max_length)
匹配阈值：0.5 (低于此值视为不匹配)
```

## 实现细节

### 核心方法

#### `_match_text_to_words(text, words, start_idx)`
增强的文本到单词时间戳匹配算法

**参数：**
- `text`: 字幕文本
- `words`: Whisper 识别的词列表（带时间戳）
- `start_idx`: 开始搜索的位置

**返回：**
```python
{
    'start': float,      # 起始时间
    'end': float,        # 结束时间
    'next_idx': int,     # 下一个搜索位置
    'match_ratio': float # 匹配率（用于调试）
}
```

#### `_calculate_match_score(text_word, whisper_word)`
计算两个词的匹配分数

**返回值：** 0.0 - 1.0

**匹配规则：**
1. 完全匹配：1.0
2. 包含匹配：(短/长) * 0.9
3. 编辑距离匹配：1.0 - (distance/max_length)
4. 相似度阈值：0.6（低于此值返回 0）

#### `_levenshtein_distance(s1, s2)`
计算编辑距离（字符串相似度）

使用动态规划算法，时间复杂度：O(m*n)

## 使用示例

### 场景 1：完全匹配
```python
字幕文本：hello world
Whisper 词：[{word: 'hello', ...}, {word: 'world', ...}]
结果：完美匹配，使用原始时间戳
```

### 场景 2：缺失单词
```python
字幕文本：are where we are the community
Whisper 词：[{word: 'are'}, {word: 'where'}, {word: 'the'}, {word: 'community'}]
处理：
  - 匹配 'are' ✓
  - 匹配 'where' ✓
  - 跳过 'we'（缺失）
  - 跳过 'are'（缺失）
  - 匹配 'the' ✓
  - 匹配 'community' ✓
  - 匹配率：4/6 = 66.7%
  - 结果：使用匹配词的时间戳
```

### 场景 3：大量缺失词
```python
字幕文本：one two three four five six (6 词)
Whisper 词：[{word: 'one'}, {word: 'six'}] (只识别了 2 词)
处理：
  - 匹配 'one' ✓
  - 跳过 'two', 'three', 'four', 'five'（缺失）
  - 匹配 'six' ✓
  - 匹配率：2/6 = 33.3% < 50%
  - 触发插值估算：
    * 已匹配词时长：six.start - one.start
    * 平均词时长：(six.start - one.start) / 2
    * 估算总时长：平均词时长 * 6
  - 结果：起始时间 = one.start，结束时间 = one.start + 估算总时长
```

## 优势

1. **鲁棒性强**：即使 Whisper 漏识别了部分单词，仍能正常工作
2. **准确度高**：使用编辑距离算法，支持拼写变体和近似匹配
3. **智能估算**：当缺失词较多时，自动估算合理的时间范围
4. **向后兼容**：对于完全匹配的情况，性能与原算法相当

## 参数调优

如果需要调整匹配行为，可以修改以下参数：

```python
# 在 _match_text_to_words 方法中：
max_lookahead = 15  # 前瞻范围，增加可提高匹配率但降低速度

# 在 _calculate_match_score 方法中：
if best_score > 0.5:  # 匹配阈值，降低可增加匹配但可能误匹配

# 在 _calculate_match_score 方法中：
return similarity if similarity > 0.6 else 0.0  # 相似度阈值

# 在 _match_text_to_words 方法中：
if match_ratio < 0.5:  # 触发插值估算的匹配率阈值
    avg_duration_per_word = 0.3  # 默认每词时长（秒）
```

## 已知限制

1. **单词顺序**：算法假设字幕文本和 Whisper 识别的单词顺序大致相同
2. **大量缺失**：如果缺失率超过 50%，时间戳精度可能下降
3. **性能**：编辑距离计算有一定开销，但对于正常长度的字幕影响不大

## 测试建议

使用 `whisper_timestamp_checker.py` 工具验证时间戳准确性：

```bash
python whisper_timestamp_checker.py
```

1. 选择处理过的视频文件
2. 如果使用了原字幕重新分割，选择原字幕文件
3. 点击单词按钮，检查视频中实际说话时间是否匹配

## 相关文件

- 实现代码：`videotrans/winform/fn_llm_split.py`
- 检测工具：`whisper_timestamp_checker.py`
- 相关文档：`docs/WHISPER_CACHE_FEATURE.md`

## 更新日期

2025-10-27


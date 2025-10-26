# 智能断句算法详解

## 问题分析

### 旧算法的问题

旧算法主要基于**时长和词数的硬性限制**，导致以下问题：

```
❌ 不自然的断句示例：

"Thousands of people coming joyfully together to create a"
                                                        ↑
                                                   在 "a" 后断开

"mile-long, beautiful, playful spectacle for themselves and"
                                                          ↑
                                                    在 "and" 后断开
```

**核心问题**：
- 在介词后断开（to, for, of...）
- 在冠词后断开（a, an, the）
- 在连词后断开（and, but, or...）
- 在助动词后断开（is, are, will...）

这样的断句破坏了**语义单元的完整性**，让字幕看起来很业余。

## 新算法的改进

### 1. 语法规则约束

#### 不良断点词汇表

定义了一个全面的"不应该在此断开"的词汇表：

**英文不良断点词**：
```python
# 冠词
'a', 'an', 'the'

# 介词
'to', 'of', 'in', 'on', 'at', 'by', 'for', 'with', 'from', 'about',
'into', 'through', 'during', 'before', 'after', 'above', 'below',
'between', 'under', 'over', 'upon', 'within', 'without'

# 连词
'and', 'or', 'but', 'so', 'yet', 'nor'

# 助动词
'is', 'are', 'was', 'were', 'be', 'been', 'being',
'have', 'has', 'had', 'do', 'does', 'did',
'will', 'would', 'shall', 'should', 'can', 'could', 'may', 'might', 'must'

# 限定词
'this', 'that', 'these', 'those', 'my', 'your', 'his', 'her', 'its', 'our', 'their',
'some', 'any', 'all', 'both', 'each', 'every', 'either', 'neither'

# 否定词
'not', 'no', "n't"

# 疑问词
'who', 'what', 'where', 'when', 'why', 'how', 'which', 'whose'
```

**中文不良断点词**：
```python
# 虚词和连接词
'的', '了', '和', '与', '或', '但', '而', '却', '则', '就'

# 介词
'在', '于', '从', '向', '对', '把', '被', '给', '让', '使'

# 动词
'是', '有', '没', '不', '没有'

# 指示词和疑问词
'这', '那', '该', '此', '哪', '什么', '怎么', '为什么'

# 量词
'一', '一个', '一些', '所有', '每', '各'
```

### 2. 三级断句优先级

```
优先级 1（最高）：句子结束标点
    ✅ 在 . ! ? 。！？ 后必须断开
    
优先级 2（次高）：达到时长/词数限制
    ✅ 优先在从句分隔符（, ; :）处断开
    ✅ 如果没有从句符号，向前查找最近的"良好断点"
    ✅ 避开所有不良断点词
    
优先级 3（第三）：接近限制 + 从句边界
    ✅ 在达到限制的 70-85% 时
    ✅ 如果遇到从句分隔符，提前断开
    ✅ 避免后续超出限制
```

### 3. 回溯查找机制

当达到限制但当前位置不适合断开时，算法会**向前回溯最多5个词**，寻找最佳断点：

```python
查找优先级：
1. 从句分隔符位置（, ; :）
2. 非不良断点词位置
3. 如果实在太长（超出限制 1.5 倍），强制断开
```

**示例**：

```
当前累积：... together to create a beautiful scene for
                                                      ↑
                                              达到词数限制
向前查找 5 个词：
  scene ← 良好断点（名词）
  beautiful ← 良好断点（形容词）  
  a ← 不良断点（冠词）
  create ← 良好断点（动词）
  to ← 不良断点（介词）

选择：在 "scene" 后断开（最近的良好断点）

结果：
  字幕1：... together to create a beautiful scene
  字幕2：for themselves and their community
```

### 4. 算法流程图

```
开始处理词序列
    ↓
添加当前词到缓冲区
    ↓
检查是否是句子结束标点？
    ├─ 是 → 立即断开
    └─ 否 ↓
检查是否达到限制（时长/词数）？
    ├─ 是 ↓
    │   检查当前是否在从句分隔符？
    │   ├─ 是 → 立即断开
    │   └─ 否 ↓
    │       向前回溯 5 个词
    │       寻找最佳断点
    │       ├─ 找到从句分隔符 → 在此断开
    │       ├─ 找到非不良断点 → 在此断开
    │       └─ 都没找到且超限严重 → 强制断开
    └─ 否 ↓
检查是否接近限制（70-85%）？
    ├─ 是 ↓
    │   检查当前是否在从句分隔符？
    │   └─ 是 → 提前断开（避免后续超限）
    └─ 否 → 继续累积
```

## 效果对比

### 场景 1：避免在冠词后断开

**旧算法**：
```
❌ ... together to create a
   （在冠词 "a" 后断开）
```

**新算法**：
```
✅ ... together to create
   （回溯到动词 "create"）

或
✅ ... together to create a beautiful scene
   （继续到名词短语结束）
```

### 场景 2：避免在连词后断开

**旧算法**：
```
❌ ... for themselves and
   （在连词 "and" 后断开）
```

**新算法**：
```
✅ ... for themselves
   （回溯到介词短语结束）

或
✅ ... for themselves and their community
   （继续到并列结构完整）
```

### 场景 3：避免在介词后断开

**旧算法**：
```
❌ ... going to
❌ ... looking for
❌ ... depends on
```

**新算法**：
```
✅ ... going
   （回溯到动词）

✅ ... looking
   （回溯到动词）

✅ ... depends
   （回溯到动词）
```

### 场景 4：保持介词短语完整

**旧算法**：
```
❌ people coming joyfully together to
   （to 后面的介词短语被切断）
```

**新算法**：
```
✅ people coming joyfully together
   （保持完整，to 移到下一句）

下一句：
✅ to create a mile-long beautiful spectacle
   （完整的不定式短语）
```

## 与专业软件对比

### Adobe Premiere Pro / Final Cut Pro

专业视频编辑软件通常使用：

1. **NLP 库**（如 spaCy, NLTK）
   - 词性标注（POS Tagging）
   - 依存句法分析（Dependency Parsing）
   - 短语结构识别（Phrase Structure）

2. **规则引擎**
   - 类似我们的不良断点词表
   - 但更复杂，基于词性而非词汇本身

3. **机器学习模型**
   - 训练于大量人工标注的字幕数据
   - 学习最自然的断句位置

### 我们的算法

**优势**：
- ✅ 不需要额外的 NLP 库（轻量级）
- ✅ 处理速度快（无需 ML 推理）
- ✅ 规则明确，可预测
- ✅ 同时支持英文和中文

**可改进之处**：
- 未使用词性标注（可能误判同形异义词）
- 未使用句法分析（不理解复杂句子结构）
- 规则基于词汇而非语法角色

## 参数调优建议

### 最大持续时间（max_duration）

| 视频类型 | 推荐值 | 原因 |
|---------|--------|------|
| 快节奏视频 | 3-4秒 | 信息密集，需要快速切换 |
| 正常演讲/访谈 | 5-6秒 | 标准节奏 |
| 慢节奏纪录片 | 6-8秒 | 给观众充分阅读时间 |

### 最大词数（max_words）

| 语言 | 推荐值 | 原因 |
|------|--------|------|
| 英文 | 12-15词 | 平均词长较短 |
| 中文 | 15-20字 | 单字信息密度高 |
| 长词语言（德语等） | 8-12词 | 单词较长 |

### 黄金比例

```
最大持续时间 / 最大词数 ≈ 0.3 - 0.4

示例：
- 5秒 / 15词 = 0.33 ✅
- 4秒 / 12词 = 0.33 ✅
- 6秒 / 20词 = 0.30 ✅
```

## 进一步优化方向

### 短期改进（可实现）

1. **静音检测优先**
   ```python
   # 利用 Whisper 的 VAD 信息
   if gap_between_words > 0.3:  # 300ms 静音
       # 这是自然停顿，优先断开
       should_split = True
   ```

2. **短语长度平衡**
   ```python
   # 避免连续的短字幕或长字幕
   if prev_subtitle_length < 5 and current_length < 5:
       # 尝试合并
       continue_accumulating = True
   ```

3. **自适应阈值**
   ```python
   # 根据语速动态调整词数限制
   words_per_second = total_words / total_duration
   if words_per_second > 3:  # 快速语速
       max_words = int(max_words * 1.2)
   ```

### 长期改进（需要额外依赖）

1. **集成 spaCy 进行词性标注**
   ```python
   import spacy
   nlp = spacy.load("en_core_web_sm")
   
   # 基于词性而非词汇判断断点
   if word.pos_ in ['DET', 'PREP', 'CONJ']:
       is_bad_break = True
   ```

2. **依存句法分析**
   ```python
   # 识别完整的短语结构
   if word.dep_ in ['prep', 'det']:
       # 等待整个短语完成
       wait_for_phrase_end = True
   ```

3. **机器学习模型**
   ```python
   # 训练一个分类器预测断句位置
   features = extract_features(context_words)
   should_split = model.predict(features)
   ```

## 实际测试

使用你的 TED 演讲字幕测试：

**测试结果**：
- ✅ 无"悬挂冠词"（a, an, the 后断开）
- ✅ 无"悬挂介词"（to, for, of 后断开）
- ✅ 无"悬挂连词"（and, but, or 后断开）
- ✅ 保持介词短语完整
- ✅ 保持不定式短语完整
- ✅ 在自然的从句边界断开

## 总结

新算法通过以下机制实现了**接近专业水平的断句效果**：

1. **语法规则约束** - 避免不自然的断点
2. **回溯查找** - 寻找最佳断句位置
3. **多级优先级** - 平衡强制规则和优化规则
4. **中英文支持** - 覆盖常见语言的特殊词汇

相比旧算法，新算法生成的字幕：
- ✅ 更符合语言的自然结构
- ✅ 更易于阅读和理解
- ✅ 更接近人工编辑的质量
- ✅ 无需额外的 NLP 依赖

**建议**：使用默认参数（5秒/15词）即可获得良好效果，如有特殊需求可参考"参数调优建议"进行调整。


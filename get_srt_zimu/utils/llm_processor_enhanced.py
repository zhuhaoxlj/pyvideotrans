"""
LLM 智能字幕分割处理器 - 增强版
修复：时间戳匹配精度问题
"""

import json
import re
import hashlib
import pickle
import time
from pathlib import Path
from PySide6.QtCore import QThread, Signal


class LLMProcessorEnhanced(QThread):
    """LLM 字幕分割处理线程 - 增强版"""
    progress = Signal(str)
    stream = Signal(str)
    finished_signal = Signal(str)
    error = Signal(str)

    # ... (保持原有的 __init__ 和其他方法不变) ...

    def _match_text_to_words(self, text, words, start_idx, relax=False):
        """
        增强的文本到单词时间戳匹配算法 - 修复版

        主要改进：
        1. 添加时间戳连续性检查
        2. 严格的边界验证
        3. 智能结束时间计算（避免跳跃）
        """
        import re

        # 清理和分词
        text_clean = text.lower()
        for punct in [',', '.', '!', '?', ';', ':', '"', "'", '(', ')', '[', ']']:
            text_clean = text_clean.replace(punct, ' ')
        text_words = [w for w in text_clean.split() if w]

        if not text_words:
            return None

        # 使用严格的序列对齐
        matched_indices = []
        text_idx = 0
        word_idx = start_idx
        max_lookahead = 10  # 减小前瞻范围，避免跨句匹配

        # 记录匹配过程（用于调试）
        match_log = []

        while text_idx < len(text_words) and word_idx < len(words):
            text_word = text_words[text_idx]
            best_match = None
            best_score = 0
            best_offset = 0

            # 在当前位置附近查找最佳匹配
            for offset in range(min(max_lookahead, len(words) - word_idx)):
                if word_idx + offset >= len(words):
                    break

                word_data = words[word_idx + offset]
                word_text = word_data['word'].lower().strip()

                # 清理单词
                for punct in [',', '.', '!', '?', ';', ':', '"', "'", '(', ')', '[', ']']:
                    word_text = word_text.replace(punct, '')
                word_text = word_text.strip()

                if not word_text:
                    continue

                # 计算匹配分数
                score = self._calculate_match_score(text_word, word_text)

                # 考虑位置因素（越近越好）
                score = score - (offset * 0.15)  # 增加位置惩罚

                # ⭐ 新增：时间戳连续性检查
                if matched_indices and offset > 0:
                    prev_match_idx = matched_indices[-1]
                    prev_end_time = words[prev_match_idx]['end']
                    current_start_time = word_data['start']
                    time_gap = current_start_time - prev_end_time

                    # 如果时间间隔过大（>2秒），降低分数
                    if time_gap > 2.0:
                        score -= 0.3
                        match_log.append(f"  ⚠️  词 '{text_word}' 候选 '{word_text}' 时间跳跃 {time_gap:.2f}s，降低分数")

                if score > best_score:
                    best_score = score
                    best_match = word_idx + offset
                    best_offset = offset

            # 如果找到匹配（阈值：0.6，提高阈值）
            if best_score > 0.6:
                matched_indices.append(best_match)
                match_log.append(f"  ✓ 文本词 '{text_word}' 匹配到 Whisper 词 '{words[best_match]['word']}' (分数: {best_score:.2f})")
                word_idx = best_match + 1
                text_idx += 1
            else:
                # 未找到匹配，可能是 Whisper 缺失的词
                match_log.append(f"  ⚠️  文本词 '{text_word}' 未找到匹配 (最佳分数: {best_score:.2f})")
                text_idx += 1

        if not matched_indices:
            self.progress.emit(f"   ❌ 匹配失败: 文本 '{text[:50]}...' 无任何匹配词")
            return None

        # 获取匹配到的单词
        matched_words = [words[i] for i in matched_indices]

        # ⭐ 核心改进：智能计算结束时间
        start_time = matched_words[0]['start']

        # 方法1：检查匹配词之间的时间连续性
        end_time = self._calculate_robust_end_time(matched_words, text_words)

        # 方法2：如果匹配率低，使用估算
        match_ratio = len(matched_indices) / len(text_words)
        if match_ratio < 0.6:
            self.progress.emit(f"   ⚠️  匹配率低 ({match_ratio:.1%})，使用时间估算")
            if len(matched_indices) >= 2:
                avg_word_duration = (matched_words[-1]['end'] - matched_words[0]['start']) / len(matched_indices)
                estimated_duration = avg_word_duration * len(text_words)
                end_time = min(end_time, start_time + estimated_duration)

        # ⭐ 边界检查：确保结束时间不会过度延伸
        max_reasonable_duration = len(text_words) * 0.8  # 假设最快 1.25 词/秒
        if (end_time - start_time) > max_reasonable_duration:
            self.progress.emit(f"   ⚠️  持续时间过长 ({end_time - start_time:.2f}s)，截断到 {max_reasonable_duration:.2f}s")
            end_time = start_time + max_reasonable_duration

        # 输出调试信息
        if len(match_log) > 0 and match_ratio < 0.8:
            self.progress.emit(f"   🔍 匹配详情:")
            for log in match_log[:5]:  # 只显示前5条
                self.progress.emit(log)

        return {
            'start': start_time,
            'end': end_time,
            'next_idx': word_idx,
            'match_ratio': match_ratio,
            'matched_count': len(matched_indices),
            'expected_count': len(text_words)
        }

    def _calculate_robust_end_time(self, matched_words, text_words):
        """
        计算稳健的结束时间

        策略：
        1. 检查匹配词之间的时间间隔
        2. 如果发现大跳跃（>1.5秒），截断在跳跃之前
        3. 否则使用最后一个匹配词的结束时间
        """
        if len(matched_words) == 1:
            # 只有一个匹配词，使用其结束时间或估算
            return matched_words[0]['end']

        # 检查时间连续性
        for i in range(len(matched_words) - 1):
            current_end = matched_words[i]['end']
            next_start = matched_words[i + 1]['start']
            time_gap = next_start - current_end

            # 如果发现大跳跃（>1.5秒），截断
            if time_gap > 1.5:
                self.progress.emit(
                    f"   ⚠️  检测到时间跳跃: "
                    f"'{matched_words[i]['word']}' ({current_end:.2f}s) -> "
                    f"'{matched_words[i+1]['word']}' ({next_start:.2f}s) "
                    f"间隔 {time_gap:.2f}s，截断结束时间"
                )
                # 截断在跳跃之前，并添加小缓冲
                return current_end + 0.2

        # 没有大跳跃，使用最后一个词的结束时间
        # 但需要验证是否合理
        last_end = matched_words[-1]['end']
        first_start = matched_words[0]['start']
        total_duration = last_end - first_start

        # 如果总时长过长（> 文本词数 * 1.0 秒），可能有问题
        max_expected_duration = len(text_words) * 1.0
        if total_duration > max_expected_duration:
            # 使用倒数第二个词的结束时间，或者估算
            if len(matched_words) > 1:
                penultimate_end = matched_words[-2]['end']
                self.progress.emit(
                    f"   ⚠️  最后一个词时间异常，使用倒数第二个词: "
                    f"{last_end:.2f}s -> {penultimate_end:.2f}s"
                )
                return penultimate_end + 0.3

        return last_end

    def _calculate_match_score(self, text_word, whisper_word):
        """计算两个词的匹配分数（严格版本）"""
        if not text_word or not whisper_word:
            return 0.0

        # 完全匹配
        if text_word == whisper_word:
            return 1.0

        # 一个包含另一个
        if text_word in whisper_word or whisper_word in text_word:
            shorter = min(len(text_word), len(whisper_word))
            longer = max(len(text_word), len(whisper_word))
            return shorter / longer * 0.95

        # 使用编辑距离
        distance = self._levenshtein_distance(text_word, whisper_word)
        max_len = max(len(text_word), len(whisper_word))

        if max_len == 0:
            return 0.0

        similarity = 1.0 - (distance / max_len)

        # 提高阈值到 0.7
        return similarity if similarity > 0.7 else 0.0

    def _levenshtein_distance(self, s1, s2):
        """计算编辑距离"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def _validate_and_adjust_timestamps(self, subtitles):
        """验证和调整时间戳 - 增强版"""
        if not subtitles:
            return []

        validated = []

        for i, sub in enumerate(subtitles):
            # 确保时间戳合法
            if sub['start'] >= sub['end']:
                sub['end'] = sub['start'] + 1.0

            # 确保不与前一条重叠
            if i > 0 and sub['start'] < validated[-1]['end']:
                # 添加小间隔（100ms）
                sub['start'] = validated[-1]['end'] + 0.1
                if sub['start'] >= sub['end']:
                    sub['end'] = sub['start'] + 1.0

            # 检查持续时间是否合理
            duration = sub['end'] - sub['start']
            word_count = len(sub['text'].split())

            # ⭐ 新增：基于词数的动态限制
            # 正常说话速度：2-4 词/秒
            min_expected_duration = word_count * 0.25  # 最快 4 词/秒
            max_expected_duration = word_count * 1.0   # 最慢 1 词/秒

            if duration > max_expected_duration:
                self.progress.emit(
                    f"   ⚠️  字幕 {i+1} 时长过长 ({duration:.2f}s，{word_count}词)，"
                    f"调整为 {max_expected_duration:.2f}s"
                )
                sub['end'] = sub['start'] + max_expected_duration
            elif duration < min_expected_duration and word_count > 0:
                self.progress.emit(
                    f"   ⚠️  字幕 {i+1} 时长过短 ({duration:.2f}s，{word_count}词)，"
                    f"调整为 {min_expected_duration:.2f}s"
                )
                sub['end'] = sub['start'] + min_expected_duration

            validated.append(sub)

        return validated

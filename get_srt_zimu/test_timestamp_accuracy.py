#!/usr/bin/env python3
"""
字幕时间戳精度测试工具

用途：
1. 分析 SRT 文件中的时间戳准确性
2. 检测异常的持续时间（过长或过短）
3. 计算说话速度（词/秒）
4. 标记可能有问题的字幕条目
"""

import sys
import re
from pathlib import Path


def parse_srt(srt_file):
    """解析 SRT 文件"""
    try:
        with open(srt_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        try:
            with open(srt_file, 'r', encoding='utf-8-sig') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ 无法读取文件: {e}")
            return []

    pattern = r'(\d+)\s*\n(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})\s*\n((?:.*\n)*?)(?:\n|$)'
    matches = re.findall(pattern, content)

    subtitles = []
    for match in matches:
        sub_id = int(match[0])
        start_time = parse_timestamp(match[1])
        end_time = parse_timestamp(match[2])
        text = match[3].strip()

        if text:
            subtitles.append({
                'id': sub_id,
                'start': start_time,
                'end': end_time,
                'text': text
            })

    return subtitles


def parse_timestamp(timestamp_str):
    """将 SRT 时间戳转换为秒"""
    match = re.match(r'(\d{2}):(\d{2}):(\d{2}),(\d{3})', timestamp_str)
    if match:
        h, m, s, ms = map(int, match.groups())
        return h * 3600 + m * 60 + s + ms / 1000.0
    return 0.0


def format_time(seconds):
    """格式化时间显示"""
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes:02d}:{secs:06.3f}"


def analyze_subtitle_timing(subtitles):
    """分析字幕时间戳"""
    print("=" * 80)
    print("🔍 字幕时间戳精度分析报告")
    print("=" * 80)
    print()

    issues = []
    stats = {
        'total': len(subtitles),
        'too_long': 0,
        'too_short': 0,
        'too_fast': 0,
        'too_slow': 0,
        'overlapping': 0,
        'gaps': 0
    }

    for i, sub in enumerate(subtitles):
        duration = sub['end'] - sub['start']
        word_count = len(sub['text'].split())

        if word_count == 0:
            continue

        # 计算说话速度（词/秒）
        words_per_second = word_count / duration if duration > 0 else 0

        # 检测异常
        issues_found = []

        # 1. 持续时间过长（> 每词 1.0 秒）
        max_expected = word_count * 1.0
        if duration > max_expected:
            stats['too_long'] += 1
            issues_found.append(f"持续时间过长 ({duration:.2f}s，预期 ≤{max_expected:.2f}s)")

        # 2. 持续时间过短（< 每词 0.25 秒）
        min_expected = word_count * 0.25
        if duration < min_expected and duration > 0:
            stats['too_short'] += 1
            issues_found.append(f"持续时间过短 ({duration:.2f}s，预期 ≥{min_expected:.2f}s)")

        # 3. 说话速度过快（> 4 词/秒）
        if words_per_second > 4:
            stats['too_fast'] += 1
            issues_found.append(f"说话速度过快 ({words_per_second:.2f} 词/秒)")

        # 4. 说话速度过慢（< 1 词/秒）
        if words_per_second < 1 and words_per_second > 0:
            stats['too_slow'] += 1
            issues_found.append(f"说话速度过慢 ({words_per_second:.2f} 词/秒)")

        # 5. 与前一条重叠
        if i > 0 and sub['start'] < subtitles[i-1]['end']:
            stats['overlapping'] += 1
            overlap = subtitles[i-1]['end'] - sub['start']
            issues_found.append(f"与前一条重叠 ({overlap:.2f}s)")

        # 6. 与前一条间隔过大（> 3 秒）
        if i > 0:
            gap = sub['start'] - subtitles[i-1]['end']
            if gap > 3:
                stats['gaps'] += 1
                issues_found.append(f"间隔过大 ({gap:.2f}s)")

        if issues_found:
            issues.append({
                'sub': sub,
                'issues': issues_found,
                'duration': duration,
                'words_per_second': words_per_second
            })

    # 输出统计
    print("📊 总体统计:")
    print(f"   总字幕数: {stats['total']}")
    print(f"   ✅ 正常: {stats['total'] - len(issues)}")
    print(f"   ⚠️  异常: {len(issues)}")
    print()

    print("🚨 异常类型分布:")
    print(f"   持续时间过长: {stats['too_long']}")
    print(f"   持续时间过短: {stats['too_short']}")
    print(f"   说话速度过快: {stats['too_fast']}")
    print(f"   说话速度过慢: {stats['too_slow']}")
    print(f"   字幕重叠: {stats['overlapping']}")
    print(f"   间隔过大: {stats['gaps']}")
    print()

    # 输出前 20 个异常
    if issues:
        print("=" * 80)
        print(f"⚠️  前 {min(20, len(issues))} 个异常字幕:")
        print("=" * 80)
        print()

        for i, issue_data in enumerate(issues[:20], 1):
            sub = issue_data['sub']
            duration = issue_data['duration']
            wps = issue_data['words_per_second']

            print(f"【{i}】字幕 #{sub['id']}")
            print(f"   时间: {format_time(sub['start'])} --> {format_time(sub['end'])}")
            print(f"   文本: {sub['text'][:60]}{'...' if len(sub['text']) > 60 else ''}")
            print(f"   持续: {duration:.2f}s | 词数: {len(sub['text'].split())} | 速度: {wps:.2f} 词/秒")
            print(f"   问题:")
            for issue in issue_data['issues']:
                print(f"      • {issue}")
            print()

    # 计算平均说话速度
    valid_speeds = []
    for sub in subtitles:
        duration = sub['end'] - sub['start']
        word_count = len(sub['text'].split())
        if duration > 0 and word_count > 0:
            wps = word_count / duration
            if 1 <= wps <= 4:  # 只统计正常范围
                valid_speeds.append(wps)

    if valid_speeds:
        avg_speed = sum(valid_speeds) / len(valid_speeds)
        print("=" * 80)
        print(f"📈 平均说话速度: {avg_speed:.2f} 词/秒（基于 {len(valid_speeds)} 条正常字幕）")
        print(f"   正常范围: 2-4 词/秒")
        print("=" * 80)

    return stats, issues


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python test_timestamp_accuracy.py <SRT文件路径>")
        print()
        print("示例:")
        print("  python test_timestamp_accuracy.py output/video_llm_resplit.srt")
        sys.exit(1)

    srt_file = sys.argv[1]

    if not Path(srt_file).exists():
        print(f"❌ 文件不存在: {srt_file}")
        sys.exit(1)

    print(f"📄 分析文件: {srt_file}")
    print()

    subtitles = parse_srt(srt_file)

    if not subtitles:
        print("❌ 未找到字幕内容")
        sys.exit(1)

    stats, issues = analyze_subtitle_timing(subtitles)

    # 总结
    print()
    if len(issues) == 0:
        print("✅ 所有字幕时间戳都正常！")
    elif len(issues) < stats['total'] * 0.1:
        print(f"✅ 时间戳质量良好（异常率 {len(issues)/stats['total']*100:.1f}%）")
    elif len(issues) < stats['total'] * 0.3:
        print(f"⚠️  时间戳质量一般（异常率 {len(issues)/stats['total']*100:.1f}%）")
    else:
        print(f"❌ 时间戳质量较差（异常率 {len(issues)/stats['total']*100:.1f}%），建议重新生成")


if __name__ == "__main__":
    main()

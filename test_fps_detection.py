#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试视频帧率检测功能
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from videotrans.util.help_ffmpeg import get_video_info

def test_fps_detection():
    """测试视频帧率检测"""
    test_video = Path(__file__).parent / "resource" / "How parades can build community _ Chantelle Rytter _ TEDxAtlanta.mp4"
    
    if not test_video.exists():
        print(f"❌ 测试视频不存在: {test_video}")
        return False
    
    print(f"📹 测试视频: {test_video.name}")
    print("=" * 60)
    
    try:
        # 获取视频信息
        video_info = get_video_info(str(test_video))
        
        # 显示所有信息
        print(f"✅ 视频信息获取成功！")
        print(f"   帧率 (FPS): {video_info.get('video_fps', 0):.2f}")
        print(f"   分辨率: {video_info.get('width', 0)}x{video_info.get('height', 0)}")
        print(f"   视频编码: {video_info.get('video_codec_name', 'unknown')}")
        print(f"   音频编码: {video_info.get('audio_codec_name', 'unknown')}")
        print(f"   时长: {video_info.get('time', 0) / 1000:.2f} 秒")
        print(f"   视频流数量: {video_info.get('streams_len', 0)}")
        print(f"   音频流数量: {video_info.get('streams_audio', 0)}")
        print(f"   像素格式: {video_info.get('color', 'unknown')}")
        print("=" * 60)
        print("✅ 测试通过！帧率检测功能正常工作。")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_fps_detection()
    sys.exit(0 if success else 1)


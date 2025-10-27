#!/usr/bin/env python3
"""
Whisper 缓存功能测试脚本
用于验证缓存的创建、读取和验证功能
"""

import hashlib
import pickle
from pathlib import Path
import time

def get_file_hash(filepath):
    """计算文件的哈希值"""
    hash_obj = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            # 分块读取，避免大文件占用过多内存
            for chunk in iter(lambda: f.read(8192), b''):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except Exception as e:
        print(f'❌ 计算哈希值失败: {str(e)}')
        return None

def get_cache_key(video_file, srt_file=None):
    """生成缓存键"""
    video_hash = get_file_hash(video_file)
    if not video_hash:
        return None
    
    if srt_file:
        srt_hash = get_file_hash(srt_file)
        if not srt_hash:
            return None
        return f"{video_hash}_{srt_hash}"
    
    return video_hash

def save_cache(cache_dir, cache_key, all_words, language):
    """保存缓存"""
    if not cache_key:
        return False
    
    cache_file = cache_dir / f"{cache_key}.pkl"
    try:
        cache_data = {
            'all_words': all_words,
            'language': language,
            'timestamp': time.time()
        }
        with open(cache_file, 'wb') as f:
            pickle.dump(cache_data, f)
        print(f'✅ 缓存已保存: {cache_file.name}')
        print(f'   - 文件大小: {cache_file.stat().st_size / 1024:.2f} KB')
        print(f'   - 词数: {len(all_words)}')
        print(f'   - 语言: {language}')
        return True
    except Exception as e:
        print(f'❌ 保存缓存失败: {str(e)}')
        return False

def load_cache(cache_dir, cache_key):
    """加载缓存"""
    if not cache_key:
        return None
    
    cache_file = cache_dir / f"{cache_key}.pkl"
    if not cache_file.exists():
        print(f'❌ 缓存文件不存在: {cache_file.name}')
        return None
    
    try:
        with open(cache_file, 'rb') as f:
            cache_data = pickle.load(f)
        print(f'✅ 缓存加载成功: {cache_file.name}')
        print(f'   - 文件大小: {cache_file.stat().st_size / 1024:.2f} KB')
        print(f'   - 词数: {len(cache_data["all_words"])}')
        print(f'   - 语言: {cache_data["language"]}')
        print(f'   - 创建时间: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(cache_data["timestamp"]))}')
        return cache_data
    except Exception as e:
        print(f'❌ 读取缓存失败: {str(e)}')
        return None

def test_cache_basic():
    """测试基本的缓存功能"""
    print("=" * 60)
    print("测试 1: 基本缓存功能")
    print("=" * 60)
    
    # 创建临时缓存目录
    cache_dir = Path("./test_cache")
    cache_dir.mkdir(exist_ok=True)
    
    # 模拟词级时间戳数据
    test_words = [
        {'word': 'Hello', 'start': 0.0, 'end': 0.5},
        {'word': ' world', 'start': 0.5, 'end': 1.0},
        {'word': '!', 'start': 1.0, 'end': 1.2},
    ]
    test_language = 'en'
    
    # 生成一个测试缓存键
    test_cache_key = 'test_' + hashlib.sha256(b'test_video').hexdigest()
    
    print(f"\n📝 测试数据:")
    print(f"   - 缓存键: {test_cache_key}")
    print(f"   - 词数: {len(test_words)}")
    print(f"   - 语言: {test_language}")
    
    # 测试保存
    print(f"\n💾 测试保存缓存...")
    success = save_cache(cache_dir, test_cache_key, test_words, test_language)
    
    if not success:
        print("❌ 保存测试失败")
        return False
    
    # 测试加载
    print(f"\n📂 测试加载缓存...")
    loaded_data = load_cache(cache_dir, test_cache_key)
    
    if not loaded_data:
        print("❌ 加载测试失败")
        return False
    
    # 验证数据
    print(f"\n🔍 验证缓存数据...")
    if loaded_data['all_words'] == test_words:
        print("✅ 词数据匹配")
    else:
        print("❌ 词数据不匹配")
        return False
    
    if loaded_data['language'] == test_language:
        print("✅ 语言数据匹配")
    else:
        print("❌ 语言数据不匹配")
        return False
    
    # 清理测试文件
    print(f"\n🧹 清理测试文件...")
    cache_file = cache_dir / f"{test_cache_key}.pkl"
    cache_file.unlink()
    cache_dir.rmdir()
    print("✅ 测试完成！")
    
    return True

def test_file_hash():
    """测试文件哈希功能"""
    print("\n" + "=" * 60)
    print("测试 2: 文件哈希功能")
    print("=" * 60)
    
    # 创建测试文件
    test_file = Path("./test_video.txt")
    test_content = b"This is a test video file content"
    
    print(f"\n📝 创建测试文件...")
    test_file.write_bytes(test_content)
    print(f"   - 文件: {test_file}")
    print(f"   - 大小: {len(test_content)} bytes")
    
    # 计算哈希
    print(f"\n🔐 计算文件哈希...")
    hash1 = get_file_hash(test_file)
    print(f"   - 哈希值: {hash1}")
    
    # 再次计算，验证一致性
    print(f"\n🔄 再次计算哈希（验证一致性）...")
    hash2 = get_file_hash(test_file)
    print(f"   - 哈希值: {hash2}")
    
    if hash1 == hash2:
        print("✅ 哈希值一致")
    else:
        print("❌ 哈希值不一致")
        test_file.unlink()
        return False
    
    # 修改文件内容
    print(f"\n✏️  修改文件内容...")
    test_file.write_bytes(test_content + b" modified")
    
    # 计算新哈希
    print(f"\n🔐 计算修改后的哈希...")
    hash3 = get_file_hash(test_file)
    print(f"   - 哈希值: {hash3}")
    
    if hash3 != hash1:
        print("✅ 哈希值已改变（符合预期）")
    else:
        print("❌ 哈希值未改变（不符合预期）")
        test_file.unlink()
        return False
    
    # 清理
    print(f"\n🧹 清理测试文件...")
    test_file.unlink()
    print("✅ 测试完成！")
    
    return True

def test_cache_key_generation():
    """测试缓存键生成"""
    print("\n" + "=" * 60)
    print("测试 3: 缓存键生成")
    print("=" * 60)
    
    # 创建测试文件
    video_file = Path("./test_video.mp4")
    srt_file = Path("./test_subtitle.srt")
    
    video_file.write_bytes(b"video content")
    srt_file.write_bytes(b"subtitle content")
    
    print(f"\n📝 创建测试文件...")
    print(f"   - 视频: {video_file}")
    print(f"   - 字幕: {srt_file}")
    
    # 测试仅视频模式
    print(f"\n🔑 测试仅视频模式...")
    key1 = get_cache_key(video_file)
    print(f"   - 缓存键: {key1}")
    print(f"   - 长度: {len(key1)}")
    
    # 测试视频+字幕模式
    print(f"\n🔑 测试视频+字幕模式...")
    key2 = get_cache_key(video_file, srt_file)
    print(f"   - 缓存键: {key2}")
    print(f"   - 长度: {len(key2)}")
    
    if key1 != key2:
        print("✅ 不同模式生成不同的缓存键（符合预期）")
    else:
        print("❌ 不同模式生成相同的缓存键（不符合预期）")
        video_file.unlink()
        srt_file.unlink()
        return False
    
    # 清理
    print(f"\n🧹 清理测试文件...")
    video_file.unlink()
    srt_file.unlink()
    print("✅ 测试完成！")
    
    return True

def main():
    """运行所有测试"""
    print("\n" + "🚀 " * 20)
    print("Whisper 缓存功能测试")
    print("🚀 " * 20 + "\n")
    
    tests = [
        ("基本缓存功能", test_cache_basic),
        ("文件哈希功能", test_file_hash),
        ("缓存键生成", test_cache_key_generation),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n❌ 测试异常: {test_name}")
            print(f"   错误: {str(e)}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    # 输出总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"✅ 通过: {passed}/{len(tests)}")
    print(f"❌ 失败: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n🎉 所有测试通过！")
        return True
    else:
        print(f"\n⚠️  有 {failed} 个测试失败")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)


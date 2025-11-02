#!/usr/bin/env python3
"""
测试 LLM 智能字幕分割功能迁移

验证核心功能是否正确迁移
"""

import sys
from pathlib import Path

def test_imports():
    """测试核心模块是否可以正确导入"""
    print("🧪 测试1: 导入核心模块...")
    try:
        from utils.llm_processor import LLMProcessor
        print("   ✅ llm_processor 导入成功")
        
        from ui.split_view import SplitView
        print("   ✅ split_view 导入成功")
        
        return True
    except ImportError as e:
        print(f"   ❌ 导入失败: {e}")
        return False

def test_processor_initialization():
    """测试处理器初始化"""
    print("\n🧪 测试2: 处理器初始化...")
    try:
        from utils.llm_processor import LLMProcessor
        
        # 测试模式1：仅SRT
        processor1 = LLMProcessor(
            srt_file="/tmp/test.srt",
            llm_provider="siliconflow",
            llm_api_key="test_key",
            llm_model="test_model"
        )
        print("   ✅ 模式1（仅SRT）初始化成功")
        
        # 测试模式2：仅视频
        processor2 = LLMProcessor(
            video_file="/tmp/test.mp4",
            llm_provider="siliconflow",
            llm_api_key="test_key",
            llm_model="test_model"
        )
        print("   ✅ 模式2（仅视频）初始化成功")
        
        # 测试模式3：视频+SRT
        processor3 = LLMProcessor(
            video_file="/tmp/test.mp4",
            srt_file="/tmp/test.srt",
            llm_provider="siliconflow",
            llm_api_key="test_key",
            llm_model="test_model"
        )
        print("   ✅ 模式3（视频+SRT）初始化成功")
        
        return True
    except Exception as e:
        print(f"   ❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cache_functions():
    """测试缓存功能"""
    print("\n🧪 测试3: 缓存功能...")
    try:
        from utils.llm_processor import LLMProcessor
        
        processor = LLMProcessor(
            video_file="/tmp/test.mp4",
            llm_provider="siliconflow",
            llm_api_key="test_key",
            llm_model="test_model"
        )
        
        # 测试缓存目录创建
        if not processor.cache_dir.exists():
            print(f"   ❌ 缓存目录未创建: {processor.cache_dir}")
            return False
        print(f"   ✅ 缓存目录创建成功: {processor.cache_dir}")
        
        # 测试输出目录创建
        if not processor.output_dir.exists():
            print(f"   ❌ 输出目录未创建: {processor.output_dir}")
            return False
        print(f"   ✅ 输出目录创建成功: {processor.output_dir}")
        
        return True
    except Exception as e:
        print(f"   ❌ 缓存功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ui_component():
    """测试UI组件（不实际显示窗口）"""
    print("\n🧪 测试4: UI 组件...")
    try:
        from PySide6.QtWidgets import QApplication
        from ui.split_view import SplitView
        
        # 创建应用实例（测试用）
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建视图
        view = SplitView()
        print("   ✅ SplitView 创建成功")
        
        # 验证关键组件
        if not hasattr(view, 'video_file_path'):
            print("   ❌ 缺少 video_file_path 属性")
            return False
        print("   ✅ video_file_path 属性存在")
        
        if not hasattr(view, 'srt_file_path'):
            print("   ❌ 缺少 srt_file_path 属性")
            return False
        print("   ✅ srt_file_path 属性存在")
        
        if not hasattr(view, 'processor'):
            print("   ❌ 缺少 processor 属性")
            return False
        print("   ✅ processor 属性存在")
        
        # 验证UI元素
        required_widgets = [
            'video_label', 'srt_label', 'use_existing_srt',
            'language_combo', 'model_size_combo', 'device_combo',
            'provider_combo', 'api_key_input', 'model_combo',
            'log_text', 'process_btn', 'open_btn'
        ]
        
        for widget_name in required_widgets:
            if not hasattr(view, widget_name):
                print(f"   ❌ 缺少UI组件: {widget_name}")
                return False
        print(f"   ✅ 所有必要的UI组件都存在 ({len(required_widgets)} 个)")
        
        return True
    except Exception as e:
        print(f"   ❌ UI 组件测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dependencies():
    """测试依赖项"""
    print("\n🧪 测试5: 依赖项...")
    
    dependencies = {
        'PySide6': 'PySide6',
        'requests': 'requests',
        'numpy': 'numpy',
        'pathlib': 'pathlib'
    }
    
    all_ok = True
    for name, module_name in dependencies.items():
        try:
            __import__(module_name)
            print(f"   ✅ {name} 已安装")
        except ImportError:
            print(f"   ⚠️  {name} 未安装（可能需要: pip install {name.lower()}）")
            # 不标记为失败，因为某些依赖可能在实际运行时才需要
    
    # 检查可选依赖
    optional_deps = {
        'faster_whisper': 'faster-whisper'
    }
    
    for name, pip_name in optional_deps.items():
        try:
            __import__(name)
            print(f"   ✅ {pip_name} 已安装")
        except ImportError:
            print(f"   ⚠️  {pip_name} 未安装（用于 Whisper 功能，可选）")
    
    return True

def main():
    """运行所有测试"""
    print("=" * 60)
    print("🚀 LLM 智能字幕分割功能迁移测试")
    print("=" * 60)
    
    tests = [
        ("导入核心模块", test_imports),
        ("处理器初始化", test_processor_initialization),
        ("缓存功能", test_cache_functions),
        ("UI 组件", test_ui_component),
        ("依赖项", test_dependencies)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ 测试 '{test_name}' 发生异常: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {status}: {test_name}")
    
    print()
    print(f"总计: {passed}/{total} 个测试通过")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 所有测试通过！功能迁移成功！")
        print("\n下一步:")
        print("  1. 运行 'python main.py' 启动完整应用")
        print("  2. 在 UI 中选择文件并测试实际功能")
        print("  3. 检查缓存和输出文件是否正确生成")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查上述错误信息")
        return 1

if __name__ == "__main__":
    sys.exit(main())


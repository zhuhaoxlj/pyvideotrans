# LLM 配置共享说明

## 功能说明

**AI智能分割字幕** 和 **AI字幕翻译** 现在共享相同的 LLM 配置信息。这意味着：

- ✅ 在任一功能中配置 LLM，另一个功能自动同步
- ✅ 只需配置一次，两个功能都能使用
- ✅ 配置自动保存，下次打开自动加载
- ✅ 支持多个 LLM 提供商的 API Key 同时保存

## 共享的配置项

### 1. LLM 提供商
- OpenAI
- Claude/Anthropic  
- Gemini
- DeepSeek
- SiliconFlow
- Local（本地模型）

**共享方式**: 保存在 `config.params['llm_provider']`

### 2. 模型名称
- 如: `gpt-4o-mini`, `claude-3-5-sonnet-20241022`, `deepseek-ai/DeepSeek-V3.1-Terminus`

**共享方式**: 保存在 `config.params['llm_model']`

### 3. API Base URL
- 自定义的 API 地址
- 代理地址

**共享方式**: 保存在 `config.params['llm_base_url']`

### 4. API Key
- 每个提供商的 API 密钥
- 支持同时保存多个提供商的 Key

**共享方式**: 保存在 `.env` 文件中，根据提供商自动切换

## 配置保存位置

### config.params
```
~/Videos/pyvideotrans/params.json
```

保存内容：
```json
{
  "llm_provider": "openai",
  "llm_model": "gpt-4o-mini",
  "llm_base_url": "https://api.openai.com/v1"
}
```

### .env 文件
```
/Users/mark/Downloads/pyvideotrans/.env
```

保存内容：
```bash
OPENAI_API_KEY=sk-xxx...
ANTHROPIC_API_KEY=sk-ant-xxx...
GEMINI_API_KEY=AIza...
DEEPSEEK_API_KEY=sk-xxx...
SILICONFLOW_API_KEY=sk-xxx...
```

## 使用场景示例

### 场景 1: 首次配置

1. 打开 **AI智能分割字幕**
2. 选择 LLM 提供商: `OpenAI`
3. 输入 API Key: `sk-xxx...`
4. 选择模型: `gpt-4o-mini`
5. 配置自动保存

**结果**: 
- API Key 保存到 `.env` 文件中的 `OPENAI_API_KEY`
- 提供商、模型等保存到 `config.params`
- 打开 **AI字幕翻译** 时自动加载这些配置

### 场景 2: 切换提供商

在 **AI字幕翻译** 中：

1. 当前使用 `OpenAI`
2. 切换到 `SiliconFlow`
3. 自动加载之前保存的 `SILICONFLOW_API_KEY`
4. 自动加载之前保存的 `SiliconFlow` 模型配置

**结果**:
- 不需要重新输入 API Key
- 配置立即生效并保存
- 在 **AI智能分割字幕** 中打开也是相同配置

### 场景 3: 多提供商切换

1. 配置了 `OpenAI`: API Key + 模型
2. 配置了 `SiliconFlow`: API Key + 模型  
3. 配置了 `DeepSeek`: API Key + 模型

**结果**:
- 三个提供商的 API Key 都保存在 `.env` 中
- 切换提供商时自动加载对应的 Key
- 两个功能都可以快速切换使用

### 场景 4: 团队协作

假设团队成员 A 配置好了 LLM：

```bash
# .env 文件
SILICONFLOW_API_KEY=team-shared-key
```

```json
// params.json
{
  "llm_provider": "siliconflow",
  "llm_model": "deepseek-ai/DeepSeek-V3.1-Terminus",
  "llm_base_url": "https://api.siliconflow.cn/v1/chat/completions"
}
```

团队成员 B 克隆项目后：
- 复制 `.env` 文件
- `params.json` 由 Git 管理（或复制）
- 打开任一功能自动加载团队配置
- 无需重新配置

## 技术实现

### 自动保存

所有配置项在修改时自动保存：

```python
# 提供商改变时
winobj.provider_combo.currentIndexChanged.connect(provider_changed)

# 模型改变时
winobj.model_combo.currentTextChanged.connect(save_llm_config)

# API Key 改变时
winobj.api_key_input.textChanged.connect(save_api_key_to_env)

# Base URL 改变时  
winobj.base_url_input.textChanged.connect(save_llm_config)
```

### 自动加载

打开窗口时自动加载保存的配置：

```python
# 加载提供商
saved_provider = config.params.get('llm_provider', 'openai')
winobj.provider_combo.setCurrentData(saved_provider)

# 加载模型
saved_model = config.params.get('llm_model', '')
winobj.model_combo.setCurrentText(saved_model)

# 加载 Base URL
saved_base_url = config.params.get('llm_base_url', '')
winobj.base_url_input.setText(saved_base_url)

# 加载 API Key
load_api_key_from_env()
```

### 提供商切换

切换提供商时自动处理：

```python
def provider_changed(index):
    provider = winobj.provider_combo.currentData()
    
    # 1. 更新模型列表
    update_model_list(provider)
    
    # 2. 加载对应的 API Key
    load_api_key_from_env()
    
    # 3. 保存配置
    save_llm_config()
```

## 配置优先级

### API Key 读取顺序
1. 环境变量（优先级最高）
2. `.env` 文件
3. 手动输入

### 配置加载顺序
1. `config.params` 中的保存值
2. 默认值

## 注意事项

### 1. API Key 安全

- ⚠️ `.env` 文件不应提交到 Git
- ⚠️ 添加 `.env` 到 `.gitignore`
- ✅ 团队共享可使用 `.env.example` 模板

```bash
# .gitignore
.env

# .env.example（提交到 Git）
OPENAI_API_KEY=your-key-here
SILICONFLOW_API_KEY=your-key-here
```

### 2. 配置文件位置

- `params.json` 在用户主目录: `~/Videos/pyvideotrans/`
- `.env` 在项目根目录: `/path/to/pyvideotrans/`

### 3. 配置同步

- 配置是实时同步的
- 在一个功能中修改，另一个功能打开时会看到最新配置
- 如果两个窗口同时打开，需要重新打开才能看到同步

### 4. 多个模型

- 模型列表根据提供商动态更新
- 可以手动输入自定义模型名称
- 自定义模型也会被保存

## 最佳实践

### 推荐配置流程

1. **首次配置**
   ```
   打开任一功能 → 配置 LLM → 测试连接 → 开始使用
   ```

2. **日常使用**
   ```
   直接打开功能 → 配置自动加载 → 开始使用
   ```

3. **切换提供商**
   ```
   选择新提供商 → API Key 自动加载 → 调整模型（如需） → 开始使用
   ```

### 配置建议

1. **为每个常用提供商配置 API Key**
   - 这样切换时不需要重新输入

2. **使用稳定的模型作为默认**
   - 如: `gpt-4o-mini`, `deepseek-chat`

3. **测试连接后再使用**
   - 确保配置正确

4. **定期更新 API Key**
   - 增强安全性

## 故障排查

### 问题 1: 配置没有同步

**原因**: 可能是两个窗口同时打开

**解决**: 
```
关闭窗口 → 重新打开 → 配置会自动加载
```

### 问题 2: API Key 丢失

**检查**:
```bash
# 查看 .env 文件
cat /path/to/pyvideotrans/.env

# 查看 params.json
cat ~/Videos/pyvideotrans/params.json
```

**解决**: 重新输入 API Key，会自动保存

### 问题 3: 切换提供商后 API Key 为空

**原因**: 该提供商的 Key 没有保存过

**解决**: 输入 API Key，系统会自动保存

### 问题 4: 模型列表中没有想要的模型

**解决**: 
```
手动输入模型名称 → 系统会添加并保存
```

## 总结

通过配置共享机制：

- ✅ **提高效率**: 只需配置一次
- ✅ **降低错误**: 减少重复输入
- ✅ **统一管理**: 集中管理 API Key
- ✅ **无缝切换**: 快速切换提供商
- ✅ **自动持久化**: 配置自动保存

这使得 LLM 功能的使用更加便捷和高效！

---

**更新日期**: 2025-01-27  
**适用版本**: v1.0.0+


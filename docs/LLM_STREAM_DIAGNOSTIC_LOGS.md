# LLM 流式传输诊断日志说明

## 更新时间
2025-10-27

## 问题描述

用户反馈 LLM API 调用时会卡住，日志显示：
```
⏳ 正在调用 LLM API，请稍候...
📡 LLM 响应流:
```

之后没有任何输出，不知道卡在哪里。

## 解决方案

为 SiliconFlow 流式传输添加了详细的诊断日志，可以精确定位问题。

## 📊 新增的诊断日志

### 1. 请求准备阶段
```
🌐 连接到: https://api.siliconflow.cn/v1/chat/completions
📦 模型: deepseek-ai/DeepSeek-R1
📝 Prompt 长度: 2345 字符
```

**说明**：显示目标 URL、使用的模型和 Prompt 大小

### 2. 发送请求阶段
```
🔄 正在发送 HTTP 请求...
```

**说明**：表示正在建立连接并发送数据

### 3. 收到响应阶段
```
✅ 收到响应！(耗时: 1.23秒)
📊 HTTP 状态码: 200
📋 响应头: {'content-type': 'text/event-stream', ...}
```

**说明**：
- 显示从发送到收到响应的时间
- HTTP 状态码（200 表示成功）
- 响应头信息（可以看到是否真的是流式传输）

### 4. 开始读取流
```
🔄 开始读取流式数据...
```

**说明**：表示开始接收流式数据

### 5. 收到第一行数据
```
📥 收到第一行数据: data: {"id":"chatcmpl-xxx",...
```

**说明**：显示第一行数据内容，确认数据格式正确

### 6. 心跳日志（每 5 秒）
```
💓 接收中... (已处理 50 行, 25 个数据块)
💓 接收中... (已处理 120 行, 60 个数据块)
```

**说明**：证明数据正在持续接收，不是卡死了

### 7. 流式传输完成
```
🏁 流式传输完成！
```

**说明**：收到 `[DONE]` 标记，表示传输结束

### 8. 接收总结
```
📊 接收完成: 共 150 行, 75 个数据块, 68 个内容片段
📝 总内容长度: 1234 字符
```

**说明**：显示接收统计信息

## 🔍 错误诊断日志

### 请求超时
```
❌ 请求超时！(120秒)
```

**可能原因**：
- 网络连接问题
- 服务器响应慢
- 防火墙拦截

### 连接错误
```
❌ 连接错误: [Errno 61] Connection refused
```

**可能原因**：
- 无法连接到服务器
- DNS 解析失败
- 网络不通

### HTTP 错误
```
❌ HTTP 错误: 401
📋 错误详情: {"error": {"message": "Invalid API key", "type": "authentication_error"}}
```

**可能原因**：
- `401`: API Key 无效或过期
- `404`: 模型名称错误
- `429`: 超过速率限制
- `500`: 服务器内部错误

### JSON 解析失败
```
⚠️  JSON 解析失败: data: invalid json...
```

**可能原因**：
- 响应格式不正确
- 数据损坏
- 非标准格式

### 流式传输异常
```
⚠️  流式传输异常: Connection reset by peer
📋 错误堆栈: [完整的错误堆栈信息]
```

**可能原因**：
- 网络中断
- 服务器断开连接
- 读取超时

## 📋 完整的日志流程示例

### 正常情况
```
⏳ 正在调用 LLM API，请稍候...
📡 LLM 响应流:
   🌐 连接到: https://api.siliconflow.cn/v1/chat/completions
   📦 模型: deepseek-ai/DeepSeek-R1
   📝 Prompt 长度: 2345 字符
   🔄 正在发送 HTTP 请求...
   ✅ 收到响应！(耗时: 1.23秒)
   📊 HTTP 状态码: 200
   📋 响应头: {'content-type': 'text/event-stream', 'transfer-encoding': 'chunked'}
   🔄 开始读取流式数据...
   📥 收到第一行数据: data: {"id":"chatcmpl-xxx","object":"chat.completion.chunk",...
   [流式输出内容开始显示...]
   💓 接收中... (已处理 50 行, 25 个数据块)
   [继续流式输出...]
   💓 接收中... (已处理 100 行, 50 个数据块)
   [继续流式输出...]
   🏁 流式传输完成！
   📊 接收完成: 共 150 行, 75 个数据块, 68 个内容片段
   📝 总内容长度: 1234 字符
✅ LLM响应完成 (耗时: 12.5秒)
```

### 异常情况 - API Key 错误
```
⏳ 正在调用 LLM API，请稍候...
📡 LLM 响应流:
   🌐 连接到: https://api.siliconflow.cn/v1/chat/completions
   📦 模型: deepseek-ai/DeepSeek-R1
   📝 Prompt 长度: 2345 字符
   🔄 正在发送 HTTP 请求...
   ✅ 收到响应！(耗时: 0.35秒)
   📊 HTTP 状态码: 401
   📋 响应头: {'content-type': 'application/json'}
   ❌ HTTP 错误: 401
   📋 错误详情: {"error": {"message": "Invalid API key", "type": "authentication_error"}}
⚠️  LLM调用失败: HTTPError
```

### 异常情况 - 网络超时
```
⏳ 正在调用 LLM API，请稍候...
📡 LLM 响应流:
   🌐 连接到: https://api.siliconflow.cn/v1/chat/completions
   📦 模型: deepseek-ai/DeepSeek-R1
   📝 Prompt 长度: 2345 字符
   🔄 正在发送 HTTP 请求...
   [等待 120 秒...]
   ❌ 请求超时！(120秒)
⚠️  LLM调用失败: Timeout
```

### 异常情况 - 卡在读取流
```
⏳ 正在调用 LLM API，请稍候...
📡 LLM 响应流:
   🌐 连接到: https://api.siliconflow.cn/v1/chat/completions
   📦 模型: deepseek-ai/DeepSeek-R1
   📝 Prompt 长度: 2345 字符
   🔄 正在发送 HTTP 请求...
   ✅ 收到响应！(耗时: 1.23秒)
   📊 HTTP 状态码: 200
   📋 响应头: {'content-type': 'text/event-stream'}
   🔄 开始读取流式数据...
   [卡在这里，没有收到任何数据]
   💓 接收中... (已处理 0 行, 0 个数据块)  ← 5秒后出现
   💓 接收中... (已处理 0 行, 0 个数据块)  ← 10秒后出现
   💓 接收中... (已处理 0 行, 0 个数据块)  ← 15秒后出现
```

**问题**：服务器返回 200 但没有发送数据

## 🎯 根据日志定位问题

### 问题 1: 卡在"正在发送 HTTP 请求"
```
🔄 正在发送 HTTP 请求...
[卡住，没有下一条日志]
```

**原因**：网络连接问题或防火墙阻止
**解决**：
- 检查网络连接
- 检查防火墙设置
- 尝试使用代理
- 检查是否能 ping 通 `api.siliconflow.cn`

### 问题 2: 收到响应但卡在"开始读取流式数据"
```
✅ 收到响应！(耗时: 1.23秒)
📊 HTTP 状态码: 200
🔄 开始读取流式数据...
[卡住，没有收到第一行数据]
```

**原因**：服务器没有返回流式数据
**解决**：
- 检查响应头是否包含 `content-type: text/event-stream`
- 可能是模型不支持流式输出
- 可能是服务器端问题

### 问题 3: HTTP 401 错误
```
❌ HTTP 错误: 401
📋 错误详情: {"error": {"message": "Invalid API key"}}
```

**原因**：API Key 无效
**解决**：
- 检查 API Key 是否正确
- 检查 API Key 是否过期
- 重新生成 API Key

### 问题 4: HTTP 404 错误
```
❌ HTTP 错误: 404
📋 错误详情: {"error": {"message": "Model not found"}}
```

**原因**：模型名称错误
**解决**：
- 检查模型名称拼写
- 确认该模型在该平台是否可用
- 查看平台文档获取正确的模型名称

### 问题 5: 接收数据慢
```
💓 接收中... (已处理 10 行, 5 个数据块)  ← 5秒
💓 接收中... (已处理 12 行, 6 个数据块)  ← 10秒
💓 接收中... (已处理 15 行, 7 个数据块)  ← 15秒
```

**原因**：网络带宽低或服务器响应慢
**解决**：
- 等待完成（这是正常的，只是慢）
- 检查网络速度
- 考虑更换网络或时间段

## 🛠️ 技术实现

### 关键代码片段

```python
# 请求前日志
self.post(type='logs', text=f'   🌐 连接到: {url}')
self.post(type='logs', text=f'   📦 模型: {data["model"]}')

# 发送请求并计时
request_start = time.time()
response = requests.post(url, headers=headers, json=data, stream=True, timeout=120)
request_time = time.time() - request_start

# 响应后日志
self.post(type='logs', text=f'   ✅ 收到响应！(耗时: {request_time:.2f}秒)')
self.post(type='logs', text=f'   📊 HTTP 状态码: {response.status_code}')

# 心跳日志（每 5 秒）
if current_time - last_log_time > 5:
    self.post(type='logs', text=f'   💓 接收中... (已处理 {line_count} 行, {chunk_count} 个数据块)')
```

## 📝 使用建议

### 1. 首次使用时
- 仔细观察所有日志
- 确认每个阶段都正常
- 记录正常情况下的时间

### 2. 遇到问题时
- 查看卡在哪个阶段
- 对照本文档找原因
- 检查日志中的错误信息

### 3. 性能优化
- 观察"收到响应"的耗时
- 如果经常超过 5 秒，可能是网络问题
- 观察心跳日志的数据增长速度

## 🎉 总结

通过这些详细的诊断日志，你可以：

✅ **精确定位问题**：知道卡在哪个步骤
✅ **快速诊断**：根据错误信息找原因
✅ **监控进度**：实时了解接收状态
✅ **性能分析**：了解各阶段耗时

现在再也不会出现"不知道为什么卡住"的情况了！

---

**更新日期**: 2025-10-27  
**实现者**: AI Assistant  
**版本**: 1.0.0  
**状态**: ✅ 已完成


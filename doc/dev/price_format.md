
## price 格式说明
```json5
{
  "currency": "USD",  // 计价货币单位: USD, CNY, EUR 等
  "strategy": "input-tiered",  // 计价策略, 当前仅支持 input-tiered, 即根据输入长度分层计价
  "unit": "1M-token",  // 计价单位, 通常是 1M-token, 表示每百万token
  "tiers": [  // 分层计价的层级定义
    {
      "range": "[0,200k]",  // 输入长度范围. k:1024, m:1024*1024
      "input_text":  2.0,  // 输入文本 token 的价格
      "input_image": 2.0,  // 输入图像 token 的价格
      "input_video": 2.0,  // 输入视频 token 的价格
      "input_audio": 2.0,  // 输入音频 token 的价格
      "output_text": 12.0,  // 输出文本 token 的价格
      "output_image": 120.0,  // 输出图像 token 的价格
      "cached": {
        "strategy": "ttl",  // 缓存计价策略: 当前仅支持 ttl, 即根据缓存的 ttl 长短分层计价
        "ttl": [
          {
            "range": "(0,5m]",  // ttl 范围. 5m 表示 5分钟, 1h 表示 1小时
            "read_text": 0.5,   // 读取文本缓存 token 的价格
            "read_image": 0.5,  // 读取图像缓存 token 的价格
            "read_video": null,  // 不支持这种输入
            "read_audio": null,  // 不支持这种输入
            "write_text": 6.25,   // 写入文本缓存 token 的价格
            "write_image": 6.25,  // 写入图像缓存 token 的价格
            "write_video": null,  // 不支持这种输入
            "write_audio": null,  // 不支持这种输入
          },
          {
            "range": "(5m,1h]",  // ttl 范围. 5m 表示 5分钟, 1h 表示 1小时
            "read_text": 0.5,   // 读取文本缓存 token 的价格
            "read_image": 0.5,  // 读取图像缓存 token 的价格
            "read_video": null,  // 不支持这种输入
            "read_audio": null,  // 不支持这种输入
            "write_text": 10,   // 写入文本缓存 token 的价格
            "write_image": 10,  // 写入图像缓存 token 的价格
            "write_video": null,  // 不支持这种输入
            "write_audio": null,  // 不支持这种输入
          }
        ]
      }
    },
    {
      "range": "(200k,inf)", // 输入长度范围, inf 表示无穷大, 无所谓开闭区间
      "input_text":  4.0,    // 输入文本 token 的价格
      "input_image": 4.0,    // 输入图像 token 的价格
      "input_video": 4.0,    // 输入视频 token 的价格
      "input_audio": 4.0,    // 输入音频 token 的价格
      "output_text": 18.0,   // 输出文本 token 的价格
      "output_image": null,  // 不存在这种情况
      "cached": {
        "strategy": "ttl",  // 缓存计价策略: 当前仅支持 ttl, 即根据缓存的 ttl 长短分层计价
        "ttl": [
          {
            "range": "(0,5m]",  // ttl 范围. 5m 表示 5分钟, 1h 表示 1小时
            "read_text": 0.5,   // 读取文本缓存 token 的价格
            "read_image": 0.5,  // 读取图像缓存 token 的价格
            "read_video": null,  // 不支持这种输入
            "read_audio": null,  // 不支持这种输入
            "write_text": 6.25,   // 写入文本缓存 token 的价格
            "write_image": 6.25,  // 写入图像缓存 token 的价格
            "write_video": null,  // 不支持这种输入
            "write_audio": null,  // 不支持这种输入
          },
          {
            "range": "(5m,1h]",  // ttl 范围. 5m 表示 5分钟, 1h 表示 1小时
            "read_text": 0.5,   // 读取文本缓存 token 的价格
            "read_image": 0.5,  // 读取图像缓存 token 的价格
            "read_video": null,  // 不支持这种输入
            "read_audio": null,  // 不支持这种输入
            "write_text": 10,   // 写入文本缓存 token 的价格
            "write_image": 10,  // 写入图像缓存 token 的价格
            "write_video": null,  // 不支持这种输入
            "write_audio": null,  // 不支持这种输入
          }
        ]
      }
    }
  ]
}
```

## usage 格式说明

```json5
{
    "completion_tokens": 86,                 // 输出总 token 数
    "prompt_tokens": 64,                     // 输入总 token 数
    "total_tokens": 939,                     // 输入输出总 token 数
    "prompt_tokens_details": {
        "audio_tokens": null,                // 输入音频 token 数, 如果不支持音频输入或没有音频输入则为 null
        "cached_tokens": 0,                  // 读取缓存 token 数, 如果没有使用缓存则为 0 或 null. 这部分 token 数包含在 prompt_tokens 中, 但计费单价使用 cached_tokens 的价格
        "cache_creation_tokens": 0           // 写入缓存 token 数, 如果没有使用缓存则为 0 或 null. 写入缓存的时间根据输入参数确定
    },
    "completion_tokens_details": {
        "accepted_prediction_tokens": null,  // 启用 Predicted Outputs 时, 模型接受的预测输出 token 数. 如果没有启用 Predicted Outputs 或没有预测输出则为 null
        "rejected_prediction_tokens": null,  // 启用 Predicted Outputs 时, 模型拒绝的预测输出 token 数. 如果没有启用 Predicted Outputs 或没有预测输出则为 null
        "audio_tokens": null,                // 输出音频 token 数, 如果不支持音频输出或没有音频输出则为 null
        "reasoning_tokens": null,            // 推理 token 数, 仅包含模型推理使用的 token 数. 如果没有推理过程则为 null
        "text_tokens": 465                   // 输出文本 token 数, 仅包含模型生成的文本输出 token 数. 如果没有文本输出则为 null
    }
}
```

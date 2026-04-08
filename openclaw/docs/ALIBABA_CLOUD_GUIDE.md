# 阿里云通义千问(Qwen)配置指南

## 快速开始

### 1. 获取API密钥

1. 访问阿里云DashScope控制台: https://dashscope.console.aliyun.com/
2. 注册/登录账号
3. 开通DashScope服务
4. 创建API密钥 (API-KEY)

### 2. 配置OpenClaw

**方式A: 使用专用配置文件 (推荐)**

```bash
# 复制阿里云配置模板
cp alibaba-cloud-config.yaml openclaw-config.yaml

# 编辑文件,替换API密钥
# 将 api_key: "sk-your-dashscope-api-key" 
# 改为你的真实密钥
```

**方式B: 手动编辑配置文件**

编辑 `openclaw-config.yaml`:

```yaml
llms:
  default:
    provider: "alibaba"  # 或 "dashscope", "qwen", "openai"
    api_key: "sk-your-actual-api-key"  # 你的API密钥
    model: "qwen-turbo"  # 模型选择见下方
    base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
    temperature: 0.7
    max_tokens: 2000
```

**方式C: 使用环境变量**

编辑 `.env` 文件:

```bash
OPENCLAW_LLM_PROVIDER=alibaba
OPENCLAW_LLM_API_KEY=sk-your-actual-api-key
OPENCLAW_LLM_MODEL=qwen-turbo
```

### 3. 启动服务

```bash
openclaw start
```

---

## 可用模型

| 模型 | 说明 | 适用场景 |
|------|------|----------|
| qwen-turbo | 速度快,成本低 | 日常对话,简单任务 |
| qwen-plus | 性能均衡 | 复杂对话,代码生成 |
| qwen-max | 最强性能 | 专业任务,复杂推理 |
| qwen-long | 长文本支持 | 文档分析,长文总结 |

---

## 配置选项详解

### Provider名称 (任选其一)

```yaml
provider: "alibaba"      # 推荐
provider: "dashscope"    # 别名
provider: "qwen"         # 别名  
provider: "openai"       # 兼容模式(需设置base_url)
```

### 完整配置示例

```yaml
llms:
  default:
    provider: "alibaba"
    api_key: "sk-xxxxxxxxxxxxxxxx"
    model: "qwen-plus"
    base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
    temperature: 0.7        # 0-1,越高越创意
    max_tokens: 2000        # 最大生成token数
  
  # 可以配置多个模型
  fast:
    provider: "alibaba"
    api_key: "sk-xxxxxxxxxxxxxxxx"
    model: "qwen-turbo"
    
  powerful:
    provider: "alibaba"
    api_key: "sk-xxxxxxxxxxxxxxxx"
    model: "qwen-max"
```

---

## 测试配置

### 方法1: 命令行测试

```bash
# 查看配置的LLM
openclaw llms

# 应该显示:
# Configured LLM Providers
# +--------+----------+------------+-------------+
# | Name   | Provider | Model      | API Key Set |
# +--------+----------+------------+-------------+
# | default| alibaba  | qwen-turbo | Yes         |
# +--------+----------+------------+-------------+
```

### 方法2: 运行测试脚本

```bash
python test_client.py
```

### 方法3: 控制台对话测试

```bash
openclaw start

# 在提示符后输入:
> 你好,请用一句话介绍自己
[Bot]: 你好!我是通义千问,由阿里云开发的大型语言模型。
```

---

## 常见问题

### Q1: API密钥在哪里获取?

访问: https://dashscope.console.aliyun.com/apiKey

### Q2: 如何查看用量和费用?

访问: https://dashscope.console.aliyun.com/usage

### Q3: 支持的地区?

- 中国大陆: dashscope.aliyuncs.com
- 国际: dashscope-intl.aliyuncs.com

### Q4: 如何切换国际endpoint?

```yaml
llms:
  default:
    provider: "alibaba"
    api_key: "your-key"
    base_url: "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
```

### Q5: 遇到认证错误?

检查:
1. API密钥是否正确复制(无空格)
2. 账户是否有余额
3. DashScope服务是否已开通

### Q6: 如何调整回复长度?

```yaml
llms:
  default:
    max_tokens: 500    # 减少长度
    # 或
    max_tokens: 4000   # 增加长度
```

---

## 高级用法

### 多模型配置

```yaml
llms:
  # 默认使用turbo(快速便宜)
  default:
    provider: "alibaba"
    api_key: "sk-xxx"
    model: "qwen-turbo"
  
  # 复杂任务用max
  advanced:
    provider: "alibaba"
    api_key: "sk-xxx"
    model: "qwen-max"
```

在代码中指定模型:

```python
response = await llm_manager.chat(
    messages,
    provider_name="advanced"  # 使用qwen-max
)
```

### 自定义温度参数

```yaml
llms:
  creative:  # 高创意模式
    provider: "alibaba"
    model: "qwen-plus"
    temperature: 0.9
  
  precise:  # 精确模式
    provider: "alibaba"
    model: "qwen-plus"
    temperature: 0.3
```

---

## 性能优化建议

1. **选择合适的模型**
   - 日常对话: qwen-turbo
   - 代码生成: qwen-plus
   - 复杂推理: qwen-max

2. **调整temperature**
   - 事实问答: 0.3-0.5
   - 创意写作: 0.7-0.9
   - 代码生成: 0.2-0.4

3. **设置合理的max_tokens**
   - 短回复: 500-1000
   - 中等回复: 1500-2000
   - 长回复: 3000-4000

---

## 参考资料

- DashScope官方文档: https://help.aliyun.com/zh/dashscope/
- OpenAI兼容接口: https://help.aliyun.com/zh/dashscope/developer-reference/compatibility-of-openai-with-dashscope
- API定价: https://help.aliyun.com/zh/dashscope/product-overview/pricing

---

## 技术支持

遇到问题?
1. 查看官方文档
2. 检查API密钥和配置
3. 查看日志输出
4. 提交Issue

祝使用愉快! 🚀

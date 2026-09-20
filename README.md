# TypeSafe API 独立测试

这个目录不依赖仓库里的其他项目，用 TypeSafe 官方 Python SDK 调用 System One API。

TypeSafe 的定位不是普通聊天生成，而是把一个 `state`（文本、JSON 对象或数组）同时交给多个窄问题，返回可以直接给程序使用的结构化答案：

- `Noul`：是/否概率，字段为 `noul`，范围 0 到 1。
- `Choice`：从有限选项中选择，返回 `choice`、每个选项的 `probabilities` 和 `confidence`。
- `Score`：按有序标准评分，返回 `score`、`probabilities` 和 `confidence`。

## 准备

需要 Python 3.10+、`uv`，以及控制台创建的 API Key。脚本会自动读取当前目录中的 `.env`。

```bash
cd /usr/local/work/data1/ai/chrome_private/typesafe_api_test
cp .env.example .env
# 然后把 .env 中的 TYPESAFE_API_KEY 改成真实值
uv sync
```

`.env.example` 只是模板，脚本不会读取它。正确文件名必须是 `.env`，内容不要带 Markdown 转义符：

```dotenv
TYPESAFE_API_KEY=your-key-here
TYPESAFE_DEFAULT_MODEL=jev-latest
```

## 运行

用内置客服工单示例发起一次请求：

```bash
uv run python main.py
```

评估自己的文本：

```bash
uv run python main.py '客户说已经扣款两次，要求马上退款'
```

列出当前账号可用的模型：

```bash
uv run python main.py --list-models
```

指定模型：

```bash
uv run python main.py --model jev-1.13.0 '这条消息是否需要人工优先处理？'
```

脚本打印 API 原始 JSON，因此可以直接看到服务端实际使用的版本模型、三种答案、概率/置信度和 token 用量。`jev-latest` 是稳定别名；如果需要结果可复现，使用版本号（当前文档示例为 `jev-1.13.0`）。

## 当前限制

文档显示当前 Jev 接受文本、JSON 对象或文本数组，不直接接受图片、音频、视频；这些内容需要先转成文本或结构化字段。英文是主要训练语言，中文等语言应先用自己的数据验证准确率和置信度。

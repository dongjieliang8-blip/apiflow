# APIFlow

> 多智能体 AI API 测试与文档生成流水线

## 项目简介

APIFlow 是一个基于多智能体协作的 API 测试与文档自动生成工具。通过四个专业化智能体（Agent）按顺序协作，自动完成从 API 端点分析、测试用例生成、OpenAPI 文档创建到质量验证的完整流程。

### 解决的痛点

- **手动编写测试耗时费力**：传统方式需要逐个端点手写测试用例，效率低下
- **文档与代码不同步**：API 更新后文档往往滞后，导致前后端协作困难
- **测试覆盖不全面**：人工测试容易遗漏边界情况和异常路径
- **质量标准不一致**：缺乏统一的质量验证标准和自动化检查

### 流水线架构

```
Analyzer >> Tester >> Documenter >> Validator
```

| 智能体 | 职责 | 输出 |
|--------|------|------|
| **Analyzer** | 分析源码，提取 API 端点定义 | 端点列表、请求/响应模型、认证需求 |
| **Tester** | 为每个端点生成测试用例 | 测试套件：正常路径、边界值、异常情况、认证测试 |
| **Documenter** | 生成 OpenAPI 3.0 文档 | 完整的 Swagger/OpenAPI 规范文件 |
| **Validator** | 质量验证与一致性检查 | 质量评分、覆盖报告、改进建议 |

## 快速开始

### 环境要求

- Python 3.9+
- DeepSeek API 密钥

### 安装

```bash
# 克隆项目
git clone <your-repo-url>
cd apiflow

# 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # macOS/Linux

# 安装依赖
pip install -r requirements.txt
```

### 配置

复制 `.env.example` 为 `.env`，填入你的 API 密钥：

```bash
cp .env.example .env
```

编辑 `.env`：

```
DEEPSEEK_API_KEY=sk-your-deepseek-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
APIFLOW_MODEL=deepseek-chat
```

### 使用方法

**运行完整流水线：**

```bash
python -m src.main run demo/sample_api.py --base-url http://localhost:5000
```

**仅运行分析：**

```bash
python -m src.main analyze-only demo/sample_api.py
```

**查看当前配置：**

```bash
python -m src.main config
```

## 命令行选项

### `run` -- 运行完整流水线

```
Usage: python -m src.main run [OPTIONS] SOURCE

Options:
  --base-url TEXT       API 基础 URL（默认: http://localhost:5000）
  -o, --output TEXT     报告输出文件（默认: apiflow_report.json）
  --model TEXT          模型名称覆盖
  --temperature FLOAT   温度参数（默认: 0.3）
```

### `analyze-only` -- 仅分析端点

```
Usage: python -m src.main analyze-only [OPTIONS] SOURCE

仅运行 Analyzer 智能体，提取 API 端点信息。
```

### `config` -- 查看配置

```
Usage: python -m src.main config

显示当前 API 密钥（脱敏）、模型名称、基础 URL 等配置。
```

## 项目结构

```
apiflow/
├── .env.example              # 环境变量模板
├── .gitignore
├── README.md
├── requirements.txt          # Python 依赖
├── APPLICATION.md            # 申请材料
├── demo/
│   └── sample_api.py         # 示例 FastAPI 应用
├── src/
│   ├── __init__.py
│   ├── main.py               # CLI 入口（Click）
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── analyzer.py       # 端点分析智能体
│   │   ├── tester.py         # 测试用例生成智能体
│   │   ├── documenter.py     # OpenAPI 文档生成智能体
│   │   └── validator.py      # 质量验证智能体
│   └── utils/
│       ├── __init__.py
│       └── api.py            # DeepSeek API 封装
└── tests/
    └── __init__.py
```

## 示例输出

运行完整流水线后，会生成 `apiflow_report.json`，包含：

```json
{
  "source": "demo/sample_api.py",
  "base_url": "http://localhost:5000",
  "analysis": {
    "endpoints": [...],
    "total_endpoints": 7,
    "framework": "FastAPI"
  },
  "tests": {
    "test_suite": [...],
    "total_tests": 28
  },
  "documentation": {
    "openapi": "3.0.3",
    "paths": {...}
  },
  "validation": {
    "validation_passed": true,
    "score": 85,
    "issues": [...],
    "recommendations": [...]
  }
}
```

## 支持的 API 框架

APIFlow 通过分析源码来提取端点信息，理论上支持任何基于 Python 的 Web 框架：

- **FastAPI** -- 推荐，原生支持 OpenAPI
- **Flask** -- 通过 flask-smorest 或手写路由
- **Django REST Framework** -- 通过 @api_view 装饰器
- **Starlette** -- 底层 ASGI 框架

## 技术栈

- **CLI 框架**: Click -- 命令行参数解析与子命令
- **终端美化**: Rich -- 彩色输出、表格、进度条
- **HTTP 客户端**: httpx -- 异步 HTTP 请求（调用 DeepSeek API）
- **数据模型**: Pydantic -- 结构化数据验证
- **环境配置**: python-dotenv -- .env 文件加载

## License

MIT

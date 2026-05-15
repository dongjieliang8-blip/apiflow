# APIFlow -- 申请材料

## 项目基本信息

- **项目名称**: APIFlow
- **项目类型**: 多智能体 AI API 测试与文档生成流水线
- **技术栈**: Python, Click, Rich, httpx, Pydantic, DeepSeek API
- **GitHub**: （待填写）

## 项目描述

APIFlow 是一个多智能体 AI API 测试与文档自动生成流水线。通过四个专业化智能体（Analyzer >> Tester >> Documenter >> Validator）按顺序协作，自动完成从 API 端点分析、测试用例生成、OpenAPI 文档创建到质量验证的完整流程。

### 解决的核心问题

在后端开发中，API 测试和文档编写是两个极其耗时且容易出错的环节：

1. **测试编写效率低**：一个包含 10 个端点的 API，手动编写完整测试用例可能需要数小时。每个端点需要覆盖正常路径、边界值、异常情况、认证场景等，工作量巨大。

2. **文档与代码脱节**：API 文档往往是手动维护的，代码更新后文档很难及时同步，导致前后端协作困难，接口对接频繁出错。

3. **测试覆盖不全面**：人工测试容易遗漏边界情况（如空字符串输入、极大数值、特殊字符等），导致线上 bug。

4. **质量标准不统一**：不同开发者的测试和文档质量参差不齐，缺乏统一的验证标准。

### 解决方案

APIFlow 使用多智能体协作模式，将上述流程自动化：

- **Analyzer（分析器）**：扫描源码文件，自动识别所有 API 端点（路由、参数、请求体、响应模型、认证需求）
- **Tester（测试器）**：基于分析结果，为每个端点生成全面的测试用例（正常路径、边界测试、异常输入、认证测试）
- **Documenter（文档器）**：生成符合 OpenAPI 3.0 标准的完整 API 文档，可直接导入 Swagger UI
- **Validator（验证器）**：对流水线输出进行质量检查，评估测试覆盖率、文档一致性，给出评分和改进建议

### 技术亮点

1. **LLM 驱动的智能分析**：使用 DeepSeek 大语言模型理解代码语义，比静态分析更准确
2. **结构化输出**：所有智能体输出严格的 JSON 格式，确保流水线数据流转可靠
3. **框架无关**：支持 FastAPI、Flask、Django 等任何 Python Web 框架
4. **质量闭环**：Validator 智能体对整个流水线输出做一致性验证，确保端点分析、测试用例、文档三者对齐

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

## 使用方式

```bash
# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 DEEPSEEK_API_KEY

# 安装依赖
pip install -r requirements.txt

# 运行完整流水线
python -m src.main run demo/sample_api.py

# 查看输出报告
cat apiflow_report.json
```

## 多智能体协作模式说明

APIFlow 采用经典的流水线（Pipeline）架构，四个智能体各司其职：

1. **Analyzer** -- 负责"理解"：解析源码，提取端点元信息（方法、路径、参数、响应、认证）
2. **Tester** -- 负责"验证"：基于端点信息生成测试用例，覆盖正常和异常路径
3. **Documenter** -- 负责"文档"：将端点信息转化为标准 OpenAPI 3.0 规范
4. **Validator** -- 负责"把关"：对比三个阶段的输出，检查一致性和完整性，输出质量评分

这种流水线设计的优势：
- 每个智能体专注单一职责，prompt 更精确，输出质量更高
- 后续智能体可以利用前序智能体的输出作为上下文，实现信息增值
- Validator 作为最后一环，对整体质量进行兜底检查

## 与现有方案的对比

| 特性 | 手动测试/文档 | Postman + 手动 | APIFlow |
|------|-------------|---------------|---------|
| 测试编写效率 | 低 | 中 | 高 |
| 文档同步性 | 差 | 中 | 好（自动生成） |
| 边界测试覆盖 | 不全面 | 取决于使用者 | 自动覆盖 |
| 质量验证 | 无 | 无 | 自动评分 |
| 学习成本 | 低 | 中 | 低（一条命令） |
| 框架支持 | 通用 | 通用 | Python 框架 |

## 未来规划

1. **实际执行测试**：不仅生成测试用例，还能通过 httpx 实际发送请求并验证响应
2. **CI/CD 集成**：支持在 GitHub Actions / GitLab CI 中自动运行
3. **增量分析**：只分析变更的端点，提升大型项目的效率
4. **多语言支持**：扩展到 Go (Gin/Echo)、Java (Spring Boot) 等框架
5. **测试报告可视化**：生成 HTML 测试报告，包含覆盖率图表

# arXiv 论文深度研读报告生成器

自动下载 arXiv 论文 LaTeX 源码，提取图片，使用 LLM 生成深度研读报告。

## 功能

- **LaTeX 解析**: 下载并解析 arXiv 论文源码
- **图片提取**: 自动提取论文中的图片资源
- **LLM 深度阅读**: 基于分类的智能阅读指南
- **图文报告**: 生成 Markdown + PDF 格式的研读报告

## 安装

```bash
# 克隆仓库
git clone https://github.com/gcmarks/arxiv-paper-reader.git
cd arxiv-paper-reader

# 安装依赖
cd openclaw-skills-arxiv-reader
pip install -r requirements.txt
pip install "httpx[socks]"

# 安装 Playwright (用于 PDF 生成)
pip install playwright
playwright install chromium
```

## 配置

编辑 `openclaw-skills-arxiv-reader/.env`:

```bash
LLM_BASE_URL=https://api.openai.com/v1  # 或其他 API
LLM_API_KEY=your_api_key
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.6
LLM_MAX_TOKENS=32000
```

## 使用

### 单篇论文

```bash
cd openclaw-skills-arxiv-reader
python main.py --arxiv-id 2603.12644
```

### 批量处理

```bash
python main.py --arxiv-ids 2603.12644 2603.11853 2603.10387
```

## 输出

```
~/workspace/papers/{paper_id}/
├── {paper_id}.pdf              # 原文 PDF
├── {paper_id}_研读报告.md       # Markdown 报告
├── {paper_id}_研读报告.pdf      # PDF 报告
├── latex/                      # LaTeX 源码
└── images/                     # 提取的图片
```

## 报告结构

1. 论文元信息
2. 一句话总结
3. 动机与核心创新
4. 架构设计
5. 工具使用
6. 记忆管理
7. 多 Agent 协作
8. 评估方法
9. 对比分析
10. 局限性

## 支持的分类

- `agent_systems`: Agent 系统相关
- `benchmark`: 基准测试
- `llm_training`: LLM 训练
- `multimodal`: 多模态
- `rag_and_retrieval`: RAG 与检索
- `general`: 通用

## License

MIT

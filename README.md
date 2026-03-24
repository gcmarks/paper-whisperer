# arXiv Paper Reader

**AgentSkill** - arXiv 论文深度研读报告生成器

自动下载 arXiv 论文 LaTeX 源码，提取图片，使用 LLM 生成深度研读报告。

## 安装

```bash
openclaw skills add https://github.com/gcmarks/arxiv-paper-reader
```

或手动安装：

```bash
cd ~/.openclaw/skills
git clone https://github.com/gcmarks/arxiv-paper-reader.git
cd arxiv-paper-reader/openclaw-skills-arxiv-reader
pip install -r requirements.txt
```

## 配置

编辑 `openclaw-skills-arxiv-reader/.env`:

```bash
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=your_api_key
LLM_MODEL=gpt-4
```

## 使用

```bash
cd ~/.openclaw/skills/arxiv-paper-reader/openclaw-skills-arxiv-reader
python main.py --arxiv-id 2603.12644
```

## 子技能

### arxiv-latex-report

下载 LaTeX 源码，提取图片，生成图文报告。

### arxiv-deep-reader

LLM 驱动的深度阅读，支持分类：
- `agent_systems`: Agent 系统
- `benchmark`: 基准测试
- `llm_training`: LLM 训练
- `multimodal`: 多模态
- `rag_and_retrieval`: RAG 检索
- `general`: 通用

## 输出

```
~/workspace/papers/{paper_id}/
├── {paper_id}.pdf              # 原文
├── {paper_id}_研读报告.md       # Markdown
├── {paper_id}_研读报告.pdf      # PDF
├── latex/                      # 源码
└── images/                     # 图片
```

## License

MIT

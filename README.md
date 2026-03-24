# arXiv Paper Reader

**OpenClaw AgentSkill** - arXiv 论文深度研读报告生成器

为 [OpenClaw](https://github.com/openclaw/openclaw) 设计的论文阅读技能，自动下载 arXiv 论文 LaTeX 源码，提取图片，使用 LLM 生成深度研读报告。

![OpenClaw](https://img.shields.io/badge/OpenClaw-AgentSkill-blue)
![Python](https://img.shields.io/badge/Python-3.10+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 效果展示

### 论文图表提取

自动从 LaTeX 源码提取论文图片：

| 架构图 | 风险分类图 | 防御架构图 |
|--------|-----------|-----------|
| ![](docs/images/1.png) | ![](docs/images/2.png) | ![](docs/images/3.png) |

### 深度研读报告

生成的报告包含：

- 📄 **论文元信息** - 标题、作者、单位、arXiv 链接
- 🎯 **一句话总结** - 快速把握核心贡献
- 🏗️ **架构设计** - 系统模块、协作机制
- 🔧 **工具使用** - 工具调用、接口设计
- 🧠 **记忆管理** - 长短期记忆、状态存储
- 🤝 **多 Agent 协作** - 通信、角色分配
- 📊 **评估方法** - 指标、基准测试
- ⚖️ **对比分析** - 与现有方法对比
- ⚠️ **局限性** - 未解决问题

### 示例报告

[📥 下载示例 PDF](docs/sample-report.pdf) - OpenClaw 安全论文深度研读报告 (2603.12644)

---

## 安装

### 方式一：OpenClaw CLI

```bash
openclaw skills add https://github.com/gcmarks/paper-whisperer
```

### 方式二：手动安装

```bash
cd ~/.openclaw/skills
git clone https://github.com/gcmarks/paper-whisperer.git
cd arxiv-paper-reader/openclaw-skills-arxiv-reader
pip install -r requirements.txt
pip install "httpx[socks]"
```

### 安装 PDF 生成依赖

```bash
pip install playwright markdown
playwright install chromium
```

---

## 配置

复制并编辑配置文件：

```bash
cd ~/.openclaw/skills/arxiv-paper-reader/openclaw-skills-arxiv-reader
cp .env.example .env
```

编辑 `.env`：

```bash
# 百炼 API
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_API_KEY=your_api_key
LLM_MODEL=qwen3.5-plus

# 或 OpenAI API
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=your_api_key
LLM_MODEL=gpt-4
```

---

## 使用

### 命令行

```bash
cd ~/.openclaw/skills/arxiv-paper-reader/openclaw-skills-arxiv-reader

# 单篇论文
python main.py --arxiv-id 2603.12644

# 查看支持的分类
python main.py --list
```

### 在 OpenClaw 中使用

发送 arXiv 链接给 OpenClaw，说：

> "帮我深度分析这篇论文：https://arxiv.org/abs/2603.12644"

---

## 子技能

### arxiv-latex-report

下载 LaTeX 源码，提取图片，生成图文报告。

**功能**：
- 下载 arXiv 源码包 (tar.gz)
- 解析 `.tex` 文件结构
- 提取所有图片资源
- 生成 Markdown + PDF 报告

### arxiv-deep-reader

LLM 驱动的深度阅读，按论文分类生成研读笔记。

**支持分类**：

| 分类 | 描述 |
|------|------|
| `agent_systems` | Agent 系统相关 |
| `benchmark` | 基准测试 |
| `llm_training` | LLM 训练 |
| `multimodal` | 多模态 |
| `rag_and_retrieval` | RAG 与检索 |
| `technique_report` | 技术报告 |
| `general` | 通用 |

---

## 输出

```
~/workspace/papers/{paper_id}/
├── {paper_id}.pdf                    # 原文 PDF
├── {paper_id}_研读报告.md             # Markdown 报告
├── {paper_id}_研读报告.pdf            # PDF 报告（含嵌入图片）
├── latex/                            # LaTeX 源码
│   ├── main.tex
│   └── imgs/
└── images/                           # 提取的图片
    ├── 1.png
    ├── 2.png
    └── ...
```

---

## 技术细节

### LaTeX 解析

- 支持多层 `\input{}` 和 `\include{}`
- 提取 figure 环境中的图片路径和 caption
- 支持 ICML、NeurIPS 等常见会议格式
- 自动处理相对路径

### LLM 阅读

- **Pass 1**: 快速理解，分类论文
- **Pass 2**: 深度阅读，按分类指南分析
- **Pass 3**: 附录补充（可选）

### PDF 生成

- 使用 Playwright Chromium 渲染
- 图片自动嵌入为 base64
- 支持中文显示
- 自动居中、缩放

---

## 依赖

| 包 | 用途 |
|----|------|
| `httpx` | HTTP 请求 |
| `openai` | LLM API |
| `playwright` | PDF 渲染 |
| `markdown` | Markdown 转 HTML |

---

## 已知问题

1. 部分论文不提供 LaTeX 源码，会回退到 PDF 文本提取
2. 5 分钟超时可能不够深度阅读，建议设置 10+ 分钟
3. 图片嵌入会增大 PDF 体积

---

## 相关链接

- [OpenClaw](https://github.com/openclaw/openclaw) - 开源 AI Agent 框架
- [ClawHub](https://clawhub.com) - OpenClaw Skills 市场
- [OpenClaw Docs](https://docs.openclaw.ai) - 文档

---

## License

MIT
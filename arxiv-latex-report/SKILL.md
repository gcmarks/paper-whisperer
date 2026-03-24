---
name: arxiv-latex-report
description: 下载 arXiv 论文 LaTeX 源码，解析结构，生成图文并茂的深度阅读报告。当用户要求"图文报告"、"带图的论文分析"或提供 arXiv 链接并要求深度分析时触发。
allowed-tools: Read, Write, Exec
---

# arXiv LaTeX 源码解析与图文报告生成

从 arXiv 下载 LaTeX 源码，提取完整结构（摘要、章节、公式、图表），生成图文并茂的专业阅读报告。

## 核心能力

1. **源码下载** — 获取 arXiv 论文的原始 LaTeX 文件
2. **结构解析** — 识别标题、作者、摘要、章节、公式、图表
3. **图片提取** — 从源码包中提取所有图片资源
4. **双模报告** — Part A 深度分析 + Part B 核心提炼，图文混排

## 工作流程

### Step 1: 下载 LaTeX 源码

```bash
# 创建工作目录
mkdir -p ~/workspace/papers/{paper_id}/latex
cd ~/workspace/papers/{paper_id}/latex

# 下载源码包
curl -L -o source.tar.gz "https://arxiv.org/e-print/{paper_id}"

# 解压
tar -xzf source.tar.gz

# 查找主 tex 文件
ls *.tex
```

**注意**: 部分论文不提供源码（只有 PDF），此时回退到 trafilatura 提取 PDF 文本。

### Step 2: 解析 LaTeX 结构

使用 Python 解析 `.tex` 文件：

```python
import re
from pathlib import Path

def parse_latex(tex_content):
    """解析 LaTeX 文件结构"""
    
    result = {
        'title': '',
        'authors': [],
        'abstract': '',
        'sections': [],
        'figures': [],
        'tables': [],
        'equations': [],
        'citations': []
    }
    
    # 提取标题
    title_match = re.search(r'\\title\{([^}]+)\}', tex_content, re.DOTALL)
    if title_match:
        result['title'] = clean_latex(title_match.group(1))
    
    # 提取作者
    author_match = re.search(r'\\author\{([^}]+)\}', tex_content, re.DOTALL)
    if author_match:
        result['authors'] = parse_authors(author_match.group(1))
    
    # 提取摘要
    abstract_match = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', tex_content, re.DOTALL)
    if abstract_match:
        result['abstract'] = clean_latex(abstract_match.group(1))
    
    # 提取章节
    section_pattern = r'\\(section|subsection|subsubsection)\{([^}]+)\}(.*?)(?=\\(section|subsection|subsubsection|\\begin\{references\}|$))'
    for match in re.finditer(section_pattern, tex_content, re.DOTALL):
        level = match.group(1)
        title = clean_latex(match.group(2))
        content = clean_latex(match.group(3))
        result['sections'].append({
            'level': level,
            'title': title,
            'content': content
        })
    
    # 提取图片
    figure_pattern = r'\\begin\{figure\}.*?\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}.*?\\caption\{([^}]+)\}.*?\\end\{figure\}'
    for match in re.finditer(figure_pattern, tex_content, re.DOTALL):
        result['figures'].append({
            'path': match.group(1),
            'caption': clean_latex(match.group(2))
        })
    
    # 提取表格
    table_pattern = r'\\begin\{table\}.*?\\caption\{([^}]+)\}.*?\\begin\{tabular\}(.*?)\\end\{tabular\}.*?\\end\{table\}'
    for match in re.finditer(table_pattern, tex_content, re.DOTALL):
        result['tables'].append({
            'caption': clean_latex(match.group(1)),
            'content': match.group(2)
        })
    
    # 提取公式（编号的）
    eq_pattern = r'\\begin\{equation\}(.*?)\\end\{equation\}'
    for match in re.finditer(eq_pattern, tex_content, re.DOTALL):
        result['equations'].append(clean_latex(match.group(1)))
    
    return result

def clean_latex(text):
    """清理 LaTeX 标记"""
    # 移除注释
    text = re.sub(r'%.*?\n', '\n', text)
    # 移除常见标记
    text = re.sub(r'\\text(bf|it|tt)\{([^}]+)\}', r'\2', text)
    text = re.sub(r'\\emph\{([^}]+)\}', r'\1', text)
    text = re.sub(r'\\cite\{[^}]+\}', '[cite]', text)
    text = re.sub(r'\\ref\{[^}]+\}', '[ref]', text)
    text = re.sub(r'\\label\{[^}]+\}', '', text)
    text = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', text)
    text = re.sub(r'[{}\\]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
```

### Step 3: 提取图片资源

```bash
# 查找所有图片
find . -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.pdf" -o -name "*.eps" \)

# 复制到报告目录
mkdir -p ~/workspace/papers/{paper_id}/images
cp *.png *.jpg *.pdf *.eps ~/workspace/papers/{paper_id}/images/ 2>/dev/null
```

### Step 4: 生成图文报告

报告结构：

```markdown
# [论文标题] 图文研读报告

## 基本信息
- **arXiv**: {id}
- **作者**: {authors}
- **日期**: {date}

---

## 摘要

{abstract}

---

## Part A: 深度专业分析

### 1. 研究背景与问题

{背景内容}

### 2. 核心方法

{方法内容，嵌入公式}

**公式 1**: 
$$
{equation}
$$

### 3. 关键发现

{发现内容，嵌入图表}

![图1: {caption}](images/figure1.png)
*图1: {caption}*

| 指标 | 数值 |
|------|------|
{table_content}

### 4. 理论贡献

{贡献内容}

---

## Part B: 核心逻辑与价值提炼

### 核心洞察

{洞察}

### 创新点

1. {创新1}
2. {创新2}

### 局限与未来方向

{局限}

---

## 附录：原始资源

- LaTeX 源码: `latex/`
- 图片资源: `images/`
```

### Step 5: 图片处理

对于 PDF/EPS 格式的图片，转换为 PNG 便于查看：

```bash
# 使用 ImageMagick 转换
convert figure.pdf figure.png

# 或使用 pdftoppm
pdftoppm -png figure.pdf figure
```

## 输出文件结构

```
~/workspace/papers/{paper_id}/
├── {paper_id}_研读报告.md    # 最终报告
├── latex/                     # LaTeX 源码
│   ├── main.tex
│   ├── *.tex
│   └── *.bib
└── images/                    # 提取的图片
    ├── figure1.png
    ├── figure2.png
    └── ...
```

## 错误处理

1. **无源码**: arXiv 部分论文只提供 PDF，回退到 trafilatura + OCR
2. **复杂格式**: 多文件项目需要识别 `\input{}` 和 `\include{}`
3. **图片缺失**: 部分图片可能是外部链接，需要单独下载

## 使用方式

用户发送 arXiv 链接并要求"图文报告"时：

1. 提取 paper ID
2. 执行上述流程
3. 交付最终报告文件

---

## 依赖

- Python 3
- curl / wget
- tar
- ImageMagick (可选，图片转换)
- pdftoppm (可选，PDF 转图片)
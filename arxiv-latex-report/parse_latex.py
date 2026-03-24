#!/usr/bin/env python3
"""
arXiv LaTeX Parser - 解析论文源码结构
"""

import re
import sys
import json
from pathlib import Path


def clean_latex(text: str) -> str:
    """清理 LaTeX 标记，提取纯文本"""
    if not text:
        return ""
    
    # 移除注释
    text = re.sub(r'%.*?$', '', text, flags=re.MULTILINE)
    
    # 处理 figure 环境（提取 caption）
    text = re.sub(r'\\begin\{figure\*?\}.*?\\caption\{([^}]+)\}.*?\\end\{figure\*?\}', r'[Figure: \1]', text, flags=re.DOTALL)
    text = re.sub(r'\\begin\{figure\*?\}.*?\\end\{figure\*?\}', '', text, flags=re.DOTALL)
    
    # 处理 itemize/enumerate 环境
    text = re.sub(r'\\begin\{itemize\}', '', text)
    text = re.sub(r'\\end\{itemize\}', '', text)
    text = re.sub(r'\\begin\{enumerate\}', '', text)
    text = re.sub(r'\\end\{enumerate\}', '', text)
    text = re.sub(r'\\item\s*', '- ', text)
    
    # 处理常见标记
    replacements = [
        (r'\\textbf\{([^}]+)\}', r'\1'),
        (r'\\textit\{([^}]+)\}', r'\1'),
        (r'\\texttt\{([^}]+)\}', r'\1'),
        (r'\\text\{([^}]+)\}', r'\1'),
        (r'\\emph\{([^}]+)\}', r'\1'),
        (r'\\url\{([^}]+)\}', r'\1'),
        (r'\\href\{[^}]+\}\{([^}]+)\}', r'\1'),
        (r'\\cite\{[^}]+\}', '[cite]'),
        (r'\\ref\{[^}]+\}', '[ref]'),
        (r'\\label\{[^}]+\}', ''),
        (r'\\footnote\{[^}]+\}', ''),
        (r'\\footnotemark', ''),
        (r'\\footnotetext\{[^}]+\}', ''),
        (r'\\noindent', ''),
        (r'\\centering', ''),
        (r'\\par\b', '\n\n'),
        (r'\\\\', '\n'),
        (r'\\newline', '\n'),
        (r'\\quad', '  '),
        (r'\\qquad', '    '),
        (r'~', ' '),
        (r'``', '"'),
        (r"''", '"'),
        (r"`", "'"),
        (r'\\includegraphics(?:\[[^\]]*\])?\{[^}]+\}', '[Image]'),
    ]
    
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text)
    
    # 清理剩余的花括号（保留数学模式）
    text = re.sub(r'(?<!\$)\{([^{}]*)\}(?!\$)', r'\1', text)
    
    # 清理多余空白
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    text = re.sub(r' +', ' ', text)
    
    return text.strip()


def extract_title(content: str) -> str:
    """提取标题"""
    # 尝试多种标题格式（包括 ICML 格式）
    patterns = [
        r'\\icmltitle\{([^}]+)\}',  # ICML 格式
        r'\\title\{([^}]+)\}',
        r'\\title\*?\{([^}]+)\}',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return clean_latex(match.group(1))
    return ""


def extract_authors(content: str) -> list:
    """提取作者列表"""
    authors = []
    
    # 尝试 ICML 格式: \icmlauthor{Name}{affiliation}
    icml_pattern = r'\\icmlauthor\{([^}]+)\}\{[^}]*\}'
    icml_authors = re.findall(icml_pattern, content)
    if icml_authors:
        return [clean_latex(a) for a in icml_authors]
    
    # 尝试 author 环境
    author_match = re.search(r'\\begin\{author\}(.*?)\\end\{author\}', content, re.DOTALL)
    if author_match:
        author_block = author_match.group(1)
        # 提取每个作者
        for match in re.finditer(r'\\author\{([^}]+)\}', author_block):
            authors.append(clean_latex(match.group(1)))
        if authors:
            return authors
    
    # 尝试 \author{} 命令
    author_match = re.search(r'\\author\{(.*?)\}(?:\s*\\maketitle)?', content, re.DOTALL)
    if author_match:
        author_block = author_match.group(1)
        # 分割作者（按 and 或 ,）
        author_block = clean_latex(author_block)
        if ' and ' in author_block:
            authors = [a.strip() for a in re.split(r'\s+and\s+', author_block)]
        elif ',' in author_block:
            authors = [a.strip() for a in author_block.split(',')]
        else:
            authors = [author_block.strip()]
    
    return authors


def extract_abstract(content: str) -> str:
    """提取摘要"""
    match = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', content, re.DOTALL)
    if match:
        return clean_latex(match.group(1))
    return ""


def extract_sections(content: str) -> list:
    """提取章节结构"""
    sections = []
    
    # 匹配 section, subsection, subsubsection
    pattern = r'\\(section|subsection|subsubsection)\*?\{([^}]+)\}'
    
    for match in re.finditer(pattern, content):
        level = match.group(1)
        title = clean_latex(match.group(2))
        start = match.end()
        
        # 找到下一个同级或更高级标题
        next_pattern = r'\\(section|subsection|subsubsection)\*?\{'
        next_match = re.search(next_pattern, content[start:])
        
        if next_match:
            end = start + next_match.start()
        else:
            # 找到 \end{document} 或 references
            end_match = re.search(r'\\(end\{document\}|begin\{references\}|bibliography)', content[start:])
            end = start + end_match.start() if end_match else len(content)
        
        section_content = content[start:end]
        
        # 提取该章节的主要内容（前 500 字符作为预览）
        content_preview = clean_latex(section_content)[:500]
        
        sections.append({
            'level': level,
            'title': title,
            'content': content_preview,
            'full_content': section_content
        })
    
    return sections


def extract_figures(content: str, latex_dir: str = None) -> list:
    """提取图片信息"""
    figures = []
    
    # 匹配 figure 环境
    figure_pattern = r'\\begin\{figure\}.*?\\end\{figure\}'
    
    for i, match in enumerate(re.finditer(figure_pattern, content, re.DOTALL)):
        figure_block = match.group(0)
        
        # 提取图片路径
        img_match = re.search(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', figure_block)
        img_path = img_match.group(1) if img_match else None
        
        # 提取 caption
        caption_match = re.search(r'\\caption\{([^}]+)\}', figure_block, re.DOTALL)
        caption = clean_latex(caption_match.group(1)) if caption_match else f"Figure {i+1}"
        
        # 提取 label
        label_match = re.search(r'\\label\{([^}]+)\}', figure_block)
        label = label_match.group(1) if label_match else None
        
        figures.append({
            'index': i + 1,
            'path': img_path,
            'caption': caption,
            'label': label
        })
    
    return figures


def extract_tables(content: str) -> list:
    """提取表格信息"""
    tables = []
    
    # 匹配 table 环境
    table_pattern = r'\\begin\{table\}.*?\\end\{table\}'
    
    for i, match in enumerate(re.finditer(table_pattern, content, re.DOTALL)):
        table_block = match.group(0)
        
        # 提取 caption
        caption_match = re.search(r'\\caption\{([^}]+)\}', table_block, re.DOTALL)
        caption = clean_latex(caption_match.group(1)) if caption_match else f"Table {i+1}"
        
        # 提取 tabular 内容
        tabular_match = re.search(r'\\begin\{tabular\}\{[^}]+\}(.*?)\\end\{tabular\}', table_block, re.DOTALL)
        tabular_content = tabular_match.group(1) if tabular_match else ""
        
        # 解析表格为 Markdown
        table_md = convert_tabular_to_md(tabular_content)
        
        tables.append({
            'index': i + 1,
            'caption': caption,
            'markdown': table_md
        })
    
    return tables


def convert_tabular_to_md(tabular: str) -> str:
    """将 LaTeX tabular 转换为 Markdown 表格"""
    lines = []
    
    # 按行分割
    rows = tabular.split('\\\\')
    
    for row in rows:
        # 跳过 \hline 和 \toprule 等
        row = re.sub(r'\\(hline|toprule|midrule|bottomrule)', '', row)
        row = row.strip()
        
        if not row:
            continue
        
        # 按 & 分割单元格
        cells = [clean_latex(cell.strip()) for cell in row.split('&')]
        
        if cells:
            lines.append('| ' + ' | '.join(cells) + ' |')
    
    # 添加表头分隔线
    if len(lines) >= 1:
        num_cols = lines[0].count('|') - 1
        separator = '| ' + ' | '.join(['---'] * num_cols) + ' |'
        lines.insert(1, separator)
    
    return '\n'.join(lines)


def extract_equations(content: str) -> list:
    """提取公式"""
    equations = []
    
    # 编号的 equation 环境
    eq_pattern = r'\\begin\{equation\}(.*?)\\end\{equation\}'
    for i, match in enumerate(re.finditer(eq_pattern, content, re.DOTALL)):
        eq_content = match.group(1).strip()
        equations.append({
            'type': 'numbered',
            'index': i + 1,
            'latex': eq_content
        })
    
    # align 环境
    align_pattern = r'\\begin\{align\}(.*?)\\end\{align\}'
    for i, match in enumerate(re.finditer(align_pattern, content, re.DOTALL)):
        eq_content = match.group(1).strip()
        equations.append({
            'type': 'align',
            'index': len(equations) + 1,
            'latex': eq_content
        })
    
    return equations


def find_main_tex(latex_dir: str) -> str:
    """找到主 tex 文件"""
    latex_path = Path(latex_dir)
    tex_files = list(latex_path.glob('*.tex'))
    
    if not tex_files:
        return None
    
    # 常见主文件名
    main_names = ['main.tex', 'paper.tex', 'article.tex', 'document.tex']
    for name in main_names:
        for tex_file in tex_files:
            if tex_file.name == name:
                return str(tex_file)
    
    # 查找包含 \documentclass 的文件
    for tex_file in tex_files:
        content = tex_file.read_text(errors='ignore')
        if '\\documentclass' in content:
            return str(tex_file)
    
    # 返回第一个 tex 文件
    return str(tex_files[0]) if tex_files else None


def parse_paper(latex_dir: str) -> dict:
    """解析论文"""
    main_tex = find_main_tex(latex_dir)
    
    if not main_tex:
        return {'error': 'No .tex file found'}
    
    content = Path(main_tex).read_text(errors='ignore')
    
    # 处理 \input{} 和 \include{}
    def include_replacer(match):
        include_type = match.group(1)
        filename = match.group(2)
        if not filename.endswith('.tex'):
            filename += '.tex'
        include_path = Path(latex_dir) / filename
        if include_path.exists():
            return include_path.read_text(errors='ignore')
        return ""
    
    content = re.sub(r'\\(input|include)\{([^}]+)\}', include_replacer, content)
    
    return {
        'main_file': main_tex,
        'title': extract_title(content),
        'authors': extract_authors(content),
        'abstract': extract_abstract(content),
        'sections': extract_sections(content),
        'figures': extract_figures(content, latex_dir),
        'tables': extract_tables(content),
        'equations': extract_equations(content),
        'raw_content': content
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python parse_latex.py <latex_dir>")
        sys.exit(1)
    
    latex_dir = sys.argv[1]
    result = parse_paper(latex_dir)
    
    # 输出 JSON
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
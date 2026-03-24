#!/usr/bin/env python3
"""
arXiv 论文图文报告生成器
下载 LaTeX 源码 → 解析结构 → 提取图片 → 生成 Markdown 报告
"""

import os
import re
import sys
import json
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlparse


def extract_paper_id(url: str) -> str:
    """从 arXiv URL 提取论文 ID"""
    # 匹配格式: 2603.12644 或 old-style/category/12345
    patterns = [
        r'arxiv\.org/(?:abs|pdf|e-print|html)/(\d+\.\d+)',
        r'arxiv\.org/(?:abs|pdf|e-print)/([a-z-]+/\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url, re.IGNORECASE)
        if match:
            return match.group(1)
    
    # 直接是 ID
    if re.match(r'\d{4}\.\d{4,5}', url):
        return url
    
    return None


def download_latex(paper_id: str, output_dir: str) -> bool:
    """下载 arXiv LaTeX 源码"""
    latex_dir = Path(output_dir) / 'latex'
    latex_dir.mkdir(parents=True, exist_ok=True)
    
    # 下载源码包
    url = f"https://arxiv.org/e-print/{paper_id}"
    tar_path = Path(output_dir) / 'source.tar.gz'
    
    print(f"Downloading LaTeX source from {url}...")
    
    try:
        subprocess.run([
            'curl', '-L', '-o', str(tar_path), url
        ], check=True, capture_output=True)
        
        # 解压
        print(f"Extracting to {latex_dir}...")
        subprocess.run([
            'tar', '-xzf', str(tar_path), '-C', str(latex_dir)
        ], check=True, capture_output=True)
        
        # 清理 tar 文件
        tar_path.unlink()
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error downloading/extracting: {e}")
        return False


def extract_images(latex_dir: str, output_dir: str) -> list:
    """提取并转换图片"""
    images_dir = Path(output_dir) / 'images'
    images_dir.mkdir(parents=True, exist_ok=True)
    
    latex_path = Path(latex_dir)
    image_files = []
    
    # 支持的图片格式
    extensions = ['.png', '.jpg', '.jpeg', '.pdf', '.eps', '.ps', '.svg']
    
    for ext in extensions:
        for img_file in latex_path.rglob(f'*{ext}'):
            dest_file = images_dir / img_file.name
            
            # PDF/EPS 转 PNG
            if ext in ['.pdf', '.eps', '.ps']:
                png_file = images_dir / f"{img_file.stem}.png"
                try:
                    # 尝试用 ImageMagick
                    subprocess.run([
                        'convert', str(img_file), str(png_file)
                    ], check=True, capture_output=True)
                    image_files.append(str(png_file))
                except:
                    # 尝试用 pdftoppm
                    try:
                        subprocess.run([
                            'pdftoppm', '-png', str(img_file), 
                            str(images_dir / img_file.stem)
                        ], check=True, capture_output=True)
                        image_files.append(str(png_file))
                    except:
                        shutil.copy(img_file, dest_file)
                        image_files.append(str(dest_file))
            else:
                shutil.copy(img_file, dest_file)
                image_files.append(str(dest_file))
    
    return image_files


def generate_report(paper_data: dict, paper_id: str, output_dir: str) -> str:
    """生成 Markdown 报告"""
    
    report_path = Path(output_dir) / f'{paper_id}_图文研读报告.md'
    
    title = paper_data.get('title', 'Unknown Title')
    authors = paper_data.get('authors', [])
    abstract = paper_data.get('abstract', '')
    sections = paper_data.get('sections', [])
    figures = paper_data.get('figures', [])
    tables = paper_data.get('tables', [])
    equations = paper_data.get('equations', [])
    
    # 构建报告
    lines = []
    
    # 标题
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"**arXiv**: {paper_id}")
    if authors:
        lines.append(f"**作者**: {', '.join(authors)}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # 摘要
    if abstract:
        lines.append("## 摘要")
        lines.append("")
        lines.append(abstract)
        lines.append("")
        lines.append("---")
        lines.append("")
    
    # Part A: 深度分析
    lines.append("## Part A: 深度专业分析")
    lines.append("")
    
    # 章节
    for section in sections:
        level = section['level']
        heading_prefix = '#' * (2 if level == 'section' else 3 if level == 'subsection' else 4)
        lines.append(f"{heading_prefix} {section['title']}")
        lines.append("")
        
        # 内容（截取前 1000 字符）
        content = section.get('content', '')
        if len(content) > 1000:
            content = content[:1000] + '...'
        lines.append(content)
        lines.append("")
    
    # 关键公式
    if equations:
        lines.append("### 关键公式")
        lines.append("")
        for eq in equations[:5]:  # 只显示前 5 个
            lines.append(f"**公式 {eq['index']}:**")
            lines.append("")
            lines.append("$$")
            lines.append(eq['latex'])
            lines.append("$$")
            lines.append("")
    
    # 图表
    if figures:
        lines.append("### 图表")
        lines.append("")
        for fig in figures[:10]:  # 只显示前 10 个
            img_path = f"images/{Path(fig['path']).stem}.png" if fig['path'] else None
            if img_path:
                lines.append(f"![{fig['caption']}]({img_path})")
            else:
                lines.append(f"**图 {fig['index']}:** {fig['caption']}")
            lines.append("")
    
    # 表格
    if tables:
        lines.append("### 数据表格")
        lines.append("")
        for table in tables[:5]:
            lines.append(f"**{table['caption']}**")
            lines.append("")
            lines.append(table['markdown'])
            lines.append("")
    
    lines.append("---")
    lines.append("")
    
    # Part B: 核心提炼
    lines.append("## Part B: 核心逻辑与价值提炼")
    lines.append("")
    lines.append("### 核心洞察")
    lines.append("")
    lines.append("*(待分析补充)*")
    lines.append("")
    lines.append("### 创新点")
    lines.append("")
    lines.append("1. *(待分析补充)*")
    lines.append("2. *(待分析补充)*")
    lines.append("")
    lines.append("### 局限与未来方向")
    lines.append("")
    lines.append("*(待分析补充)*")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # 附录
    lines.append("## 附录：原始资源")
    lines.append("")
    lines.append(f"- LaTeX 源码: `latex/`")
    lines.append(f"- 图片资源: `images/`")
    lines.append("")
    
    # 写入文件
    report_path.write_text('\n'.join(lines), encoding='utf-8')
    
    return str(report_path)


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_report.py <arxiv_url_or_id> [output_dir]")
        print("Example: python generate_report.py https://arxiv.org/abs/2603.12644")
        sys.exit(1)
    
    url_or_id = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    # 提取论文 ID
    paper_id = extract_paper_id(url_or_id)
    if not paper_id:
        print(f"Error: Cannot extract paper ID from {url_or_id}")
        sys.exit(1)
    
    # 设置输出目录
    if not output_dir:
        output_dir = Path.home() / 'workspace' / 'papers' / paper_id.replace('/', '_')
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Paper ID: {paper_id}")
    print(f"Output directory: {output_dir}")
    
    # 下载 LaTeX 源码
    latex_dir = output_dir / 'latex'
    if not download_latex(paper_id, str(output_dir)):
        print("Warning: Could not download LaTeX source, falling back to PDF extraction")
        # TODO: 实现 PDF 回退方案
        sys.exit(1)
    
    # 解析论文
    sys.path.insert(0, str(Path(__file__).parent))
    from parse_latex import parse_paper
    
    print("Parsing LaTeX structure...")
    paper_data = parse_paper(str(latex_dir))
    
    if 'error' in paper_data:
        print(f"Error parsing paper: {paper_data['error']}")
        sys.exit(1)
    
    # 提取图片
    print("Extracting images...")
    image_files = extract_images(str(latex_dir), str(output_dir))
    print(f"Found {len(image_files)} images")
    
    # 生成报告
    print("Generating report...")
    report_path = generate_report(paper_data, paper_id.replace('/', '_'), str(output_dir))
    
    print(f"\nDone! Report saved to: {report_path}")
    print(f"Images saved to: {output_dir / 'images'}")
    
    # 输出摘要
    print(f"\n---\nTitle: {paper_data.get('title', 'N/A')}")
    print(f"Authors: {', '.join(paper_data.get('authors', []))}")
    print(f"Sections: {len(paper_data.get('sections', []))}")
    print(f"Figures: {len(paper_data.get('figures', []))}")
    print(f"Tables: {len(paper_data.get('tables', []))}")
    print(f"Equations: {len(paper_data.get('equations', []))}")


if __name__ == '__main__':
    main()
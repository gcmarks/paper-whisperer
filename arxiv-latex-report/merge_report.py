#!/usr/bin/env python3
"""
合并 arxiv-latex-report 和 openclaw-skills-arxiv-reader 的输出
生成图文并茂的深度研读报告
"""

import os
import re
import sys
from pathlib import Path
from datetime import datetime


def find_images(images_dir: str) -> dict:
    """查找图片文件"""
    images = {}
    img_path = Path(images_dir)
    if not img_path.exists():
        return images
    
    for ext in ['*.png', '*.jpg', '*.jpeg', '*.pdf']:
        for f in img_path.glob(ext):
            images[f.stem] = str(f)
    
    return images


def generate_image_section(images: dict, latex_dir: str = None) -> str:
    """生成图片部分"""
    if not images:
        return ""
    
    # 尝试从 LaTeX 源码提取图片说明
    captions = {}
    if latex_dir:
        tex_files = list(Path(latex_dir).glob('*.tex'))
        for tex_file in tex_files:
            try:
                content = tex_file.read_text(errors='ignore')
                # 提取 figure 环境中的 caption
                pattern = r'\\begin\{figure\*?\}.*?\\includegraphics.*?\{imgs/(\d+)\.png\}.*?\\caption\{([^}]+)\}'
                for match in re.finditer(pattern, content, re.DOTALL):
                    img_num = match.group(1)
                    caption = match.group(2).strip()
                    captions[img_num] = caption
            except:
                pass
    
    lines = ["\n## 论文图表\n"]
    
    # 按数字排序
    sorted_keys = sorted(images.keys(), key=lambda x: int(x) if x.isdigit() else 999)
    
    for img_name in sorted_keys:
        img_path = images[img_name]
        caption = captions.get(img_name, f"图 {img_name}")
        # 使用相对路径
        rel_path = f"images/{img_name}.png"
        lines.append(f"### {caption}")
        lines.append("")
        lines.append(f"![{caption}]({rel_path})")
        lines.append(f"*{caption}*")
        lines.append("")
    
    return "\n".join(lines)


def merge_reports(
    arxiv_reader_output: str,
    images_dir: str,
    latex_dir: str,
    output_path: str,
    paper_id: str,
    title: str,
    authors: str
) -> str:
    """合并报告"""
    
    # 查找图片
    images = find_images(images_dir)
    
    # 读取 arxiv-reader 输出
    reader_content = arxiv_reader_output
    
    # 构建完整报告
    report = f"""# {title}

**arXiv**: [{paper_id}](https://arxiv.org/abs/{paper_id})  
**作者**: {authors}  
**阅读时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

"""

    # 添加图片部分（在正文前）
    if images:
        report += generate_image_section(images, latex_dir)
        report += "\n---\n\n"
    
    # 添加深度分析笔记
    report += "## 深度研读笔记\n\n"
    report += reader_content
    
    # 添加附录
    report += """
---

## 附录：原始资源

- **LaTeX 源码**: `latex/`
- **论文图片**: `images/`
- **原始 PDF**: [{paper_id}.pdf](https://arxiv.org/pdf/{paper_id}.pdf)

---

*本报告由 arxiv-latex-report + openclaw-skills-arxiv-reader 联合生成*
"""
    
    # 保存报告
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(report, encoding='utf-8')
    
    return str(output_file)


def main():
    if len(sys.argv) < 3:
        print("Usage: python merge_report.py <arxiv_reader_output.md> <output_dir> [paper_id]")
        print("Example: python merge_report.py notes.md ~/workspace/papers/2603.12644 2603.12644")
        sys.exit(1)
    
    reader_file = sys.argv[1]
    output_dir = sys.argv[2]
    paper_id = sys.argv[3] if len(sys.argv) > 3 else "unknown"
    
    # 读取 arxiv-reader 输出
    with open(reader_file, 'r', encoding='utf-8') as f:
        reader_content = f.read()
    
    # 提取标题和作者
    title_match = re.search(r'^# (.+)$', reader_content, re.MULTILINE)
    title = title_match.group(1) if title_match else f"Paper {paper_id}"
    
    authors_match = re.search(r'\*\*作者\*\*: (.+)$', reader_content, re.MULTILINE)
    authors = authors_match.group(1) if authors_match else "Unknown"
    
    # 清理重复的标题
    reader_content = re.sub(r'^# .+\n', '', reader_content, count=1)
    reader_content = re.sub(r'\*\*arXiv\*\*: .+\n', '', reader_content)
    reader_content = re.sub(r'\*\*作者\*\*: .+\n', '', reader_content)
    reader_content = re.sub(r'\*\*阅读时间\*\*: .+\n', '', reader_content)
    
    # 路径
    images_dir = os.path.join(output_dir, 'images')
    latex_dir = os.path.join(output_dir, 'latex')
    output_path = os.path.join(output_dir, f'{paper_id}_深度研读报告.md')
    
    # 合并
    result = merge_reports(
        reader_content,
        images_dir,
        latex_dir,
        output_path,
        paper_id,
        title,
        authors
    )
    
    print(f"合并报告已保存: {result}")
    print(f"图片数量: {len(find_images(images_dir))}")


if __name__ == '__main__':
    main()
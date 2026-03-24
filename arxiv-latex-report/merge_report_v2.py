#!/usr/bin/env python3
"""
合并 arxiv-latex-report 和 openclaw-skills-arxiv-reader 的输出
智能图片放置 + 中文报告
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
    
    for ext in ['*.png', '*.jpg', '*.jpeg']:
        for f in img_path.glob(ext):
            images[f.stem] = str(f)
    
    return images


def extract_captions(latex_dir: str) -> dict:
    """从 LaTeX 源码提取图片说明"""
    captions = {}
    if not latex_dir:
        return captions
    
    tex_files = list(Path(latex_dir).glob('*.tex'))
    for tex_file in tex_files:
        try:
            content = tex_file.read_text(errors='ignore')
            # 提取 figure 环境中的 caption
            pattern = r'\\begin\{figure\*?\}.*?\\includegraphics.*?\{imgs/(\d+)\.png\}.*?\\caption\{([^}]+)\}'
            for match in re.finditer(pattern, content, re.DOTALL):
                img_num = match.group(1)
                caption = match.group(2).strip()
                # 清理 LaTeX 标记
                caption = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', caption)
                captions[img_num] = caption
        except:
            pass
    
    return captions


def get_image_context(caption: str) -> str:
    """根据图片说明判断应该插入的位置"""
    caption_lower = caption.lower()
    
    # 架构图
    if any(kw in caption_lower for kw in ['architectural overview', 'architecture', '架构']):
        return 'architecture'
    
    # 风险分类
    if any(kw in caption_lower for kw in ['risk taxonomy', 'risk', 'taxonomy', '风险', '分类']):
        return 'risk'
    
    # FASA
    if any(kw in caption_lower for kw in ['fasa', 'defense', '防御']):
        return 'fasa'
    
    # 威胁/攻击
    if any(kw in caption_lower for kw in ['threat', 'attack', 'exploit', '威胁', '攻击']):
        return 'threat'
    
    # 风险示意图
    if any(kw in caption_lower for kw in ['illustration', 'overview', '示意']):
        return 'overview'
    
    return 'general'


def generate_image_markdown(img_name: str, caption: str, rel_path: str) -> str:
    """生成图片 Markdown"""
    return f"""
![{caption}]({rel_path})
*图：{caption}*
"""


def merge_reports(
    reader_output: str,
    images_dir: str,
    latex_dir: str,
    output_path: str,
    paper_id: str
) -> str:
    """合并报告，智能放置图片"""
    
    # 查找图片和说明
    images = find_images(images_dir)
    captions = extract_captions(latex_dir)
    
    # 按上下文分组图片
    image_groups = {
        'overview': [],
        'architecture': [],
        'risk': [],
        'fasa': [],
        'threat': [],
        'general': []
    }
    
    for img_name in sorted(images.keys(), key=lambda x: int(x) if x.isdigit() else 999):
        caption = captions.get(img_name, f"图 {img_name}")
        context = get_image_context(caption)
        rel_path = f"images/{img_name}.png"
        image_groups[context].append((img_name, caption, rel_path))
    
    # 构建报告
    report = f"""# OpenClaw 安全论文深度研读报告

**arXiv**: [{paper_id}](https://arxiv.org/abs/{paper_id})  
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

"""
    
    # 添加概述图片
    if image_groups['overview']:
        for img_name, caption, rel_path in image_groups['overview']:
            report += generate_image_markdown(img_name, caption, rel_path)
        report += "\n---\n\n"
    
    # 解析 reader 输出，按章节插入图片
    sections = re.split(r'\n## (\d+\. .+?)\n', reader_output)
    
    current_section = ""
    for i, section in enumerate(sections):
        if not section.strip():
            continue
        
        # 判断是否是章节标题
        if re.match(r'\d+\. ', section):
            current_section = section
            report += f"\n## {section}\n\n"
        else:
            # 根据章节内容插入相关图片
            section_lower = section.lower()
            
            # 架构相关章节
            if '架构' in current_section or 'architecture' in section_lower:
                for img_name, caption, rel_path in image_groups['architecture']:
                    if img_name not in report:  # 避免重复
                        report += generate_image_markdown(img_name, caption, rel_path)
                image_groups['architecture'] = []  # 清空已使用的
            
            # 风险相关章节
            if '风险' in current_section or 'risk' in section_lower or '威胁' in current_section:
                for img_name, caption, rel_path in image_groups['risk']:
                    if img_name not in report:
                        report += generate_image_markdown(img_name, caption, rel_path)
                image_groups['risk'] = []
            
            # FASA 相关章节
            if 'fasa' in section_lower or '防御' in current_section:
                for img_name, caption, rel_path in image_groups['fasa']:
                    if img_name not in report:
                        report += generate_image_markdown(img_name, caption, rel_path)
                image_groups['fasa'] = []
            
            # 威胁相关
            if '威胁' in current_section or 'threat' in section_lower:
                for img_name, caption, rel_path in image_groups['threat']:
                    if img_name not in report:
                        report += generate_image_markdown(img_name, caption, rel_path)
                image_groups['threat'] = []
            
            report += section
    
    # 添加剩余图片
    remaining = []
    for group in image_groups.values():
        remaining.extend(group)
    
    if remaining:
        report += "\n---\n\n## 附录：论文图表\n\n"
        for img_name, caption, rel_path in remaining:
            report += generate_image_markdown(img_name, caption, rel_path)
    
    # 添加资源附录
    report += f"""
---

## 附录：原始资源

- **LaTeX 源码**: `latex/`
- **论文图片**: `images/`
- **原始 PDF**: [{paper_id}.pdf](https://arxiv.org/pdf/{paper_id}.pdf)

---

*本报告由 arxiv-latex-report + openclaw-skills-arxiv-reader 联合生成*
"""
    
    # 保存
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(report, encoding='utf-8')
    
    return str(output_file)


def main():
    if len(sys.argv) < 3:
        print("Usage: python merge_report_v2.py <reader_output.md> <output_dir> [paper_id]")
        sys.exit(1)
    
    reader_file = sys.argv[1]
    output_dir = sys.argv[2]
    paper_id = sys.argv[3] if len(sys.argv) > 3 else "unknown"
    
    with open(reader_file, 'r', encoding='utf-8') as f:
        reader_content = f.read()
    
    images_dir = os.path.join(output_dir, 'images')
    latex_dir = os.path.join(output_dir, 'latex')
    output_path = os.path.join(output_dir, f'{paper_id}_深度研读报告_图文版.md')
    
    result = merge_reports(
        reader_content,
        images_dir,
        latex_dir,
        output_path,
        paper_id
    )
    
    print(f"合并报告已保存: {result}")
    print(f"图片数量: {len(find_images(images_dir))}")


if __name__ == '__main__':
    main()
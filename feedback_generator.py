import json
import os
from datetime import datetime

class FeedbackGenerator:
    def __init__(self):
        pass
    
    def generate_feedback(self, scores, comparison, student_doc, reference_doc=None):
        """生成评语"""
        feedback = {
            'strengths': [],
            'weaknesses': [],
            'suggestions': [],
            'summary': '',
            'detailed_comments': []
        }
        
        self._analyze_strengths(feedback, scores, comparison)
        self._analyze_weaknesses(feedback, scores, comparison)
        self._generate_suggestions(feedback, scores, comparison)
        self._generate_summary(feedback, scores, comparison)
        self._generate_detailed_comments(feedback, scores, comparison, student_doc)
        
        return feedback
    
    def _analyze_strengths(self, feedback, scores, comparison):
        """分析优点"""
        if scores['structure'] >= 16:
            feedback['strengths'].append("报告结构完整，章节组织合理")
        
        if scores['content'] >= 21:
            feedback['strengths'].append("内容与参考答案匹配度高")
        
        if scores['images'] >= 40:
            feedback['strengths'].append("图片数量充足，与参考答案大致匹配")
        
        if comparison.get('content_similarity', 0) >= 0.7:
            feedback['strengths'].append("整体内容与参考答案一致性好")
        
        if not comparison.get('missing_sections', []):
            feedback['strengths'].append("所有要求章节均已覆盖")
    
    def _analyze_weaknesses(self, feedback, scores, comparison):
        """分析不足"""
        if scores['structure'] < 16:
            feedback['weaknesses'].append(f"结构完整性有待提高（得分: {scores['structure']}/20）")
        
        if scores['content'] < 21:
            feedback['weaknesses'].append(f"内容与参考答案匹配度较低（得分: {scores['content']}/30）")
        
        if scores['images'] < 40:
            image_comp = comparison.get('image_comparison', {})
            ref_count = image_comp.get('ref_count', 0)
            stu_count = image_comp.get('stu_count', 0)
            feedback['weaknesses'].append(f"图片数量与参考答案存在差异（学生: {stu_count}张，参考: {ref_count}张，得分: {scores['images']}/50）")
        
        missing_sections = comparison.get('missing_sections', [])
        if missing_sections:
            feedback['weaknesses'].append(f"缺失以下章节: {', '.join(missing_sections)}")
        
        for diff in comparison.get('differences', []):
            if diff['type'] == 'content_mismatch':
                feedback['weaknesses'].append(f"{diff['section']}部分内容与参考答案差异较大")
    
    def _generate_suggestions(self, feedback, scores, comparison):
        """生成改进建议"""
        if scores['structure'] < 16:
            feedback['suggestions'].append("建议参考参考答案的章节结构，补充缺失的部分")
        
        if scores['content'] < 21:
            feedback['suggestions'].append("建议重新核对内容，确保与参考答案一致")
        
        if scores['images'] < 40:
            feedback['suggestions'].append("建议调整图片数量，使图片数量与参考答案大致一致")
        
        feedback['suggestions'].append("建议在答辩前重新通读报告，检查内容完整性和准确性")
        feedback['suggestions'].append("建议准备3-6分钟的答辩展示，重点说明实验过程和关键发现")
    
    def _generate_summary(self, feedback, scores, comparison):
        """生成总结评语"""
        total_score = scores['total']
        
        if total_score >= 90:
            summary = f"报告整体优秀（得分: {total_score}）！"
        elif total_score >= 80:
            summary = f"报告整体良好（得分: {total_score}），但仍有提升空间。"
        elif total_score >= 70:
            summary = f"报告整体中等（得分: {total_score}），需要进一步完善。"
        elif total_score >= 60:
            summary = f"报告勉强及格（得分: {total_score}），存在较多需要改进的地方。"
        else:
            summary = f"报告未及格（得分: {total_score}），需要大幅修改和完善。"
        
        if feedback['strengths']:
            summary += " 做得好的方面：" + ";".join(feedback['strengths'])[:50] + "..."
        
        if feedback['weaknesses']:
            summary += " 需要改进的地方：" + ";".join(feedback['weaknesses'])[:50] + "..."
        
        feedback['summary'] = summary
    
    def _generate_detailed_comments(self, feedback, scores, comparison, student_doc):
        """生成详细评语"""
        comments = []
        
        comments.append({
            'category': '图片匹配度',
            'score': scores['images'],
            'max_score': 50,
            'comment': self._get_images_comment(scores['images'], comparison)
        })
        
        comments.append({
            'category': '结构完整性',
            'score': scores['structure'],
            'max_score': 20,
            'comment': self._get_structure_comment(scores['structure'], comparison)
        })
        
        comments.append({
            'category': '内容匹配度',
            'score': scores['content'],
            'max_score': 30,
            'comment': self._get_content_comment(scores['content'], comparison)
        })
        
        feedback['detailed_comments'] = comments
    
    def _get_structure_comment(self, score, comparison):
        if score >= 18:
            return "报告结构完整，章节划分合理，符合实训报告规范。"
        elif score >= 14:
            return "报告结构基本完整，但部分章节可以进一步完善。"
        elif score >= 10:
            return "报告结构存在缺失，建议参考参考答案补充完整。"
        else:
            return "报告结构严重缺失，需要重新组织章节结构。"
    
    def _get_content_comment(self, score, comparison):
        if score >= 27:
            return "内容与参考答案高度一致，描述准确无误。"
        elif score >= 21:
            return "内容基本匹配，但存在少量差异。"
        elif score >= 15:
            return "内容存在较多差异，需要重新核对。"
        else:
            return "内容与参考答案严重不符，建议重新撰写。"
    
    def _get_images_comment(self, score, comparison):
        image_comp = comparison.get('image_comparison', {})
        ref_count = image_comp.get('ref_count', 0)
        stu_count = image_comp.get('stu_count', 0)
        
        if ref_count == 0:
            return "参考答案中无图片，此项不扣分。"
        
        if score >= 45:
            return f"图片数量充足（{stu_count}/{ref_count}），与参考答案大致匹配。"
        elif score >= 30:
            return f"图片数量较好（{stu_count}/{ref_count}），建议增加少量图片。"
        elif score >= 20:
            return f"图片数量存在差异（{stu_count}/{ref_count}），建议补充相关图片。"
        elif score >= 10:
            return f"图片数量较少（{stu_count}/{ref_count}），需要增加图片数量。"
        else:
            return f"图片严重不足（{stu_count}/{ref_count}），建议大幅增加图片。"

class ReportExporter:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def export_json(self, report_data, filename):
        """导出为JSON格式"""
        output_path = os.path.join(self.output_dir, f"{filename}_批改结果.json")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        return output_path
    
    def export_html(self, report_data, filename):
        """导出为HTML格式"""
        output_path = os.path.join(self.output_dir, f"{filename}_批改结果.html")
        
        html_content = self._generate_html(report_data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    def _generate_html(self, report_data):
        """生成HTML内容"""
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>实训报告批改结果 - {report_data['original_filename']}</title>
    <style>
        body {{ font-family: 'Microsoft YaHei', sans-serif; margin: 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #3498db; margin-top: 25px; }}
        .score-box {{ display: inline-block; padding: 20px; background: #ecf0f1; border-radius: 10px; margin: 10px 0; }}
        .score-value {{ font-size: 48px; font-weight: bold; color: #e74c3c; }}
        .score-label {{ font-size: 18px; color: #7f8c8d; }}
        .grade {{ font-size: 24px; color: #27ae60; margin-left: 20px; }}
        .section {{ margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 8px; }}
        .strengths {{ color: #27ae60; }}
        .weaknesses {{ color: #e74c3c; }}
        .suggestions {{ color: #3498db; }}
        .comments-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        .comments-table th, .comments-table td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
        .comments-table th {{ background: #3498db; color: white; }}
        .diff-item {{ margin: 10px 0; padding: 10px; border-left: 4px solid #e74c3c; background: #fdf2f2; }}
        .timestamp {{ color: #95a5a6; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>实训报告智能批改结果</h1>
        <p class="timestamp">批改时间：{report_data['timestamp']}</p>
        
        <div class="score-box">
            <span class="score-value">{report_data['scores']['total']}</span>
            <span class="score-label">/100</span>
            <span class="grade">等级: {report_data['grade']}</span>
        </div>
        
        <h2>得分详情</h2>
        <table class="comments-table">
            <tr>
                <th>评分维度</th>
                <th>得分</th>
                <th>满分</th>
                <th>评语</th>
            </tr>
"""
        
        for comment in report_data['feedback']['detailed_comments']:
            html += f"""
            <tr>
                <td>{comment['category']}</td>
                <td>{comment['score']}</td>
                <td>{comment['max_score']}</td>
                <td>{comment['comment']}</td>
            </tr>
"""
        
        html += """
        </table>
        
        <h2>优点</h2>
        <div class="section strengths">
            <ul>
"""
        for strength in report_data['feedback']['strengths']:
            html += f"<li>{strength}</li>"
        
        html += """
            </ul>
        </div>
        
        <h2>不足</h2>
        <div class="section weaknesses">
            <ul>
"""
        for weakness in report_data['feedback']['weaknesses']:
            html += f"<li>{weakness}</li>"
        
        html += """
            </ul>
        </div>
        
        <h2>改进建议</h2>
        <div class="section suggestions">
            <ul>
"""
        for suggestion in report_data['feedback']['suggestions']:
            html += f"<li>{suggestion}</li>"
        
        html += """
            </ul>
        </div>
        
        <h2>差异对比</h2>
"""
        
        if report_data['comparison']['missing_sections']:
            html += f"""
        <div class="diff-item">
            <strong>缺失章节:</strong> {', '.join(report_data['comparison']['missing_sections'])}
        </div>
"""
        
        if report_data['comparison']['differences']:
            for diff in report_data['comparison']['differences']:
                html += f"""
        <div class="diff-item">
            <strong>{diff['section']}:</strong> {diff['details']}
        </div>
"""
        
        html += """
    </div>
</body>
</html>
"""
        return html
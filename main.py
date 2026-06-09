import os
import argparse
from datetime import datetime
from config import REFERENCE_DIR, SUBMISSIONS_DIR, OUTPUT_DIR, REPORT_SECTIONS
from document_parser import DocumentParser
from comparator import ReportComparator
from scorer import ReportScorer
from feedback_generator import FeedbackGenerator, ReportExporter

class ReportGradingSystem:
    def __init__(self):
        self.parser = DocumentParser()
        self.comparator = ReportComparator()
        self.scorer = ReportScorer()
        self.feedback_generator = FeedbackGenerator()
        self.exporter = ReportExporter(OUTPUT_DIR)
    
    def load_reference(self, reference_path):
        """加载参考答案文档"""
        if not os.path.exists(reference_path):
            raise FileNotFoundError(f"参考答案文件不存在: {reference_path}")
        
        doc_data = self.parser.parse_document(reference_path)
        doc_data['sections'] = self.parser.extract_sections(doc_data, REPORT_SECTIONS)
        return doc_data
    
    def grade_report(self, student_path, reference_data):
        """批改单个报告"""
        if not os.path.exists(student_path):
            raise FileNotFoundError(f"学生报告文件不存在: {student_path}")
        
        student_doc = self.parser.parse_document(student_path)
        student_doc['sections'] = self.parser.extract_sections(student_doc, REPORT_SECTIONS)
        
        comparison = self.comparator.compare_documents(reference_data, student_doc)
        scores = self.scorer.calculate_scores(comparison, student_doc)
        grade = self.scorer.get_grade(scores['total'])
        feedback = self.feedback_generator.generate_feedback(scores, comparison, student_doc)
        
        report_data = {
            'original_filename': os.path.basename(student_path),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'scores': scores,
            'grade': grade,
            'comparison': comparison,
            'feedback': feedback
        }
        
        return report_data
    
    def batch_grade(self, reference_path, submissions_dir=None):
        """批量批改报告"""
        if submissions_dir is None:
            submissions_dir = SUBMISSIONS_DIR
        
        reference_data = self.load_reference(reference_path)
        results = []
        
        for filename in os.listdir(submissions_dir):
            if filename.startswith('.'):
                continue
            
            file_path = os.path.join(submissions_dir, filename)
            if not os.path.isfile(file_path):
                continue
            
            _, ext = os.path.splitext(filename)
            if ext.lower() not in ['.docx', '.doc', '.pdf', '.txt', '.md', '.rtf', '.odt']:
                continue
            
            try:
                print(f"正在批改: {filename}")
                report_data = self.grade_report(file_path, reference_data)
                
                name_without_ext = os.path.splitext(filename)[0]
                json_path = self.exporter.export_json(report_data, name_without_ext)
                html_path = self.exporter.export_html(report_data, name_without_ext)
                
                report_data['output_json'] = json_path
                report_data['output_html'] = html_path
                results.append(report_data)
                
                print(f"  得分: {report_data['scores']['total']}/100, 等级: {report_data['grade']}")
                print(f"  输出: {html_path}")
                
            except Exception as e:
                print(f"  错误: {str(e)}")
        
        return results

def main():
    parser = argparse.ArgumentParser(description='实训报告智能批改系统')
    parser.add_argument('-r', '--reference', required=True, help='参考答案文件路径')
    parser.add_argument('-s', '--submission', help='单个学生报告文件路径')
    parser.add_argument('-d', '--directory', help='学生报告文件夹路径')
    parser.add_argument('-o', '--output', help='输出目录')
    
    args = parser.parse_args()
    
    system = ReportGradingSystem()
    
    if args.output:
        system.exporter = ReportExporter(args.output)
    
    if args.submission:
        print(f"加载参考答案: {args.reference}")
        reference_data = system.load_reference(args.reference)
        print(f"参考答案章节: {list(reference_data['sections'].keys())}")
        print(f"参考答案图片数: {reference_data['image_count']}")
        
        print(f"\n批改报告: {args.submission}")
        report_data = system.grade_report(args.submission, reference_data)
        
        name_without_ext = os.path.splitext(os.path.basename(args.submission))[0]
        json_path = system.exporter.export_json(report_data, name_without_ext)
        html_path = system.exporter.export_html(report_data, name_without_ext)
        
        print(f"\n=== 批改结果 ===")
        print(f"总分: {report_data['scores']['total']}/100")
        print(f"等级: {report_data['grade']}")
        print(f"\n得分详情:")
        for k, v in report_data['scores'].items():
            if k != 'total':
                print(f"  {k}: {v}")
        print(f"\n优点:")
        for s in report_data['feedback']['strengths']:
            print(f"  - {s}")
        print(f"\n不足:")
        for w in report_data['feedback']['weaknesses']:
            print(f"  - {w}")
        print(f"\n改进建议:")
        for g in report_data['feedback']['suggestions']:
            print(f"  - {g}")
        print(f"\n输出文件:")
        print(f"  JSON: {json_path}")
        print(f"  HTML: {html_path}")
    
    elif args.directory:
        print(f"加载参考答案: {args.reference}")
        print(f"批量批改目录: {args.directory}")
        results = system.batch_grade(args.reference, args.directory)
        
        print(f"\n=== 批量批改完成 ===")
        print(f"处理报告数: {len(results)}")
        
        total_scores = [r['scores']['total'] for r in results]
        if total_scores:
            print(f"平均分: {sum(total_scores)/len(total_scores):.1f}")
            print(f"最高分: {max(total_scores)}")
            print(f"最低分: {min(total_scores)}")
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
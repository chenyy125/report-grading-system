import streamlit as st
import os
import tempfile
from datetime import datetime
from config import REPORT_SECTIONS
from document_parser import DocumentParser
from comparator import ReportComparator
from scorer import ReportScorer
from feedback_generator import FeedbackGenerator, ReportExporter

class StreamlitApp:
    def __init__(self):
        self.parser = DocumentParser()
        self.comparator = ReportComparator()
        self.scorer = ReportScorer()
        self.feedback_generator = FeedbackGenerator()
        
    def run(self):
        st.set_page_config(
            page_title="实训报告智能批改系统",
            page_icon="📝",
            layout="wide"
        )
        
        st.title("📝 实训报告智能批改系统")
        st.markdown("基于参考答案比对的智能评分系统")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📁 上传文件")
            reference_file = st.file_uploader(
                "上传参考答案报告",
                type=['docx', 'doc', 'pdf', 'txt', 'md', 'rtf', 'odt'],
                key='reference'
            )
            
            submission_files = st.file_uploader(
                "上传学生实训报告",
                type=['docx', 'doc', 'pdf', 'txt', 'md', 'rtf', 'odt'],
                accept_multiple_files=True,
                key='submissions'
            )
        
        with col2:
            st.subheader("⚙️ 评分权重配置")
            images_weight = st.slider("图片匹配度", 30, 70, 50)
            structure_weight = st.slider("结构完整性", 10, 30, 20)
            content_weight = st.slider("内容匹配度", 10, 40, 30)
            
            weights = {
                'images': images_weight,
                'structure': structure_weight,
                'content': content_weight
            }
            
            total_weight = sum(weights.values())
            if total_weight != 100:
                st.warning(f"权重总和为 {total_weight}，建议调整为 100")
        
        submit_button = st.button("🚀 开始批改", disabled=not (reference_file and submission_files))
        
        if submit_button:
            with st.spinner("正在加载参考答案..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(reference_file.name)[1]) as f:
                    f.write(reference_file.getvalue())
                    ref_path = f.name
                
                try:
                    ref_data = self.parser.parse_document(ref_path)
                    ref_data['sections'] = self.parser.extract_sections(ref_data, REPORT_SECTIONS)
                finally:
                    os.unlink(ref_path)
            
            st.success("参考答案加载完成")
            st.info(f"参考答案章节: {', '.join(ref_data['sections'].keys())}")
            st.info(f"参考答案图片数: {ref_data['image_count']}")
            
            self.scorer = ReportScorer(weights)
            
            results = []
            progress_bar = st.progress(0)
            
            for i, submission_file in enumerate(submission_files):
                with st.spinner(f"正在批改: {submission_file.name}"):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(submission_file.name)[1]) as f:
                        f.write(submission_file.getvalue())
                        sub_path = f.name
                    
                    try:
                        student_doc = self.parser.parse_document(sub_path)
                        student_doc['sections'] = self.parser.extract_sections(student_doc, REPORT_SECTIONS)
                        
                        comparison = self.comparator.compare_documents(ref_data, student_doc)
                        scores = self.scorer.calculate_scores(comparison, student_doc)
                        grade = self.scorer.get_grade(scores['total'])
                        feedback = self.feedback_generator.generate_feedback(scores, comparison, student_doc)
                        
                        report_data = {
                            'original_filename': submission_file.name,
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'scores': scores,
                            'grade': grade,
                            'comparison': comparison,
                            'feedback': feedback
                        }
                        results.append(report_data)
                    finally:
                        os.unlink(sub_path)
                
                progress_bar.progress((i + 1) / len(submission_files))
            
            st.success(f"批改完成！共处理 {len(results)} 份报告")
            
            for result in results:
                with st.expander(f"📄 {result['original_filename']} - 得分: {result['scores']['total']}/100"):
                    score_cols = st.columns(3)
                    score_cols[0].metric("图片匹配度", f"{result['scores']['images']}/{weights['images']}")
                    score_cols[1].metric("结构完整性", f"{result['scores']['structure']}/{weights['structure']}")
                    score_cols[2].metric("内容匹配度", f"{result['scores']['content']}/{weights['content']}")
                    
                    st.metric("总分", f"{result['scores']['total']}/100", result['grade'])
                    
                    feedback_cols = st.columns([1, 1, 1])
                    
                    with feedback_cols[0]:
                        st.markdown("**✅ 优点:**")
                        if result['feedback']['strengths']:
                            for s in result['feedback']['strengths']:
                                st.write(f"- {s}")
                        else:
                            st.write("暂无")
                    
                    with feedback_cols[1]:
                        st.markdown("**❌ 不足:**")
                        if result['feedback']['weaknesses']:
                            for w in result['feedback']['weaknesses']:
                                st.write(f"- {w}")
                        else:
                            st.write("暂无")
                    
                    with feedback_cols[2]:
                        st.markdown("**💡 改进建议:**")
                        if result['feedback']['suggestions']:
                            for g in result['feedback']['suggestions']:
                                st.write(f"- {g}")
                        else:
                            st.write("暂无")
                    
                    if result['comparison']['missing_sections'] or result['comparison']['differences']:
                        st.subheader("📊 差异对比")
                        if result['comparison']['missing_sections']:
                            st.warning(f"缺失章节: {', '.join(result['comparison']['missing_sections'])}")
                        
                        if result['comparison']['differences']:
                            for diff in result['comparison']['differences']:
                                st.info(f"📌 {diff['section']}: {diff['details']}")
            
            avg_score = sum(r['scores']['total'] for r in results) / len(results)
            st.metric("📊 平均分", f"{avg_score:.1f}/100")
            
            st.subheader("📥 下载批改报告")
            download_cols = st.columns(len(results) if len(results) <= 4 else 4)
            for i, result in enumerate(results):
                with download_cols[i % 4]:
                    exporter = ReportExporter(tempfile.gettempdir())
                    name = os.path.splitext(result['original_filename'])[0]
                    html_path = exporter.export_html(result, name)
                    
                    with open(html_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    
                    st.download_button(
                        label=f"下载 {result['original_filename']}",
                        data=html_content,
                        file_name=f"{name}_批改结果.html",
                        mime='text/html'
                    )

if __name__ == '__main__':
    app = StreamlitApp()
    app.run()
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import sent_tokenize
import nltk

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

class ReportComparator:
    def __init__(self, threshold=0.6):
        self.threshold = threshold
        self.vectorizer = TfidfVectorizer(
            token_pattern=r'(?u)\b\w+\b',
            stop_words=None,
            ngram_range=(1, 2)
        )
    
    def compare_documents(self, reference_doc, student_doc):
        """比对两份文档"""
        comparison = {
            'structure_match': self._compare_structure(reference_doc, student_doc),
            'content_similarity': self._compare_content(reference_doc, student_doc),
            'image_comparison': self._compare_images(reference_doc, student_doc),
            'missing_sections': [],
            'extra_sections': [],
            'differences': []
        }
        
        ref_sections = set(reference_doc.get('sections', {}).keys())
        stu_sections = set(student_doc.get('sections', {}).keys())
        
        comparison['missing_sections'] = list(ref_sections - stu_sections)
        comparison['extra_sections'] = list(stu_sections - ref_sections)
        
        comparison['differences'] = self._find_differences(reference_doc, student_doc)
        
        return comparison
    
    def _compare_structure(self, reference_doc, student_doc):
        """比对文档结构"""
        ref_sections = set(reference_doc.get('sections', {}).keys())
        stu_sections = set(student_doc.get('sections', {}).keys())
        
        if not ref_sections:
            return 0.0
        
        matched = len(ref_sections & stu_sections)
        return matched / len(ref_sections)
    
    def _compare_content(self, reference_doc, student_doc):
        """比对文档内容相似度"""
        ref_text = reference_doc.get('total_text', '')
        stu_text = student_doc.get('total_text', '')
        
        if not ref_text or not stu_text:
            return 0.0
        
        try:
            texts = [ref_text, stu_text]
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity)
        except:
            return self._simple_similarity(ref_text, stu_text)
    
    def _simple_similarity(self, text1, text2):
        """简单的相似度计算"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        return len(intersection) / max(len(words1), len(words2))
    
    def _compare_images(self, reference_doc, student_doc):
        """比对图片"""
        ref_images = reference_doc.get('image_count', 0)
        stu_images = student_doc.get('image_count', 0)
        
        if ref_images == 0:
            return {'match': True, 'ref_count': 0, 'stu_count': 0, 'ratio': 1.0}
        
        ratio = stu_images / ref_images
        return {
            'match': ratio >= 0.8,
            'ref_count': ref_images,
            'stu_count': stu_images,
            'ratio': ratio
        }
    
    def _find_differences(self, reference_doc, student_doc):
        """找出文档差异"""
        differences = []
        
        ref_sections = reference_doc.get('sections', {})
        stu_sections = student_doc.get('sections', {})
        
        for section, ref_content in ref_sections.items():
            stu_content = stu_sections.get(section, [])
            
            if not stu_content:
                differences.append({
                    'type': 'missing_section',
                    'section': section,
                    'details': f"缺失章节: {section}",
                    'reference_sample': ref_content[:2] if ref_content else []
                })
                continue
            
            ref_text = ' '.join(ref_content)
            stu_text = ' '.join(stu_content)
            
            similarity = self._compare_content(
                {'total_text': ref_text},
                {'total_text': stu_text}
            )
            
            if similarity < self.threshold:
                differences.append({
                    'type': 'content_mismatch',
                    'section': section,
                    'similarity': round(similarity, 2),
                    'details': f"内容相似度较低: {round(similarity * 100, 1)}%",
                    'reference_sample': ref_content[:1] if ref_content else [],
                    'student_sample': stu_content[:1] if stu_content else []
                })
        
        return differences
    
    def extract_key_points(self, doc_data, keywords):
        """提取关键点"""
        key_points = []
        text = doc_data.get('total_text', '')
        
        for keyword in keywords:
            if keyword in text:
                sentences = sent_tokenize(text)
                for sentence in sentences:
                    if keyword in sentence:
                        key_points.append({
                            'keyword': keyword,
                            'sentence': sentence[:100] + '...' if len(sentence) > 100 else sentence
                        })
        
        return key_points
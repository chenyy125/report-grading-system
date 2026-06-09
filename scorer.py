class ReportScorer:
    def __init__(self, weights=None):
        default_weights = {
            'images': 50,
            'structure': 20,
            'content': 30
        }
        self.weights = weights if weights else default_weights
    
    def calculate_scores(self, comparison, doc_data):
        """计算各项得分"""
        scores = {
            'images': self._score_images(comparison),
            'structure': self._score_structure(comparison),
            'content': self._score_content(comparison)
        }
        
        scores['total'] = self._calculate_total(scores)
        return scores
    
    def _score_images(self, comparison):
        """图片评分（50分）- 图片数量大致与参考答案一致即可得分"""
        max_score = self.weights['images']
        image_comp = comparison.get('image_comparison', {})
        
        ref_count = image_comp.get('ref_count', 0)
        stu_count = image_comp.get('stu_count', 0)
        ratio = image_comp.get('ratio', 0.0)
        
        if ref_count == 0:
            return max_score
        
        if stu_count == 0:
            return 0
        
        if ratio >= 0.8:
            return max_score
        elif ratio >= 0.6:
            return round(max_score * 0.8, 1)
        elif ratio >= 0.4:
            return round(max_score * 0.6, 1)
        elif ratio >= 0.2:
            return round(max_score * 0.3, 1)
        else:
            return 0
    
    def _score_structure(self, comparison):
        """结构完整性评分（20分）"""
        max_score = self.weights['structure']
        structure_match = comparison.get('structure_match', 0.0)
        missing_sections = len(comparison.get('missing_sections', []))
        
        base_score = structure_match * max_score
        deduction = min(missing_sections * 4, max_score * 0.5)
        
        return max(0, round(base_score - deduction, 1))
    
    def _score_content(self, comparison):
        """内容匹配度评分（30分）"""
        max_score = self.weights['content']
        content_similarity = comparison.get('content_similarity', 0.0)
        
        differences = comparison.get('differences', [])
        content_mismatches = [d for d in differences if d['type'] == 'content_mismatch']
        mismatch_count = len(content_mismatches)
        
        base_score = content_similarity * max_score
        deduction = min(mismatch_count * 5, max_score * 0.4)
        
        return max(0, round(base_score - deduction, 1))
    
    def _calculate_total(self, scores):
        """计算总分"""
        total = sum(scores[dim] for dim in ['images', 'structure', 'content'])
        return round(total, 1)
    
    def get_grade(self, total_score):
        """根据总分获取等级"""
        if total_score >= 90:
            return '优秀'
        elif total_score >= 80:
            return '良好'
        elif total_score >= 70:
            return '中等'
        elif total_score >= 60:
            return '及格'
        else:
            return '不及格'
    
    def get_score_details(self, scores):
        """获取详细得分说明"""
        details = []
        
        details.append(f"图片匹配度: {scores['images']}/{self.weights['images']}")
        details.append(f"结构完整性: {scores['structure']}/{self.weights['structure']}")
        details.append(f"内容匹配度: {scores['content']}/{self.weights['content']}")
        details.append(f"总分: {scores['total']}/100")
        
        return details
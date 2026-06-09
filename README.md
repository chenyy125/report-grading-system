# 实训报告智能批改系统

基于Trae的实训报告智能批改系统，支持多种格式文档的自动评分与评语生成。

## 功能特点

- 📄 **文档解析**: 支持docx、doc、pdf、txt、md、rtf、odt格式文档解析
- 📊 **参考答案比对**: 将学生报告与参考答案进行结构、内容和图片比对
- 🎯 **自动评分**: 多维度评分（图片匹配度、结构完整性、内容匹配度）
- 💬 **评语生成**: 自动生成个性化评语和改进建议
- 📤 **报告输出**: 支持JSON和HTML格式的批改报告导出
- 📁 **批量处理**: 支持批量处理整个文件夹的学生报告
- 🌐 **Web界面**: 提供Streamlit Web界面，便于教师使用

## 技术栈

- Python 3.8+
- python-docx (docx解析)
- pdfplumber (pdf解析)
- scikit-learn (文本相似度计算)
- nltk (文本处理)
- Streamlit (Web界面)

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 命令行模式

批改单个报告：
```bash
python main.py -r reference/reference_report.docx -s submissions/student_report.docx
```

批量批改：
```bash
python main.py -r reference/reference_report.docx -d submissions/
```

### Web界面模式

```bash
streamlit run app.py
```
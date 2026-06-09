import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

REFERENCE_DIR = os.path.join(BASE_DIR, 'reference')
SUBMISSIONS_DIR = os.path.join(BASE_DIR, 'submissions')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')

os.makedirs(REFERENCE_DIR, exist_ok=True)
os.makedirs(SUBMISSIONS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

IMAGE_THRESHOLD = 0.8

SIMILARITY_THRESHOLD = 0.6

REPORT_SECTIONS = [
    '实训目的', '实验目的', '目的',
    '实训步骤', '实验步骤', '步骤', '过程',
    '实验结果', '实训结果', '结果',
    '问题反思', '反思', '总结',
    '心得体会', '体会', '感想'
]
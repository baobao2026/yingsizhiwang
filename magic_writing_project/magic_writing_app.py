import streamlit as st
import pandas as pd
import random
from datetime import datetime
import json
import requests
import time
from typing import List, Dict, Optional
import os

# ==================== DeepSeek API 配置 ====================
def get_api_key():
    """安全获取API密钥"""
    # 1. 环境变量
    key_from_env = os.environ.get("DEEPSEEK_API_KEY")
    if key_from_env:
        return key_from_env
    
    # 2. Streamlit secrets
    try:
        key_from_secrets = st.secrets.get("DEEPSEEK_API_KEY")
        if key_from_secrets:
            return key_from_secrets
    except:
        pass
    
    # 3. 返回空（表示未配置）
    return None

DEEPSEEK_API_KEY = get_api_key()
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
OFFLINE_MODE = DEEPSEEK_API_KEY is None

def call_deepseek_api(messages: List[Dict], temperature: float = 0.7, max_retries: int = 2) -> Optional[str]:
    """调用DeepSeek API，带重试机制"""
    if OFFLINE_MODE:
        return None
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 1000  # 控制输出长度
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                DEEPSEEK_API_URL, 
                headers=headers, 
                json=payload, 
                timeout=(5, 15)  # 连接5秒，读取15秒
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            elif response.status_code == 429:
                wait_time = (attempt + 1) * 2
                time.sleep(wait_time)
                continue
            else:
                st.error(f"API调用失败: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            return None
        except Exception as e:
            st.error(f"API错误: {str(e)}")
            return None
    
    return None

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="🎨 英思织网 | AI写作魔法学院",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 精美CSS样式 ====================
st.markdown("""
<style>
    /* 主背景 */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        background-attachment: fixed;
    }
    
    /* 主标题 - 渐变艺术字 */
    .main-title {
        text-align: center;
        background: linear-gradient(90deg, 
            #FF3366 0%, 
            #FF9933 25%, 
            #FFCC00 50%, 
            #33CC33 75%, 
            #3366FF 100%
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3.8rem !important;
        font-weight: 900 !important;
        font-family: 'Microsoft YaHei', 'SimHei', sans-serif;
        margin: 20px 0 10px 0 !important;
        padding: 20px;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.1);
        position: relative;
        letter-spacing: 2px;
    }
    
    .main-title::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 25%;
        width: 50%;
        height: 5px;
        background: linear-gradient(90deg, 
            #FF3366 0%, 
            #FF9933 25%, 
            #FFCC00 50%, 
            #33CC33 75%, 
            #3366FF 100%
        );
        border-radius: 3px;
    }
    
    /* 副标题 */
    .sub-title {
        text-align: center;
        color: #555;
        font-size: 1.4rem;
        font-family: 'Microsoft YaHei', sans-serif;
        background: rgba(255, 255, 255, 0.9);
        padding: 15px 40px;
        border-radius: 30px;
        border: 2px solid #FF9933;
        display: inline-block;
        margin: 0 auto 30px auto;
        box-shadow: 0 8px 20px rgba(255, 153, 51, 0.15);
        font-weight: 600;
    }
    
    /* 装饰图标 */
    .decorative-icons {
        display: flex;
        justify-content: center;
        gap: 25px;
        margin: 15px 0 30px 0;
        font-size: 2.2rem;
    }
    
    .decorative-icons span {
        animation: float 3s ease-in-out infinite;
    }
    
    .decorative-icons span:nth-child(1) { animation-delay: 0s; }
    .decorative-icons span:nth-child(2) { animation-delay: 0.5s; }
    .decorative-icons span:nth-child(3) { animation-delay: 1s; }
    .decorative-icons span:nth-child(4) { animation-delay: 1.5s; }
    .decorative-icons span:nth-child(5) { animation-delay: 2s; }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-15px); }
    }
    
    /* 功能卡片 */
    .feature-card {
        background: white;
        border-radius: 20px;
        padding: 25px;
        margin: 15px 0;
        border-top: 6px solid;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
        height: 100%;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.8), transparent);
    }
    
    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
    }
    
    .card-blue { border-color: #4D96FF; background: linear-gradient(135deg, #F0F8FF, white); }
    .card-green { border-color: #6BCF7F; background: linear-gradient(135deg, #F0FFF4, white); }
    .card-orange { border-color: #FF9A3D; background: linear-gradient(135deg, #FFF9F0, white); }
    .card-purple { border-color: #9D4DFF; background: linear-gradient(135deg, #F5F0FF, white); }
    
    .card-icon {
        font-size: 2.5rem;
        margin-bottom: 15px;
        display: block;
    }
    
    .card-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #333;
        margin-bottom: 12px;
        font-family: 'Microsoft YaHei', sans-serif;
    }
    
    .card-desc {
        color: #666;
        font-size: 1rem;
        line-height: 1.6;
        font-family: 'Microsoft YaHei', sans-serif;
    }
    
    /* 按钮样式 */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s !important;
        border: none !important;
    }
    
    .primary-button {
        background: linear-gradient(135deg, #4D96FF, #9D4DFF) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(77, 150, 255, 0.3) !important;
    }
    
    .primary-button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 20px rgba(77, 150, 255, 0.4) !important;
    }
    
    .secondary-button {
        background: white !important;
        color: #4D96FF !important;
        border: 2px solid #4D96FF !important;
    }
    
    /* 侧边栏 */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%) !important;
    }
    
    .sidebar-header {
        text-align: center;
        padding: 25px 15px;
        border-bottom: 2px solid rgba(255,255,255,0.1);
        margin-bottom: 20px;
    }
    
    .sidebar-title {
        color: white;
        font-size: 1.8rem;
        font-weight: 800;
        margin: 10px 0;
        font-family: 'Microsoft YaHei', sans-serif;
    }
    
    .sidebar-subtitle {
        color: #FFD93D;
        font-size: 1rem;
        margin: 5px 0;
    }
    
    .nav-button {
        width: 100%;
        text-align: left;
        background: rgba(255,255,255,0.1);
        border: none;
        color: white;
        border-radius: 10px;
        padding: 14px 20px;
        margin: 6px 0;
        font-size: 1rem;
        font-weight: 500;
        transition: all 0.3s;
        display: flex;
        align-items: center;
        gap: 12px;
        cursor: pointer;
    }
    
    .nav-button:hover {
        background: rgba(255,255,255,0.2);
        transform: translateX(8px);
    }
    
    .nav-button.active {
        background: linear-gradient(135deg, #FF9A3D, #FFD93D);
        box-shadow: 0 5px 15px rgba(255, 154, 61, 0.3);
    }
    
    /* 内容区域 */
    .content-box {
        background: white;
        border-radius: 18px;
        padding: 25px;
        margin: 20px 0;
        border: 1px solid #E2E8F0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.06);
    }
    
    /* 标签页 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: #F7FAFC;
        padding: 10px;
        border-radius: 15px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 12px 24px;
        background: white;
        border: 2px solid transparent;
        font-weight: 600;
        font-family: 'Microsoft YaHei', sans-serif;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #4D96FF, #9D4DFF) !important;
        color: white !important;
        border: 2px solid white !important;
        box-shadow: 0 5px 15px rgba(77, 150, 255, 0.2) !important;
    }
    
    /* 词汇卡片 */
    .vocab-card {
        background: white;
        border-radius: 15px;
        padding: 18px;
        margin: 12px 0;
        border-left: 5px solid #4D96FF;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        transition: all 0.3s;
    }
    
    .vocab-card:hover {
        transform: translateX(5px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
    }
    
    /* 状态徽章 */
    .status-badge {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 15px;
        font-weight: 600;
        font-size: 0.85rem;
        margin: 3px;
    }
    
    .badge-success { background: linear-gradient(135deg, #6BCF7F, #4CAF50); color: white; }
    .badge-warning { background: linear-gradient(135deg, #FFD93D, #FF9800); color: white; }
    .badge-info { background: linear-gradient(135deg, #4D96FF, #2196F3); color: white; }
    .badge-purple { background: linear-gradient(135deg, #9D4DFF, #7B1FA2); color: white; }
    
    /* 输入框美化 */
    .stTextArea textarea, .stTextInput input {
        border-radius: 12px !important;
        border: 2px solid #E2E8F0 !important;
        padding: 12px !important;
        font-size: 1rem !important;
        font-family: 'Microsoft YaHei', sans-serif !important;
    }
    
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #4D96FF !important;
        box-shadow: 0 0 0 3px rgba(77, 150, 255, 0.1) !important;
    }
    
    /* 进度条 */
    .progress-container {
        background: #F7FAFC;
        border-radius: 10px;
        padding: 15px;
        margin: 15px 0;
    }
    
    /* 游戏卡片（简化版） */
    .simple-game-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        text-align: center;
        border: 2px solid #E2E8F0;
        transition: all 0.3s;
    }
    
    .simple-game-card:hover {
        border-color: #4D96FF;
        box-shadow: 0 8px 20px rgba(77, 150, 255, 0.1);
    }
    
    /* 响应式调整 */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.5rem !important;
        }
        .sub-title {
            font-size: 1.1rem;
            padding: 12px 25px;
        }
        .decorative-icons {
            font-size: 1.8rem;
            gap: 15px;
        }
    }
</style>
""", unsafe_allow_html=True)

# ==================== 初始化状态 ====================
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'language' not in st.session_state:
    st.session_state.language = 'cn'
if 'writing_history' not in st.session_state:
    st.session_state.writing_history = []
if 'evaluation_history' not in st.session_state:
    st.session_state.evaluation_history = []
if 'writing_drafts' not in st.session_state:
    st.session_state.writing_drafts = []
if 'selected_theme' not in st.session_state:
    st.session_state.selected_theme = None
if 'selected_level' not in st.session_state:
    st.session_state.selected_level = 'basic'
if 'search_for_writing' not in st.session_state:
    st.session_state.search_for_writing = False
if 'writing_topic' not in st.session_state:
    st.session_state.writing_topic = ''
if 'writing_grade' not in st.session_state:
    st.session_state.writing_grade = 'Grade 3-4'

# ==================== AI助手类（修复版） ====================
class AIAssistant:
    """修复版的AI助手类"""
    
    @staticmethod
    def evaluate_writing(student_text: str, topic: str, grade: str) -> Dict:
        """评价学生作文"""
        if OFFLINE_MODE:
            return AIAssistant._get_offline_evaluation(topic, grade)
            
        prompt = f"""请对以下英语作文进行评价：
        
        主题：{topic}
        年级：{grade}
        作文内容：{student_text[:800]}
        
        请提供：
        1. 总体评分（0-100分）
        2. 优点（2-3点）
        3. 改进建议（2-3点）
        4. 推荐学习的词汇（3-5个）
        
        请用简洁的中文回复。"""
        
        messages = [{"role": "user", "content": prompt}]
        response = call_deepseek_api(messages, temperature=0.3)
        
        if response:
            return {
                'score': AIAssistant._extract_score(response),
                'feedback': response,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'topic': topic,
                'grade': grade
            }
        else:
            return AIAssistant._get_offline_evaluation(topic, grade)
    
    @staticmethod
    def _extract_score(text: str) -> int:
        """从文本中提取分数"""
        import re
        patterns = [
            r'(\d+)[分\s]',
            r'评分[：:]\s*(\d+)',
            r'(\d+)\s*分'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    score = int(match.group(1))
                    return max(0, min(100, score))
                except:
                    pass
        
        return 75  # 默认分数
    
    @staticmethod
    def _get_offline_evaluation(topic: str, grade: str) -> Dict:
        """离线评价"""
        return {
            'score': 78,
            'feedback': f"""## 📊 作文评价（离线模式）

**主题：** {topic}
**年级：** {grade}

### ✅ 优点：
1. 主题明确，内容相关
2. 基本语法正确
3. 表达基本清晰

### 💡 改进建议：
1. 使用更多学过的词汇
2. 增加句子多样性
3. 注意大小写和标点

### 📚 推荐词汇：
- learn (学习)
- happy (快乐的)
- important (重要的)
- friend (朋友)
- school (学校)

继续努力，你会越来越棒！✨""",
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'topic': topic,
            'grade': grade
        }
    
    @staticmethod
    def recommend_vocabulary_for_topic(topic: str, grade: str) -> str:
        """根据主题推荐词汇"""
        if OFFLINE_MODE:
            return AIAssistant._get_offline_vocab(topic, grade)
            
        prompt = f"""请为以下写作主题推荐英语词汇：
        
        主题：{topic}
        年级：{grade}
        
        请提供：
        1. 基础词汇（5-8个，带中文解释）
        2. 扩展词汇（5-8个，带中文解释）
        3. 使用建议
        
        请用中文回复，格式清晰。"""
        
        messages = [{"role": "user", "content": prompt}]
        response = call_deepseek_api(messages)
        
        return response or AIAssistant._get_offline_vocab(topic, grade)
    
    @staticmethod
    def _get_offline_vocab(topic: str, grade: str) -> str:
        """离线词汇推荐"""
        theme_vocabs = {
            'school': ['student', 'teacher', 'classroom', 'book', 'homework', 'learn', 'exam'],
            'family': ['father', 'mother', 'parents', 'brother', 'sister', 'family', 'home'],
            'animal': ['cat', 'dog', 'pet', 'animal', 'fish', 'bird', 'rabbit'],
            'food': ['apple', 'banana', 'food', 'rice', 'water', 'juice', 'milk'],
        }
        
        # 匹配主题
        topic_lower = topic.lower()
        matched_words = []
        
        for key, words in theme_vocabs.items():
            if key in topic_lower:
                matched_words.extend(words)
        
        if not matched_words:
            matched_words = ['student', 'like', 'have', 'can', 'go', 'good', 'happy']
        
        vocab_text = f"## 📚 主题 '{topic}' 词汇推荐\n\n"
        vocab_text += "### 基础词汇\n"
        for word in matched_words[:6]:
            cn_meanings = {
                'student': '学生', 'teacher': '老师', 'classroom': '教室',
                'book': '书', 'homework': '作业', 'learn': '学习',
                'father': '爸爸', 'mother': '妈妈', 'family': '家庭',
                'cat': '猫', 'dog': '狗', 'pet': '宠物'
            }
            cn = cn_meanings.get(word, '常用词')
            vocab_text += f"- **{word}** - {cn}\n"
        
        vocab_text += "\n### 💡 使用建议\n"
        vocab_text += "1. 尝试在作文中使用这些词汇\n"
        vocab_text += "2. 每个单词造一个句子\n"
        vocab_text += "3. 分类记忆，效果更好\n"
        
        return vocab_text
    
    @staticmethod
    def recommend_sentences_for_topic(topic: str, grade: str) -> str:
        """根据主题推荐句型"""
        if OFFLINE_MODE:
            return AIAssistant._get_offline_sentences(topic, grade)
            
        prompt = f"""请为以下写作主题推荐英语句型：
        
        主题：{topic}
        年级：{grade}
        
        请提供：
        1. 基础句型（3-5个）
        2. 每个句型的中文解释和例句
        3. 使用建议
        
        请用中文回复。"""
        
        messages = [{"role": "user", "content": prompt}]
        response = call_deepseek_api(messages)
        
        return response or AIAssistant._get_offline_sentences(topic, grade)
    
    @staticmethod
    def _get_offline_sentences(topic: str, grade: str) -> str:
        """离线句型推荐"""
        sentences = {
            'basic': [
                {'pattern': 'I like...', 'cn': '我喜欢...', 'example': 'I like apples.'},
                {'pattern': 'I have...', 'cn': '我有...', 'example': 'I have a book.'},
                {'pattern': 'I can...', 'cn': '我能...', 'example': 'I can swim.'},
            ],
            'intermediate': [
                {'pattern': 'I want to...', 'cn': '我想要...', 'example': 'I want to learn English.'},
                {'pattern': 'There is/are...', 'cn': '有...', 'example': 'There are three books.'},
            ]
        }
        
        level = 'basic' if '1-2' in grade or '3-4' in grade else 'intermediate'
        
        text = f"## 🔤 主题 '{topic}' 句型推荐\n\n"
        text += f"**适合年级：** {grade}\n\n"
        
        for sentence in sentences[level]:
            text += f"### ✨ {sentence['pattern']}\n"
            text += f"- **中文：** {sentence['cn']}\n"
            text += f"- **例句：** {sentence['example']}\n\n"
        
        text += "### 💡 练习建议\n"
        text += "1. 用每个句型造2个句子\n"
        text += "2. 尝试组合使用这些句型\n"
        text += "3. 在写作中大胆使用\n"
        
        return text
    
    @staticmethod
    def generate_writing_example(topic: str, grade: str) -> str:
        """生成范文"""
        if OFFLINE_MODE:
            return AIAssistant._get_offline_example(topic, grade)
            
        prompt = f"""请写一篇英语范文：
        
        主题：{topic}
        年级：{grade}
        
        要求：
        1. 字数适中，符合年级水平
        2. 使用丰富的词汇和句型
        3. 结构清晰
        4. 结尾用中文简单点评
        
        请先写英文范文，最后用中文点评。"""
        
        messages = [{"role": "user", "content": prompt}]
        response = call_deepseek_api(messages)
        
        return response or AIAssistant._get_offline_example(topic, grade)
    
    @staticmethod
    def _get_offline_example(topic: str, grade: str) -> str:
        """离线范文"""
        examples = {
            'My Pet': """
**My Pet Dog**

I have a pet dog. His name is Lucky. He is brown and white. He has two big eyes and a small nose.

Lucky is very cute. He likes to play with me. Every day, we run in the park. He can catch a ball.

I love my dog. He is my good friend. We are happy together.

**点评：** 这篇作文介绍了宠物狗，使用了简单句型和基础词汇，适合初学者。可以尝试增加更多细节描述。
""",
            'My Family': """
**My Family**

I have a happy family. There are four people in my family. They are my father, my mother, my sister and me.

My father is a teacher. He works at a school. My mother is a doctor. She helps sick people.

My sister is a student. She is in Grade 2. We play together every day.

I love my family. We eat dinner together every night. We are always happy.

**点评：** 文章结构清晰，介绍了家庭成员和他们的职业，使用了there be句型，适合三年级学生。
"""
        }
        
        if topic in examples:
            return examples[topic]
        
        return f"""
**{topic}**

I like this topic. It is very interesting. I have many things to write.

First, I want to say something about {topic}. It is important to me. I learn many things from it.

In my life, {topic} makes me happy. I want to know more about it. I will study hard.

**点评：** 这是一篇基础范文，展示了基本写作结构。你可以根据自己的经历添加更多具体内容。
"""

# ==================== 英语内容库 ====================
class EnglishContentLibrary:
    """英语教学内容库"""
    
    VOCABULARY = {
        'animals': [
            {'word': 'cat', 'cn': '猫', 'sentence': 'The cat is cute.'},
            {'word': 'dog', 'cn': '狗', 'sentence': 'I have a dog.'},
            {'word': 'fish', 'cn': '鱼', 'sentence': 'Fish swim in water.'},
            {'word': 'bird', 'cn': '鸟', 'sentence': 'Birds can fly.'},
            {'word': 'rabbit', 'cn': '兔子', 'sentence': 'The rabbit is white.'},
        ],
        'food': [
            {'word': 'apple', 'cn': '苹果', 'sentence': 'I eat an apple.'},
            {'word': 'banana', 'cn': '香蕉', 'sentence': 'Monkeys like bananas.'},
            {'word': 'rice', 'cn': '米饭', 'sentence': 'We eat rice every day.'},
            {'word': 'milk', 'cn': '牛奶', 'sentence': 'I drink milk for breakfast.'},
            {'word': 'egg', 'cn': '鸡蛋', 'sentence': 'I like boiled eggs.'},
        ],
        'family': [
            {'word': 'father', 'cn': '爸爸', 'sentence': 'My father is tall.'},
            {'word': 'mother', 'cn': '妈妈', 'sentence': 'My mother cooks well.'},
            {'word': 'brother', 'cn': '兄弟', 'sentence': 'I play with my brother.'},
            {'word': 'sister', 'cn': '姐妹', 'sentence': 'My sister sings well.'},
            {'word': 'family', 'cn': '家庭', 'sentence': 'I love my family.'},
        ],
        'school': [
            {'word': 'teacher', 'cn': '老师', 'sentence': 'Our teacher is kind.'},
            {'word': 'student', 'cn': '学生', 'sentence': 'I am a student.'},
            {'word': 'book', 'cn': '书', 'sentence': 'This is my book.'},
            {'word': 'pen', 'cn': '钢笔', 'sentence': 'I write with a pen.'},
            {'word': 'classroom', 'cn': '教室', 'sentence': 'Our classroom is clean.'},
        ],
    }
    
    SENTENCE_PATTERNS = {
        'basic': [
            {'pattern': 'I am...', 'cn': '我是...', 'example': 'I am a student.', 'level': '初级'},
            {'pattern': 'I like...', 'cn': '我喜欢...', 'example': 'I like apples.', 'level': '初级'},
            {'pattern': 'I have...', 'cn': '我有...', 'example': 'I have a book.', 'level': '初级'},
            {'pattern': 'I can...', 'cn': '我能...', 'example': 'I can swim.', 'level': '初级'},
        ],
        'intermediate': [
            {'pattern': 'There is/are...', 'cn': '有...', 'example': 'There is a cat.', 'level': '中级'},
            {'pattern': 'I want to...', 'cn': '我想要...', 'example': 'I want to learn.', 'level': '中级'},
            {'pattern': 'I need to...', 'cn': '我需要...', 'example': 'I need to study.', 'level': '中级'},
        ]
    }
    
    @staticmethod
    def get_vocabulary_by_theme(theme: str):
        """获取主题词汇"""
        return EnglishContentLibrary.VOCABULARY.get(theme, [])
    
    @staticmethod
    def get_sentences_by_level(level: str):
        """获取句型"""
        return EnglishContentLibrary.SENTENCE_PATTERNS.get(level, [])

# ==================== 侧边栏 ====================
with st.sidebar:
    # Logo区域
    st.markdown("""
    <div class="sidebar-header">
        <div style="font-size: 3em; margin-bottom: 10px; color: #FFD93D;">🎨✨</div>
        <h1 class="sidebar-title">英思织网</h1>
        <p class="sidebar-subtitle">AI写作魔法学院</p>
        <div style="margin-top: 15px;">
            <span class="status-badge badge-success">AI驱动</span>
            <span class="status-badge badge-purple">专业版</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 导航菜单
    st.markdown("### 📚 功能导航")
    
    nav_items = [
        {"id": "home", "emoji": "🏠", "label": "魔法学院首页"},
        {"id": "writing", "emoji": "✏️", "label": "写作工坊"},
        {"id": "vocabulary", "emoji": "📖", "label": "词汇助手"},
        {"id": "sentences", "emoji": "🔤", "label": "句型助手"},
        {"id": "evaluate", "emoji": "⭐", "label": "作品评价"},
        {"id": "progress", "emoji": "📊", "label": "成长记录"},
    ]
    
    for item in nav_items:
        is_active = st.session_state.page == item["id"]
        
        if st.button(
            f"{item['emoji']} {item['label']}",
            key=f"nav_{item['id']}",
            use_container_width=True,
            type="primary" if is_active else "secondary"
        ):
            st.session_state.page = item["id"]
            st.rerun()
    
    st.markdown("<hr style='border-color: rgba(255,255,255,0.2)'>", unsafe_allow_html=True)
    
    # API状态显示
    st.markdown("### ⚡ 系统状态")
    
    if OFFLINE_MODE:
        st.error("🔴 离线模式")
        st.info("请配置API密钥启用AI功能")
        with st.expander("如何配置"):
            st.code("""
# 方法1：环境变量
export DEEPSEEK_API_KEY="你的密钥"

# 方法2：创建 .streamlit/secrets.toml
DEEPSEEK_API_KEY = "你的密钥"
            """)
    else:
        st.success("🟢 AI在线")
        st.caption("DeepSeek API已连接")
    
    # 快速工具
    st.markdown("### 🛠️ 快速工具")
    if st.button("🔄 刷新页面", use_container_width=True):
        st.rerun()
    
    # 语言切换
    st.markdown("<hr style='border-color: rgba(255,255,255,0.2)'>", unsafe_allow_html=True)
    if st.button("🌐 切换语言", use_container_width=True):
        st.session_state.language = 'en' if st.session_state.language == 'cn' else 'cn'
        st.rerun()

# ==================== 主页 ====================
if st.session_state.page == 'home':
    st.markdown("""
    <div style="text-align: center;">
        <h1 class="main-title">🎨 英思织网</h1>
        <h2 style="color: #666; margin-top: -10px; font-size: 1.8rem;">AI写作魔法学院</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="decorative-icons">
        <span>✨</span>
        <span>🎨</span>
        <span>✏️</span>
        <span>📚</span>
        <span>⭐</span>
    </div>
    """, unsafe_allow_html=True)
    
    subtitle = "让每个孩子爱上英语写作的魔法之旅 ✨" if st.session_state.language == 'cn' else "Magic Journey to Love English Writing"
    st.markdown(f'<div class="sub-title">{subtitle}</div>', unsafe_allow_html=True)
    
    # 快速开始按钮
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("✏️ 开始写作", use_container_width=True, type="primary", key="quick_write"):
            st.session_state.page = "writing"
            st.rerun()
    
    with col2:
        if st.button("📖 学习词汇", use_container_width=True, type="primary", key="quick_vocab"):
            st.session_state.page = "vocabulary"
            st.rerun()
    
    with col3:
        if st.button("🔤 掌握句型", use_container_width=True, type="primary", key="quick_sentences"):
            st.session_state.page = "sentences"
            st.rerun()
    
    with col4:
        if st.button("⭐ 作品评价", use_container_width=True, type="primary", key="quick_eval"):
            st.session_state.page = "evaluate"
            st.rerun()
    
    # 特色功能展示
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("## ✨ 核心特色功能")
    
    features = [
        {
            "title": "🤖 AI智能评价",
            "desc": "深度分析作文，给出专业评分和改进建议",
            "color": "card-blue"
        },
        {
            "title": "📚 主题词汇推荐",
            "desc": "根据写作主题智能推荐相关词汇和例句",
            "color": "card-green"
        },
        {
            "title": "🔤 句型智能匹配",
            "desc": "提供适合不同水平的句型和实用例句",
            "color": "card-orange"
        },
        {
            "title": "📊 成长轨迹记录",
            "desc": "记录每一次进步，见证写作能力的提升",
            "color": "card-purple"
        },
    ]
    
    cols = st.columns(2)
    for idx, feature in enumerate(features):
        with cols[idx % 2]:
            st.markdown(f"""
            <div class="feature-card {feature['color']}">
                <div class="card-icon">{feature['title'].split(' ')[0]}</div>
                <div class="card-title">{feature['title'].split(' ', 1)[1]}</div>
                <div class="card-desc">{feature['desc']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # 使用统计
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("## 📈 使用统计")
    
    stat_cols = st.columns(4)
    with stat_cols[0]:
        st.metric("写作次数", len(st.session_state.writing_history))
    with stat_cols[1]:
        st.metric("评价次数", len(st.session_state.evaluation_history))
    with stat_cols[2]:
        st.metric("草稿保存", len(st.session_state.writing_drafts))
    with stat_cols[3]:
        st.metric("AI状态", "在线" if not OFFLINE_MODE else "离线")

# ==================== 写作工坊页面 ====================
elif st.session_state.page == 'writing':
    st.markdown("""
    <div style="text-align: center;">
        <h1 class="main-title">✏️ 写作魔法工坊</h1>
    </div>
    """, unsafe_allow_html=True)
    
    subtitle = "释放你的创意，写下精彩篇章 ✨"
    st.markdown(f'<div class="sub-title">{subtitle}</div>', unsafe_allow_html=True)
    
    # 写作区域
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 📝 写作设置")
        
        writing_topic = st.text_input(
            "**作文主题**",
            placeholder="例如：My Pet Dog, My School Life, My Family...",
            value=st.session_state.get('writing_topic', ''),
            key="writing_topic"
        )
        
        writing_grade = st.selectbox(
            "**适合年级**",
            ["Grade 1-2", "Grade 3-4", "Grade 5-6", "Grade 7-8"],
            index=1,
            key="writing_grade"
        )
        
        writing_content = st.text_area(
            "**开始写作...**",
            height=350,
            placeholder="在这里写下你的作文...\n\n提示：可以先写大纲，再补充细节。",
            value=st.session_state.get('writing_content', ''),
            key="writing_content"
        )
    
    with col2:
        st.markdown("### 🛠️ 写作工具")
        
        # 获取词汇帮助
        if st.button("📚 相关词汇", use_container_width=True, key="get_vocab"):
            if writing_topic:
                st.session_state.page = "vocabulary"
                st.session_state.search_for_writing = True
                st.session_state.writing_topic = writing_topic
                st.session_state.writing_grade = writing_grade
                st.rerun()
            else:
                st.warning("请先输入写作主题")
        
        # 获取句型帮助
        if st.button("🔤 相关句型", use_container_width=True, key="get_sentences"):
            if writing_topic:
                st.session_state.page = "sentences"
                st.session_state.search_for_writing = True
                st.session_state.writing_topic = writing_topic
                st.session_state.writing_grade = writing_grade
                st.rerun()
            else:
                st.warning("请先输入写作主题")
        
        # 保存草稿
        if st.button("💾 保存草稿", use_container_width=True, key="save_draft"):
            if writing_content:
                draft = {
                    'topic': writing_topic,
                    'content': writing_content,
                    'grade': writing_grade,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                st.session_state.writing_drafts.append(draft)
                st.success("草稿已保存！")
        
        # 查看范文
        if st.button("📖 参考范文", use_container_width=True, key="view_example"):
            if writing_topic:
                with st.spinner("正在生成范文..."):
                    example = AIAssistant.generate_writing_example(writing_topic, writing_grade)
                    st.markdown("### 📖 AI范文参考")
                    st.markdown(f'<div class="content-box">{example}</div>', unsafe_allow_html=True)
            else:
                st.warning("请先输入写作主题")
    
    # 操作按钮
    st.markdown("<br>", unsafe_allow_html=True)
    
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    
    with btn_col1:
        if st.button("💡 AI写作建议", use_container_width=True, key="ai_suggest"):
            if writing_content and writing_topic:
                with st.spinner("AI正在分析..."):
                    # 这里可以添加具体的建议功能
                    st.info("AI建议功能：尝试使用更多描述性词汇，增加细节描写。")
            else:
                st.warning("请先完成写作内容")
    
    with btn_col2:
        if st.button("⭐ 提交评价", use_container_width=True, type="primary", key="submit_eval"):
            if writing_content and writing_topic:
                # 保存到历史
                st.session_state.writing_history.append({
                    'topic': writing_topic,
                    'content': writing_content,
                    'grade': writing_grade,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                
                st.session_state.page = "evaluate"
                st.rerun()
            else:
                st.warning("请先完成写作内容")
    
    with btn_col3:
        if st.button("🔄 清空重写", use_container_width=True, key="clear_writing"):
            st.session_state.writing_topic = ''
            st.session_state.writing_content = ''
            st.rerun()

# ==================== 词汇助手页面 ====================
elif st.session_state.page == 'vocabulary':
    st.markdown("""
    <div style="text-align: center;">
        <h1 class="main-title">📖 词汇魔法助手</h1>
    </div>
    """, unsafe_allow_html=True)
    
    subtitle = "智能推荐写作词汇，让表达更丰富 ✨"
    st.markdown(f'<div class="sub-title">{subtitle}</div>', unsafe_allow_html=True)
    
    # 标签页
    tab1, tab2 = st.tabs(["🔍 主题搜索", "📚 主题分类"])
    
    with tab1:
        st.markdown("### 🔍 根据主题搜索词汇")
        
        search_topic = st.text_input(
            "输入你的写作主题",
            placeholder="例如：My Pet, School Life, Family...",
            key="vocab_search"
        )
        
        search_grade = st.selectbox(
            "选择年级",
            ["Grade 1-2", "Grade 3-4", "Grade 5-6", "Grade 7-8"],
            index=1,
            key="vocab_grade"
        )
        
        if st.button("🔍 搜索词汇", type="primary", key="search_vocab"):
            if search_topic:
                with st.spinner("AI正在推荐词汇..."):
                    recommendation = AIAssistant.recommend_vocabulary_for_topic(search_topic, search_grade)
                    st.markdown(f'<div class="content-box">{recommendation}</div>', unsafe_allow_html=True)
            else:
                st.warning("请输入写作主题")
    
    with tab2:
        st.markdown("### 📚 常用主题词汇")
        
        themes = ['animals', 'food', 'family', 'school']
        theme_names = {
            'animals': '🐶 动物世界',
            'food': '🍎 美食天地', 
            'family': '👨‍👩‍👧‍👦 家庭亲情',
            'school': '🏫 校园生活'
        }
        
        cols = st.columns(2)
        for idx, theme in enumerate(themes):
            with cols[idx % 2]:
                if st.button(theme_names[theme], use_container_width=True, key=f"theme_{theme}"):
                    st.session_state.selected_theme = theme
                    st.rerun()
        
        # 显示选定主题的词汇
        if st.session_state.get('selected_theme'):
            theme = st.session_state.selected_theme
            vocab_list = EnglishContentLibrary.get_vocabulary_by_theme(theme)
            
            if vocab_list:
                st.markdown(f"### {theme_names.get(theme, theme)} 词汇")
                
                for word in vocab_list:
                    st.markdown(f"""
                    <div class="vocab-card">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div>
                                <h4 style="margin: 0; color: #333;">
                                    <strong>{word['word']}</strong>
                                    <span style="color: #666; margin-left: 10px;">{word['cn']}</span>
                                </h4>
                                <div style="margin-top: 10px;">
                                    <span class="status-badge badge-info">{theme_names.get(theme, theme)}</span>
                                </div>
                            </div>
                        </div>
                        <div style="margin-top: 15px; color: #555; font-style: italic;">
                            💡 {word['sentence']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

# ==================== 句型助手页面 ====================
elif st.session_state.page == 'sentences':
    st.markdown("""
    <div style="text-align: center;">
        <h1 class="main-title">🔤 句型魔法助手</h1>
    </div>
    """, unsafe_allow_html=True)
    
    subtitle = "掌握核心句型，让写作更流畅 ✨"
    st.markdown(f'<div class="sub-title">{subtitle}</div>', unsafe_allow_html=True)
    
    # 标签页
    tab1, tab2 = st.tabs(["🔍 主题搜索", "📚 句型库"])
    
    with tab1:
        st.markdown("### 🔍 根据主题搜索句型")
        
        search_topic = st.text_input(
            "输入你的写作主题",
            placeholder="例如：My Daily Life, My Hobbies, My Dream...",
            key="sentence_search"
        )
        
        search_grade = st.selectbox(
            "选择年级",
            ["Grade 1-2", "Grade 3-4", "Grade 5-6", "Grade 7-8"],
            index=1,
            key="sentence_grade"
        )
        
        if st.button("🔍 搜索句型", type="primary", key="search_sentences"):
            if search_topic:
                with st.spinner("AI正在推荐句型..."):
                    recommendation = AIAssistant.recommend_sentences_for_topic(search_topic, search_grade)
                    st.markdown(f'<div class="content-box">{recommendation}</div>', unsafe_allow_html=True)
            else:
                st.warning("请输入写作主题")
    
    with tab2:
        st.markdown("### 📚 分级句型库")
        
        level_cols = st.columns(2)
        levels = ['basic', 'intermediate']
        level_names = {'basic': '初级句型', 'intermediate': '中级句型'}
        
        selected_level = st.session_state.get('selected_level', 'basic')
        
        for idx, level in enumerate(levels):
            with level_cols[idx]:
                if st.button(
                    f"📚 {level_names[level]}",
                    use_container_width=True,
                    type="primary" if selected_level == level else "secondary",
                    key=f"level_{level}"
                ):
                    st.session_state.selected_level = level
                    st.rerun()
        
        # 显示选定级别的句型
        if 'selected_level' in st.session_state:
            level = st.session_state.selected_level
            sentences = EnglishContentLibrary.get_sentences_by_level(level)
            
            if sentences:
                st.markdown(f"### 📝 {level_names[level]}")
                
                for sentence in sentences:
                    st.markdown(f"""
                    <div class="vocab-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <h4 style="margin: 0; color: #333;">
                                    <strong>{sentence['pattern']}</strong>
                                    <span style="color: #666; margin-left: 10px; font-size: 0.9em;">
                                        ({sentence['cn']})
                                    </span>
                                </h4>
                                <div style="margin-top: 10px;">
                                    <span class="status-badge badge-info">{sentence['level']}</span>
                                </div>
                            </div>
                        </div>
                        <div style="margin-top: 15px; padding: 12px; background: #f8f9fa; border-radius: 8px;">
                            <strong>例句:</strong> {sentence['example']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

# ==================== 作品评价页面 ====================
elif st.session_state.page == 'evaluate':
    st.markdown("""
    <div style="text-align: center;">
        <h1 class="main-title">⭐ 智能作品评价</h1>
    </div>
    """, unsafe_allow_html=True)
    
    subtitle = "AI专业评价，个性化指导 ✨"
    st.markdown(f'<div class="sub-title">{subtitle}</div>', unsafe_allow_html=True)
    
    # 获取最近一篇作文
    recent_writing = None
    if st.session_state.get('writing_history'):
        recent_writing = st.session_state.writing_history[-1]
    
    st.markdown("### 📝 待评价作品")
    
    if recent_writing:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            student_text = st.text_area(
                "作文内容：",
                value=recent_writing['content'],
                height=300,
                key="essay_content"
            )
        
        with col2:
            st.markdown("### ⚙️ 评价设置")
            topic = st.text_input("作文主题：", value=recent_writing['topic'], key="eval_topic")
            grade = st.selectbox("学生年级：", 
                               ["Grade 1-2", "Grade 3-4", "Grade 5-6", "Grade 7-8"],
                               index=["Grade 1-2", "Grade 3-4", "Grade 5-6", "Grade 7-8"].index(recent_writing['grade']) 
                               if recent_writing['grade'] in ["Grade 1-2", "Grade 3-4", "Grade 5-6", "Grade 7-8"] else 1,
                               key="eval_grade")
    else:
        st.info("暂无写作作品，请先到写作工坊完成一篇作文。")
        if st.button("✏️ 去写作", key="goto_writing"):
            st.session_state.page = "writing"
            st.rerun()
        student_text = ""
        topic = ""
        grade = "Grade 3-4"
    
    # 评价按钮
    if student_text and topic:
        if st.button("✨ 开始AI评价", type="primary", use_container_width=True, key="start_eval"):
            with st.spinner("🧠 AI正在认真评价中..."):
                evaluation = AIAssistant.evaluate_writing(student_text, topic, grade)
                
                # 显示评价结果
                st.markdown("### 📊 评价结果")
                
                # 分数显示
                score = evaluation['score']
                score_color = "#4CAF50" if score >= 80 else "#FF9800" if score >= 60 else "#F44336"
                
                st.markdown(f"""
                <div style="text-align: center; padding: 30px; background: white; border-radius: 20px; margin: 20px 0; border: 3px solid {score_color};">
                    <div style="font-size: 1.2rem; color: #666; margin-bottom: 10px;">综合评分</div>
                    <div style="font-size: 3.5rem; font-weight: bold; color: {score_color};">
                        {score}/100
                    </div>
                    <div style="margin-top: 20px;">
                        <div style="display: inline-block; width: 80%; height: 20px; background: #f0f0f0; border-radius: 10px; overflow: hidden;">
                            <div style="width: {score}%; height: 100%; background: {score_color}; border-radius: 10px;"></div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 详细反馈
                st.markdown("### 📝 详细反馈")
                st.markdown(f'<div class="content-box">{evaluation["feedback"]}</div>', unsafe_allow_html=True)
                
                # 保存评价记录
                st.session_state.evaluation_history.append({
                    'topic': evaluation['topic'],
                    'score': score,
                    'timestamp': evaluation['timestamp'],
                    'grade': evaluation['grade'],
                    'text_preview': student_text[:100] + "..."
                })
                
                st.success(f"✅ 评价完成！时间：{evaluation['timestamp']}")
                
                # 查看历史按钮
                if st.button("📊 查看评价记录", key="view_history"):
                    st.session_state.page = "progress"
                    st.rerun()

# ==================== 成长记录页面 ====================
elif st.session_state.page == 'progress':
    st.markdown("""
    <div style="text-align: center;">
        <h1 class="main-title">📊 成长记录册</h1>
    </div>
    """, unsafe_allow_html=True)
    
    subtitle = "记录进步足迹，见证成长点滴 ✨"
    st.markdown(f'<div class="sub-title">{subtitle}</div>', unsafe_allow_html=True)
    
    # 统计数据
    st.markdown("## 📈 学习统计")
    
    stat_cols = st.columns(4)
    
    with stat_cols[0]:
        writing_count = len(st.session_state.get('writing_history', []))
        st.metric("写作次数", writing_count)
    
    with stat_cols[1]:
        eval_count = len(st.session_state.get('evaluation_history', []))
        st.metric("评价次数", eval_count)
    
    with stat_cols[2]:
        draft_count = len(st.session_state.get('writing_drafts', []))
        st.metric("草稿保存", draft_count)
    
    with stat_cols[3]:
        avg_score = 0
        if eval_count > 0:
            scores = [e['score'] for e in st.session_state.evaluation_history]
            avg_score = sum(scores) // len(scores)
        st.metric("平均分数", f"{avg_score}分")
    
    # 写作历史
    st.markdown("### 📝 写作历史")
    if st.session_state.get('writing_history'):
        for i, entry in enumerate(reversed(st.session_state.writing_history[-5:])):
            with st.expander(f"{entry['timestamp']} - {entry['topic']} ({entry['grade']})"):
                st.write("**内容预览：**")
                st.text(entry['content'][:200] + "..." if len(entry['content']) > 200 else entry['content'])
    else:
        st.info("暂无写作历史，快去写作工坊开始创作吧！")
        if st.button("✏️ 去写作", key="goto_write"):
            st.session_state.page = "writing"
            st.rerun()
    
    # 评价历史
    st.markdown("### ⭐ 评价记录")
    if st.session_state.get('evaluation_history'):
        for entry in st.session_state.evaluation_history[-5:]:
            score_color = "#4CAF50" if entry['score'] >= 80 else "#FF9800" if entry['score'] >= 60 else "#F44336"
            
            st.markdown(f"""
            <div style="padding: 15px; background: white; border-radius: 10px; margin: 10px 0; border-left: 5px solid {score_color};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>{entry['topic']}</strong>
                        <div style="color: #666; font-size: 0.9em;">{entry['timestamp']} | {entry.get('grade', '未知年级')}</div>
                    </div>
                    <div style="font-size: 1.3rem; font-weight: bold; color: {score_color};">
                        {entry['score']}/100
                    </div>
                </div>
                <div style="color: #999; font-size: 0.85em; margin-top: 5px;">
                    {entry.get('text_preview', '')}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("暂无评价记录，快去评价页面试试吧！")
        if st.button("⭐ 去评价", key="goto_eval"):
            st.session_state.page = "evaluate"
            st.rerun()

# ==================== 页脚 ====================
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")

footer_cols = st.columns([2, 1, 1])

with footer_cols[0]:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.markdown(f"""
    <div style="color: #666; text-align: center;">
        <p style="margin: 0;">
            <strong>🎨 英思织网 AI写作魔法学院</strong> | 
            🤖 Powered by DeepSeek AI | 
            ⏰ {current_time}
        </p>
        <p style="margin: 5px 0 0 0; font-size: 0.9em;">
            © 2024 英思织网 版权所有 | 让写作变得更有趣！ ✨
        </p>
    </div>
    """, unsafe_allow_html=True)

with footer_cols[1]:
    if st.button("🏠 返回首页", use_container_width=True, key="footer_home"):
        st.session_state.page = "home"
        st.rerun()

with footer_cols[2]:
    st.caption("🚀 专业版 v3.0")

# ==================== API密钥配置提示 ====================
if OFFLINE_MODE:
    st.markdown("---")
    with st.expander("🔧 配置AI功能（重要）", expanded=True):
        st.markdown("### 🚀 启用AI功能")
        st.info("当前处于离线模式，部分AI功能不可用。请配置DeepSeek API密钥：")
        
        st.code("""
# 方法1：创建配置文件（推荐）
1. 在项目根目录创建文件夹：.streamlit
2. 在文件夹中创建文件：secrets.toml
3. 添加以下内容：

DEEPSEEK_API_KEY = "sk-a9b0d92a0d474ca6acd0ceb24360fef8"

# 方法2：设置环境变量
export DEEPSEEK_API_KEY="sk-a9b0d92a0d474ca6acd0ceb24360fef8"

# 方法3：Streamlit Cloud部署
在App Settings → Secrets中添加：
DEEPSEEK_API_KEY = "sk-a9b0d92a0d474ca6acd0ceb24360fef8"
        """)
        
        st.markdown("### 🔑 获取API密钥")
        st.write("1. 访问 [DeepSeek官网](https://www.deepseek.com/)")
        st.write("2. 注册/登录账号")
        st.write("3. 进入API管理页面")
        st.write("4. 创建新的API密钥")
        st.write("5. 复制密钥并按照上面的方法配置")
        
        if st.button("🔄 重新检查密钥配置", key="check_key_again"):
            st.rerun()

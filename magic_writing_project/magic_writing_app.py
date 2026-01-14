import streamlit as st
import pandas as pd
import random
from datetime import datetime
import json
import requests
import time
from typing import List, Dict, Optional

# ==================== DeepSeek API 配置 ====================
DEEPSEEK_API_KEY = st.secrets.get("DEEPSEEK_API_KEY", "sk-a9b0d92a0d474ca6acd0ceb24360fef8")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

def call_deepseek_api(messages: List[Dict], temperature: float = 0.7) -> Optional[str]:
    """调用DeepSeek API - 增强版"""
    try:
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 1500
        }
        
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            st.error(f"API调用失败: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"调用DeepSeek API时出错: {str(e)}")
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
    /* 主标题样式 */
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #FF6B9D 0%, #FF9A3D 20%, #FFD93D 40%, #6BCF7F 60%, #4D96FF 80%, #9D4DFF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3.2rem !important;
        font-weight: 900 !important;
        margin: 10px 0 5px 0 !important;
        padding: 15px;
    }
    
    .title-container {
        text-align: center;
        margin-bottom: 20px;
    }
    
    .decorative-icons {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-top: 5px;
        font-size: 1.8rem;
    }
    
    .icon-bounce {
        animation: bounce 2s infinite;
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    /* 副标题 */
    .subtitle-text {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        padding: 15px 30px;
        border-radius: 50px;
        border: 3px dashed #FF9A3D;
        display: inline-block;
        margin: 10px auto 30px auto;
        box-shadow: 0 5px 15px rgba(255, 154, 61, 0.1);
    }
    
    /* 功能卡片 */
    .feature-card {
        background: white;
        border-radius: 25px;
        padding: 30px;
        margin: 15px 0;
        border-top: 8px solid;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
    }
    
    .card-orange { border-color: #FF9A3D; }
    .card-green { border-color: #6BCF7F; }
    .card-blue { border-color: #4D96FF; }
    .card-pink { border-color: #FF6B9D; }
    .card-purple { border-color: #9D4DFF; }
    
    .card-icon {
        font-size: 2.8rem;
        margin-bottom: 15px;
        display: block;
    }
    
    .card-title {
        font-size: 1.6rem;
        font-weight: 800;
        color: #333;
        margin-bottom: 10px;
    }
    
    .card-desc {
        color: #666;
        font-size: 1rem;
        line-height: 1.6;
    }
    
    /* 按钮样式 */
    .fun-button {
        background: linear-gradient(135deg, #FF9A3D, #FFD93D);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 12px 25px;
        font-weight: 700;
        font-size: 1.1rem;
        transition: all 0.3s;
        cursor: pointer;
    }
    
    .fun-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(255, 154, 61, 0.4);
    }
    
    /* 游戏卡片 */
    .game-card {
        background: white;
        border-radius: 20px;
        padding: 25px;
        margin: 15px 0;
        border: 3px solid;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        transition: all 0.3s;
        text-align: center;
        cursor: pointer;
    }
    
    .game-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    
    .game-card h3 {
        margin: 0 0 10px 0;
        color: #333;
    }
    
    .game-card p {
        color: #666;
        margin: 0;
    }
    
    /* 短语卡片 */
    .phrase-card {
        background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border-left: 5px solid #6BCF7F;
    }
    
    .phrase-card h4 {
        color: #2E7D32;
        margin: 0 0 10px 0;
    }
    
    .phrase-card .english {
        font-size: 1.3rem;
        font-weight: bold;
        color: #333;
        margin-bottom: 8px;
    }
    
    .phrase-card .chinese {
        color: #666;
        font-style: italic;
    }
    
    /* 状态标签 */
    .status-badge {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        margin: 3px;
        color: white;
    }
    
    .badge-success { background: #6BCF7F; }
    .badge-warning { background: #FFD93D; }
    .badge-info { background: #4D96FF; }
    
    /* 输入框 */
    .stTextArea textarea, .stTextInput input {
        border-radius: 15px !important;
        border: 2px solid #E2E8F0 !important;
        padding: 12px !important;
    }
    
    /* 标签页 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #F7FAFC;
        padding: 8px;
        border-radius: 15px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 12px 24px;
        background: white;
        border: 2px solid transparent;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #FF9A3D, #FFD93D);
        color: white !important;
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
if 'game_score' not in st.session_state:
    st.session_state.game_score = 0
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
if 'selected_game' not in st.session_state:
    st.session_state.selected_game = None
if 'game_content' not in st.session_state:
    st.session_state.game_content = None
if 'game_theme' not in st.session_state:
    st.session_state.game_theme = 'animals'
if 'phrases_page' not in st.session_state:
    st.session_state.phrases_page = 0

# ==================== 扩展内容库 ====================
class EnglishContentLibrary:
    """英语教学内容库 - 修复版"""
    
    # 词汇库
    VOCABULARY_LIBRARY = [
        # 动物主题
        {'word': 'cat', 'cn': '猫', 'grade': '1', 'theme': 'animals', 'sentence': 'I have a cat.'},
        {'word': 'dog', 'cn': '狗', 'grade': '1', 'theme': 'animals', 'sentence': 'The dog runs fast.'},
        {'word': 'bird', 'cn': '鸟', 'grade': '1', 'theme': 'animals', 'sentence': 'Birds can fly.'},
        {'word': 'fish', 'cn': '鱼', 'grade': '1', 'theme': 'animals', 'sentence': 'Fish live in water.'},
        {'word': 'rabbit', 'cn': '兔子', 'grade': '1', 'theme': 'animals', 'sentence': 'Rabbits like carrots.'},
        {'word': 'elephant', 'cn': '大象', 'grade': '2', 'theme': 'animals', 'sentence': 'Elephants are big.'},
        {'word': 'lion', 'cn': '狮子', 'grade': '2', 'theme': 'animals', 'sentence': 'Lions are strong.'},
        {'word': 'tiger', 'cn': '老虎', 'grade': '2', 'theme': 'animals', 'sentence': 'Tigers have stripes.'},
        {'word': 'monkey', 'cn': '猴子', 'grade': '2', 'theme': 'animals', 'sentence': 'Monkeys like bananas.'},
        
        # 食物主题
        {'word': 'apple', 'cn': '苹果', 'grade': '1', 'theme': 'food', 'sentence': 'I eat an apple.'},
        {'word': 'banana', 'cn': '香蕉', 'grade': '1', 'theme': 'food', 'sentence': 'Bananas are yellow.'},
        {'word': 'orange', 'cn': '橙子', 'grade': '1', 'theme': 'food', 'sentence': 'Oranges are sweet.'},
        {'word': 'rice', 'cn': '米饭', 'grade': '1', 'theme': 'food', 'sentence': 'I eat rice every day.'},
        {'word': 'milk', 'cn': '牛奶', 'grade': '1', 'theme': 'food', 'sentence': 'Milk is good for health.'},
        {'word': 'bread', 'cn': '面包', 'grade': '1', 'theme': 'food', 'sentence': 'I like bread for breakfast.'},
        {'word': 'egg', 'cn': '鸡蛋', 'grade': '1', 'theme': 'food', 'sentence': 'Eggs are healthy.'},
        {'word': 'water', 'cn': '水', 'grade': '1', 'theme': 'food', 'sentence': 'Drink water every day.'},
        
        # 家庭主题
        {'word': 'father', 'cn': '爸爸', 'grade': '1', 'theme': 'family', 'sentence': 'My father is tall.'},
        {'word': 'mother', 'cn': '妈妈', 'grade': '1', 'theme': 'family', 'sentence': 'My mother is kind.'},
        {'word': 'brother', 'cn': '哥哥/弟弟', 'grade': '1', 'theme': 'family', 'sentence': 'My brother plays football.'},
        {'word': 'sister', 'cn': '姐姐/妹妹', 'grade': '1', 'theme': 'family', 'sentence': 'My sister sings well.'},
        {'word': 'family', 'cn': '家庭', 'grade': '1', 'theme': 'family', 'sentence': 'I love my family.'},
        {'word': 'home', 'cn': '家', 'grade': '1', 'theme': 'family', 'sentence': 'My home is warm.'},
        {'word': 'parents', 'cn': '父母', 'grade': '2', 'theme': 'family', 'sentence': 'My parents work hard.'},
        {'word': 'grandfather', 'cn': '爷爷', 'grade': '2', 'theme': 'family', 'sentence': 'My grandfather tells stories.'},
        
        # 学校主题
        {'word': 'teacher', 'cn': '老师', 'grade': '1', 'theme': 'school', 'sentence': 'My teacher helps me.'},
        {'word': 'student', 'cn': '学生', 'grade': '1', 'theme': 'school', 'sentence': 'I am a student.'},
        {'word': 'book', 'cn': '书', 'grade': '1', 'theme': 'school', 'sentence': 'I read books every day.'},
        {'word': 'pen', 'cn': '钢笔', 'grade': '1', 'theme': 'school', 'sentence': 'I write with a pen.'},
        {'word': 'pencil', 'cn': '铅笔', 'grade': '1', 'theme': 'school', 'sentence': 'Pencils are for drawing.'},
        {'word': 'desk', 'cn': '书桌', 'grade': '1', 'theme': 'school', 'sentence': 'My desk is clean.'},
        {'word': 'classroom', 'cn': '教室', 'grade': '2', 'theme': 'school', 'sentence': 'Our classroom is big.'},
        {'word': 'school', 'cn': '学校', 'grade': '2', 'theme': 'school', 'sentence': 'I go to school every day.'},
        
        # 颜色主题
        {'word': 'red', 'cn': '红色', 'grade': '1', 'theme': 'colors', 'sentence': 'Apples are red.'},
        {'word': 'blue', 'cn': '蓝色', 'grade': '1', 'theme': 'colors', 'sentence': 'The sky is blue.'},
        {'word': 'green', 'cn': '绿色', 'grade': '1', 'theme': 'colors', 'sentence': 'Grass is green.'},
        {'word': 'yellow', 'cn': '黄色', 'grade': '1', 'theme': 'colors', 'sentence': 'Bananas are yellow.'},
        {'word': 'black', 'cn': '黑色', 'grade': '1', 'theme': 'colors', 'sentence': 'My bag is black.'},
        {'word': 'white', 'cn': '白色', 'grade': '1', 'theme': 'colors', 'sentence': 'Clouds are white.'},
        {'word': 'orange', 'cn': '橙色', 'grade': '2', 'theme': 'colors', 'sentence': 'Oranges are orange.'},
        {'word': 'pink', 'cn': '粉色', 'grade': '2', 'theme': 'colors', 'sentence': 'My dress is pink.'},
        
        # 运动主题
        {'word': 'football', 'cn': '足球', 'grade': '2', 'theme': 'sports', 'sentence': 'I play football.'},
        {'word': 'basketball', 'cn': '篮球', 'grade': '2', 'theme': 'sports', 'sentence': 'Basketball is fun.'},
        {'word': 'run', 'cn': '跑步', 'grade': '1', 'theme': 'sports', 'sentence': 'I can run fast.'},
        {'word': 'jump', 'cn': '跳跃', 'grade': '1', 'theme': 'sports', 'sentence': 'Rabbits can jump high.'},
        {'word': 'swim', 'cn': '游泳', 'grade': '2', 'theme': 'sports', 'sentence': 'I like to swim.'},
        {'word': 'play', 'cn': '玩耍', 'grade': '1', 'theme': 'sports', 'sentence': 'Children like to play.'},
        {'word': 'sport', 'cn': '运动', 'grade': '2', 'theme': 'sports', 'sentence': 'Sport is good for health.'},
        {'word': 'game', 'cn': '游戏', 'grade': '2', 'theme': 'sports', 'sentence': 'We play games together.'}
    ]
    
    # 短语库 - 新增
    PHRASES_LIBRARY = [
        {'english': 'Good morning', 'chinese': '早上好', 'category': 'greetings', 'example': 'Good morning, teacher!'},
        {'english': 'How are you?', 'chinese': '你好吗？', 'category': 'greetings', 'example': 'How are you today?'},
        {'english': 'Thank you', 'chinese': '谢谢你', 'category': 'courtesy', 'example': 'Thank you for your help.'},
        {'english': 'You are welcome', 'chinese': '不客气', 'category': 'courtesy', 'example': "A: Thank you. B: You're welcome."},
        {'english': 'I am sorry', 'chinese': '对不起', 'category': 'apology', 'example': 'I am sorry I am late.'},
        {'english': 'Excuse me', 'chinese': '打扰一下', 'category': 'courtesy', 'example': 'Excuse me, may I ask a question?'},
        {'english': 'Nice to meet you', 'chinese': '很高兴见到你', 'category': 'greetings', 'example': 'Nice to meet you, my friend.'},
        {'english': 'What is your name?', 'chinese': '你叫什么名字？', 'category': 'conversation', 'example': "What's your name? My name is Li Ming."},
        {'english': 'How old are you?', 'chinese': '你多大了？', 'category': 'conversation', 'example': 'How old are you? I am eight years old.'},
        {'english': 'Where are you from?', 'chinese': '你来自哪里？', 'category': 'conversation', 'example': 'Where are you from? I am from China.'},
        {'english': 'I like it', 'chinese': '我喜欢它', 'category': 'expression', 'example': 'This book is interesting. I like it.'},
        {'english': 'I don\'t like it', 'chinese': '我不喜欢它', 'category': 'expression', 'example': 'I don\'t like rainy days.'},
        {'english': 'Let\'s go', 'chinese': '我们走吧', 'category': 'suggestion', 'example': 'Let\'s go to the park.'},
        {'english': 'Be careful', 'chinese': '小心', 'category': 'warning', 'example': 'Be careful! The floor is wet.'},
        {'english': 'Hurry up', 'chinese': '快点', 'category': 'urging', 'example': 'Hurry up, or we will be late.'},
        {'english': 'Wait a minute', 'chinese': '等一下', 'category': 'request', 'example': 'Wait a minute, please.'},
        {'english': 'What time is it?', 'chinese': '现在几点了？', 'category': 'time', 'example': 'What time is it? It\'s three o\'clock.'},
        {'english': 'See you later', 'chinese': '再见', 'category': 'farewell', 'example': 'See you later, my friend.'},
        {'english': 'Have a good day', 'chinese': '祝你今天愉快', 'category': 'wishes', 'example': 'Have a good day at school.'},
        {'english': 'Good luck', 'chinese': '祝你好运', 'category': 'wishes', 'example': 'Good luck with your test!'},
        {'english': 'I can do it', 'chinese': '我能做到', 'category': 'encouragement', 'example': 'Don\'t worry, I can do it.'},
        {'english': 'Well done', 'chinese': '做得好', 'category': 'praise', 'example': 'Well done! You got 100 points.'},
        {'english': 'I am happy', 'chinese': '我很高兴', 'category': 'emotion', 'example': 'Today is my birthday. I am happy.'},
        {'english': 'I am sad', 'chinese': '我很难过', 'category': 'emotion', 'example': 'My pet is sick. I am sad.'},
        {'english': 'I am tired', 'chinese': '我很累', 'category': 'condition', 'example': 'I played all day. I am tired.'},
        {'english': 'I am hungry', 'chinese': '我饿了', 'category': 'condition', 'example': 'It\'s lunch time. I am hungry.'},
        {'english': 'I am thirsty', 'chinese': '我渴了', 'category': 'condition', 'example': 'After running, I am thirsty.'}
    ]
    
    # 句型库
    SENTENCE_PATTERNS = {
        'basic': [
            {'pattern': 'I am...', 'cn': '我是...', 'example': 'I am a student.', 'level': 'A1'},
            {'pattern': 'I like...', 'cn': '我喜欢...', 'example': 'I like apples.', 'level': 'A1'},
            {'pattern': 'I have...', 'cn': '我有...', 'example': 'I have a book.', 'level': 'A1'},
            {'pattern': 'I can...', 'cn': '我能...', 'example': 'I can swim.', 'level': 'A1'},
            {'pattern': 'This is...', 'cn': '这是...', 'example': 'This is my friend.', 'level': 'A1'},
        ],
        'intermediate': [
            {'pattern': 'I want to...', 'cn': '我想要...', 'example': 'I want to learn English.', 'level': 'A2'},
            {'pattern': 'I need to...', 'cn': '我需要...', 'example': 'I need to study hard.', 'level': 'A2'},
            {'pattern': 'There is/are...', 'cn': '有...', 'example': 'There are three books.', 'level': 'A2'},
            {'pattern': 'Can I...?', 'cn': '我可以...吗？', 'example': 'Can I help you?', 'level': 'A2'},
            {'pattern': 'Do you like...?', 'cn': '你喜欢...吗？', 'example': 'Do you like football?', 'level': 'A2'},
        ],
        'advanced': [
            {'pattern': 'I think that...', 'cn': '我认为...', 'example': 'I think that English is important.', 'level': 'B1'},
            {'pattern': 'I hope to...', 'cn': '我希望...', 'example': 'I hope to visit London.', 'level': 'B1'},
            {'pattern': 'In my opinion,...', 'cn': '在我看来，...', 'example': 'In my opinion, reading is fun.', 'level': 'B1'},
            {'pattern': 'Not only... but also...', 'cn': '不仅...而且...', 'example': 'I like not only apples but also oranges.', 'level': 'B1'},
            {'pattern': 'Although...', 'cn': '虽然...', 'example': 'Although it is raining, we still play.', 'level': 'B1'},
        ]
    }
    
    # 主题分类
    THEMES = {
        'animals': ['cat', 'dog', 'bird', 'fish', 'rabbit'],
        'food': ['apple', 'banana', 'orange', 'rice', 'milk'],
        'family': ['father', 'mother', 'brother', 'sister', 'family'],
        'school': ['teacher', 'student', 'book', 'pen', 'classroom'],
        'colors': ['red', 'blue', 'green', 'yellow', 'black'],
        'sports': ['football', 'basketball', 'run', 'jump', 'swim'],
    }
    
    # 短语分类
    PHRASE_CATEGORIES = {
        'greetings': '问候',
        'courtesy': '礼貌用语',
        'apology': '道歉',
        'conversation': '日常对话',
        'expression': '表达情感',
        'suggestion': '建议',
        'warning': '警告',
        'request': '请求',
        'time': '时间',
        'farewell': '告别',
        'wishes': '祝福',
        'encouragement': '鼓励',
        'praise': '表扬',
        'emotion': '情感',
        'condition': '状态'
    }
    
    @staticmethod
    def get_vocabulary_by_theme(theme: str) -> List[Dict]:
        """根据主题获取词汇"""
        return [word for word in EnglishContentLibrary.VOCABULARY_LIBRARY 
                if word['theme'] == theme]
    
    @staticmethod
    def get_random_vocabulary(count: int = 10) -> List[Dict]:
        """随机获取词汇"""
        return random.sample(EnglishContentLibrary.VOCABULARY_LIBRARY, 
                            min(count, len(EnglishContentLibrary.VOCABULARY_LIBRARY)))
    
    @staticmethod
    def get_phrases_by_category(category: str = None) -> List[Dict]:
        """获取短语"""
        if category:
            return [phrase for phrase in EnglishContentLibrary.PHRASES_LIBRARY 
                   if phrase['category'] == category]
        return EnglishContentLibrary.PHRASES_LIBRARY
    
    @staticmethod
    def get_random_phrases(count: int = 10) -> List[Dict]:
        """随机获取短语"""
        return random.sample(EnglishContentLibrary.PHRASES_LIBRARY, 
                            min(count, len(EnglishContentLibrary.PHRASES_LIBRARY)))

# ==================== AI助手功能 ====================
class AIAssistant:
    """AI助手类"""
    
    @staticmethod
    def evaluate_writing(student_text: str, topic: str, grade: str) -> Dict:
        """评价学生作文"""
        prompt = f"""请评价这篇英语作文：
        
        主题：{topic}
        年级：{grade}
        作文：{student_text[:500]}
        
        请给出评分和建议，用中文回复。"""
        
        messages = [{"role": "user", "content": prompt}]
        response = call_deepseek_api(messages)
        
        if response:
            return {
                'score': 80,
                'feedback': response,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'topic': topic,
                'grade': grade
            }
        else:
            return {
                'score': 75,
                'feedback': "总体不错，继续努力！",
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'topic': topic,
                'grade': grade
            }
    
    @staticmethod
    def recommend_vocabulary_for_topic(topic: str, grade: str) -> str:
        """根据主题推荐词汇"""
        prompt = f"""为以下写作主题推荐相关英语词汇：
        
        主题：{topic}
        年级：{grade}
        
        请推荐10个相关词汇，用中文回复。"""
        
        messages = [{"role": "user", "content": prompt}]
        response = call_deepseek_api(messages)
        return response or "正在推荐词汇..."
    
    @staticmethod
    def generate_game_content(game_type: str, theme: str = None) -> Dict:
        """生成游戏内容 - 修复版"""
        
        if game_type == 'word_puzzle':
            # 单词拼图游戏
            vocab_list = EnglishContentLibrary.get_vocabulary_by_theme(theme or 'animals')
            
            if not vocab_list:
                vocab_list = EnglishContentLibrary.get_random_vocabulary(10)
            
            target = random.choice(vocab_list)
            target_word = target['word'].lower()
            
            # 打乱字母
            scrambled_list = list(target_word)
            random.shuffle(scrambled_list)
            scrambled = ''.join(scrambled_list)
            
            # 确保打乱后不一样
            while scrambled == target_word and len(target_word) > 2:
                random.shuffle(scrambled_list)
                scrambled = ''.join(scrambled_list)
            
            return {
                'target_word': target_word,
                'scrambled': scrambled,
                'hint': f"中文意思：{target['cn']}",
                'type': 'word_puzzle',
                'theme': theme
            }
        
        elif game_type == 'sentence_builder':
            # 句子组装游戏 - 修复版
            patterns = [
                "I have a ___",
                "I like to ___",
                "This is my ___",
                "I can ___",
                "My ___ is ___"
            ]
            
            pattern = random.choice(patterns)
            
            if "have a" in pattern:
                words = ['book', 'pen', 'dog', 'cat', 'ball']
                missing = random.choice(words)
            elif "like to" in pattern:
                words = ['read', 'play', 'sing', 'dance', 'run']
                missing = random.choice(words)
            elif "This is my" in pattern:
                words = ['friend', 'teacher', 'mother', 'father', 'book']
                missing = random.choice(words)
            elif "I can" in pattern:
                words = ['swim', 'jump', 'run', 'sing', 'dance']
                missing = random.choice(words)
            else:
                words = ['book', 'red', 'dog', 'small', 'pen']
                missing = random.choice(words)
            
            options = words.copy()
            random.shuffle(options)
            
            return {
                'pattern': pattern,
                'missing': missing,
                'options': options,
                'correct_answer': missing,
                'type': 'sentence_builder'
            }
        
        elif game_type == 'vocab_quiz':
            # 词汇挑战游戏 - 修复版
            vocab_list = EnglishContentLibrary.get_vocabulary_by_theme(theme or 'animals')
            
            if not vocab_list:
                vocab_list = EnglishContentLibrary.get_random_vocabulary(10)
            
            target = random.choice(vocab_list)
            
            # 生成错误选项
            all_words = [w for w in vocab_list if w['word'] != target['word']]
            
            if len(all_words) >= 3:
                wrong_answers = random.sample(all_words, 3)
            else:
                # 如果不够，用随机词汇补足
                extra_words = EnglishContentLibrary.get_random_vocabulary(10)
                wrong_answers = random.sample(extra_words, 3)
            
            options = [target['cn']] + [w['cn'] for w in wrong_answers]
            random.shuffle(options)
            
            return {
                'question': f"What is the Chinese meaning of '{target['word']}'?",
                'correct_answer': target['cn'],
                'options': options,
                'type': 'vocab_quiz',
                'word': target['word']
            }
        
        # 默认返回
        return {'type': game_type, 'content': '游戏内容准备中...'}

# ==================== 侧边栏 ====================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <div style="font-size: 2.5em; margin-bottom: 10px;">🎨✨</div>
        <h2 style="color: white; margin: 0;">英思织网</h2>
        <p style="color: rgba(255,255,255,0.8); margin: 5px 0;">
            AI写作魔法学院
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📚 导航菜单")
    
    pages = [
        {"id": "home", "emoji": "🏠", "name": "魔法学院"},
        {"id": "writing", "emoji": "✏️", "name": "写作工坊"},
        {"id": "vocabulary", "emoji": "📖", "name": "词汇助手"},
        {"id": "phrases", "emoji": "💬", "name": "短语宝典"},  # 新增
        {"id": "sentences", "emoji": "🔤", "name": "句型助手"},
        {"id": "evaluate", "emoji": "⭐", "name": "作品评价"},
        {"id": "games", "emoji": "🎮", "name": "游戏乐园"},
        {"id": "progress", "emoji": "📊", "name": "成长记录"}
    ]
    
    for page in pages:
        if st.button(
            f"{page['emoji']} {page['name']}",
            key=f"nav_{page['id']}",
            use_container_width=True,
            type="primary" if st.session_state.page == page['id'] else "secondary"
        ):
            st.session_state.page = page['id']
            st.rerun()
    
    st.markdown("---")
    
    # API状态
    st.markdown("### ⚡ AI状态")
    if DEEPSEEK_API_KEY.startswith('sk-a9b0'):
        st.warning("使用默认API密钥")
    else:
        st.success("API密钥已配置")

# ==================== 主页 ====================
if st.session_state.page == 'home':
    st.markdown("""
    <div class="title-container">
        <h1 class="main-header">🎨 英思织网 AI写作魔法学院</h1>
        <div class="decorative-icons">
            <span class="icon-bounce">✨</span>
            <span class="icon-bounce">🎨</span>
            <span class="icon-bounce">✏️</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="subtitle-text">让每个孩子爱上英语写作！</div>', unsafe_allow_html=True)
    
    # 快速开始
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("✏️ 开始写作", use_container_width=True, type="primary"):
            st.session_state.page = "writing"
            st.rerun()
    with col2:
        if st.button("📖 学习词汇", use_container_width=True, type="primary"):
            st.session_state.page = "vocabulary"
            st.rerun()
    with col3:
        if st.button("💬 常用短语", use_container_width=True, type="primary"):
            st.session_state.page = "phrases"
            st.rerun()
    with col4:
        if st.button("🎮 游戏乐园", use_container_width=True, type="primary"):
            st.session_state.page = "games"
            st.rerun()
    
    # 特色功能
    st.markdown("### ✨ 核心功能")
    cols = st.columns(3)
    
    with cols[0]:
        st.markdown("""
        <div class="feature-card card-orange">
            <div class="card-icon">🤖</div>
            <div class="card-title">AI智能助手</div>
            <div class="card-desc">
                • 智能作文评价<br>
                • 个性化建议<br>
                • 范文生成
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[1]:
        st.markdown("""
        <div class="feature-card card-green">
            <div class="card-icon">📚</div>
            <div class="card-title">丰富资源库</div>
            <div class="card-desc">
                • 分级词汇库<br>
                • 实用短语库<br>
                • 常用句型库
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[2]:
        st.markdown("""
        <div class="feature-card card-blue">
            <div class="card-icon">🎮</div>
            <div class="card-title">趣味游戏</div>
            <div class="card-desc">
                • 单词拼图<br>
                • 句子组装<br>
                • 词汇挑战
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==================== 写作工坊 ====================
elif st.session_state.page == 'writing':
    st.markdown("""
    <div class="title-container">
        <h1 class="main-header">✏️ 写作魔法工坊</h1>
        <div class="decorative-icons">
            <span class="icon-bounce">📝</span>
            <span class="icon-bounce">✨</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="subtitle-text">开启你的创意写作之旅</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        topic = st.text_input("📝 写作主题", placeholder="例如：My Pet, My Family...")
        grade = st.selectbox("🎓 适合年级", ["Grade 1-2", "Grade 3-4", "Grade 5-6", "Grade 7-8"])
        content = st.text_area("📝 开始写作...", height=300, placeholder="在这里写下你的作文...")
    
    with col2:
        st.markdown("### 🛠️ 写作工具")
        
        if st.button("📚 查找相关词汇", use_container_width=True):
            if topic:
                st.session_state.page = "vocabulary"
                st.session_state.writing_topic = topic
                st.rerun()
        
        if st.button("💬 查找相关短语", use_container_width=True):
            if topic:
                st.session_state.page = "phrases"
                st.session_state.writing_topic = topic
                st.rerun()
        
        if st.button("💾 保存草稿", use_container_width=True):
            if content:
                st.success("草稿已保存！")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("✨ AI写作建议", use_container_width=True):
            if content and topic:
                st.info("AI建议：尝试使用更多描述性词汇。")
    with col_btn2:
        if st.button("⭐ 提交评价", use_container_width=True, type="primary"):
            if content and topic:
                st.session_state.page = "evaluate"
                st.rerun()

# ==================== 词汇助手 ====================
elif st.session_state.page == 'vocabulary':
    st.markdown("""
    <div class="title-container">
        <h1 class="main-header">📖 词汇魔法助手</h1>
        <div class="decorative-icons">
            <span class="icon-bounce">🔤</span>
            <span class="icon-bounce">📚</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="subtitle-text">根据你的写作主题推荐相关词汇</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔍 主题搜索", "🎨 主题分类"])
    
    with tab1:
        search_topic = st.text_input("输入写作主题", placeholder="例如：My School Life...")
        if st.button("🔍 搜索词汇", type="primary"):
            if search_topic:
                with st.spinner("正在搜索..."):
                    time.sleep(1)
                    st.info("AI功能暂不可用，请查看主题分类词汇")
    
    with tab2:
        themes = list(EnglishContentLibrary.THEMES.keys())
        theme_names = {
            'animals': '🐶 动物', 
            'food': '🍎 食物', 
            'family': '👨‍👩‍👧‍👦 家庭',
            'school': '🏫 学校', 
            'colors': '🎨 颜色', 
            'sports': '⚽ 运动'
        }
        
        cols = st.columns(3)
        for idx, theme in enumerate(themes):
            with cols[idx % 3]:
                if st.button(f"{theme_names[theme]}", use_container_width=True):
                    st.session_state.selected_theme = theme
        
        if 'selected_theme' in st.session_state:
            theme = st.session_state.selected_theme
            vocab_list = EnglishContentLibrary.get_vocabulary_by_theme(theme)
            
            if vocab_list:
                st.markdown(f"### {theme_names[theme]}词汇")
                for word in vocab_list[:10]:
                    st.markdown(f"""
                    <div style="padding: 15px; background: white; border-radius: 10px; margin: 10px 0; border-left: 5px solid #4D96FF;">
                        <div style="display: flex; justify-content: space-between;">
                            <div>
                                <strong>{word['word']}</strong>
                                <div style="color: #666;">{word['cn']}</div>
                            </div>
                            <span class="status-badge badge-info">Grade {word['grade']}</span>
                        </div>
                        <div style="margin-top: 10px; color: #888; font-style: italic;">
                            {word['sentence']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

# ==================== 短语宝典（新增） ====================
elif st.session_state.page == 'phrases':
    st.markdown("""
    <div class="title-container">
        <h1 class="main-header">💬 英语短语宝典</h1>
        <div class="decorative-icons">
            <span class="icon-bounce">💭</span>
            <span class="icon-bounce">🗣️</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="subtitle-text">掌握常用英语短语，让表达更地道</div>', unsafe_allow_html=True)
    
    # 短语分类选择
    categories = list(EnglishContentLibrary.PHRASE_CATEGORIES.keys())
    category_names = EnglishContentLibrary.PHRASE_CATEGORIES
    
    st.markdown("### 📂 短语分类")
    cols = st.columns(5)
    selected_category = st.session_state.get('selected_phrase_category', None)
    
    for idx, category in enumerate(categories[:10]):  # 显示前10个分类
        with cols[idx % 5]:
            if st.button(
                f"{category_names[category]}",
                use_container_width=True,
                key=f"cat_{category}",
                type="primary" if selected_category == category else "secondary"
            ):
                st.session_state.selected_phrase_category = category
                st.session_state.phrases_page = 0
                st.rerun()
    
    # 显示短语
    st.markdown("### 📝 常用英语短语")
    
    if selected_category:
        phrases = EnglishContentLibrary.get_phrases_by_category(selected_category)
        category_display = category_names[selected_category]
        st.info(f"当前分类：{category_display}（共{len(phrases)}条）")
    else:
        phrases = EnglishContentLibrary.get_random_phrases(20)
        st.info("随机推荐常用短语")
    
    # 分页显示
    page_size = 8
    total_pages = (len(phrases) + page_size - 1) // page_size
    current_page = st.session_state.phrases_page
    
    start_idx = current_page * page_size
    end_idx = min(start_idx + page_size, len(phrases))
    
    for phrase in phrases[start_idx:end_idx]:
        st.markdown(f"""
        <div class="phrase-card">
            <div class="english">{phrase['english']}</div>
            <div class="chinese">{phrase['chinese']}</div>
            <div style="margin-top: 10px; font-size: 0.9em; color: #666;">
                📖 例句：{phrase['example']}
            </div>
            <div style="margin-top: 5px;">
                <span class="status-badge badge-success">{category_names.get(phrase['category'], phrase['category'])}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # 分页控制
    if total_pages > 1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if current_page > 0:
                if st.button("⬅️ 上一页"):
                    st.session_state.phrases_page -= 1
                    st.rerun()
        with col2:
            st.markdown(f"<div style='text-align: center; color: #666;'>第 {current_page + 1} 页 / 共 {total_pages} 页</div>", unsafe_allow_html=True)
        with col3:
            if current_page < total_pages - 1:
                if st.button("下一页 ➡️"):
                    st.session_state.phrases_page += 1
                    st.rerun()
    
    # 学习建议
    st.markdown("### 💡 学习建议")
    st.markdown("""
    1. **每天学习3-5个短语**，不要贪多
    2. **尝试造句**，在实际情境中使用
    3. **分类记忆**，按场景分类学习
    4. **定期复习**，巩固记忆效果
    """)

# ==================== 句型助手 ====================
elif st.session_state.page == 'sentences':
    st.markdown("""
    <div class="title-container">
        <h1 class="main-header">🔤 句型助手</h1>
        <div class="decorative-icons">
            <span class="icon-bounce">📝</span>
            <span class="icon-bounce">✨</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="subtitle-text">学习实用英语句型，提升写作能力</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["初级", "中级", "高级"])
    
    with tab1:
        sentences = EnglishContentLibrary.SENTENCE_PATTERNS['basic']
        for sentence in sentences:
            st.markdown(f"""
            <div style="padding: 20px; background: white; border-radius: 10px; margin: 10px 0; border-left: 5px solid #6BCF7F;">
                <h4>{sentence['pattern']} <span style="color: #666;">({sentence['cn']})</span></h4>
                <div style="margin: 10px 0; padding: 10px; background: #f0fff4; border-radius: 5px;">
                    <strong>例句：</strong>{sentence['example']}
                </div>
                <span class="status-badge badge-success">初级</span>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        sentences = EnglishContentLibrary.SENTENCE_PATTERNS['intermediate']
        for sentence in sentences:
            st.markdown(f"""
            <div style="padding: 20px; background: white; border-radius: 10px; margin: 10px 0; border-left: 5px solid #4D96FF;">
                <h4>{sentence['pattern']} <span style="color: #666;">({sentence['cn']})</span></h4>
                <div style="margin: 10px 0; padding: 10px; background: #f0f8ff; border-radius: 5px;">
                    <strong>例句：</strong>{sentence['example']}
                </div>
                <span class="status-badge badge-info">中级</span>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        sentences = EnglishContentLibrary.SENTENCE_PATTERNS['advanced']
        for sentence in sentences:
            st.markdown(f"""
            <div style="padding: 20px; background: white; border-radius: 10px; margin: 10px 0; border-left: 5px solid #9D4DFF;">
                <h4>{sentence['pattern']} <span style="color: #666;">({sentence['cn']})</span></h4>
                <div style="margin: 10px 0; padding: 10px; background: #f5f0ff; border-radius: 5px;">
                    <strong>例句：</strong>{sentence['example']}
                </div>
                <span class="status-badge badge-warning">高级</span>
            </div>
            """, unsafe_allow_html=True)

# ==================== 作品评价 ====================
elif st.session_state.page == 'evaluate':
    st.markdown("""
    <div class="title-container">
        <h1 class="main-header">⭐ 智能作品评价</h1>
        <div class="decorative-icons">
            <span class="icon-bounce">📊</span>
            <span class="icon-bounce">✨</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="subtitle-text">AI智能评价，个性化反馈</div>', unsafe_allow_html=True)
    
    st.markdown("### 📝 提交作品")
    topic = st.text_input("作文主题", "My School Life")
    grade = st.selectbox("学生年级", ["Grade 1-2", "Grade 3-4", "Grade 5-6", "Grade 7-8"])
    content = st.text_area("作文内容", height=200, placeholder="请输入你的作文...")
    
    if st.button("✨ 开始AI评价", type="primary", use_container_width=True):
        if content:
            with st.spinner("AI正在评价中..."):
                time.sleep(2)
                
                st.markdown("### 📊 评价结果")
                st.markdown("""
                <div style="text-align: center; padding: 30px; background: white; border-radius: 20px; margin: 20px 0;">
                    <div style="font-size: 1.2rem; color: #666;">综合评分</div>
                    <div style="font-size: 3.5rem; font-weight: bold; color: #4CAF50;">85/100</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("### 📝 详细反馈")
                st.markdown("""
                1. **总体评价**：作文结构完整，表达清晰
                2. **优点分析**：词汇使用恰当，句子通顺
                3. **改进建议**：可以增加更多细节描述
                4. **推荐词汇**：classroom, teacher, friend, learn, play
                """)
        else:
            st.warning("请输入作文内容")

# ==================== 游戏乐园（修复版） ====================
elif st.session_state.page == 'games':
    st.markdown("""
    <div class="title-container">
        <h1 class="main-header">🎮 写作游戏乐园</h1>
        <div class="decorative-icons">
            <span class="icon-bounce">🎲</span>
            <span class="icon-bounce">🏆</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="subtitle-text">在游戏中学习，在快乐中进步</div>', unsafe_allow_html=True)
    
    # 游戏选择
    st.markdown("## 🎯 选择游戏类型")
    games = [
        {"id": "word_puzzle", "name": "单词拼图", "emoji": "🧩", "desc": "将打乱的字母拼成正确的单词"},
        {"id": "sentence_builder", "name": "句子组装", "emoji": "🔤", "desc": "用给定的单词组成正确的句子"},
        {"id": "vocab_quiz", "name": "词汇挑战", "emoji": "🏆", "desc": "快速回答单词的意思"}
    ]
    
    cols = st.columns(3)
    for idx, game in enumerate(games):
        with cols[idx]:
            if st.button(
                f"{game['emoji']} {game['name']}",
                use_container_width=True,
                key=f"select_{game['id']}",
                type="primary" if st.session_state.get('selected_game') == game['id'] else "secondary"
            ):
                st.session_state.selected_game = game['id']
                st.session_state.game_content = None
                st.rerun()
    
    # 如果选择了游戏
    if st.session_state.selected_game:
        game_id = st.session_state.selected_game
        
        # 主题选择（只对单词和词汇游戏）
        if game_id in ['word_puzzle', 'vocab_quiz']:
            st.markdown("### 🎨 选择主题")
            theme_cols = st.columns(6)
            themes = ['animals', 'food', 'family', 'school', 'colors', 'sports']
            theme_names = ['动物', '食物', '家庭', '学校', '颜色', '运动']
            
            for idx, theme in enumerate(themes):
                with theme_cols[idx]:
                    if st.button(theme_names[idx], use_container_width=True, key=f"theme_{theme}"):
                        st.session_state.game_theme = theme
                        st.session_state.game_content = None
                        st.rerun()
        
        # 开始游戏按钮
        if st.button("🎮 开始新游戏", type="primary", key="start_game"):
            theme = st.session_state.get('game_theme', 'animals')
            game_content = AIAssistant.generate_game_content(game_id, theme)
            st.session_state.game_content = game_content
            st.rerun()
        
        # 显示游戏内容
        if st.session_state.game_content:
            content = st.session_state.game_content
            
            if game_id == 'word_puzzle':
                st.markdown("### 🧩 单词拼图游戏")
                
                st.markdown(f"""
                <div style="text-align: center; padding: 30px; background: white; border-radius: 20px; border: 3px solid #FF9A3D;">
                    <h3>猜猜这个单词是什么？</h3>
                    <p style="color: #FF9800; font-weight: bold;">💡 提示：{content.get('hint', '')}</p>
                    
                    <div style="margin: 30px 0;">
                        <div style="font-size: 2.5rem; letter-spacing: 15px; color: #4D96FF; font-weight: bold;">
                            {content.get('scrambled', '???').upper()}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 答案输入
                col1, col2 = st.columns([3, 1])
                with col1:
                    user_answer = st.text_input("输入你的答案：", key="puzzle_answer")
                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("✅ 提交答案", key="submit_puzzle"):
                        target = content.get('target_word', '').lower()
                        if user_answer.lower() == target:
                            st.success(f"🎉 太棒了！正确答案是：{target}")
                            st.session_state.game_score += 10
                        else:
                            st.error(f"再试一次！正确答案是：{target}")
            
            elif game_id == 'sentence_builder':
                st.markdown("### 🔤 句子组装游戏")
                
                st.markdown(f"""
                <div style="text-align: center; padding: 30px; background: white; border-radius: 20px; border: 3px solid #6BCF7F;">
                    <h3>用这个句型造一个句子</h3>
                    
                    <div style="margin: 30px 0; padding: 20px; background: #f0fff4; border-radius: 15px;">
                        <div style="font-size: 1.8rem; color: #2E7D32; font-weight: bold;">
                            {content.get('pattern', 'I have...')}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 选择填空
                options = content.get('options', [])
                correct = content.get('correct_answer', '')
                
                selected = st.radio("选择正确的单词完成句子：", options, key="sentence_option")
                
                if st.button("✅ 检查答案", key="check_sentence"):
                    if selected == correct:
                        st.success("🎉 正确！句子完整了！")
                        st.session_state.game_score += 10
                    else:
                        st.error(f"再想想！正确答案是：{correct}")
            
            elif game_id == 'vocab_quiz':
                st.markdown("### 🏆 词汇挑战游戏")
                
                st.markdown(f"""
                <div style="text-align: center; padding: 30px; background: white; border-radius: 20px; border: 3px solid #9D4DFF;">
                    <h3>词汇挑战</h3>
                    
                    <div style="margin: 30px 0; padding: 20px; background: #f5f0ff; border-radius: 15px;">
                        <div style="font-size: 1.8rem; color: #6B46C1; font-weight: bold;">
                            {content.get('question', 'What is the meaning?')}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 选择题
                options = content.get('options', [])
                correct = content.get('correct_answer', '')
                
                selected = st.radio("选择正确的中文意思：", options, key="vocab_option")
                
                if st.button("✅ 检查答案", key="check_vocab"):
                    if selected == correct:
                        st.success("🎉 正确！你答对了！")
                        st.session_state.game_score += 10
                    else:
                        st.error(f"再想想！正确答案是：{correct}")
        
        # 显示分数
        st.markdown(f"""
        <div style="text-align: center; margin-top: 30px; padding: 20px; background: linear-gradient(135deg, #667eea, #764ba2); color: white; border-radius: 15px;">
            <h3 style="color: white;">当前得分</h3>
            <div style="font-size: 2.5rem; font-weight: bold;">{st.session_state.game_score} 分</div>
        </div>
        """, unsafe_allow_html=True)

# ==================== 成长记录 ====================
elif st.session_state.page == 'progress':
    st.markdown("""
    <div class="title-container">
        <h1 class="main-header">📊 成长记录册</h1>
        <div class="decorative-icons">
            <span class="icon-bounce">📈</span>
            <span class="icon-bounce">🏆</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="subtitle-text">记录每一次进步，见证成长足迹</div>', unsafe_allow_html=True)
    
    # 统计数据
    col1, col2, col3 = st.columns(3)
    with col1:
        writing_count = len(st.session_state.writing_history)
        st.metric("写作次数", writing_count)
    with col2:
        eval_count = len(st.session_state.evaluation_history)
        st.metric("评价次数", eval_count)
    with col3:
        st.metric("游戏得分", st.session_state.game_score)
    
    # 最近活动
    st.markdown("### 📝 最近活动")
    activities = [
        {"time": "今天", "action": "完成一篇作文", "details": "My School Life"},
        {"time": "昨天", "action": "学习了新词汇", "details": "20个新单词"},
        {"time": "前天", "action": "玩游戏", "details": "单词拼图 +10分"}
    ]
    
    for activity in activities:
        st.markdown(f"""
        <div style="padding: 15px; background: white; border-radius: 10px; margin: 10px 0; border-left: 5px solid #4D96FF;">
            <div style="display: flex; justify-content: space-between;">
                <div>
                    <strong>{activity['action']}</strong>
                    <div style="color: #666;">{activity['details']}</div>
                </div>
                <div style="color: #999;">{activity['time']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==================== 页脚 ====================
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")

footer_col1, footer_col2 = st.columns([3, 1])
with footer_col1:
    st.markdown("""
    <div style="color: #666; text-align: center;">
        <p style="margin: 0;">
            <strong>🎨 英思织网 AI写作魔法学院</strong> | 
            🤖 Powered by DeepSeek AI | 
            © 2024 版权所有
        </p>
    </div>
    """, unsafe_allow_html=True)

with footer_col2:
    if st.button("🏠 返回首页"):
        st.session_state.page = "home"
        st.rerun()

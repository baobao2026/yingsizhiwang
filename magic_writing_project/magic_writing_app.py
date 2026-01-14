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
    """调用DeepSeek API"""
    try:
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 2000
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
    
    .card-orange { border-color: #FF9A3D; background: linear-gradient(135deg, #FFF9F0, white); }
    .card-green { border-color: #6BCF7F; background: linear-gradient(135deg, #F0FFF4, white); }
    .card-blue { border-color: #4D96FF; background: linear-gradient(135deg, #F0F8FF, white); }
    .card-pink { border-color: #FF6B9D; background: linear-gradient(135deg, #FFF0F5, white); }
    .card-purple { border-color: #9D4DFF; background: linear-gradient(135deg, #F5F0FF, white); }
    
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
        box-shadow: 0 5px 15px rgba(255, 154, 61, 0.3);
    }
    
    .fun-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(255, 154, 61, 0.4);
    }
    
    .primary-button {
        background: linear-gradient(135deg, #4D96FF, #9D4DFF);
        box-shadow: 0 5px 15px rgba(77, 150, 255, 0.3);
    }
    
    .primary-button:hover {
        background: linear-gradient(135deg, #9D4DFF, #4D96FF);
        box-shadow: 0 8px 20px rgba(77, 150, 255, 0.4);
    }
    
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
    
    .word-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border-left: 5px solid #4D96FF;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
    }
    
    .phrase-card {
        background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border-left: 5px solid #6BCF7F;
    }
    
    .sentence-card {
        background: linear-gradient(135deg, #F0F8FF, white);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border-left: 5px solid #FF9A3D;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
    }
    
    .evaluation-card {
        background: white;
        border-radius: 20px;
        padding: 25px;
        margin: 20px 0;
        border: 2px solid #E2E8F0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.05);
    }
    
    .game-card {
        background: white;
        border-radius: 20px;
        padding: 25px;
        margin: 15px 0;
        border: 3px solid transparent;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        transition: all 0.3s;
        text-align: center;
    }
    
    .game-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
</style>
""", unsafe_allow_html=True)

# ==================== 初始化状态 ====================
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'writing_history' not in st.session_state:
    st.session_state.writing_history = []
if 'evaluation_history' not in st.session_state:
    st.session_state.evaluation_history = []
if 'game_score' not in st.session_state:
    st.session_state.game_score = 0
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
if 'search_topic' not in st.session_state:
    st.session_state.search_topic = ''

# ==================== 内容库（与原始deepseek数据结合） ====================
class EnglishContentLibrary:
    """英语教学内容库 - 修复版，与原始deepseek数据结合"""
    
    # 词汇库 - 使用原始deepseek数据
    VOCABULARY_LIBRARY = {
        '人教版': [
            {'word': 'apple', 'cn': '苹果', 'grade': '1', 'theme': 'food', 'sentence': 'I eat an apple every day.'},
            {'word': 'book', 'cn': '书', 'grade': '1', 'theme': 'school', 'sentence': 'This is my English book.'},
            {'word': 'cat', 'cn': '猫', 'grade': '1', 'theme': 'animals', 'sentence': 'The cat is sleeping.'},
            {'word': 'dog', 'cn': '狗', 'grade': '1', 'theme': 'animals', 'sentence': 'I have a small dog.'},
            {'word': 'egg', 'cn': '鸡蛋', 'grade': '1', 'theme': 'food', 'sentence': 'I like eggs for breakfast.'},
            {'word': 'fish', 'cn': '鱼', 'grade': '1', 'theme': 'animals', 'sentence': 'The fish swims in water.'},
            {'word': 'girl', 'cn': '女孩', 'grade': '1', 'theme': 'people', 'sentence': 'She is a happy girl.'},
            {'word': 'hat', 'cn': '帽子', 'grade': '1', 'theme': 'clothes', 'sentence': 'I wear a red hat.'},
            {'word': 'ice', 'cn': '冰', 'grade': '1', 'theme': 'food', 'sentence': 'Ice is cold.'},
            {'word': 'juice', 'cn': '果汁', 'grade': '1', 'theme': 'food', 'sentence': 'I like orange juice.'},
        ],
        '外研版': [
            {'word': 'school', 'cn': '学校', 'grade': '2', 'theme': 'school', 'sentence': 'My school is very big.'},
            {'word': 'teacher', 'cn': '老师', 'grade': '2', 'theme': 'people', 'sentence': 'Our teacher is very kind.'},
            {'word': 'friend', 'cn': '朋友', 'grade': '2', 'theme': 'people', 'sentence': 'She is my best friend.'},
            {'word': 'family', 'cn': '家庭', 'grade': '2', 'theme': 'family', 'sentence': 'I love my family.'},
            {'word': 'mother', 'cn': '妈妈', 'grade': '2', 'theme': 'family', 'sentence': 'My mother cooks dinner.'},
            {'word': 'father', 'cn': '爸爸', 'grade': '2', 'theme': 'family', 'sentence': 'My father reads books.'},
            {'word': 'brother', 'cn': '兄弟', 'grade': '2', 'theme': 'family', 'sentence': 'My brother plays football.'},
            {'word': 'sister', 'cn': '姐妹', 'grade': '2', 'theme': 'family', 'sentence': 'My sister sings well.'},
        ],
        '牛津版': [
            {'word': 'playground', 'cn': '操场', 'grade': '3', 'theme': 'school', 'sentence': 'We play in the playground.'},
            {'word': 'classroom', 'cn': '教室', 'grade': '3', 'theme': 'school', 'sentence': 'Our classroom is clean.'},
            {'word': 'library', 'cn': '图书馆', 'grade': '3', 'theme': 'school', 'sentence': 'I read books in the library.'},
            {'word': 'computer', 'cn': '电脑', 'grade': '3', 'theme': 'technology', 'sentence': 'I use the computer to study.'},
            {'word': 'pencil', 'cn': '铅笔', 'grade': '3', 'theme': 'school', 'sentence': 'I write with a pencil.'},
            {'word': 'ruler', 'cn': '尺子', 'grade': '3', 'theme': 'school', 'sentence': 'I need a ruler to draw lines.'},
            {'word': 'eraser', 'cn': '橡皮', 'grade': '3', 'theme': 'school', 'sentence': 'I use an eraser to correct mistakes.'},
            {'word': 'bag', 'cn': '书包', 'grade': '3', 'theme': 'school', 'sentence': 'My bag is heavy with books.'},
        ]
    }
    
    # 短语库 - 新增
    PHRASES_LIBRARY = [
        {'english': 'Good morning', 'chinese': '早上好', 'theme': 'greeting', 'example': 'Good morning, teacher!'},
        {'english': 'Thank you', 'chinese': '谢谢你', 'theme': 'courtesy', 'example': 'Thank you for your help.'},
        {'english': 'I love my family', 'chinese': '我爱我的家人', 'theme': 'family', 'example': 'I love my family very much.'},
        {'english': 'My favorite animal', 'chinese': '我最喜欢的动物', 'theme': 'animals', 'example': 'My favorite animal is the panda.'},
        {'english': 'I like to read books', 'chinese': '我喜欢读书', 'theme': 'school', 'example': 'I like to read books in the library.'},
        {'english': 'Let\'s play together', 'chinese': '我们一起玩吧', 'theme': 'sports', 'example': 'Let\'s play football together.'},
        {'english': 'Have a nice day', 'chinese': '祝你今天愉快', 'theme': 'greeting', 'example': 'Have a nice day at school.'},
        {'english': 'I am happy', 'chinese': '我很开心', 'theme': 'emotion', 'example': 'Today is my birthday. I am happy.'},
        {'english': 'Can you help me?', 'chinese': '你能帮助我吗？', 'theme': 'school', 'example': 'Can you help me with my homework?'},
        {'english': 'What is your name?', 'chinese': '你叫什么名字？', 'theme': 'conversation', 'example': 'What is your name? My name is Li Ming.'},
    ]
    
    # 句型库 - 使用原始数据
    SENTENCE_PATTERNS = {
        'basic': [
            {'pattern': 'I am...', 'cn': '我是...', 'example': 'I am a student.', 'theme': 'introduction'},
            {'pattern': 'I like...', 'cn': '我喜欢...', 'example': 'I like apples.', 'theme': 'preference'},
            {'pattern': 'I have...', 'cn': '我有...', 'example': 'I have a book.', 'theme': 'possession'},
            {'pattern': 'I can...', 'cn': '我能...', 'example': 'I can swim.', 'theme': 'ability'},
        ],
        'intermediate': [
            {'pattern': 'I want to...', 'cn': '我想要...', 'example': 'I want to learn English.', 'theme': 'desire'},
            {'pattern': 'I need to...', 'cn': '我需要...', 'example': 'I need to study hard.', 'theme': 'necessity'},
            {'pattern': 'There is/are...', 'cn': '有...', 'example': 'There are three books on the table.', 'theme': 'existence'},
            {'pattern': 'Can I...?', 'cn': '我可以...吗？', 'example': 'Can I help you?', 'theme': 'permission'},
        ]
    }
    
    @staticmethod
    def get_all_vocabulary() -> List[Dict]:
        """获取所有词汇"""
        all_vocab = []
        for textbook, words in EnglishContentLibrary.VOCABULARY_LIBRARY.items():
            for word in words:
                word_copy = word.copy()
                word_copy['textbook'] = textbook
                all_vocab.append(word_copy)
        return all_vocab
    
    @staticmethod
    def search_vocabulary_by_theme(theme_keyword: str) -> List[Dict]:
        """根据主题关键词搜索词汇"""
        theme_keyword = theme_keyword.lower()
        all_vocab = EnglishContentLibrary.get_all_vocabulary()
        
        # 主题映射
        theme_mapping = {
            'school': ['school', 'teacher', 'student', 'classroom', 'book', 'library'],
            'family': ['family', 'father', 'mother', 'brother', 'sister', 'home'],
            'animals': ['animals', 'cat', 'dog', 'fish', 'bird', 'pet'],
            'food': ['food', 'apple', 'egg', 'juice', 'eat', 'drink'],
            'sports': ['sports', 'play', 'football', 'run', 'jump', 'game'],
        }
        
        # 找到匹配的主题
        matched_theme = None
        for theme, keywords in theme_mapping.items():
            if any(keyword in theme_keyword for keyword in keywords):
                matched_theme = theme
                break
        
        if matched_theme:
            return [word for word in all_vocab if word['theme'] == matched_theme][:10]
        
        # 如果没有匹配的主题，返回通用词汇
        return all_vocab[:10]
    
    @staticmethod
    def search_phrases_by_theme(theme_keyword: str) -> List[Dict]:
        """根据主题关键词搜索短语"""
        theme_keyword = theme_keyword.lower()
        
        # 主题映射
        theme_mapping = {
            'school': ['school', 'teacher', 'student', 'study', 'learn'],
            'family': ['family', 'father', 'mother', 'home', 'love'],
            'animals': ['animals', 'pet', 'cat', 'dog', 'animal'],
            'greeting': ['hello', 'morning', 'thank', 'please'],
            'daily': ['day', 'happy', 'help', 'name'],
        }
        
        # 找到匹配的主题
        matched_theme = None
        for theme, keywords in theme_mapping.items():
            if any(keyword in theme_keyword for keyword in keywords):
                matched_theme = theme
                break
        
        if matched_theme:
            return [phrase for phrase in EnglishContentLibrary.PHRASES_LIBRARY 
                   if phrase['theme'] == matched_theme]
        
        # 如果没有匹配，返回所有短语
        return EnglishContentLibrary.PHRASES_LIBRARY[:10]
    
    @staticmethod
    def search_sentences_by_theme(theme_keyword: str) -> List[Dict]:
        """根据主题关键词搜索句型"""
        # 合并所有句型
        all_sentences = []
        for level in EnglishContentLibrary.SENTENCE_PATTERNS.values():
            all_sentences.extend(level)
        
        theme_keyword = theme_keyword.lower()
        
        # 关键词匹配
        matched_sentences = []
        for sentence in all_sentences:
            if (theme_keyword in sentence['pattern'].lower() or 
                theme_keyword in sentence['example'].lower() or
                theme_keyword in sentence.get('theme', '')):
                matched_sentences.append(sentence)
        
        return matched_sentences[:10] if matched_sentences else all_sentences[:10]

# ==================== AI助手（修复评价功能） ====================
class AIAssistant:
    """AI助手类 - 修复版"""
    
    @staticmethod
    def evaluate_writing(student_text: str, topic: str, grade: str) -> Dict:
        """评价学生作文 - 修复版，包含详细建议"""
        prompt = f"""Please evaluate this English writing and provide detailed feedback in both English and Chinese:

Topic: {topic}
Grade Level: {grade}
Student's Writing: {student_text}

Please provide:
1. Overall Score (0-100)
2. Detailed feedback in Chinese including:
   - Structural suggestions
   - Vocabulary improvement suggestions  
   - Sentence pattern suggestions
   - Grammar corrections
3. Rewritten version (if needed)
4. Recommended vocabulary and sentence patterns to learn

Format your response in a clear, structured way with both English and Chinese."""

        messages = [{"role": "user", "content": prompt}]
        response = call_deepseek_api(messages)
        
        if response:
            return {
                'score': AIAssistant._extract_score(response),
                'feedback': response,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'topic': topic,
                'grade': grade
            }
        else:
            # 备用方案
            return AIAssistant._get_default_feedback(student_text, topic, grade)
    
    @staticmethod
    def _extract_score(text: str) -> int:
        """从文本中提取分数"""
        import re
        match = re.search(r'(\d+)/100', text)
        if match:
            return int(match.group(1))
        
        match = re.search(r'score.*?(\d+)', text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        
        return 75
    
    @staticmethod
    def _get_default_feedback(student_text: str, topic: str, grade: str) -> Dict:
        """默认反馈"""
        return {
            'score': 75,
            'feedback': f"""
## 📊 作文评价报告

### 总体评分：75/100

### 📝 详细评价：

**优点 (Strengths):**
- 主题明确，表达了基本思想
- 句子结构基本正确
- 使用了相关主题词汇

**需要改进的地方 (Areas for Improvement):**
1. **文章结构 (Structure):**
   - 建议增加开头和结尾段落
   - 可以加入更多细节描述
   
2. **词汇使用 (Vocabulary):**
   - 尝试使用更多形容词：happy, wonderful, beautiful
   - 学习更多动词：enjoy, appreciate, cherish
   
3. **句型变化 (Sentence Patterns):**
   - 使用复合句：Not only... but also...
   - 尝试使用从句：I love my family because...
   
4. **语法建议 (Grammar):**
   - 注意主谓一致
   - 检查时态使用

### ✨ 修改建议：
**Original:** {student_text}

**Improved version:**
I love my family very much. My father is a teacher and my mother is a nurse. They work hard every day. My little brother is cute and funny. We often play together after school. Family is the most important thing in my life.

### 📚 推荐学习：
- **Vocabulary:** family, parents, siblings, home, love, happy, together
- **Sentence Patterns:** 
  - I have a... who...
  - My favorite... is...
  - We like to... together
""",
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'topic': topic,
            'grade': grade
        }
    
    @staticmethod
    def generate_writing_example(topic: str, grade: str) -> str:
        """生成范文"""
        prompt = f"""请为以下主题写一篇英语范文，并提供中文翻译：

主题：{topic}
年级：{grade}

要求：
1. 字数适当，符合年级水平
2. 包含丰富的词汇和句型
3. 结构清晰（开头、主体、结尾）
4. 情感真挚，有感染力

请提供英语范文和中文翻译。"""

        messages = [{"role": "user", "content": prompt}]
        response = call_deepseek_api(messages)
        return response or f"正在为'{topic}'主题生成范文..."

# ==================== 游戏模块（从其他项目借鉴的稳定游戏） ====================
class GameManager:
    """游戏管理器 - 使用稳定可靠的游戏逻辑"""
    
    @staticmethod
    def word_scramble_game(theme: str = 'animals') -> Dict:
        """单词拼图游戏 - 修复版"""
        # 主题词汇映射
        theme_words = {
            'animals': ['CAT', 'DOG', 'FISH', 'BIRD', 'RABBIT', 'LION', 'TIGER'],
            'school': ['BOOK', 'PEN', 'DESK', 'CHAIR', 'TEACHER', 'STUDENT'],
            'family': ['FATHER', 'MOTHER', 'SISTER', 'BROTHER', 'FAMILY'],
            'food': ['APPLE', 'BANANA', 'RICE', 'MILK', 'WATER', 'BREAD'],
        }
        
        words = theme_words.get(theme, theme_words['animals'])
        target_word = random.choice(words)
        
        # 打乱字母（确保有效）
        scrambled = list(target_word)
        random.shuffle(scrambled)
        scrambled_word = ''.join(scrambled)
        
        # 确保打乱后不同
        attempts = 0
        while scrambled_word == target_word and attempts < 10:
            random.shuffle(scrambled)
            scrambled_word = ''.join(scrambled)
            attempts += 1
        
        return {
            'type': 'word_scramble',
            'target_word': target_word,
            'scrambled': scrambled_word,
            'hint': f"单词主题：{theme}，有{len(target_word)}个字母",
            'theme': theme
        }
    
    @staticmethod
    def multiple_choice_game(theme: str = 'animals') -> Dict:
        """选择题游戏 - 更稳定"""
        questions = [
            {
                'question': "What is the English word for '苹果'?",
                'options': ['Apple', 'Banana', 'Orange', 'Pear'],
                'answer': 'Apple',
                'theme': 'food'
            },
            {
                'question': "Which word means '老师' in English?",
                'options': ['Student', 'Teacher', 'Doctor', 'Nurse'],
                'answer': 'Teacher',
                'theme': 'school'
            },
            {
                'question': "How do you say '猫' in English?",
                'options': ['Dog', 'Cat', 'Bird', 'Fish'],
                'answer': 'Cat',
                'theme': 'animals'
            },
            {
                'question': "What is '家庭' in English?",
                'options': ['School', 'Family', 'House', 'Home'],
                'answer': 'Family',
                'theme': 'family'
            },
            {
                'question': "Which word means '书' in English?",
                'options': ['Pen', 'Book', 'Desk', 'Chair'],
                'answer': 'Book',
                'theme': 'school'
            }
        ]
        
        # 根据主题筛选问题
        filtered_questions = [q for q in questions if q['theme'] == theme]
        if not filtered_questions:
            filtered_questions = questions
        
        question = random.choice(filtered_questions)
        
        return {
            'type': 'multiple_choice',
            'question': question['question'],
            'options': question['options'],
            'answer': question['answer'],
            'theme': theme
        }
    
    @staticmethod
    def sentence_completion_game() -> Dict:
        """句子补全游戏"""
        sentences = [
            {
                'sentence': "I ___ a book every day.",
                'options': ['read', 'eat', 'drink', 'sleep'],
                'answer': 'read'
            },
            {
                'sentence': "My mother ___ dinner for us.",
                'options': ['cooks', 'reads', 'writes', 'plays'],
                'answer': 'cooks'
            },
            {
                'sentence': "We ___ to school together.",
                'options': ['go', 'eat', 'sleep', 'run'],
                'answer': 'go'
            },
            {
                'sentence': "I like to ___ with my friends.",
                'options': ['play', 'cook', 'read', 'write'],
                'answer': 'play'
            },
            {
                'sentence': "The cat ___ on the sofa.",
                'options': ['sleeps', 'eats', 'drinks', 'reads'],
                'answer': 'sleeps'
            }
        ]
        
        item = random.choice(sentences)
        
        return {
            'type': 'sentence_completion',
            'sentence': item['sentence'],
            'options': item['options'],
            'answer': item['answer']
        }

# ==================== 侧边栏 ====================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <div style="font-size: 2.5em; margin-bottom: 10px;">🎨✨</div>
        <h2 style="color: white; margin: 0;">英思织网</h2>
        <p style="color: rgba(255,255,255,0.8); margin: 5px 0;">AI写作魔法学院</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📚 导航菜单")
    
    pages = [
        {"id": "home", "emoji": "🏠", "name": "魔法学院"},
        {"id": "writing", "emoji": "✏️", "name": "写作工坊"},
        {"id": "vocabulary", "emoji": "📖", "name": "词汇助手"},
        {"id": "phrases", "emoji": "💬", "name": "短语宝典"},
        {"id": "sentences", "emoji": "🔤", "name": "句型助手"},
        {"id": "evaluate", "emoji": "⭐", "name": "作品评价"},
        {"id": "games", "emoji": "🎮", "name": "游戏乐园"},
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

# ==================== 主页（恢复特色介绍） ====================
if st.session_state.page == 'home':
    st.markdown('<h1 class="main-header">🎨 英思织网 AI写作魔法学院</h1>', unsafe_allow_html=True)
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
    
    # 特色功能展示 - 恢复原始介绍
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### ✨ 核心特色功能")
    
    features_col1, features_col2, features_col3 = st.columns(3)
    
    with features_col1:
        st.markdown("""
        <div class="feature-card card-orange">
            <div class="card-icon">🤖</div>
            <div class="card-title">AI智能助手</div>
            <div class="card-desc">
                • 智能作文评价<br>
                • 个性化建议<br>
                • 范文生成<br>
                • 实时反馈
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with features_col2:
        st.markdown("""
        <div class="feature-card card-green">
            <div class="card-icon">📚</div>
            <div class="card-title">主题词汇推荐</div>
            <div class="card-desc">
                • 根据写作主题推荐词汇<br>
                • 分级词汇库<br>
                • 生动例句<br>
                • 智能分类
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with features_col3:
        st.markdown("""
        <div class="feature-card card-blue">
            <div class="card-icon">🔤</div>
            <div class="card-title">句型智能匹配</div>
            <div class="card-desc">
                • 主题句型推荐<br>
                • 难度分级<br>
                • 实用例句<br>
                • 造句练习
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==================== 写作工坊 ====================
elif st.session_state.page == 'writing':
    st.markdown('<h1 class="main-header">✏️ 写作魔法工坊</h1>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-text">开启你的创意写作之旅</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        topic = st.text_input("📝 写作主题", 
                            value=st.session_state.get('writing_topic', ''),
                            placeholder="例如：My Pet, My Family, My School...",
                            key="writing_topic_input")
        
        grade = st.selectbox(
            "🎓 适合年级",
            ["Grade 1-2", "Grade 3-4", "Grade 5-6", "Grade 7-8"],
            index=1,
            key="writing_grade_select"
        )
        
        content = st.text_area("📝 开始你的写作...", height=300, placeholder="在这里写下你的作文...")
    
    with col2:
        st.markdown("### 🛠️ 写作工具")
        
        # 搜索相关资源
        if st.button("📚 搜索相关词汇", use_container_width=True, key="search_vocab_writing"):
            if topic:
                st.session_state.page = "vocabulary"
                st.session_state.search_topic = topic
                st.rerun()
            else:
                st.warning("请先输入写作主题")
        
        if st.button("💬 搜索相关短语", use_container_width=True, key="search_phrases_writing"):
            if topic:
                st.session_state.page = "phrases"
                st.session_state.search_topic = topic
                st.rerun()
            else:
                st.warning("请先输入写作主题")
        
        if st.button("🔤 搜索相关句型", use_container_width=True, key="search_sentences_writing"):
            if topic:
                st.session_state.page = "sentences"
                st.session_state.search_topic = topic
                st.rerun()
            else:
                st.warning("请先输入写作主题")
        
        # 范文学习
        if st.button("📖 AI生成范文", use_container_width=True, key="generate_example"):
            if topic:
                with st.spinner("AI正在生成范文..."):
                    example = AIAssistant.generate_writing_example(topic, grade)
                    st.markdown("### 📖 AI范文示例")
                    st.markdown(f'<div class="evaluation-card">{example}</div>', unsafe_allow_html=True)
            else:
                st.warning("请先输入写作主题")
    
    # 提交评价按钮
    if st.button("⭐ 提交AI评价", type="primary", use_container_width=True, key="submit_evaluation"):
        if content and topic:
            st.session_state.writing_topic = topic
            st.session_state.writing_grade = grade
            st.session_state.page = "evaluate"
            st.rerun()
        else:
            st.warning("请先完成写作内容")

# ==================== 词汇助手（修复搜索功能） ====================
elif st.session_state.page == 'vocabulary':
    st.markdown('<h1 class="main-header">📖 词汇魔法助手</h1>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-text">根据你的写作主题推荐相关词汇</div>', unsafe_allow_html=True)
    
    # 搜索框
    search_topic = st.text_input(
        "🔍 输入写作主题搜索相关词汇",
        value=st.session_state.get('search_topic', ''),
        placeholder="例如：My School Life, My Family, My Pet...",
        key="vocab_search_input"
    )
    
    if search_topic:
        st.info(f"📝 正在搜索与 **'{search_topic}'** 相关的词汇...")
        
        # 从内容库搜索
        vocab_list = EnglishContentLibrary.search_vocabulary_by_theme(search_topic)
        
        if vocab_list:
            st.markdown(f"### 📚 相关词汇推荐（{len(vocab_list)}个）")
            
            for word in vocab_list:
                st.markdown(f"""
                <div class="word-card">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <h4 style="margin: 0; font-size: 1.2rem;">
                                <strong>{word['word']}</strong>
                                <span style="color: #666; margin-left: 10px;">{word['cn']}</span>
                            </h4>
                            <div style="margin-top: 10px;">
                                <span class="status-badge badge-info">Grade {word['grade']}</span>
                                <span class="status-badge badge-success">{word.get('textbook', '通用')}</span>
                                <span class="status-badge badge-warning">{word['theme']}</span>
                            </div>
                        </div>
                    </div>
                    <div style="margin-top: 15px; color: #666; font-style: italic;">
                        📝 {word['sentence']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("未找到相关词汇，尝试更具体的主题")
    
    else:
        st.info("请输入写作主题来搜索相关词汇")

# ==================== 短语宝典（修复搜索功能） ====================
elif st.session_state.page == 'phrases':
    st.markdown('<h1 class="main-header">💬 英语短语宝典</h1>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-text">掌握常用英语短语，让表达更地道</div>', unsafe_allow_html=True)
    
    # 搜索框
    search_topic = st.text_input(
        "🔍 输入主题搜索相关短语",
        value=st.session_state.get('search_topic', ''),
        placeholder="例如：school, family, greeting...",
        key="phrase_search_input"
    )
    
    if search_topic:
        st.info(f"📝 正在搜索与 **'{search_topic}'** 相关的短语...")
        
        # 从内容库搜索
        phrases = EnglishContentLibrary.search_phrases_by_theme(search_topic)
        
        if phrases:
            for phrase in phrases:
                st.markdown(f"""
                <div class="phrase-card">
                    <div style="font-size: 1.3rem; font-weight: bold; color: #333; margin-bottom: 10px;">
                        {phrase['english']}
                    </div>
                    <div style="color: #666; margin-bottom: 10px;">
                        {phrase['chinese']}
                    </div>
                    <div style="margin-top: 10px; font-size: 0.9em; color: #666;">
                        📖 例句：{phrase['example']}
                    </div>
                    <div style="margin-top: 5px;">
                        <span class="status-badge badge-success">{phrase['theme']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("显示通用短语...")
            for phrase in EnglishContentLibrary.PHRASES_LIBRARY[:10]:
                st.markdown(f"""
                <div class="phrase-card">
                    <div style="font-size: 1.3rem; font-weight: bold; color: #333; margin-bottom: 10px;">
                        {phrase['english']}
                    </div>
                    <div style="color: #666; margin-bottom: 10px;">
                        {phrase['chinese']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ==================== 句型助手（修复搜索功能） ====================
elif st.session_state.page == 'sentences':
    st.markdown('<h1 class="main-header">🔤 句型助手</h1>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-text">学习实用英语句型，提升写作能力</div>', unsafe_allow_html=True)
    
    # 搜索框
    search_topic = st.text_input(
        "🔍 输入主题搜索相关句型",
        value=st.session_state.get('search_topic', ''),
        placeholder="例如：family, school, like, have...",
        key="sentence_search_input"
    )
    
    if search_topic:
        st.info(f"📝 正在搜索与 **'{search_topic}'** 相关的句型...")
        
        # 从内容库搜索
        sentences = EnglishContentLibrary.search_sentences_by_theme(search_topic)
        
        if sentences:
            for sentence in sentences:
                st.markdown(f"""
                <div class="sentence-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h4 style="margin: 0; color: #333;">
                                <strong>{sentence['pattern']}</strong>
                                <span style="color: #666; margin-left: 10px; font-size: 0.9em;">
                                    ({sentence['cn']})
                                </span>
                            </h4>
                        </div>
                    </div>
                    <div style="margin-top: 15px; padding: 12px; background: #f8f9fa; border-radius: 10px;">
                        <strong>📝 例句:</strong> {sentence['example']}
                    </div>
                    <div style="margin-top: 10px;">
                        <span class="status-badge badge-info">{sentence.get('theme', '通用')}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ==================== 作品评价（修复评价功能） ====================
elif st.session_state.page == 'evaluate':
    st.markdown('<h1 class="main-header">⭐ 智能作品评价</h1>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-text">AI智能评价，个性化反馈</div>', unsafe_allow_html=True)
    
    # 显示当前作文信息
    topic = st.session_state.get('writing_topic', 'My Writing')
    grade = st.session_state.get('writing_grade', 'Grade 3-4')
    
    st.markdown(f"### 📝 评价作文")
    st.markdown(f"**主题：** {topic}")
    st.markdown(f"**年级：** {grade}")
    
    # 输入或显示作文内容
    student_text = st.text_area(
        "作文内容：",
        height=200,
        placeholder="请在这里输入或粘贴你的作文...",
        key="essay_input"
    )
    
    if st.button("✨ 开始AI评价", type="primary", use_container_width=True, key="start_evaluation"):
        if student_text:
            with st.spinner("🤖 AI正在认真评价中，请稍候..."):
                # 调用AI评价
                evaluation = AIAssistant.evaluate_writing(student_text, topic, grade)
                
                # 显示评价结果
                st.markdown("## 📊 AI评价报告")
                
                # 分数显示
                score = evaluation['score']
                score_color = "#4CAF50" if score >= 80 else "#FF9800" if score >= 60 else "#F44336"
                
                st.markdown(f"""
                <div class="evaluation-card">
                    <div style="text-align: center;">
                        <div style="font-size: 1.2rem; color: #666; margin-bottom: 10px;">综合评分</div>
                        <div style="font-size: 3.5rem; font-weight: bold; color: {score_color};">
                            {score}/100
                        </div>
                        <div style="margin-top: 20px;">
                            <div style="display: inline-block; width: 80%; height: 20px; background: #f0f0f0; border-radius: 10px; overflow: hidden;">
                                <div style="width: {score}%; height: 100%; background: {score_color};"></div>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 详细反馈
                st.markdown("### 📝 详细反馈与建议")
                st.markdown(f'<div class="evaluation-card">{evaluation["feedback"]}</div>', unsafe_allow_html=True)
                
                # 保存评价记录
                st.session_state.evaluation_history.append({
                    'topic': evaluation['topic'],
                    'score': score,
                    'timestamp': evaluation['timestamp'],
                    'grade': evaluation['grade']
                })
                
                st.success(f"✅ 评价完成！评价时间：{evaluation['timestamp']}")
        else:
            st.warning("请输入作文内容")

# ==================== 游戏乐园（使用稳定游戏） ====================
elif st.session_state.page == 'games':
    st.markdown('<h1 class="main-header">🎮 写作游戏乐园</h1>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-text">在游戏中学习，在快乐中进步</div>', unsafe_allow_html=True)
    
    # 游戏选择
    st.markdown("## 🎯 选择游戏类型")
    
    games = [
        {"id": "word_scramble", "name": "单词拼图", "emoji": "🧩", "desc": "将打乱的字母拼成正确的单词"},
        {"id": "multiple_choice", "name": "词汇选择", "emoji": "✅", "desc": "选择正确的单词意思"},
        {"id": "sentence_completion", "name": "句子补全", "emoji": "🔤", "desc": "选择正确单词完成句子"}
    ]
    
    cols = st.columns(3)
    for idx, game in enumerate(games):
        with cols[idx]:
            if st.button(
                f"{game['emoji']} {game['name']}",
                use_container_width=True,
                key=f"select_game_{game['id']}",
                type="primary" if st.session_state.selected_game == game['id'] else "secondary"
            ):
                st.session_state.selected_game = game['id']
                st.session_state.game_content = None
                st.rerun()
    
    # 如果选择了游戏
    if st.session_state.selected_game:
        game_id = st.session_state.selected_game
        
        # 主题选择
        if game_id in ['word_scramble', 'multiple_choice']:
            st.markdown("### 🎨 选择主题")
            themes = ['animals', 'school', 'family', 'food']
            theme_names = {'animals': '🐶 动物', 'school': '🏫 学校', 'family': '👨‍👩‍👧‍👦 家庭', 'food': '🍎 食物'}
            
            theme_cols = st.columns(4)
            for idx, theme in enumerate(themes):
                with theme_cols[idx]:
                    if st.button(
                        theme_names[theme],
                        use_container_width=True,
                        key=f"theme_{theme}",
                        type="primary" if st.session_state.game_theme == theme else "secondary"
                    ):
                        st.session_state.game_theme = theme
                        st.session_state.game_content = None
                        st.rerun()
        
        # 开始游戏按钮
        if st.button("🎮 开始新游戏", type="primary", key="start_new_game", use_container_width=True):
            theme = st.session_state.get('game_theme', 'animals')
            
            if game_id == 'word_scramble':
                game_content = GameManager.word_scramble_game(theme)
            elif game_id == 'multiple_choice':
                game_content = GameManager.multiple_choice_game(theme)
            elif game_id == 'sentence_completion':
                game_content = GameManager.sentence_completion_game()
            else:
                game_content = {'type': 'default', 'message': '游戏准备中...'}
            
            st.session_state.game_content = game_content
            st.rerun()
        
        # 显示游戏内容
        if st.session_state.game_content:
            content = st.session_state.game_content
            
            if content['type'] == 'word_scramble':
                st.markdown("### 🧩 单词拼图游戏")
                
                st.markdown(f"""
                <div style="text-align: center; padding: 30px; background: white; border-radius: 20px; border: 3px solid #FF9A3D; margin: 20px 0;">
                    <h3>猜猜这个单词是什么？</h3>
                    <div style="background: #FFF3E0; padding: 15px; border-radius: 10px; margin: 20px 0;">
                        <p style="color: #FF9800; font-weight: bold;">💡 {content.get('hint', '提示')}</p>
                    </div>
                    
                    <div style="margin: 30px 0;">
                        <div style="font-size: 2.5rem; letter-spacing: 15px; color: #4D96FF; font-weight: bold; 
                                    padding: 20px; background: #F0F8FF; border-radius: 15px; border: 2px dashed #4D96FF;">
                            {content.get('scrambled', '???')}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 答案输入
                col1, col2 = st.columns([3, 1])
                with col1:
                    user_answer = st.text_input("输入拼出的单词：", key="game_answer", placeholder="输入大写英文单词...").upper()
                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("✅ 提交答案", key="submit_game_answer", use_container_width=True):
                        target = content.get('target_word', '').upper()
                        if user_answer.strip() == target:
                            st.success(f"🎉 太棒了！正确答案是：{target}")
                            st.session_state.game_score += 10
                            st.balloons()
                        else:
                            st.error(f"再试一次！正确答案是：{target}")
            
            elif content['type'] == 'multiple_choice':
                st.markdown("### ✅ 词汇选择题")
                
                st.markdown(f"""
                <div style="text-align: center; padding: 30px; background: white; border-radius: 20px; border: 3px solid #6BCF7F; margin: 20px 0;">
                    <h3>词汇挑战</h3>
                    
                    <div style="margin: 30px 0; padding: 20px; background: #f0fff4; border-radius: 15px;">
                        <div style="font-size: 1.8rem; color: #2E7D32; font-weight: bold;">
                            {content.get('question', '问题加载中...')}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 选择题
                options = content.get('options', [])
                correct = content.get('answer', '')
                
                if options:
                    selected = st.radio("选择正确答案：", options, key="multiple_choice_option")
                    
                    if st.button("✅ 检查答案", key="check_multiple_choice", use_container_width=True):
                        if selected == correct:
                            st.success("🎉 正确！你答对了！")
                            st.session_state.game_score += 10
                        else:
                            st.error(f"再想想！正确答案是：{correct}")
            
            elif content['type'] == 'sentence_completion':
                st.markdown("### 🔤 句子补全游戏")
                
                st.markdown(f"""
                <div style="text-align: center; padding: 30px; background: white; border-radius: 20px; border: 3px solid #9D4DFF; margin: 20px 0;">
                    <h3>完成这个句子</h3>
                    
                    <div style="margin: 30px 0; padding: 20px; background: #f5f0ff; border-radius: 15px;">
                        <div style="font-size: 1.8rem; color: #6B46C1; font-weight: bold;">
                            {content.get('sentence', '句子加载中...')}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 选择题
                options = content.get('options', [])
                correct = content.get('answer', '')
                
                if options:
                    selected = st.radio("选择正确单词完成句子：", options, key="sentence_completion_option")
                    
                    if st.button("✅ 检查答案", key="check_sentence_completion", use_container_width=True):
                        if selected == correct:
                            st.success("🎉 正确！句子完整了！")
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
    
    else:
        st.info("请选择一个游戏开始")

# ==================== 页脚 ====================
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown("""
<div style="color: #666; text-align: center;">
    <p style="margin: 0;">
        <strong>🎨 英思织网 AI写作魔法学院</strong> | 
        🤖 Powered by DeepSeek AI | 
        © 2024 版权所有
    </p>
</div>
""", unsafe_allow_html=True)

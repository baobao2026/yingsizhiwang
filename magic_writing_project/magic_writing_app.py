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
    
    .card-orange { border-color: #FF9A3D; }
    .card-green { border-color: #6BCF7F; }
    .card-blue { border-color: #4D96FF; }
    .card-pink { border-color: #FF6B9D; }
    
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
    }
    
    .fun-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(255, 154, 61, 0.4);
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
    
    .example-card {
        background: linear-gradient(135deg, #e3f2fd, #bbdefb);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        border-left: 5px solid #2196F3;
    }
    
    .example-title {
        color: #1976D2;
        font-weight: bold;
        font-size: 1.2rem;
        margin-bottom: 10px;
    }
    
    .example-content {
        background: white;
        padding: 15px;
        border-radius: 10px;
        font-style: italic;
        margin: 10px 0;
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
if 'search_topic' not in st.session_state:
    st.session_state.search_topic = ''

# ==================== 内容库 ====================
class ContentLibrary:
    """内容库 - 包含词汇、短语、句型"""
    
    # 词汇库
    VOCABULARY = [
        # 动物主题
        {'word': 'rabbit', 'cn': '兔子', 'grade': '1', 'theme': 'animals'},
        {'word': 'cat', 'cn': '猫', 'grade': '1', 'theme': 'animals'},
        {'word': 'dog', 'cn': '狗', 'grade': '1', 'theme': 'animals'},
        {'word': 'bird', 'cn': '鸟', 'grade': '1', 'theme': 'animals'},
        {'word': 'fish', 'cn': '鱼', 'grade': '1', 'theme': 'animals'},
        
        # 学校主题
        {'word': 'teacher', 'cn': '老师', 'grade': '1', 'theme': 'school'},
        {'word': 'student', 'cn': '学生', 'grade': '1', 'theme': 'school'},
        {'word': 'book', 'cn': '书', 'grade': '1', 'theme': 'school'},
        {'word': 'pen', 'cn': '钢笔', 'grade': '1', 'theme': 'school'},
        {'word': 'classroom', 'cn': '教室', 'grade': '2', 'theme': 'school'},
        
        # 家庭主题
        {'word': 'father', 'cn': '爸爸', 'grade': '1', 'theme': 'family'},
        {'word': 'mother', 'cn': '妈妈', 'grade': '1', 'theme': 'family'},
        {'word': 'family', 'cn': '家庭', 'grade': '1', 'theme': 'family'},
        {'word': 'home', 'cn': '家', 'grade': '1', 'theme': 'family'},
        {'word': 'love', 'cn': '爱', 'grade': '2', 'theme': 'family'},
        
        # 食物主题
        {'word': 'apple', 'cn': '苹果', 'grade': '1', 'theme': 'food'},
        {'word': 'banana', 'cn': '香蕉', 'grade': '1', 'theme': 'food'},
        {'word': 'rice', 'cn': '米饭', 'grade': '1', 'theme': 'food'},
        {'word': 'milk', 'cn': '牛奶', 'grade': '1', 'theme': 'food'},
        {'word': 'water', 'cn': '水', 'grade': '1', 'theme': 'food'},
    ]
    
    # 短语库
    PHRASES = [
        # 学校相关
        {'english': 'Good morning, teacher!', 'chinese': '老师，早上好！', 'theme': 'school'},
        {'english': 'May I go to the toilet?', 'chinese': '我可以去洗手间吗？', 'theme': 'school'},
        {'english': 'I have a question.', 'chinese': '我有一个问题。', 'theme': 'school'},
        {'english': 'Can you help me?', 'chinese': '你能帮助我吗？', 'theme': 'school'},
        {'english': 'I finished my homework.', 'chinese': '我完成了作业。', 'theme': 'school'},
        
        # 家庭相关
        {'english': 'I love my family.', 'chinese': '我爱我的家人。', 'theme': 'family'},
        {'english': 'My mother cooks dinner.', 'chinese': '我妈妈做晚饭。', 'theme': 'family'},
        {'english': 'We watch TV together.', 'chinese': '我们一起看电视。', 'theme': 'family'},
        {'english': 'Family is important.', 'chinese': '家庭很重要。', 'theme': 'family'},
        {'english': 'I help my parents.', 'chinese': '我帮助我的父母。', 'theme': 'family'},
        
        # 动物相关
        {'english': 'I have a pet dog.', 'chinese': '我有一只宠物狗。', 'theme': 'animals'},
        {'english': 'Cats are cute.', 'chinese': '猫很可爱。', 'theme': 'animals'},
        {'english': 'Birds can fly.', 'chinese': '鸟会飞。', 'theme': 'animals'},
        {'english': 'I like animals.', 'chinese': '我喜欢动物。', 'theme': 'animals'},
        {'english': 'The rabbit hops fast.', 'chinese': '兔子跳得很快。', 'theme': 'animals'},
        
        # 日常表达
        {'english': 'How are you?', 'chinese': '你好吗？', 'theme': 'daily'},
        {'english': 'Thank you very much.', 'chinese': '非常感谢。', 'theme': 'daily'},
        {'english': 'Nice to meet you.', 'chinese': '很高兴见到你。', 'theme': 'daily'},
        {'english': 'See you tomorrow.', 'chinese': '明天见。', 'theme': 'daily'},
        {'english': 'Have a nice day.', 'chinese': '祝你今天愉快。', 'theme': 'daily'},
    ]
    
    # 句型库
    SENTENCES = [
        {'pattern': 'I like...', 'cn': '我喜欢...', 'example': 'I like apples.', 'theme': 'general'},
        {'pattern': 'I have...', 'cn': '我有...', 'example': 'I have a book.', 'theme': 'general'},
        {'pattern': 'I can...', 'cn': '我能...', 'example': 'I can swim.', 'theme': 'general'},
        {'pattern': 'My... is...', 'cn': '我的...是...', 'example': 'My dog is small.', 'theme': 'general'},
        {'pattern': 'This is my...', 'cn': '这是我的...', 'example': 'This is my father.', 'theme': 'family'},
        {'pattern': 'I go to...', 'cn': '我去...', 'example': 'I go to school.', 'theme': 'school'},
        {'pattern': 'I eat...', 'cn': '我吃...', 'example': 'I eat breakfast.', 'theme': 'food'},
        {'pattern': 'I play with...', 'cn': '我和...一起玩', 'example': 'I play with my friends.', 'theme': 'general'},
        {'pattern': 'There is...', 'cn': '有...', 'example': 'There is a cat.', 'theme': 'general'},
        {'pattern': 'I want to...', 'cn': '我想要...', 'example': 'I want to learn English.', 'theme': 'general'},
    ]
    
    # 主题映射
    THEME_MAP = {
        'school': ['school', 'teacher', 'student', 'class', 'study', 'learn'],
        'family': ['family', 'father', 'mother', 'parent', 'home', 'house'],
        'animals': ['animal', 'pet', 'dog', 'cat', 'rabbit', 'bird', 'fish'],
        'food': ['food', 'eat', 'drink', 'apple', 'banana', 'rice', 'milk'],
        'sports': ['sport', 'play', 'game', 'football', 'basketball', 'run'],
        'daily': ['hello', 'thank', 'please', 'sorry', 'goodbye'],
    }
    
    @staticmethod
    def get_related_theme(topic: str) -> str:
        """根据话题获取相关主题"""
        topic_lower = topic.lower()
        for theme, keywords in ContentLibrary.THEME_MAP.items():
            for keyword in keywords:
                if keyword in topic_lower:
                    return theme
        return 'general'
    
    @staticmethod
    def search_vocabulary(topic: str) -> List[Dict]:
        """根据话题搜索词汇"""
        theme = ContentLibrary.get_related_theme(topic)
        return [word for word in ContentLibrary.VOCABULARY if word['theme'] == theme][:10]
    
    @staticmethod
    def search_phrases(topic: str) -> List[Dict]:
        """根据话题搜索短语"""
        theme = ContentLibrary.get_related_theme(topic)
        if theme == 'general':
            return ContentLibrary.PHRASES[:10]
        return [phrase for phrase in ContentLibrary.PHRASES if phrase.get('theme') == theme][:10]
    
    @staticmethod
    def search_sentences(topic: str) -> List[Dict]:
        """根据话题搜索句型"""
        theme = ContentLibrary.get_related_theme(topic)
        if theme == 'general':
            return ContentLibrary.SENTENCES[:10]
        return [sentence for sentence in ContentLibrary.SENTENCES if sentence.get('theme') == theme][:10]

# ==================== AI助手 ====================
class AIAssistant:
    """AI助手类"""
    
    @staticmethod
    def generate_writing_example(topic: str, grade: str) -> str:
        """生成范文"""
        prompt = f"""请写一篇关于{topic}的英语作文范文：
        年级：{grade}
        要求：100-200字，适合学生阅读，有中文翻译
        
        请用以下格式：
        英语范文：[这里写英语作文]
        中文翻译：[这里写中文翻译]"""
        
        messages = [{"role": "user", "content": prompt}]
        response = call_deepseek_api(messages)
        return response or f"正在为'{topic}'生成范文..."
    
    @staticmethod
    def generate_game_content(game_type: str, theme: str = None) -> Dict:
        """生成游戏内容 - 完全重写版"""
        
        if game_type == 'word_puzzle':
            # 从词汇库中选择单词
            if theme:
                vocab = [w for w in ContentLibrary.VOCABULARY if w['theme'] == theme]
            else:
                vocab = ContentLibrary.VOCABULARY
            
            if not vocab:
                vocab = [{'word': 'rabbit', 'cn': '兔子'}, {'word': 'apple', 'cn': '苹果'}]
            
            target = random.choice(vocab)
            word = target['word'].upper()
            
            # 打乱字母（确保是有效的打乱）
            letters = list(word)
            random.shuffle(letters)
            scrambled = ''.join(letters)
            
            # 确保打乱后不同
            attempts = 0
            while scrambled == word and attempts < 10:
                random.shuffle(letters)
                scrambled = ''.join(letters)
                attempts += 1
            
            return {
                'type': 'word_puzzle',
                'target_word': target['word'].lower(),
                'scrambled': scrambled,
                'hint': f"中文意思：{target['cn']}",
                'theme': theme
            }
        
        elif game_type == 'sentence_builder':
            # 句子组装游戏
            patterns = [
                "I have a ___.", 
                "I like to ___.", 
                "This is my ___.", 
                "I can ___.",
                "My ___ is ___."
            ]
            
            pattern = random.choice(patterns)
            
            # 根据模式选择单词
            if "have a" in pattern:
                words = ['book', 'pen', 'dog', 'cat', 'ball']
            elif "like to" in pattern:
                words = ['read', 'play', 'sing', 'dance', 'run']
            elif "This is my" in pattern:
                words = ['friend', 'teacher', 'mother', 'father', 'book']
            elif "I can" in pattern:
                words = ['swim', 'jump', 'run', 'sing', 'dance']
            else:
                words = ['book', 'red', 'dog', 'small', 'pen']
            
            missing = random.choice(words)
            options = words.copy()
            random.shuffle(options)
            
            return {
                'type': 'sentence_builder',
                'pattern': pattern,
                'missing': missing,
                'options': options,
                'correct_answer': missing
            }
        
        elif game_type == 'vocab_quiz':
            # 词汇挑战游戏 - 简化版
            vocab = ContentLibrary.VOCABULARY
            
            if theme:
                vocab = [w for w in vocab if w['theme'] == theme]
            
            if len(vocab) < 4:
                vocab = ContentLibrary.VOCABULARY[:10]
            
            target = random.choice(vocab)
            
            # 生成选项（确保有足够的不同单词）
            all_words = [w for w in vocab if w['word'] != target['word']]
            if len(all_words) >= 3:
                wrong_words = random.sample(all_words, 3)
            else:
                # 如果不够，补充一些常见单词
                common_words = [{'word': 'apple', 'cn': '苹果'}, {'word': 'book', 'cn': '书'}, 
                              {'word': 'cat', 'cn': '猫'}, {'word': 'dog', 'cn': '狗'}]
                wrong_words = random.sample(common_words, 3)
            
            options = [target['cn']] + [w['cn'] for w in wrong_words]
            random.shuffle(options)
            
            return {
                'type': 'vocab_quiz',
                'question': f"What is the Chinese meaning of '{target['word']}'?",
                'correct_answer': target['cn'],
                'options': options,
                'word': target['word']
            }
        
        return {'type': game_type, 'content': '游戏准备中...'}

# ==================== 侧边栏 ====================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <h2 style="color: white; margin: 0;">🎨 英思织网</h2>
        <p style="color: rgba(255,255,255,0.8); margin: 5px 0;">AI写作魔法学院</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📚 导航")
    
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

# ==================== 主页 ====================
if st.session_state.page == 'home':
    st.markdown('<h1 class="main-header">🎨 英思织网 AI写作魔法学院</h1>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-text">让每个孩子爱上英语写作！</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("✏️ 开始写作", use_container_width=True, type="primary"):
            st.session_state.page = "writing"
            st.rerun()
    with col2:
        if st.button("📖 学习词汇", use_container_width=True):
            st.session_state.page = "vocabulary"
            st.rerun()
    with col3:
        if st.button("💬 常用短语", use_container_width=True):
            st.session_state.page = "phrases"
            st.rerun()
    with col4:
        if st.button("🎮 游戏乐园", use_container_width=True):
            st.session_state.page = "games"
            st.rerun()

# ==================== 写作工坊 ====================
elif st.session_state.page == 'writing':
    st.markdown('<h1 class="main-header">✏️ 写作魔法工坊</h1>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-text">开启你的创意写作之旅</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        topic = st.text_input("📝 写作主题", placeholder="例如：My Pet, My Family...", 
                            value=st.session_state.get('writing_topic', ''))
        grade = st.selectbox("🎓 适合年级", ["Grade 1-2", "Grade 3-4", "Grade 5-6", "Grade 7-8"], 
                           index=1)
        content = st.text_area("📝 开始写作...", height=250, placeholder="在这里写下你的作文...")
        
        # 范文学习按钮
        if st.button("📖 学习范文", type="primary", key="learn_example"):
            if topic:
                with st.spinner("AI正在生成范文..."):
                    example = AIAssistant.generate_writing_example(topic, grade)
                    st.markdown("### 📖 AI范文示例")
                    st.markdown(f'<div class="example-card">{example}</div>', unsafe_allow_html=True)
            else:
                st.warning("请先输入写作主题")
    
    with col2:
        st.markdown("### 🛠️ 写作工具")
        
        # 搜索相关资源
        if st.button("🔍 搜索相关词汇", use_container_width=True):
            if topic:
                st.session_state.page = "vocabulary"
                st.session_state.search_topic = topic
                st.rerun()
        
        if st.button("💬 搜索相关短语", use_container_width=True):
            if topic:
                st.session_state.page = "phrases"
                st.session_state.search_topic = topic
                st.rerun()
        
        if st.button("🔤 搜索相关句型", use_container_width=True):
            if topic:
                st.session_state.page = "sentences"
                st.session_state.search_topic = topic
                st.rerun()
        
        if st.button("💾 保存草稿", use_container_width=True):
            if content:
                st.success("草稿已保存！")
    
    # 提交评价按钮
    if st.button("⭐ 提交评价", type="primary", use_container_width=True):
        if content and topic:
            st.session_state.page = "evaluate"
            st.rerun()

# ==================== 词汇助手（带主题搜索） ====================
elif st.session_state.page == 'vocabulary':
    st.markdown('<h1 class="main-header">📖 词汇魔法助手</h1>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-text">根据你的写作主题推荐相关词汇</div>', unsafe_allow_html=True)
    
    # 搜索框
    search_topic = st.text_input("🔍 输入写作主题搜索相关词汇", 
                                value=st.session_state.get('search_topic', ''),
                                placeholder="例如：My School, My Family, My Pet...")
    
    if search_topic:
        st.info(f"正在搜索与 '{search_topic}' 相关的词汇...")
        
        # 从本地库搜索
        vocab_list = ContentLibrary.search_vocabulary(search_topic)
        
        if vocab_list:
            st.markdown(f"### 📚 相关词汇（{len(vocab_list)}个）")
            
            # 分组显示
            cols = st.columns(2)
            for idx, word in enumerate(vocab_list):
                with cols[idx % 2]:
                    st.markdown(f"""
                    <div style="padding: 15px; background: white; border-radius: 10px; margin: 10px 0; border-left: 5px solid #4D96FF;">
                        <div style="display: flex; justify-content: space-between;">
                            <div>
                                <strong style="font-size: 1.2rem;">{word['word']}</strong>
                                <div style="color: #666;">{word['cn']}</div>
                            </div>
                            <span class="status-badge badge-info">Grade {word['grade']}</span>
                        </div>
                        <div style="margin-top: 10px;">
                            <span class="status-badge badge-success">{word['theme']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("未找到相关词汇，尝试更具体的主题")
    
    else:
        # 主题分类浏览
        st.markdown("### 🎨 按主题浏览")
        themes = ['animals', 'school', 'family', 'food']
        theme_names = {'animals': '🐶 动物', 'school': '🏫 学校', 'family': '👨‍👩‍👧‍👦 家庭', 'food': '🍎 食物'}
        
        cols = st.columns(4)
        for idx, theme in enumerate(themes):
            with cols[idx]:
                if st.button(theme_names[theme], use_container_width=True):
                    st.session_state.search_topic = theme
                    st.rerun()

# ==================== 短语宝典（带主题搜索） ====================
elif st.session_state.page == 'phrases':
    st.markdown('<h1 class="main-header">💬 英语短语宝典</h1>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-text">掌握常用英语短语，让表达更地道</div>', unsafe_allow_html=True)
    
    # 搜索框
    search_topic = st.text_input("🔍 输入主题搜索相关短语", 
                                value=st.session_state.get('search_topic', ''),
                                placeholder="例如：school, family, animals...")
    
    if search_topic:
        st.info(f"正在搜索与 '{search_topic}' 相关的短语...")
        phrases = ContentLibrary.search_phrases(search_topic)
        
        if phrases:
            for phrase in phrases:
                st.markdown(f"""
                <div style="padding: 15px; background: white; border-radius: 10px; margin: 10px 0; border-left: 5px solid #6BCF7F;">
                    <div style="font-size: 1.3rem; font-weight: bold; color: #333;">
                        {phrase['english']}
                    </div>
                    <div style="color: #666; margin: 10px 0;">
                        {phrase['chinese']}
                    </div>
                    <div style="color: #888; font-style: italic;">
                        📖 {phrase.get('theme', '通用')} · 实用短语
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("显示通用短语...")
            for phrase in ContentLibrary.PHRASES[:10]:
                st.markdown(f"""
                <div style="padding: 15px; background: white; border-radius: 10px; margin: 10px 0; border-left: 5px solid #6BCF7F;">
                    <div style="font-size: 1.3rem; font-weight: bold; color: #333;">
                        {phrase['english']}
                    </div>
                    <div style="color: #666; margin: 10px 0;">
                        {phrase['chinese']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    else:
        # 分类显示
        st.markdown("### 📂 短语分类")
        categories = ['school', 'family', 'animals', 'daily']
        category_names = {'school': '🏫 学校', 'family': '👨‍👩‍👧‍👦 家庭', 'animals': '🐶 动物', 'daily': '🌞 日常'}
        
        cols = st.columns(4)
        for idx, category in enumerate(categories):
            with cols[idx]:
                if st.button(category_names[category], use_container_width=True):
                    st.session_state.search_topic = category
                    st.rerun()

# ==================== 句型助手（带主题搜索） ====================
elif st.session_state.page == 'sentences':
    st.markdown('<h1 class="main-header">🔤 句型助手</h1>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-text">学习实用英语句型，提升写作能力</div>', unsafe_allow_html=True)
    
    # 搜索框
    search_topic = st.text_input("🔍 输入主题搜索相关句型", 
                                value=st.session_state.get('search_topic', ''),
                                placeholder="例如：school, family, animals...")
    
    if search_topic:
        st.info(f"正在搜索与 '{search_topic}' 相关的句型...")
        sentences = ContentLibrary.search_sentences(search_topic)
        
        if sentences:
            for sentence in sentences:
                st.markdown(f"""
                <div style="padding: 20px; background: white; border-radius: 10px; margin: 10px 0; border-left: 5px solid #FF9A3D;">
                    <h4>{sentence['pattern']} <span style="color: #666;">({sentence['cn']})</span></h4>
                    <div style="margin: 10px 0; padding: 10px; background: #FFF3E0; border-radius: 5px;">
                        <strong>例句：</strong> {sentence['example']}
                    </div>
                    <div style="color: #888;">
                        适用主题：{sentence.get('theme', '通用')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("显示通用句型...")
            for sentence in ContentLibrary.SENTENCES[:10]:
                st.markdown(f"""
                <div style="padding: 20px; background: white; border-radius: 10px; margin: 10px 0; border-left: 5px solid #FF9A3D;">
                    <h4>{sentence['pattern']} <span style="color: #666;">({sentence['cn']})</span></h4>
                    <div style="margin: 10px 0; padding: 10px; background: #FFF3E0; border-radius: 5px;">
                        <strong>例句：</strong> {sentence['example']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ==================== 作品评价 ====================
elif st.session_state.page == 'evaluate':
    st.markdown('<h1 class="main-header">⭐ 智能作品评价</h1>', unsafe_allow_html=True)
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

# ==================== 游戏乐园（完全重写） ====================
elif st.session_state.page == 'games':
    st.markdown('<h1 class="main-header">🎮 写作游戏乐园</h1>', unsafe_allow_html=True)
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
                key=f"game_{game['id']}",
                type="primary" if st.session_state.selected_game == game['id'] else "secondary"
            ):
                st.session_state.selected_game = game['id']
                st.session_state.game_content = None
                st.rerun()
    
    # 如果选择了游戏
    if st.session_state.selected_game:
        game_id = st.session_state.selected_game
        
        # 主题选择（针对单词游戏）
        if game_id in ['word_puzzle', 'vocab_quiz']:
            st.markdown("### 🎨 选择主题")
            themes = ['animals', 'school', 'family', 'food']
            theme_names = {'animals': '动物', 'school': '学校', 'family': '家庭', 'food': '食物'}
            
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
                    user_answer = st.text_input("输入拼出的单词：", key="puzzle_answer", placeholder="输入英文单词...")
                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("✅ 提交答案", key="submit_puzzle", use_container_width=True):
                        target = content.get('target_word', '').lower()
                        if user_answer.strip().lower() == target:
                            st.success(f"🎉 太棒了！正确答案是：{target}")
                            st.session_state.game_score += 10
                            st.balloons()
                        else:
                            st.error(f"再试一次！正确答案是：{target}")
            
            elif game_id == 'sentence_builder':
                st.markdown("### 🔤 句子组装游戏")
                
                st.markdown(f"""
                <div style="text-align: center; padding: 30px; background: white; border-radius: 20px; border: 3px solid #6BCF7F; margin: 20px 0;">
                    <h3>用这个句型造一个句子</h3>
                    
                    <div style="margin: 30px 0; padding: 20px; background: #f0fff4; border-radius: 15px;">
                        <div style="font-size: 1.8rem; color: #2E7D32; font-weight: bold;">
                            {content.get('pattern', 'I have...')}
                        </div>
                    </div>
                    
                    <div style="color: #666; margin: 20px 0;">
                        <em>选择正确的单词完成句子</em>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 选择填空
                options = content.get('options', [])
                correct = content.get('correct_answer', '')
                
                if options:
                    selected = st.radio("选择正确的单词完成句子：", options, key="sentence_option")
                    
                    if st.button("✅ 检查答案", key="check_sentence", use_container_width=True):
                        if selected == correct:
                            st.success("🎉 正确！句子完整了！")
                            st.session_state.game_score += 10
                        else:
                            st.error(f"再想想！正确答案是：{correct}")
                else:
                    st.warning("游戏选项加载中...")
            
            elif game_id == 'vocab_quiz':
                st.markdown("### 🏆 词汇挑战游戏")
                
                st.markdown(f"""
                <div style="text-align: center; padding: 30px; background: white; border-radius: 20px; border: 3px solid #9D4DFF; margin: 20px 0;">
                    <h3>词汇挑战</h3>
                    
                    <div style="margin: 30px 0; padding: 20px; background: #f5f0ff; border-radius: 15px;">
                        <div style="font-size: 1.8rem; color: #6B46C1; font-weight: bold;">
                            {content.get('question', 'What is the meaning?')}
                        </div>
                    </div>
                    
                    <div style="color: #666; margin: 20px 0;">
                        <em>选择正确的中文意思</em>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 选择题
                options = content.get('options', [])
                correct = content.get('correct_answer', '')
                
                if options and len(options) >= 4:
                    selected = st.radio("选择正确的中文意思：", options, key="vocab_option")
                    
                    if st.button("✅ 检查答案", key="check_vocab", use_container_width=True):
                        if selected == correct:
                            st.success("🎉 正确！你答对了！")
                            st.session_state.game_score += 10
                        else:
                            st.error(f"再想想！正确答案是：{correct}")
                else:
                    st.warning("游戏选项加载中...")
        
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

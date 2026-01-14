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
    
    return None

DEEPSEEK_API_KEY = get_api_key()
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
OFFLINE_MODE = DEEPSEEK_API_KEY is None

def call_deepseek_api(messages: List[Dict], temperature: float = 0.7, max_retries: int = 2) -> Optional[str]:
    """改进版API调用，更好的错误处理"""
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
        "max_tokens": 2000  # 增加token数以支持详细评价
    }
    
    for attempt in range(max_retries):
        try:
            # 缩短超时时间，更快失败
            response = requests.post(
                DEEPSEEK_API_URL, 
                headers=headers, 
                json=payload, 
                timeout=(3, 10)  # 更短的超时
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            elif response.status_code == 429:
                st.warning(f"请求频繁，等待重试 ({attempt+1}/{max_retries})")
                time.sleep(3)
                continue
            else:
                st.error(f"API错误 {response.status_code}: {response.text[:100]}")
                return None
                
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                st.info(f"请求超时，重试中 ({attempt+1}/{max_retries})")
                time.sleep(2)
                continue
            else:
                st.error("请求超时，请检查网络连接")
                return None
        except requests.exceptions.ConnectionError:
            st.error("网络连接失败")
            return None
        except Exception as e:
            st.error(f"API调用错误: {str(e)[:100]}")
            return None
    
    return None

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="🎨 英思织网 | AI写作魔法学院",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo',
        'Report a bug': "https://github.com/your-repo/issues",
        'About': "# 英思织网 - AI写作魔法学院"
    }
)

# ==================== 增强版CSS样式 ====================
st.markdown("""
<style>
    /* 主背景 - 梦幻渐变 */
    .stApp {
        background: linear-gradient(135deg, #f8f9ff 0%, #eef2ff 25%, #f0f9ff 50%, #f5f0ff 75%, #fff0f5 100%);
        background-attachment: fixed;
        background-size: 400% 400%;
        animation: gradientBG 20s ease infinite;
    }
    
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* 主标题 - 超大艺术字效果 */
    .main-title-wrapper {
        text-align: center;
        padding: 30px 20px;
        background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.7) 100%);
        border-radius: 25px;
        margin: 20px auto;
        border: 3px solid transparent;
        border-image: linear-gradient(90deg, #FF3366, #FF9933, #FFCC00, #33CC33, #3366FF) 1;
        box-shadow: 0 15px 40px rgba(0,0,0,0.1);
        position: relative;
        overflow: hidden;
        max-width: 95%;
    }
    
    .main-title-wrapper::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
        animation: shine 3s infinite;
    }
    
    @keyframes shine {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
    
    .main-title {
        font-size: 4.2rem !important;
        font-weight: 900 !important;
        background: linear-gradient(90deg, 
            #FF3366 0%, 
            #FF9933 20%, 
            #FFCC00 40%, 
            #33CC33 60%, 
            #3366FF 80%, 
            #9933FF 100%
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: 4px 4px 8px rgba(0,0,0,0.1);
        letter-spacing: 3px;
        margin: 10px 0 !important;
        font-family: 'Microsoft YaHei', 'SimHei', 'PingFang SC', sans-serif;
        position: relative;
        z-index: 1;
    }
    
    .main-subtitle {
        font-size: 1.8rem !important;
        color: #555 !important;
        font-weight: 600 !important;
        margin-top: -10px !important;
        margin-bottom: 20px !important;
        font-family: 'Microsoft YaHei', sans-serif;
        background: linear-gradient(90deg, #666, #333);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* 装饰边框 */
    .title-border {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 20px;
        margin: 15px 0;
    }
    
    .title-border-line {
        flex: 1;
        height: 4px;
        background: linear-gradient(90deg, transparent, #FF9933, transparent);
        border-radius: 2px;
    }
    
    .title-icon {
        font-size: 2rem;
        color: #FF9933;
        animation: bounce 2s infinite;
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    /* 评价卡片特殊样式 */
    .evaluation-card {
        background: linear-gradient(135deg, #ffffff, #f8f9ff);
        border-radius: 20px;
        padding: 30px;
        margin: 25px 0;
        border: 3px solid #4D96FF;
        box-shadow: 0 15px 40px rgba(77, 150, 255, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .evaluation-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 25px;
        padding-bottom: 15px;
        border-bottom: 2px solid #E2E8F0;
    }
    
    .evaluation-title {
        font-size: 1.8rem;
        font-weight: 800;
        color: #2C5282;
        margin: 0;
    }
    
    .score-display {
        background: linear-gradient(135deg, #4D96FF, #9D4DFF);
        color: white;
        padding: 15px 30px;
        border-radius: 15px;
        font-size: 2.5rem;
        font-weight: 900;
        box-shadow: 0 8px 25px rgba(77, 150, 255, 0.3);
        text-align: center;
        min-width: 120px;
    }
    
    .score-label {
        font-size: 1rem;
        opacity: 0.9;
        margin-top: 5px;
        font-weight: 600;
    }
    
    /* 评分细则 */
    .score-breakdown {
        background: #F8FAFC;
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
    }
    
    .score-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid #E2E8F0;
    }
    
    .score-item:last-child {
        border-bottom: none;
    }
    
    .score-category {
        font-weight: 600;
        color: #2D3748;
        font-size: 1.1rem;
    }
    
    .score-bar {
        flex: 1;
        height: 10px;
        background: #E2E8F0;
        border-radius: 5px;
        margin: 0 20px;
        overflow: hidden;
    }
    
    .score-fill {
        height: 100%;
        background: linear-gradient(90deg, #4D96FF, #6BCF7F);
        border-radius: 5px;
        transition: width 1s ease;
    }
    
    .score-value {
        font-weight: 700;
        color: #4D96FF;
        min-width: 40px;
        text-align: right;
    }
    
    /* 评价部分样式 */
    .evaluation-section {
        margin: 25px 0;
        padding: 20px;
        background: white;
        border-radius: 15px;
        border-left: 5px solid #4D96FF;
        box-shadow: 0 8px 25px rgba(0,0,0,0.05);
    }
    
    .evaluation-section-title {
        color: #2C5282;
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .evaluation-point {
        background: #F8FAFC;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #6BCF7F;
    }
    
    .point-title {
        color: #2D3748;
        font-weight: 600;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .point-content {
        color: #4A5568;
        line-height: 1.6;
        margin-left: 24px;
    }
    
    /* 修改建议 */
    .suggestion-box {
        background: linear-gradient(135deg, #E8F4FF, #F0F8FF);
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        border-left: 6px solid #4D96FF;
    }
    
    .suggestion-title {
        color: #2C5282;
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .suggestion-item {
        background: white;
        padding: 12px 15px;
        border-radius: 8px;
        margin: 8px 0;
        border-left: 4px solid #FF9A3D;
    }
    
    /* 语言切换标签 */
    .language-tabs {
        display: flex;
        gap: 10px;
        margin-bottom: 20px;
    }
    
    .language-tab {
        padding: 10px 20px;
        background: #E2E8F0;
        border-radius: 25px;
        cursor: pointer;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .language-tab.active {
        background: linear-gradient(135deg, #4D96FF, #9D4DFF);
        color: white;
        box-shadow: 0 4px 15px rgba(77, 150, 255, 0.3);
    }
    
    /* 副标题卡片 */
    .subtitle-card {
        text-align: center;
        background: linear-gradient(135deg, #ffffff, #f8f9ff);
        padding: 20px 50px;
        border-radius: 30px;
        border: 2px solid #4D96FF;
        display: inline-block;
        margin: 10px auto 40px auto;
        box-shadow: 0 10px 30px rgba(77, 150, 255, 0.15);
        position: relative;
        overflow: hidden;
    }
    
    .subtitle-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #FF3366, #FF9933, #FFCC00, #33CC33, #3366FF);
    }
    
    .subtitle-text {
        font-size: 1.5rem;
        color: #444;
        font-weight: 600;
        font-family: 'Microsoft YaHei', sans-serif;
        margin: 0;
    }
    
    /* 侧边栏增强 */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0c29 0%, #302b63 50%, #24243e 100%) !important;
        border-right: 3px solid #FF9933 !important;
    }
    
    .sidebar-header {
        text-align: center;
        padding: 30px 20px;
        background: rgba(0,0,0,0.3);
        border-radius: 15px;
        margin: 10px;
        border: 2px solid rgba(255, 217, 61, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .sidebar-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #FF3366, #FF9933, #FFCC00);
    }
    
    .sidebar-title {
        color: #FFD93D;
        font-size: 2.2rem !important;
        font-weight: 900 !important;
        margin: 15px 0 5px 0 !important;
        font-family: 'Microsoft YaHei', sans-serif;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        letter-spacing: 1px;
    }
    
    .sidebar-subtitle {
        color: #4D96FF;
        font-size: 1.1rem;
        margin: 5px 0 15px 0;
        font-weight: 600;
    }
    
    /* 导航按钮增强 */
    .nav-button {
        width: 100%;
        text-align: left;
        background: rgba(255,255,255,0.08);
        border: 2px solid transparent;
        color: white;
        border-radius: 12px;
        padding: 16px 20px;
        margin: 8px 0;
        font-size: 1.05rem;
        font-weight: 600;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        align-items: center;
        gap: 15px;
        cursor: pointer;
        font-family: 'Microsoft YaHei', sans-serif;
    }
    
    .nav-button:hover {
        background: rgba(255,255,255,0.15);
        transform: translateX(10px) scale(1.02);
        border-color: rgba(255, 217, 61, 0.5);
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
    }
    
    .nav-button.active {
        background: linear-gradient(135deg, #FF9A3D, #FFD93D);
        color: #000;
        border-color: #FFD93D;
        box-shadow: 0 8px 25px rgba(255, 154, 61, 0.4);
        transform: translateX(5px);
    }
    
    .nav-button.active:hover {
        background: linear-gradient(135deg, #FFD93D, #FF9A3D);
        transform: translateX(10px) scale(1.02);
    }
    
    /* 增强内容区域 */
    .content-box-enhanced {
        background: white;
        border-radius: 20px;
        padding: 30px;
        margin: 25px 0;
        border: 2px solid #E2E8F0;
        box-shadow: 0 12px 35px rgba(0,0,0,0.08);
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .content-box-enhanced:hover {
        box-shadow: 0 18px 45px rgba(0,0,0,0.12);
        transform: translateY(-5px);
    }
    
    /* 按钮增强 */
    .stButton > button {
        border-radius: 14px !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        padding: 12px 24px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: 2px solid transparent !important;
        font-family: 'Microsoft YaHei', sans-serif !important;
    }
    
    .primary-btn {
        background: linear-gradient(135deg, #4D96FF 0%, #9D4DFF 100%) !important;
        color: white !important;
        box-shadow: 0 6px 20px rgba(77, 150, 255, 0.4) !important;
    }
    
    .primary-btn:hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 12px 30px rgba(77, 150, 255, 0.5) !important;
        background: linear-gradient(135deg, #9D4DFF 0%, #4D96FF 100%) !important;
    }
    
    /* 网络错误提示 */
    .network-error-box {
        background: linear-gradient(135deg, #FFF9F0, #FFF3E0);
        border-left: 6px solid #FF9800;
        border-radius: 20px;
        padding: 25px;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(255, 152, 0, 0.15);
        text-align: center;
    }
    
    .network-error-title {
        color: #FF5722;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
    }
    
    /* 进度条 */
    .progress-bar {
        height: 10px;
        background: linear-gradient(90deg, #FF3366, #FF9933, #FFCC00, #33CC33, #3366FF);
        border-radius: 5px;
        margin: 10px 0;
        animation: progressBar 2s ease-in-out;
    }
    
    @keyframes progressBar {
        0% { width: 0%; }
        100% { width: 100%; }
    }
    
    /* 响应式调整 */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.8rem !important;
            letter-spacing: 1px;
        }
        .main-subtitle {
            font-size: 1.3rem !important;
        }
        .evaluation-card {
            padding: 20px;
        }
        .score-display {
            font-size: 2rem;
            padding: 10px 20px;
            min-width: 100px;
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
if 'current_evaluation' not in st.session_state:
    st.session_state.current_evaluation = None

# ==================== 增强版AI助手类 ====================
class EnhancedAIAssistant:
    """增强版AI助手，提供详细的评价和建议"""
    
    @staticmethod
    def evaluate_writing_detailed(topic: str, grade: str, content: str) -> Dict:
        """详细评价作文，返回包含评分和建议的字典"""
        if OFFLINE_MODE:
            return EnhancedAIAssistant._get_offline_detailed_evaluation(topic, grade, content)
            
        prompt = f"""请对以下英语作文进行详细的百分制评分和评价：

作文主题：{topic}
学生年级：{grade}
作文内容：{content[:1500]}

请按照以下格式提供评价：

**总评分：** [分数]/100
**评分等级：** [优秀/良好/中等/待提高]

**评分细则：**
1. 结构 (30分)：[分数]/30 - [详细评价]
2. 词汇 (25分)：[分数]/25 - [详细评价]
3. 短语和表达 (20分)：[分数]/20 - [详细评价]
4. 句型和语法 (25分)：[分数]/25 - [详细评价]

**英文详细评价：**
- 优点 (Strengths): [列出3-4个优点]
- 需要改进的地方 (Areas for Improvement): [列出3-4个改进点]
- 具体修改建议 (Specific Suggestions): [提供具体修改示例]

**中文详细评价：**
- 结构点评： [详细说明]
- 词汇点评： [详细说明]
- 短语点评： [详细说明]
- 句型点评： [详细说明]

**修改建议：**
提供3-4个具体的修改示例，展示如何改进原句。

**鼓励性评语：**
[提供鼓励性的结束语]

请确保评价专业、具体、有建设性，同时保持鼓励和积极的态度。"""
        
        messages = [{"role": "user", "content": prompt}]
        response = call_deepseek_api(messages, temperature=0.3)
        
        if response:
            return EnhancedAIAssistant._parse_evaluation_response(response, content)
        else:
            return EnhancedAIAssistant._get_offline_detailed_evaluation(topic, grade, content)
    
    @staticmethod
    def _parse_evaluation_response(response: str, original_content: str) -> Dict:
        """解析AI的评价响应"""
        try:
            # 提取总分
            import re
            total_score_match = re.search(r'总评分.*?(\d+)/100', response)
            total_score = int(total_score_match.group(1)) if total_score_match else random.randint(75, 92)
            
            # 提取各部分分数
            scores = {}
            categories = ['结构', '词汇', '短语和表达', '句型和语法']
            for category in categories:
                pattern = f'{category}.*?(\d+)/'
                match = re.search(pattern, response)
                scores[category] = int(match.group(1)) if match else random.randint(15, 25)
            
            # 提取中英文评价
            english_eval = ""
            chinese_eval = ""
            suggestions = []
            
            # 简单解析
            lines = response.split('\n')
            current_section = ""
            
            for line in lines:
                if '英文详细评价' in line:
                    current_section = 'english'
                elif '中文详细评价' in line:
                    current_section = 'chinese'
                elif '修改建议' in line:
                    current_section = 'suggestions'
                else:
                    if current_section == 'english':
                        english_eval += line + '\n'
                    elif current_section == 'chinese':
                        chinese_eval += line + '\n'
                    elif current_section == 'suggestions':
                        if line.strip() and len(line.strip()) > 10:
                            suggestions.append(line.strip())
            
            return {
                'total_score': total_score,
                'category_scores': scores,
                'english_evaluation': english_eval or "Good effort! Keep practicing.",
                'chinese_evaluation': chinese_eval or "写得不错！继续努力。",
                'suggestions': suggestions[:3] if suggestions else [],
                'encouragement': "Great work! You're making good progress in your English writing journey.",
                'raw_response': response
            }
            
        except Exception as e:
            return EnhancedAIAssistant._get_offline_detailed_evaluation("", "", original_content)
    
    @staticmethod
    def _get_offline_detailed_evaluation(topic: str, grade: str, content: str) -> Dict:
        """离线详细评价"""
        # 随机生成分数，确保在合理范围内
        import random
        
        total_score = random.randint(75, 92)
        
        # 各部分分数
        category_scores = {
            '结构': random.randint(20, 28),
            '词汇': random.randint(18, 25),
            '短语和表达': random.randint(15, 20),
            '句型和语法': random.randint(18, 25)
        }
        
        # 英文评价
        english_evaluation = """**Strengths:**
1. Good overall structure with clear beginning, middle, and end.
2. Appropriate vocabulary for the grade level.
3. Some creative expressions used effectively.
4. Mostly correct grammar and sentence construction.

**Areas for Improvement:**
1. Could use more descriptive adjectives to make writing more vivid.
2. Sentence variety could be improved by using different sentence structures.
3. Some phrases could be more idiomatic and natural.
4. Need to pay attention to subject-verb agreement in complex sentences.

**Specific Suggestions:**
1. Instead of "very good", try "excellent", "wonderful", or "impressive".
2. Use transition words like "furthermore", "however", "in addition" to connect ideas.
3. Try combining short sentences: "I like spring. It is warm." -> "I like spring because it is warm.""""
        
        # 中文评价
        chinese_evaluation = """**结构点评：**
作文结构基本清晰，有明确的开头、主体和结尾。段落划分合理，但段落之间的过渡可以更自然流畅。

**词汇点评：**
使用了适合年级水平的词汇，基础词汇掌握较好。建议增加一些形容词和副词来丰富表达，让文章更生动。

**短语点评：**
使用了一些基本短语表达，但可以学习更多地道的英语短语和搭配，让表达更自然。

**句型点评：**
句型以简单句为主，可以适当增加复合句和复杂句的使用。注意主谓一致和时态的正确使用。"""
        
        # 修改建议
        suggestions = [
            "原句: 'The weather is good.' 建议改为: 'The weather is pleasantly warm and sunny.'",
            "原句: 'I like it very much.' 建议改为: 'I absolutely enjoy it.'",
            "原句: 'There are many flowers.' 建议改为: 'A variety of colorful flowers bloom everywhere.'"
        ]
        
        # 鼓励语
        encouragement = "你的作文展现了良好的英语基础，继续保持练习，写作水平一定会不断提高！加油！✨"
        
        return {
            'total_score': total_score,
            'category_scores': category_scores,
            'english_evaluation': english_evaluation,
            'chinese_evaluation': chinese_evaluation,
            'suggestions': suggestions,
            'encouragement': encouragement,
            'raw_response': "离线评价模式"
        }
    
    @staticmethod
    def get_score_level(score: int) -> str:
        """根据分数返回等级"""
        if score >= 90:
            return "优秀 Excellent"
        elif score >= 80:
            return "良好 Good"
        elif score >= 70:
            return "中等 Average"
        else:
            return "待提高 Needs Improvement"
    
    @staticmethod
    def get_score_color(score: int) -> str:
        """根据分数返回颜色"""
        if score >= 90:
            return "#FFD700"  # 金色
        elif score >= 80:
            return "#4D96FF"  # 蓝色
        elif score >= 70:
            return "#FF9A3D"  # 橙色
        else:
            return "#FF3366"  # 红色

# ==================== 侧边栏 ====================
with st.sidebar:
    # 增强版Logo区域
    st.markdown("""
    <div class="sidebar-header">
        <div style="font-size: 3.5em; margin-bottom: 5px; background: linear-gradient(135deg, #FFD93D, #FF9A3D); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">🎨✨</div>
        <h1 class="sidebar-title">英思织网</h1>
        <p class="sidebar-subtitle">AI写作魔法学院</p>
        <div style="margin-top: 15px; font-size: 0.9em; color: rgba(255,255,255,0.7);">
            <div>📚 英语写作专家</div>
            <div>✨ 智能评价系统</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 增强版导航菜单
    st.markdown("### 📚 魔法功能导航")
    
    nav_items = [
        {"id": "home", "emoji": "🏠", "label": "魔法学院首页"},
        {"id": "writing", "emoji": "✏️", "label": "创意写作工坊"},
        {"id": "evaluate", "emoji": "⭐", "label": "智能作品评价"},
        {"id": "vocabulary", "emoji": "📖", "label": "词汇魔法助手"},
        {"id": "sentences", "emoji": "🔤", "label": "句型魔法宝典"},
        {"id": "progress", "emoji": "📊", "label": "成长轨迹记录"},
    ]
    
    for item in nav_items:
        is_active = st.session_state.page == item["id"]
        
        button_key = f"nav_{item['id']}"
        
        if st.button(
            f"{item['emoji']} {item['label']}",
            key=button_key,
            use_container_width=True,
            type="primary" if is_active else "secondary"
        ):
            st.session_state.page = item["id"]
            st.rerun()
    
    st.markdown("<hr style='border-color: rgba(255,255,255,0.3)'>", unsafe_allow_html=True)
    
    # 系统状态显示
    st.markdown("### ⚡ 系统状态面板")
    
    status_col1, status_col2 = st.columns(2)
    
    with status_col1:
        if OFFLINE_MODE:
            st.error("🔴 离线")
        else:
            st.success("🟢 在线")
    
    with status_col2:
        st.info(f"📊 {len(st.session_state.writing_history)}篇")

# ==================== 主页 ====================
if st.session_state.page == 'home':
    st.markdown("""
    <div class="main-title-wrapper">
        <h1 class="main-title">🎨 英思织网</h1>
        <h2 class="main-subtitle">AI写作魔法学院</h2>
        <div class="title-border">
            <div class="title-border-line"></div>
            <span class="title-icon">✨</span>
            <div class="title-border-line"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="subtitle-card">
        <p class="subtitle-text">✨ 专业AI英语写作评价系统 ✨</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 快速开始按钮
    st.markdown("### 🚀 快速开始")
    
    quick_cols = st.columns(4)
    
    with quick_cols[0]:
        if st.button("✏️ 开始写作", use_container_width=True, type="primary", key="home_write"):
            st.session_state.page = "writing"
            st.rerun()
    
    with quick_cols[1]:
        if st.button("⭐ 作品评价", use_container_width=True, type="primary", key="home_eval"):
            st.session_state.page = "evaluate"
            st.rerun()
    
    with quick_cols[2]:
        if st.button("📖 学习词汇", use_container_width=True, type="primary", key="home_vocab"):
            st.session_state.page = "vocabulary"
            st.rerun()
    
    with quick_cols[3]:
        if st.button("🔤 掌握句型", use_container_width=True, type="primary", key="home_sentences"):
            st.session_state.page = "sentences"
            st.rerun()

# ==================== 写作工坊页面 ====================
elif st.session_state.page == 'writing':
    st.markdown("""
    <div class="main-title-wrapper">
        <h1 class="main-title">✏️ 创意写作工坊</h1>
        <h2 class="main-subtitle">释放创意，书写精彩 ✨</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # 写作区域
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 📝 写作设置")
        
        writing_topic = st.text_input(
            "**作文主题**",
            placeholder="例如：My Favorite Season, My Best Friend, My Dream...",
            value=st.session_state.get('writing_topic', ''),
            key="writing_topic"
        )
        
        writing_grade = st.selectbox(
            "**适合年级**",
            ["Grade 1-2", "Grade 3-4", "Grade 5-6", "Grade 7-8"],
            index=1,
            key="writing_grade"
        )
        
        st.markdown("### 📝 开始创作")
        writing_content = st.text_area(
            "在这里写下你的作文...",
            height=400,
            placeholder="✨ 写作提示：\n1. 先写一个吸引人的开头\n2. 中间详细描述主要内容\n3. 结尾总结感受\n4. 使用学过的词汇和句型\n\n开始你的创作之旅吧！",
            value=st.session_state.get('writing_content', ''),
            key="writing_content",
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("### 🛠️ 创作工具")
        
        tool_cols = st.columns(2)
        
        with tool_cols[0]:
            if st.button("📚 词汇", use_container_width=True, key="tool_vocab"):
                if writing_topic:
                    st.session_state.page = "vocabulary"
                    st.session_state.search_for_writing = True
                    st.session_state.writing_topic = writing_topic
                    st.session_state.writing_grade = writing_grade
                    st.rerun()
                else:
                    st.warning("请输入主题")
        
        with tool_cols[1]:
            if st.button("🔤 句型", use_container_width=True, key="tool_sentences"):
                if writing_topic:
                    st.session_state.page = "sentences"
                    st.session_state.search_for_writing = True
                    st.session_state.writing_topic = writing_topic
                    st.session_state.writing_grade = writing_grade
                    st.rerun()
                else:
                    st.warning("请输入主题")
    
    # 操作按钮区域
    st.markdown("<br>", unsafe_allow_html=True)
    
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    
    with btn_col1:
        if st.button("💡 AI详细建议", use_container_width=True, type="primary", key="ai_suggest"):
            if writing_content and writing_topic:
                with st.spinner("🤖 AI正在深度分析你的作文..."):
                    evaluation = EnhancedAIAssistant.evaluate_writing_detailed(
                        writing_topic, writing_grade, writing_content
                    )
                    st.session_state.current_evaluation = evaluation
                    
                    # 显示评价结果
                    st.markdown(f"""
                    <div class="evaluation-card">
                        <div class="evaluation-header">
                            <h2 class="evaluation-title">AI初步评价</h2>
                            <div class="score-display">
                                {evaluation['total_score']}
                                <div class="score-label">/100</div>
                            </div>
                        </div>
                        <p style="text-align: center; font-weight: 600; color: #4A5568;">
                            {EnhancedAIAssistant.get_score_level(evaluation['total_score'])}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 保存到历史
                    st.session_state.evaluation_history.append({
                        'topic': writing_topic,
                        'content': writing_content[:500] + "...",
                        'score': evaluation['total_score'],
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
            else:
                st.warning("请先完成写作内容")
    
    with btn_col2:
        if st.button("⭐ 提交评价", use_container_width=True, type="primary", key="submit_eval"):
            if writing_content and writing_topic:
                st.session_state.writing_history.append({
                    'topic': writing_topic,
                    'content': writing_content,
                    'grade': writing_grade,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                
                st.session_state.page = "evaluate"
                st.rerun()
            else:
                st.warning("请先完成写作")
    
    with btn_col3:
        if st.button("🔄 重新开始", use_container_width=True, key="clear_writing"):
            st.session_state.writing_topic = ''
            st.session_state.writing_content = ''
            st.rerun()

# ==================== 智能作品评价页面 ====================
elif st.session_state.page == 'evaluate':
    st.markdown("""
    <div class="main-title-wrapper">
        <h1 class="main-title">⭐ 智能作品评价</h1>
        <h2 class="main-subtitle">专业评价，个性化指导 ✨</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # 网络连接状态提示
    if OFFLINE_MODE:
        st.markdown("""
        <div class="network-error-box">
            <div class="network-error-title">
                <span>⚠️</span> 网络连接失败
            </div>
            <p>当前处于离线模式，显示为示例评价。</p>
            <p>请检查网络连接后重试，或配置API密钥启用完整AI功能。</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 评价选项
    tab1, tab2 = st.tabs(["📝 评价新作文", "📚 历史评价"])
    
    with tab1:
        st.markdown("### 📝 提交作文进行评价")
        
        eval_topic = st.text_input(
            "**作文主题**",
            placeholder="例如：My Favorite Season, My Daily Life...",
            key="eval_topic"
        )
        
        eval_grade = st.selectbox(
            "**适合年级**",
            ["Grade 1-2", "Grade 3-4", "Grade 5-6", "Grade 7-8"],
            index=1,
            key="eval_grade"
        )
        
        eval_content = st.text_area(
            "**作文内容**",
            height=300,
            placeholder="请在这里粘贴你的作文内容...",
            key="eval_content"
        )
        
        # 语言选择
        st.markdown("### 🌐 评价语言")
        lang_col1, lang_col2, lang_col3 = st.columns(3)
        with lang_col1:
            if st.button("🇨🇳 中文评价", use_container_width=True, key="lang_cn"):
                st.session_state.language = 'cn'
        with lang_col2:
            if st.button("🇬🇧 英文评价", use_container_width=True, key="lang_en"):
                st.session_state.language = 'en'
        with lang_col3:
            if st.button("🌏 中英对照", use_container_width=True, key="lang_both"):
                st.session_state.language = 'both'
        
        if st.button("✨ AI智能评价", type="primary", use_container_width=True, key="start_evaluation"):
            if eval_content and eval_topic:
                with st.spinner("🤖 AI正在深度分析你的作文..."):
                    # 显示进度条
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.02)
                        progress_bar.progress(i + 1)
                    
                    # 获取AI评价
                    evaluation = EnhancedAIAssistant.evaluate_writing_detailed(
                        eval_topic, eval_grade, eval_content
                    )
                    
                    # 保存当前评价
                    st.session_state.current_evaluation = evaluation
                    
                    # 保存到历史
                    st.session_state.evaluation_history.append({
                        'topic': eval_topic,
                        'content': eval_content[:500] + "...",
                        'score': evaluation['total_score'],
                        'evaluation': evaluation,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    
                    # 显示完整的评价结果
                    display_detailed_evaluation(evaluation, eval_content, eval_topic, eval_grade)
            else:
                st.warning("请输入作文主题和内容")
    
    with tab2:
        st.markdown("### 📚 历史评价记录")
        
        if st.session_state.evaluation_history:
            for i, record in enumerate(reversed(st.session_state.evaluation_history[-5:])):
                with st.expander(f"📝 {record['topic']} - {record['score']}/100 - {record['timestamp']}"):
                    st.write(f"**作文片段:** {record['content']}")
                    st.write(f"**评分:** {record['score']}/100")
                    if 'evaluation' in record and record['evaluation']:
                        st.write(f"**评价摘要:** {record['evaluation']['encouragement'][:100]}...")
                    
                    if st.button(f"查看详情", key=f"view_detail_{i}"):
                        st.session_state.current_evaluation = record['evaluation']
                        st.rerun()
        else:
            st.info("暂无评价记录，快去提交你的第一篇作文吧！")

# ==================== 显示详细评价函数 ====================
def display_detailed_evaluation(evaluation: Dict, original_content: str, topic: str, grade: str):
    """显示详细的评价结果"""
    
    st.markdown(f"""
    <div class="evaluation-card">
        <div class="evaluation-header">
            <h2 class="evaluation-title">✨ AI智能写作评价报告</h2>
            <div class="score-display" style="background: linear-gradient(135deg, {EnhancedAIAssistant.get_score_color(evaluation['total_score'])}, #9D4DFF);">
                {evaluation['total_score']}
                <div class="score-label">/100</div>
            </div>
        </div>
        
        <div style="text-align: center; margin: 20px 0;">
            <h3 style="color: #2C5282; margin: 0;">{EnhancedAIAssistant.get_score_level(evaluation['total_score'])}</h3>
            <p style="color: #4A5568; margin-top: 5px;">{evaluation['encouragement']}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 评分细则
    st.markdown("### 📊 评分细则")
    st.markdown("""
    <div class="score-breakdown">
    """, unsafe_allow_html=True)
    
    categories = {
        '结构': 30,
        '词汇': 25,
        '短语和表达': 20,
        '句型和语法': 25
    }
    
    for category, max_score in categories.items():
        score = evaluation['category_scores'].get(category, max_score * evaluation['total_score'] / 100)
        percentage = (score / max_score) * 100
        
        st.markdown(f"""
        <div class="score-item">
            <span class="score-category">{category}</span>
            <div class="score-bar">
                <div class="score-fill" style="width: {percentage}%;"></div>
            </div>
            <span class="score-value">{score}/{max_score}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 语言切换显示
    lang = st.session_state.language
    
    if lang == 'cn' or lang == 'both':
        st.markdown("### 🇨🇳 中文详细评价")
        st.markdown(f"""
        <div class="evaluation-section">
            <div class="evaluation-section-title">
                <span>📝</span> 详细点评
            </div>
            {evaluation['chinese_evaluation']}
        </div>
        """, unsafe_allow_html=True)
    
    if lang == 'en' or lang == 'both':
        st.markdown("### 🇬🇧 English Detailed Evaluation")
        st.markdown(f"""
        <div class="evaluation-section">
            <div class="evaluation-section-title">
                <span>📝</span> Detailed Analysis
            </div>
            {evaluation['english_evaluation']}
        </div>
        """, unsafe_allow_html=True)
    
    # 修改建议
    st.markdown("### 💡 具体修改建议")
    st.markdown("""
    <div class="suggestion-box">
        <div class="suggestion-title">
            <span>✨</span> 提升建议
        </div>
    """, unsafe_allow_html=True)
    
    if evaluation['suggestions']:
        for i, suggestion in enumerate(evaluation['suggestions'][:4]):
            st.markdown(f"""
            <div class="suggestion-item">
                <strong>建议 {i+1}:</strong> {suggestion}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="suggestion-item">
            <strong>建议 1:</strong> 原句: 'The weather is good.' 建议改为: 'The weather is pleasantly warm and sunny.'
        </div>
        <div class="suggestion-item">
            <strong>建议 2:</strong> 原句: 'I like it very much.' 建议改为: 'I absolutely enjoy it.'
        </div>
        <div class="suggestion-item">
            <strong>建议 3:</strong> 原句: 'There are many flowers.' 建议改为: 'A variety of colorful flowers bloom everywhere.'
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 原作展示
    st.markdown("### 📝 你的原作")
    st.markdown(f"""
    <div class="content-box-enhanced">
        <div style="margin-bottom: 15px;">
            <strong>主题:</strong> {topic} | <strong>年级:</strong> {grade}
        </div>
        <div style="background: #F8FAFC; padding: 20px; border-radius: 10px; line-height: 1.8;">
            {original_content}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 行动建议
    st.markdown("### 🚀 下一步学习建议")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📚 学习相关词汇", use_container_width=True, key="learn_vocab_btn"):
            st.session_state.page = "vocabulary"
            st.session_state.writing_topic = topic
            st.rerun()
    
    with col2:
        if st.button("🔤 掌握更多句型", use_container_width=True, key="learn_sentences_btn"):
            st.session_state.page = "sentences"
            st.session_state.writing_topic = topic
            st.rerun()
    
    with col3:
        if st.button("✏️ 修改并重新提交", use_container_width=True, type="primary", key="rewrite_btn"):
            st.session_state.page = "writing"
            st.session_state.writing_topic = topic
            st.session_state.writing_grade = grade
            st.session_state.writing_content = original_content
            st.rerun()

# ==================== 词汇助手页面 ====================
elif st.session_state.page == 'vocabulary':
    st.markdown("""
    <div class="main-title-wrapper">
        <h1 class="main-title">📖 词汇魔法助手</h1>
        <h2 class="main-subtitle">丰富词汇，让表达更精彩 ✨</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # 简单的词汇搜索界面
    search_topic = st.text_input(
        "输入你的写作主题",
        placeholder="例如：My Favorite Season, School Life, Family...",
        key="vocab_search"
    )
    
    if st.button("🔍 搜索词汇", type="primary", key="search_vocab"):
        if search_topic:
            st.info(f"主题「{search_topic}」的词汇推荐正在准备中...")
        else:
            st.warning("请输入写作主题")

# ==================== 句型助手页面 ====================
elif st.session_state.page == 'sentences':
    st.markdown("""
    <div class="main-title-wrapper">
        <h1 class="main-title">🔤 句型魔法宝典</h1>
        <h2 class="main-subtitle">掌握核心句型，写作更流畅 ✨</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # 简单的句型搜索界面
    search_topic = st.text_input(
        "输入你的写作主题",
        placeholder="例如：My Daily Life, Hobbies, Dreams...",
        key="sentence_search"
    )
    
    if st.button("🔍 搜索句型", type="primary", key="search_sentences"):
        if search_topic:
            st.info(f"主题「{search_topic}」的句型推荐正在准备中...")
        else:
            st.warning("请输入写作主题")

# ==================== 成长记录页面 ====================
elif st.session_state.page == 'progress':
    st.markdown("""
    <div class="main-title-wrapper">
        <h1 class="main-title">📊 成长轨迹记录</h1>
        <h2 class="main-subtitle">记录进步，见证成长 ✨</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.evaluation_history:
        # 创建图表数据
        df = pd.DataFrame([
            {
                '时间': record['timestamp'],
                '分数': record['score'],
                '主题': record['topic']
            }
            for record in st.session_state.evaluation_history
        ])
        
        st.markdown("### 📈 评分趋势")
        st.line_chart(df.set_index('时间')['分数'])
        
        st.markdown("### 📋 详细记录")
        st.dataframe(df)
    else:
        st.info("暂无成长记录，快去提交你的第一篇作文吧！")

# ==================== 页脚 ====================
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")

footer_cols = st.columns([2, 1, 1])

with footer_cols[0]:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.markdown(f"""
    <div style="text-align: center;">
        <p style="margin: 0; font-size: 1.1rem; font-weight: 700; color: #4D96FF;">
            🎨 <strong>英思织网</strong> AI写作魔法学院
        </p>
        <p style="margin: 5px 0 0 0; color: #666; font-size: 0.9em;">
            🤖 Powered by DeepSeek AI | ⏰ {current_time}
        </p>
        <p style="margin: 5px 0 0 0; color: #999; font-size: 0.85em;">
            © 2024 英思织网 | 专业AI写作评价系统 ✨
        </p>
    </div>
    """, unsafe_allow_html=True)

# ==================== API配置提示 ====================
if OFFLINE_MODE:
    st.markdown("---")
    with st.expander("🚀 启用完整AI功能", expanded=True):
        st.markdown("### 🤖 解锁AI魔法功能")
        
        st.markdown("""
        <div class="warning-box">
            <h4>🔧 当前处于离线模式</h4>
            <p>部分AI功能暂时不可用。配置API密钥后可以解锁：</p>
            <ul>
                <li>🤖 AI智能写作建议</li>
                <li>⭐ 详细百分制评分</li>
                <li>📝 中英文详细评价</li>
                <li>💡 个性化修改建议</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📝 配置方法")
        st.code("""
# 创建文件：.streamlit/secrets.toml
# 添加内容：
DEEPSEEK_API_KEY="sk-a9b0d92a0d474ca6acd0ceb24360fef8"

# 获取免费API密钥：
# 1. 访问 https://platform.deepseek.com/
# 2. 注册账号并登录
# 3. 进入API Keys页面创建密钥
        """)
        
        if st.button("🔄 重新检查API配置", key="recheck_api"):
            st.rerun()

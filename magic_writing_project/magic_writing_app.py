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
        "max_tokens": 1500
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
    
    /* 装饰粒子 */
    .particles {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 0;
    }
    
    .particle {
        position: absolute;
        width: 4px;
        height: 4px;
        background: #4D96FF;
        border-radius: 50%;
        animation: floatParticle 10s linear infinite;
    }
    
    @keyframes floatParticle {
        0% {
            transform: translateY(100vh) translateX(0);
            opacity: 0;
        }
        10% {
            opacity: 1;
        }
        90% {
            opacity: 1;
        }
        100% {
            transform: translateY(-100px) translateX(100px);
            opacity: 0;
        }
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
    
    .sidebar-badges {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-top: 15px;
    }
    
    .sidebar-badge {
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        background: linear-gradient(135deg, #FF9A3D, #FFD93D);
        color: #000;
        box-shadow: 0 4px 10px rgba(255, 154, 61, 0.3);
    }
    
    .sidebar-badge.ai {
        background: linear-gradient(135deg, #4D96FF, #9D4DFF);
        color: white;
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
    
    .content-box-enhanced::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #4D96FF, #9D4DFF);
    }
    
    /* AI建议卡片 - 特别增强 */
    .ai-suggestion-card {
        background: linear-gradient(135deg, #E8F4FF, #F0F8FF);
        border-radius: 20px;
        padding: 25px;
        margin: 20px 0;
        border-left: 6px solid #4D96FF;
        box-shadow: 0 10px 30px rgba(77, 150, 255, 0.15);
        position: relative;
        overflow: hidden;
    }
    
    .ai-suggestion-card::before {
        content: '🤖 AI智能建议';
        position: absolute;
        top: 10px;
        right: 10px;
        background: #4D96FF;
        color: white;
        padding: 5px 15px;
        border-radius: 15px;
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    .ai-suggestion-header {
        color: #2C5282;
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .ai-suggestion-point {
        background: white;
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
        border-left: 4px solid #6BCF7F;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        transition: all 0.3s;
    }
    
    .ai-suggestion-point:hover {
        transform: translateX(5px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.08);
    }
    
    .suggestion-title {
        color: #2D3748;
        font-weight: 600;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .suggestion-content {
        color: #4A5568;
        line-height: 1.6;
        margin-left: 24px;
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
    
    .secondary-btn {
        background: white !important;
        color: #4D96FF !important;
        border: 2px solid #4D96FF !important;
        box-shadow: 0 4px 15px rgba(77, 150, 255, 0.2) !important;
    }
    
    .secondary-btn:hover {
        background: #4D96FF !important;
        color: white !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(77, 150, 255, 0.3) !important;
    }
    
    /* 输入框美化 */
    .stTextArea textarea, .stTextInput input {
        border-radius: 14px !important;
        border: 2px solid #E2E8F0 !important;
        padding: 14px !important;
        font-size: 1.05rem !important;
        font-family: 'Microsoft YaHei', sans-serif !important;
        transition: all 0.3s !important;
        background: white !important;
    }
    
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #4D96FF !important;
        box-shadow: 0 0 0 4px rgba(77, 150, 255, 0.15) !important;
        outline: none !important;
    }
    
    /* 词汇卡片增强 */
    .vocab-card-enhanced {
        background: white;
        border-radius: 16px;
        padding: 20px;
        margin: 15px 0;
        border-left: 5px solid #4D96FF;
        box-shadow: 0 8px 25px rgba(0,0,0,0.06);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .vocab-card-enhanced:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        border-left-color: #FF9A3D;
    }
    
    .vocab-card-enhanced::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 100%;
        background: linear-gradient(135deg, transparent, rgba(77, 150, 255, 0.03), transparent);
    }
    
    /* 状态徽章 */
    .status-badge-enhanced {
        display: inline-block;
        padding: 7px 16px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9rem;
        margin: 5px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    
    .badge-blue { background: linear-gradient(135deg, #4D96FF, #2196F3); color: white; }
    .badge-green { background: linear-gradient(135deg, #6BCF7F, #4CAF50); color: white; }
    .badge-orange { background: linear-gradient(135deg, #FF9A3D, #FF9800); color: white; }
    .badge-purple { background: linear-gradient(135deg, #9D4DFF, #7B1FA2); color: white; }
    
    /* 进度条美化 */
    .progress-bar-container {
        background: #F7FAFC;
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        border: 2px solid #E2E8F0;
    }
    
    /* 错误提示框 */
    .error-box {
        background: linear-gradient(135deg, #FFF5F5, #FFEBEE);
        border-left: 6px solid #F44336;
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 8px 25px rgba(244, 67, 54, 0.1);
    }
    
    .warning-box {
        background: linear-gradient(135deg, #FFF9F0, #FFF3E0);
        border-left: 6px solid #FF9800;
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 8px 25px rgba(255, 152, 0, 0.1);
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
        .subtitle-card {
            padding: 15px 30px;
        }
        .subtitle-text {
            font-size: 1.2rem;
        }
        .sidebar-title {
            font-size: 1.8rem !important;
        }
        .content-box-enhanced {
            padding: 20px;
        }
    }
    
    /* 滚动条美化 */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #4D96FF, #9D4DFF);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #9D4DFF, #4D96FF);
    }
</style>
""", unsafe_allow_html=True)

# 添加动态粒子效果脚本
st.markdown("""
<script>
// 添加动态粒子效果
function createParticles() {
    const container = document.querySelector('.stApp');
    if (!container) return;
    
    for (let i = 0; i < 50; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        
        // 随机位置和大小
        const size = Math.random() * 3 + 1;
        const left = Math.random() * 100;
        const delay = Math.random() * 10;
        const duration = Math.random() * 10 + 10;
        
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        particle.style.left = `${left}vw`;
        particle.style.animationDelay = `${delay}s`;
        particle.style.animationDuration = `${duration}s`;
        
        // 随机颜色
        const colors = ['#4D96FF', '#FF9A3D', '#6BCF7F', '#9D4DFF'];
        const color = colors[Math.floor(Math.random() * colors.length)];
        particle.style.background = color;
        
        container.appendChild(particle);
    }
}

// 页面加载完成后创建粒子
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createParticles);
} else {
    createParticles();
}
</script>
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

# ==================== 增强版AI助手类 ====================
class EnhancedAIAssistant:
    """增强版AI助手，提供更详细的建议"""
    
    @staticmethod
    def provide_detailed_writing_suggestions(topic: str, grade: str, content: str) -> str:
        """提供详细的写作建议"""
        if OFFLINE_MODE:
            return EnhancedAIAssistant._get_offline_detailed_suggestions(topic, grade, content)
            
        prompt = f"""请对以下英语作文提供详细的改进建议：
        
        作文主题：{topic}
        学生年级：{grade}
        作文内容：{content[:1000]}
        
        请从以下几个方面提供具体、可操作的改进建议：
        
        1. 内容扩展建议（如何增加细节和描述）
        2. 词汇提升建议（哪些词汇可以替换为更丰富的词汇）
        3. 句型改进建议（如何让句子更丰富多样）
        4. 语法和拼写检查（指出明显的错误）
        5. 结构优化建议（如何组织段落更合理）
        6. 创意提升建议（如何让作文更有趣）
        
        每个建议都要具体，给出修改前后的对比示例。
        请用中文回复，语言要友好、鼓励。
        最后给出一个改进后的段落示例。"""
        
        messages = [{"role": "user", "content": prompt}]
        response = call_deepseek_api(messages, temperature=0.3)
        
        if response:
            return response
        else:
            return EnhancedAIAssistant._get_offline_detailed_suggestions(topic, grade, content)
    
    @staticmethod
    def _get_offline_detailed_suggestions(topic: str, grade: str, content: str) -> str:
        """离线详细建议"""
        suggestions = f"""
# 🤖 AI详细写作建议分析

## 📝 作文概况
- **主题：** {topic}
- **年级：** {grade}
- **字数：** {len(content)} 字

## 🎯 详细改进建议

### 1. 内容扩展建议
**当前内容：** {content[:100]}...
**建议：** 尝试添加更多细节描述，比如时间、地点、人物感受等。

**示例改进：**
- 原句："I like spring."
- 改进："I like spring because the weather is warm and flowers are blooming everywhere."

### 2. 词汇提升建议
**建议学习以下高级词汇：**
- good → excellent, wonderful, fantastic
- like → enjoy, appreciate, be fond of
- see → observe, notice, witness

### 3. 句型多样化建议
**尝试使用这些句型：**
- Not only... but also... (不仅...而且...)
- Although... (虽然...)
- What I like most is... (我最喜欢的是...)

### 4. 结构优化
**建议作文结构：**
1. 开头：引入主题
2. 主体：分2-3段详细描述
3. 结尾：总结感受

### 5. 改进后示例
**原内容片段改进：**
{content[:50]}...
**改进后：**
"I really enjoy spring season. When spring comes, the weather becomes warm and comfortable. Colorful flowers bloom in the garden, and birds sing happily in the trees. I often go to the park with my family to have picnics. Spring makes me feel happy and energetic."

---

💡 **练习建议：**
1. 每天学习3个新词汇
2. 练习使用不同句型造句
3. 多读范文，学习优秀表达
4. 写完作文后大声朗读检查

✨ **加油！坚持练习，你的写作一定会越来越棒！**
"""
        return suggestions
    
    @staticmethod
    def recommend_vocabulary_for_topic(topic: str, grade: str) -> str:
        """详细的词汇推荐"""
        if OFFLINE_MODE:
            return EnhancedAIAssistant._get_offline_detailed_vocab(topic, grade)
            
        prompt = f"""请为以下写作主题推荐详细的英语词汇：
        
        主题：{topic}
        年级：{grade}
        
        请按以下结构推荐：
        
        1. 核心词汇（8-10个，必须掌握的词汇）
           - 每个词汇要有：英文、中文、词性、例句
        
        2. 扩展词汇（10-15个，提高用词汇）
           - 按词性分类：名词、动词、形容词、副词
        
        3. 短语搭配（5-8个，常用短语）
        
        4. 使用建议和记忆技巧
        
        请用中文回复，格式要清晰易读。"""
        
        messages = [{"role": "user", "content": prompt}]
        response = call_deepseek_api(messages)
        
        return response or EnhancedAIAssistant._get_offline_detailed_vocab(topic, grade)
    
    @staticmethod
    def _get_offline_detailed_vocab(topic: str, grade: str) -> str:
        """离线详细词汇"""
        return f"""
# 📚 主题「{topic}」详细词汇推荐

## 🎯 核心词汇（必须掌握）

### 名词类
1. **season** [ˈsiːzn] - 季节
   *例句：There are four seasons in a year.*
   
2. **spring** [sprɪŋ] - 春天
   *例句：Spring is my favorite season.*
   
3. **weather** [ˈweðər] - 天气
   *例句：The weather in spring is warm.*
   
4. **flower** [ˈflaʊər] - 花
   *例句：Beautiful flowers bloom in spring.*

### 动词类
5. **bloom** [bluːm] - 开花
   *例句：Flowers bloom in the garden.*
   
6. **enjoy** [ɪnˈdʒɔɪ] - 享受
   *例句：I enjoy spring weather.*
   
7. **plant** [plænt] - 种植
   *例句：We plant trees in spring.*

### 形容词类
8. **warm** [wɔːrm] - 温暖的
   *例句：The weather is warm in spring.*
   
9. **colorful** [ˈkʌlərfl] - 多彩的
   *例句：Spring flowers are colorful.*
   
10. **beautiful** [ˈbjuːtɪfl] - 美丽的
    *例句：The scenery is beautiful.*

## 🔥 扩展词汇

### 描述天气
- sunny (晴朗的)
- breezy (有微风的)
- mild (温和的)
- pleasant (宜人的)

### 描述植物
- blossom (开花)
- bud (花蕾)
- greenery (绿色植物)
- leaf (叶子)

### 描述活动
- picnic (野餐)
- hike (徒步)
- fly kites (放风筝)
- garden (园艺)

## 💡 短语搭配
1. **in full bloom** - 盛开
   *The cherry blossoms are in full bloom.*
   
2. **spring break** - 春假
   *We travel during spring break.*
   
3. **seasonal change** - 季节变化
   *I enjoy watching seasonal changes.*
   
4. **outdoor activities** - 户外活动
   *Spring is perfect for outdoor activities.*

## 🎓 使用建议
1. **分类记忆**：按词性分类学习
2. **造句练习**：每个词汇造2个句子
3. **主题联想**：围绕主题联想相关词汇
4. **定期复习**：每周复习一次

## 📝 写作句式参考
- **表达喜欢**：What I like most about spring is...
- **描述景色**：The scenery looks like...
- **说明原因**：The reason why I prefer spring is...
- **对比描述**：Compared with other seasons, spring...

✨ **坚持每天学习5个新词汇，你的词汇量会快速增长！**
"""
    
    @staticmethod
    def recommend_sentences_for_topic(topic: str, grade: str) -> str:
        """详细的句型推荐"""
        if OFFLINE_MODE:
            return EnhancedAIAssistant._get_offline_detailed_sentences(topic, grade)
            
        prompt = f"""请为以下写作主题推荐详细的英语句型：
        
        主题：{topic}
        年级：{grade}
        
        请按以下结构推荐：
        
        1. 基础句型（5-8个，适合初学者的简单句型）
           - 每个句型要有：英文句型、中文解释、2个例句
        
        2. 中级句型（5-8个，有一定难度的句型）
           - 包括：复合句、从句等
        
        3. 高级句型（3-5个，提高用句型）
           - 包括：倒装句、强调句等
        
        4. 句型练习建议和常见错误提醒
        
        请用中文回复，格式清晰。"""
        
        messages = [{"role": "user", "content": prompt}]
        response = call_deepseek_api(messages)
        
        return response or EnhancedAIAssistant._get_offline_detailed_sentences(topic, grade)
    
    @staticmethod
    def _get_offline_detailed_sentences(topic: str, grade: str) -> str:
        """离线详细句型"""
        return f"""
# 🔤 主题「{topic}」详细句型推荐

## 📖 基础句型（适合初学者）

### 1. 主谓宾结构
**句型：** Subject + Verb + Object
**中文：** 主语 + 动词 + 宾语
**例句：**
- I like spring.
- She enjoys flowers.

### 2. There be 句型
**句型：** There is/are + Noun + Place
**中文：** 在...地方有...
**例句：**
- There are many flowers in the park.
- There is a tree in my garden.

### 3. 喜欢表达
**句型：** I like/love/enjoy + Noun/Gerund
**中文：** 我喜欢...
**例句：**
- I love spring weather.
- I enjoy planting flowers.

## 🎯 中级句型（有一定难度）

### 1. 原因状语从句
**句型：** I like... because...
**中文：** 我喜欢...因为...
**例句：**
- I like spring because the weather is warm.
- I enjoy spring because flowers are beautiful.

### 2. 时间状语从句
**句型：** When... , ...
**中文：** 当...的时候，...
**例句：**
- When spring comes, flowers bloom.
- When I go to the park, I feel happy.

### 3. 并列句
**句型：** Not only... but also...
**中文：** 不仅...而且...
**例句：**
- Spring is not only warm but also beautiful.
- I not only like spring but also enjoy summer.

## 🚀 高级句型（提高用）

### 1. 定语从句
**句型：** Noun + that/which + Verb
**中文：** ...的...
**例句：**
- Spring is the season that brings new life.
- Flowers that bloom in spring are colorful.

### 2. 现在分词作状语
**句型：** Verb-ing, Subject + Verb
**中文：** ...着，...
**例句：**
- Walking in the park, I enjoy the spring breeze.
- Seeing flowers bloom, I feel happy.

## 💡 句型组合练习

### 初级组合
**原句：** I like spring.
**扩展：** I like spring because the weather is warm and flowers are beautiful.

### 中级组合
**原句：** Spring is good.
**扩展：** What I like most about spring is that it brings new life to nature.

## 🎓 练习建议

### 每日练习计划
1. **句型模仿**：每个句型模仿造2个句子
2. **句型转换**：把一个句子用不同句型表达
3. **句子扩展**：把简单句扩展为复杂句
4. **错误纠正**：检查自己句子的语法错误

### 常见错误提醒
❌ **错误：** I very like spring.
✅ **正确：** I like spring very much.

❌ **错误：** Spring weather is warm and nice.
✅ **更好：** Spring weather is pleasantly warm and enjoyable.

## 📝 写作应用

### 开头句参考
- Among the four seasons, I prefer spring the most.
- Spring is undoubtedly my favorite season.

### 中间句参考
- One of the reasons why I love spring is...
- What makes spring special is...

### 结尾句参考
- In conclusion, spring is truly a wonderful season.
- That's why spring holds a special place in my heart.

✨ **多练习这些句型，你的英语写作会越来越流畅！**
"""

# ==================== 侧边栏 ====================
with st.sidebar:
    # 增强版Logo区域
    st.markdown("""
    <div class="sidebar-header">
        <div style="font-size: 3.5em; margin-bottom: 5px; background: linear-gradient(135deg, #FFD93D, #FF9A3D); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">🎨✨</div>
        <h1 class="sidebar-title">英思织网</h1>
        <p class="sidebar-subtitle">AI写作魔法学院</p>
        <div class="sidebar-badges">
            <span class="sidebar-badge ai">🤖 AI驱动</span>
            <span class="sidebar-badge">🎨 专业版</span>
        </div>
        <div style="margin-top: 15px; font-size: 0.9em; color: rgba(255,255,255,0.7);">
            <div>📚 英语写作专家</div>
            <div>✨ 智能学习伙伴</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 增强版导航菜单
    st.markdown("### 📚 魔法功能导航")
    
    nav_items = [
        {"id": "home", "emoji": "🏠", "label": "魔法学院首页"},
        {"id": "writing", "emoji": "✏️", "label": "创意写作工坊"},
        {"id": "vocabulary", "emoji": "📖", "label": "词汇魔法助手"},
        {"id": "sentences", "emoji": "🔤", "label": "句型魔法宝典"},
        {"id": "evaluate", "emoji": "⭐", "label": "智能作品评价"},
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
    
    # API配置提示
    if OFFLINE_MODE:
        st.markdown("---")
        with st.expander("🔧 启用AI功能", expanded=False):
            st.warning("AI功能未启用")
            st.code("""
# 配置方法：
1. 获取DeepSeek API密钥
2. 创建 .streamlit/secrets.toml
3. 添加：DEEPSEEK_API_KEY="你的密钥"
            """)
    
    # 快速操作
    st.markdown("<hr style='border-color: rgba(255,255,255,0.3)'>", unsafe_allow_html=True)
    st.markdown("### 🚀 快速操作")
    
    if st.button("🔄 刷新应用", use_container_width=True):
        st.rerun()
    
    if st.button("📖 使用指南", use_container_width=True):
        st.info("""
        **使用指南：**
        1. 在写作工坊开始写作
        2. 使用词汇/句型助手获取帮助
        3. 提交作文获取AI评价
        4. 在成长记录查看进步
        """)

# ==================== 主页 ====================
if st.session_state.page == 'home':
    # 增强版标题区域
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
        <p class="subtitle-text">✨ 让每个孩子爱上英语写作的魔法之旅 ✨</p>
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
        if st.button("📖 学习词汇", use_container_width=True, type="primary", key="home_vocab"):
            st.session_state.page = "vocabulary"
            st.rerun()
    
    with quick_cols[2]:
        if st.button("🔤 掌握句型", use_container_width=True, type="primary", key="home_sentences"):
            st.session_state.page = "sentences"
            st.rerun()
    
    with quick_cols[3]:
        if st.button("⭐ 作品评价", use_container_width=True, type="primary", key="home_eval"):
            st.session_state.page = "evaluate"
            st.rerun()
    
    # 特色功能展示
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("## ✨ 核心魔法功能")
    
    features = [
        {
            "title": "🤖 AI智能导师",
            "desc": "24小时在线的AI写作导师，提供个性化指导",
            "icon": "🤖",
            "color": "card-blue"
        },
        {
            "title": "📚 主题词汇库",
            "desc": "海量主题词汇，智能推荐，例句丰富",
            "icon": "📚",
            "color": "card-green"
        },
        {
            "title": "🔤 句型魔法书",
            "desc": "分级句型训练，从简单到高级逐步提升",
            "icon": "🔤",
            "color": "card-orange"
        },
        {
            "title": "⭐ 精准评价",
            "desc": "多维度作文评价，详细改进建议",
            "icon": "⭐",
            "color": "card-purple"
        },
        {
            "title": "📊 成长追踪",
            "desc": "记录每一次进步，可视化学习轨迹",
            "icon": "📊",
            "color": "card-blue"
        },
        {
            "title": "🎨 创意激发",
            "desc": "创意写作提示，激发写作灵感",
            "icon": "🎨",
            "color": "card-green"
        },
    ]
    
    feature_cols = st.columns(3)
    for idx, feature in enumerate(features):
        with feature_cols[idx % 3]:
            st.markdown(f"""
            <div class="feature-card {feature['color']}">
                <div style="font-size: 2.5rem; margin-bottom: 15px;">{feature['icon']}</div>
                <div class="card-title">{feature['title']}</div>
                <div class="card-desc">{feature['desc']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # 使用统计
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("## 📈 学习数据中心")
    
    stat_cols = st.columns(4)
    
    with stat_cols[0]:
        writing_count = len(st.session_state.writing_history)
        st.metric("📝 写作作品", writing_count, "篇")
    
    with stat_cols[1]:
        eval_count = len(st.session_state.evaluation_history)
        st.metric("⭐ 评价记录", eval_count, "次")
    
    with stat_cols[2]:
        draft_count = len(st.session_state.writing_drafts)
        st.metric("💾 保存草稿", draft_count, "个")
    
    with stat_cols[3]:
        if OFFLINE_MODE:
            st.metric("🤖 AI状态", "离线", "需配置")
        else:
            st.metric("🤖 AI状态", "在线", "已连接")

# ==================== 写作工坊页面 ====================
elif st.session_state.page == 'writing':
    # 标题区域
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
                st.success("✅ 草稿已保存！")
        
        # 查看范文
        if st.button("📖 参考范文", use_container_width=True, key="view_example"):
            if writing_topic:
                with st.spinner("🤖 AI正在生成范文..."):
                    example = EnhancedAIAssistant.recommend_sentences_for_topic(writing_topic, writing_grade)
                    st.markdown("### 📖 写作参考")
                    st.markdown(f'<div class="content-box-enhanced">{example}</div>', unsafe_allow_html=True)
            else:
                st.warning("请输入主题")
    
    # 操作按钮区域
    st.markdown("<br>", unsafe_allow_html=True)
    
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    
    with btn_col1:
        if st.button("💡 AI详细建议", use_container_width=True, type="primary", key="ai_suggest"):
            if writing_content and writing_topic:
                with st.spinner("🤖 AI正在深度分析你的作文..."):
                    suggestions = EnhancedAIAssistant.provide_detailed_writing_suggestions(
                        writing_topic, writing_grade, writing_content
                    )
                    
                    # 显示详细的AI建议
                    st.markdown("""
                    <div class="ai-suggestion-card">
                        <div class="ai-suggestion-header">
                            <span>🤖</span> AI智能写作分析报告
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f'<div class="content-box-enhanced">{suggestions}</div>', unsafe_allow_html=True)
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

# ==================== 词汇助手页面 ====================
elif st.session_state.page == 'vocabulary':
    st.markdown("""
    <div class="main-title-wrapper">
        <h1 class="main-title">📖 词汇魔法助手</h1>
        <h2 class="main-subtitle">丰富词汇，让表达更精彩 ✨</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # 标签页
    tab1, tab2 = st.tabs(["🔍 智能搜索", "📚 主题分类"])
    
    with tab1:
        st.markdown("### 🔍 智能词汇搜索")
        
        search_topic = st.text_input(
            "输入你的写作主题",
            placeholder="例如：My Favorite Season, School Life, Family...",
            key="vocab_search"
        )
        
        search_grade = st.selectbox(
            "选择年级",
            ["Grade 1-2", "Grade 3-4", "Grade 5-6", "Grade 7-8"],
            index=1,
            key="vocab_grade"
        )
        
        if st.button("🔍 智能搜索词汇", type="primary", use_container_width=True, key="search_vocab"):
            if search_topic:
                with st.spinner("🤖 AI正在智能推荐词汇..."):
                    try:
                        recommendation = EnhancedAIAssistant.recommend_vocabulary_for_topic(search_topic, search_grade)
                        st.markdown(f'<div class="content-box-enhanced">{recommendation}</div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"搜索失败：{str(e)[:100]}")
                        st.info("正在使用本地词汇库...")
                        # 显示本地备用
                        st.markdown(f'<div class="content-box-enhanced">主题"{search_topic}"的词汇推荐正在准备中...</div>', unsafe_allow_html=True)
            else:
                st.warning("请输入写作主题")
    
    with tab2:
        st.markdown("### 📚 主题词汇库")
        
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

# ==================== 句型助手页面 ====================
elif st.session_state.page == 'sentences':
    st.markdown("""
    <div class="main-title-wrapper">
        <h1 class="main-title">🔤 句型魔法宝典</h1>
        <h2 class="main-subtitle">掌握核心句型，写作更流畅 ✨</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # 标签页
    tab1, tab2 = st.tabs(["🔍 智能搜索", "📖 句型宝库"])
    
    with tab1:
        st.markdown("### 🔍 智能句型搜索")
        
        search_topic = st.text_input(
            "输入你的写作主题",
            placeholder="例如：My Daily Life, Hobbies, Dreams...",
            key="sentence_search"
        )
        
        search_grade = st.selectbox(
            "选择年级",
            ["Grade 1-2", "Grade 3-4", "Grade 5-6", "Grade 7-8"],
            index=1,
            key="sentence_grade"
        )
        
        if st.button("🔍 智能搜索句型", type="primary", use_container_width=True, key="search_sentences"):
            if search_topic:
                with st.spinner("🤖 AI正在智能推荐句型..."):
                    try:
                        recommendation = EnhancedAIAssistant.recommend_sentences_for_topic(search_topic, search_grade)
                        st.markdown(f'<div class="content-box-enhanced">{recommendation}</div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"搜索失败：{str(e)[:100]}")
                        st.info("正在使用本地句型库...")
                        # 显示本地备用
                        st.markdown(f'<div class="content-box-enhanced">主题"{search_topic}"的句型推荐正在准备中...</div>', unsafe_allow_html=True)
            else:
                st.warning("请输入写作主题")

# ==================== 作品评价页面 ====================
elif st.session_state.page == 'evaluate':
    st.markdown("""
    <div class="main-title-wrapper">
        <h1 class="main-title">⭐ 智能作品评价</h1>
        <h2 class="main-subtitle">专业评价，个性化指导 ✨</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # 这里保持原来的评价逻辑，但可以调用增强版建议

# ==================== 成长记录页面 ====================
elif st.session_state.page == 'progress':
    st.markdown("""
    <div class="main-title-wrapper">
        <h1 class="main-title">📊 成长轨迹记录</h1>
        <h2 class="main-subtitle">记录进步，见证成长 ✨</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # 这里保持原来的成长记录逻辑

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
            © 2024 英思织网 | 让写作变得更有趣！ ✨
        </p>
    </div>
    """, unsafe_allow_html=True)

with footer_cols[1]:
    if st.button("🏠 返回首页", use_container_width=True, key="footer_home"):
        st.session_state.page = "home"
        st.rerun()

with footer_cols[2]:
    st.caption("🚀 增强版 v4.0")

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
                <li>📚 主题词汇智能推荐</li>
                <li>🔤 个性化句型推荐</li>
                <li>⭐ 智能作文评价</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📝 配置方法")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.code("""
# 方法1：本地开发
1. 创建文件夹：.streamlit
2. 创建文件：secrets.toml
3. 添加内容：
DEEPSEEK_API_KEY="sk-a9b0d92a0d474ca6acd0ceb24360fef8"
            """)
        
        with col2:
            st.code("""
# 方法2：部署使用
1. Streamlit Cloud：
   - App Settings → Secrets
   - 添加：DEEPSEEK_API_KEY

2. 其他平台：
   - 设置环境变量
   - DEEPSEEK_API_KEY="sk-a9b0d92a0d474ca6acd0ceb24360fef8"
            """)
        
        st.markdown("### 🔑 获取API密钥")
        st.write("1. 访问 [DeepSeek官网](https://www.deepseek.com/)")
        st.write("2. 注册/登录账号")
        st.write("3. 进入API管理页面")
        st.write("4. 创建新的API密钥（目前免费）")
        
        if st.button("🔄 我已配置，重新检查", key="recheck_api"):
            st.rerun()

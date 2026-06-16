import streamlit as st
import google.generativeai as genai

# 1. 화면 기본 설정
st.set_page_config(page_title="냉파 AI 셰프", page_icon="🍳", layout="centered")

# 2. API 키 설정 (Streamlit 비밀 금고에서 안전하게 가져오기)
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

# 3. 메인 타이틀
st.title("🍳 맞춤형 냉파 AI 셰프 & 레시피 상담소")
st.markdown("냉장고 재료로 레시피를 추천받고, 궁금한 점은 아래 채팅창에서 바로 셰프에게 물어보세요!")
st.markdown("---")

# === 🧠 핵심: 세션 상태(메모리) 초기화 ===
if "recipe" not in st.session_state:
    st.session_state.recipe = None
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
# ✨ 추가: 유튜브 검색용 키워드 저장을 위한 세션
if "search_query" not in st.session_state:
    st.session_state.search_query = ""

# 4. 입력 영역
col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("🛒 남은 재료 입력")
    user_ingredients = st.text_input("어떤 재료가 있나요?", placeholder="예: 삼겹살, 신김치, 대파, 두부")
with col2:
    st.subheader("🔥 요리 스타일")
    cooking_style = st.selectbox("어떤 스타일을 원하시나요?", ["초간단 자취생 요리", "건강한 다이어트식", "매콤한 술안주", "든든한 밥도둑"])

st.markdown("---")

_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    submit_button = st.button("✨ 추천 레시피 탐색 시작", use_container_width=True)

# 5. 레시피 생성 로직
if submit_button:
    if user_ingredients:
        with st.spinner(f"AI 셰프가 '{cooking_style}' 레시피를 고민 중입니다..."):
            try:
                # 최신 모델명 적용
                model = genai.GenerativeModel('gemini-3.5-flash')
                
                chat = model.start_chat(history=[])
                
                prompt = f"""
                너는 대한민국 백종원 스타일의 대중적이고 검증된 요리 전문가야. 
                사용자가 제시한 재료 [{user_ingredients}]를 바탕으로, 반드시 [{cooking_style}] 스타일에 어울리는 현실적인 레시피를 추천해줘.
                절대로 세상에 없는 괴식이나 실험적인 요리를 창작하면 안 돼.
                
                특히 주요 타겟층인 20대 대학생과 자취생의 라이프스타일에 맞춰서, 추천한 요리와 환상의 궁합을 자랑하는 '편의점 주류 가성비 조합' 또는 '찰떡궁합 음료(예: 매운 요리엔 쿨피스 등)'를 센스 있게 한 줄 덧붙여서 추천해줘.
                
                [출력 형식]
                - 요리 이름: 
                - 추천 이유: 
                - 🍶 찰떡궁합 편의점 주류/음료 페어링: 
                - 필요한 추가 기본 양념: 
                - 조리 순서: 
                """
                
                response = chat.send_message(prompt)
                
                st.session_state.recipe = response.text
                st.session_state.chat_session = chat
                st.session_state.chat_history = [] 
                
                # ✨ 추가: 나중에 유튜브 버튼에서 쓸 수 있도록 입력한 재료를 메모리에 저장
                st.session_state.search_query = user_ingredients
                
            except Exception as e:
                st.error(f"에러가 발생했습니다: {e}")
    else:
        st.warning("요리할 재료를 최소 한 개 이상 입력해 주세요!")

# 6. 결과 출력 및 💬 채팅 UI 영역
if st.session_state.recipe:
    st.success("🎉 완벽한 레시피를 찾았습니다!")
    with st.container():
        st.info(st.session_state.recipe)
        
        # ✨ 핵심 업그레이드: 유튜브 영상 검색 버튼 추가
        # 사용자가 입력한 재료 + '요리 레시피'라는 단어를 조합해 유튜브 검색 링크 자동 생성
        youtube_url = f"https://www.youtube.com/results?search_query={st.session_state.search_query} 요리 레시피"
        st.link_button("📺 이 요리 유튜브 영상으로 확인하기", youtube_url, use_container_width=True)
    
    st.markdown("---")
    st.subheader("💬 AI 셰프에게 추가 질문하기")
    st.caption("레시피에 대해 궁금한 점이나, '고기 대신 참치를 넣어도 돼?' 같은 응용 질문을 던져보세요!")
    
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    if user_question := st.chat_input("질문을 입력하세요..."):
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)
            
        with st.chat_message("ai"):
            with st.spinner("AI 셰프가 답변을 작성 중입니다..."):
                ai_response = st.session_state.chat_session.send_message(user_question)
                st.markdown(ai_response.text)
        
        st.session_state.chat_history.append({"role": "ai", "content": ai_response.text})

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
# 웹페이지 특성상 버튼을 누를 때마다 화면이 초기화되는 것을 막기 위해, 
# 레시피 결과와 채팅 기록을 컴퓨터 메모리에 안전하게 저장해두는 공간입니다.
if "recipe" not in st.session_state:
    st.session_state.recipe = None
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 4. 입력 영역 (기존과 동일)
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
                # 모델 설정
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # 일반 생성이 아닌 '채팅 모드(start_chat)'로 AI를 실행하여 문맥을 기억하게 만듭니다.
                chat = model.start_chat(history=[])
                
                prompt = f"""
                너는 대중적이고 검증된 한식 요리 전문가야. 
                사용자가 제시한 재료 [{user_ingredients}]를 바탕으로, 반드시 [{cooking_style}] 스타일에 어울리는 레시피를 추천해줘.
                
                [출력 형식]
                - 요리 이름: 
                - 추천 이유: 
                - 필요한 추가 기본 양념: 
                - 조리 순서: 
                """
                
                # AI에게 질문을 던지고 답변 받기
                response = chat.send_message(prompt)
                
                # 방금 나온 레시피와 채팅 세션을 메모리에 저장!
                st.session_state.recipe = response.text
                st.session_state.chat_session = chat
                st.session_state.chat_history = [] # 새 레시피를 뽑으면 예전 채팅 기록은 초기화
                
            except Exception as e:
                st.error(f"에러가 발생했습니다: {e}")
    else:
        st.warning("요리할 재료를 최소 한 개 이상 입력해 주세요!")

# 6. === 결과 출력 및 💬 채팅 UI 영역 ===
# 메모리에 저장된 레시피가 있다면 화면에 항상 띄워줍니다.
if st.session_state.recipe:
    st.success("🎉 완벽한 레시피를 찾았습니다!")
    with st.container():
        st.info(st.session_state.recipe)
    
    st.markdown("---")
    st.subheader("💬 AI 셰프에게 추가 질문하기")
    st.caption("레시피에 대해 궁금한 점이나, '고기 대신 참치를 넣어도 돼?' 같은 응용 질문을 던져보세요!")
    
    # 저장된 이전 채팅 말풍선들을 순서대로 화면에 그리기
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # 사용자 채팅 입력창 (제일 하단에 고정됨)
    if user_question := st.chat_input("질문을 입력하세요..."):
        # 1. 내 질문을 화면에 띄우고 메모리에 저장
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)
            
        # 2. AI의 답변 받아오기 (chat_session을 쓰기 때문에 방금 추천해준 레시피가 뭔지 알고 있습니다!)
        with st.chat_message("ai"):
            with st.spinner("AI 셰프가 답변을 작성 중입니다..."):
                ai_response = st.session_state.chat_session.send_message(user_question)
                st.markdown(ai_response.text)
        
        # 3. AI 답변을 메모리에 저장
        st.session_state.chat_history.append({"role": "ai", "content": ai_response.text})

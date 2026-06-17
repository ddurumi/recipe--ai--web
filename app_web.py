import streamlit as st
import google.generativeai as genai

# 1. 화면 기본 설정
st.set_page_config(page_title="냉파 AI 셰프", page_icon="🍳", layout="centered")

# 2. API 키 설정
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

# 3. 메인 타이틀
st.title("🍳 맞춤형 냉파 AI 셰프 & 레시피 상담소")
st.markdown("냉장고 재료로 레시피를 추천받고, 궁금한 점은 아래 채팅창에서 바로 셰프에게 물어보세요!")
st.markdown("---")

# 세션 상태 초기화 (임시 메모리 창고)
if "recipe" not in st.session_state:
    st.session_state.recipe = None
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "search_query" not in st.session_state:
    st.session_state.search_query = ""
# 📝 구글 시트 대신 세션 메모리에 일기를 누적 저장합니다.
if "recipe_diary_log" not in st.session_state:
    st.session_state.recipe_diary_log = []

# 입력 영역
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

# 레시피 생성
if submit_button:
    if user_ingredients:
        with st.spinner(f"AI 셰프가 '{cooking_style}' 레시피를 고민 중입니다..."):
            try:
                model = genai.GenerativeModel("gemini-2.5-flash")
                chat = model.start_chat(history=[])
                prompt = f"""
                너는 대한민국 백종원 스타일의 대중적이고 검증된 요리 전문가야.
                사용자가 제시한 재료 [{user_ingredients}]를 바탕으로 반드시 [{cooking_style}] 스타일에 어울리는 현실적인 레시피를 추천해줘.
                절대로 세상에 없는 괴식이나 실험적인 요리를 창작하면 안 돼.
                특히 주요 타겟층인 20대 대학생과 자취생의 라이프스타일에 맞춰서, 추천한 요리와 환상의 궁합을 자랑하는 편의점 음료 또는 주류 조합도 추천해줘.
                
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

                dish_name = user_ingredients
                for line in response.text.split("\n"):
                    if "요리 이름:" in line:
                        dish_name = line.split("요리 이름:")[1].replace("*", "").strip()
                        break
                st.session_state.search_query = dish_name
            except Exception as e:
                st.error(f"에러가 발생했습니다: {e}")
    else:
        st.warning("요리할 재료를 최소 한 개 이상 입력해 주세요!")

# 결과 출력
if st.session_state.recipe:
    st.success("🎉 완벽한 레시피를 찾았습니다!")
    with st.container():
        st.info(st.session_state.recipe)
        youtube_url = f"https://www.youtube.com/results?search_query={st.session_state.search_query} 만들기"
        st.link_button(f"📺 '{st.session_state.search_query}' 유튜브 영상으로 확인하기", youtube_url, use_container_width=True)

    st.markdown("---")
    st.subheader("💬 AI 셰프에게 추가 질문하기")
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

# 요리 기록장 (에러 없는 세션 저장 방식으로 롤백)
st.markdown("---")
st.subheader("📝 나만의 요리 기록장")
st.caption("오늘 추천받아 만든 요리를 기록해 보세요! (현재 데모 버전으로 브라우저를 새로고침하면 초기화됩니다)")

col_date, col_star = st.columns(2)
with col_date:
    selected_date = st.date_input("📅 요리한 날짜 선택")
with col_star:
    star_rating = st.selectbox("⭐ 요리 만족도 별점", ["⭐⭐⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐", "⭐⭐", "⭐"])

user_review = st.text_input("✍️ 맛 평가 및 한줄평을 적어주세요", placeholder="예: 진짜 백종원 맛이 나요! 최고최고")

if st.button("💾 요리 기록 저장", use_container_width=True):
    current_dish = st.session_state.search_query if st.session_state.search_query else "추천 요리"
    # 리스트에 딕셔너리 형태로 일기를 차곡차곡 임시 저장
    st.session_state.recipe_diary_log.append({
        "date": str(selected_date),
        "dish": current_dish,
        "star": star_rating,
        "review": user_review
    })
    st.success(f"🎉 '{current_dish}' 기록이 임시 저장되었습니다!")

# 히스토리 실시간 출력
if st.session_state.recipe_diary_log:
    st.markdown("---")
    st.markdown("### 📚 나의 누적 요리 히스토리")
    # 최신 순으로 정렬하여 출력
    for row in reversed(st.session_state.recipe_diary_log):
        st.markdown(f"**[{row['date']}] {row['dish']}** | {row['star']}")
        st.markdown(f"> {row['review']}")
        st.markdown("<br>", unsafe_allow_html=True)

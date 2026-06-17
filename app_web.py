import streamlit as st
import pandas as pd
from openai import OpenAI
import os

# 1. 화면 기본 설정
st.set_page_config(page_title="냉파 AI 셰프", page_icon="🍳", layout="centered")

# 2. OpenAI API 키 설정 (제미나이에서 GPT로 변경)
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=OPENAI_API_KEY)

# CSV 기반 저장소
CSV_FILE = "recipe_log.csv"

if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
else:
    df = pd.DataFrame(columns=["날짜", "요리이름", "별점", "한줄평"])

# 3. 메인 타이틀
st.title("🍳 맞춤형 냉파 AI 셰프 & 레시피 상담소")
st.markdown("냉장고 재료로 레시피를 추천받고, 궁금한 점은 아래 채팅창에서 바로 셰프에게 물어보세요!")
st.markdown("---")

# 세션 상태 초기화
if "recipe" not in st.session_state:
    st.session_state.recipe = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "search_query" not in st.session_state:
    st.session_state.search_query = ""

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

# 레시피 생성 (OpenAI 로직 적용)
if submit_button:
    if user_ingredients:
        with st.spinner(f"AI 셰프가 '{cooking_style}' 레시피를 고민 중입니다..."):
            try:
                prompt = f"""
                너는 대한민국 백종원 스타일의 대중적이고 검증된 요리 전문가야.
                사용자가 제시한 재료 [{user_ingredients}]를 바탕으로
                반드시 [{cooking_style}] 스타일에 어울리는 현실적인 레시피를 추천해줘.
                절대로 세상에 없는 괴식이나 실험적인 요리를 창작하면 안 돼.

                [중요 지시사항]
                - 요리 초보자도 완벽하게 따라 할 수 있도록 '조리 순서'를 아주아주 상세하고 길게 설명해 줘. (예: 불 조절, 볶는 시간 등 구체적으로)
                - '추천 이유'도 군침이 싹 돌게 아주 풍부하고 맛깔나게 3줄 이상 작성해 줘.
                - 요리 이름에는 입력된 재료명을 구구절절 나열하지 마라. 식당 메뉴판에 등장하는 '제육볶음', '두부김치', '부대찌개'처럼 **대중적이고 간결한 실제 요리 이름 딱 하나**만 지정해 줘. (예: 삼겹살 김치 대파 두부 볶음 (X) -> 두부김치 (O))

               
                - 요리 초보자도 완벽하게 따라 할 수 있도록 '조리 순서'를 아주 상세하고 길게 설명해 줘. 
                - '추천 이유'도 군침이 싹 돌게 아주 풍부하고 맛깔나게 3줄 이상 작성해 줘.
                - 🚨 육회, 생선회처럼 생으로 먹는 재료가 입력되면 절대 가열하거나 볶지 말고 본연의 맛을 살려줘.
                - 🚨 재료의 상식을 벗어나는 괴식이나 파괴적인 조리법(예: 육회 볶기, 과일 끓이기 등)은 절대 금지!
                
                특히 주요 타겟층인 20대 대학생과 자취생의 라이프스타일에 맞춰서,
                추천한 요리와 환상의 궁합을 자랑하는 편의점 음료 또는 주류 조합도 추천해줘.

                [출력 형식]
                - 요리 이름: (여기에 식당 메뉴판 스타일의 간결한 이름만 적을 것)
                - 추천 이유: (아주 상세하게)
                - 🍶 찰떡궁합 편의점 주류/음료 페어링:
                - 필요한 추가 기본 양념: (정확한 스푼 계량 포함)
                - 조리 순서: (1번, 2번... 단계별로 아주 구체적이고 길게 설명)
                """

                # GPT-3.5-turbo 모델 사용
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )

                st.session_state.recipe = response.choices[0].message.content
                
                # 채팅 히스토리에 첫 레시피 저장
                st.session_state.chat_history = [
                    {"role": "assistant", "content": st.session_state.recipe}
                ]

                dish_name = user_ingredients
                for line in st.session_state.recipe.split("\n"):
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

    # 추가 질문 대화 내역 출력 (첫 레시피 출력은 위에서 했으므로 제외)
    for msg in st.session_state.chat_history[1:]:
        role = "ai" if msg["role"] == "assistant" else "user"
        with st.chat_message(role):
            st.markdown(msg["content"])

    if user_question := st.chat_input("질문을 입력하세요..."):
        # 사용자 질문 화면 표시 및 메모리 저장
        with st.chat_message("user"):
            st.markdown(user_question)
        st.session_state.chat_history.append({"role": "user", "content": user_question})

        # OpenAI 답변 요청
        with st.chat_message("ai"):
            with st.spinner("AI 셰프가 답변을 작성 중입니다..."):
                chat_response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=st.session_state.chat_history
                )
                bot_reply = chat_response.choices[0].message.content
                st.markdown(bot_reply)

        st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})

# 요리 기록장
st.markdown("---")
st.subheader("📝 나만의 요리 기록장")
st.caption("오늘 추천받아 만든 요리를 기록해 보세요!")

col_date, col_star = st.columns(2)

with col_date:
    selected_date = st.date_input("📅 요리한 날짜 선택")

with col_star:
    star_rating = st.selectbox("⭐ 요리 만족도 별점", ["⭐⭐⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐", "⭐⭐", "⭐"])

user_review = st.text_input("✍️ 맛 평가 및 한줄평을 적어주세요", placeholder="예: 진짜 백종원 맛이 나요! 최고최고")

if st.button("💾 요리 기록 저장", use_container_width=True):
    current_dish = st.session_state.search_query if st.session_state.search_query else "추천 요리"

    try:
        new_data = {
            "날짜": str(selected_date),
            "요리이름": current_dish,
            "별점": star_rating,
            "한줄평": user_review
        }
        updated_df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        updated_df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")
        st.success(f"🎉 '{current_dish}' 기록이 저장되었습니다!")
        st.rerun()
    except Exception as e:
        st.error(f"저장 실패: {e}")

# 히스토리 출력
if os.path.exists(CSV_FILE):
    history_df = pd.read_csv(CSV_FILE)
    if not history_df.empty:
        st.markdown("---")
        st.markdown("### 📚 나의 누적 요리 히스토리")
        for _, row in history_df.iloc[::-1].iterrows():
            st.markdown(f"**[{row['날짜']}] {row['요리이름']}** | {row['별점']}")
            st.markdown(f"> {row['한줄평']}")
            st.markdown("<br>", unsafe_allow_html=True)

import streamlit as st
import pandas as pd
from openai import OpenAI
import os

# 1. 화면 기본 설정
st.set_page_config(page_title="냉파 AI 셰프", page_icon="🍳", layout="centered")

# 2. OpenAI API 키 설정
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

if "last_processed_voice" not in st.session_state:
    st.session_state.last_processed_voice = None

# 4. 입력 영역
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🛒 남은 재료 입력")
    user_ingredients = st.text_input("어떤 재료가 있나요?", placeholder="예: 삼겹살, 신김치, 대파, 두부")

with col2:
    st.subheader("🔥 요리 스타일")
    cooking_style = st.selectbox("어떤 스타일을 원하시나요?", ["초간단 자취생 요리", "건강한 다이어트식", "매콤한 술안주", "든든한 밥도둑"])

# 🚫 알레르기 및 기피 재료 입력창
st.subheader("🚫 알레르기 및 기피 재료 (선택)")
user_allergies = st.text_input("절대 들어가면 안 되는 재료가 있다면 적어주세요.", placeholder="예: 오이, 땅콩, 갑각류 등")

st.markdown("---")

_, btn_col, _ = st.columns([1, 2, 1])

with btn_col:
    submit_button = st.button("✨ 추천 레시피 탐색 시작", use_container_width=True)

# 5. 레시피 생성 (OpenAI 로직 적용)
if submit_button:
    if user_ingredients:
        with st.spinner(f"AI 셰프가 '{cooking_style}' 레시피를 고민 중입니다..."):
            try:
                # 알레르기 경고 블록
                allergy_block = ""
                if user_allergies:
                    allergy_block = f"""
                [🚫 초강력 알레르기/기피 재료 절대 금지 경고 🚫]
                - 사용자가 절대 먹으면 안 되는 재료: [{user_allergies}]
                - 위 재료는 주재료, 부재료, 소스, 육수, 가니쉬 등 요리의 '모든 과정'에서 100% 완벽하게 배제해라.
                - 만약 저 재료가 필수로 들어가는 요리라면, 아예 다른 메뉴를 추천하거나 안전한 대체 식재료를 사용해라.
                - 네가 출력하는 레시피 텍스트 안에 '{user_allergies}'라는 단어가 식재료로서 단 한 번이라도 등장하면 안 된다.
                    """

                prompt = f"""
                너는 대한민국 백종원 스타일의 대중적이고 검증된 요리 전문가야.
                {allergy_block}

                사용자가 제시한 재료 [{user_ingredients}]를 바탕으로
                반드시 [{cooking_style}] 스타일에 어울리는 현실적인 레시피를 추천해줘.
                절대로 세상에 없는 괴식이나 실험적인 요리를 창작하면 안 돼.

                [가장 중요한 규칙: 실존하는 레시피 제공]
                1. 절대로 새로운 요리를 창작하거나 실험적인 조합을 만들지 마라.
                2. 네가 제안할 요리는 반드시 네이버 블로그, 만개의 레시피, 또는 백종원 요리 유튜브에 실제 수없이 검색되고 존재하는 대중적인 표준 레시피여야만 한다.
                3. 사용자가 제시한 재료 중 '주재료'가 될 만한 것을 고르고, 그 주재료로 만들 수 있는 가장 대표적인 실존 메뉴를 선정해라. 
                4. 제시된 재료 중 해당 요리의 정석 레시피와 도저히 어울리지 않는 재료가 있다면, 요리에 억지로 넣지 말고 과감히 제외해라.
                
                [중요 지시사항]
                - 요리 초보자도 완벽하게 따라 할 수 있도록 '조리 순서'를 아주아주 상세하고 길게 설명해 줘. (예: 불 조절, 볶는 시간 등 구체적으로)
                - '추천 이유'도 군침이 싹 돌게 아주 풍부하고 맛깔나게 3줄 이상 작성해 줘.
                - 요리 이름에는 입력된 재료명을 구구절절 나열하지 마라. 식당 메뉴판에 등장하는 '제육볶음', '두부김치', '부대찌개'처럼 **대중적이고 간결한 실제 요리 이름 딱 하나**만 지정해 줘.
                - 🚨 육회, 생선회처럼 생으로 먹는 재료가 입력되면 절대 가열하거나 볶지 말고 본연의 맛을 살려줘.
                - 🚨 재료의 상식을 벗어나는 괴식이나 파괴적인 조리법(예: 육회 볶기, 과일 끓이기 등)은 절대 금지!
                
                특히 주요 타겟층인 20대 대학생과 자취생의 라이프스타일에 맞춰서,
                추천한 요리와 환상의 궁합을 자랑하는 편의점 음료 또는 주류 조합도 추천해줘.

                [출력 형식]
                - 요리 이름: (여기에 식당 메뉴판 스타일의 간결한 이름만 적을 것)
                - 예상 영양성분: (칼로리: XXXkcal | 탄수화물: XXg | 단백질: XXg | 지방: XXg 형식으로 기호문자와 콜론을 맞춰 반드시 한 줄로만 작성할 것. 수치는 현실적인 예상치를 계산해서 적어줄 것)
                - 추천 이유: (아주 상세하게)
                - 🍶 찰떡궁합 편의점 주류/음료 페어링:
                - 필요한 추가 기본 양념: (정확한 스푼 계량 포함)
                - 조리 순서: (1번, 2번... 단계별로 아주 구체적이고 길게 설명)
                """

                # 최신 고성능 gpt-4o-mini 모델 사용
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )

                st.session_state.recipe = response.choices[0].message.content
                
                # 채팅 히스토리에 첫 레시피 저장
                st.session_state.chat_history = [
                    {"role": "assistant", "content": st.session_state.recipe}
                ]

                # 간결해진 요리 이름을 찾아서 검색 쿼리로 지정
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

# 6. 결과 출력
if st.session_state.recipe:
    st.success("🎉 완벽한 레시피를 찾았습니다!")
    
    # 📊 영양성분 텍스트 파싱 처리
    num_kcal, num_carbo, num_protein, num_fat = "계산 불가", "계산 불가", "계산 불가", "계산 불가"
    for line in st.session_state.recipe.split("\n"):
        if "예상 영양성분:" in line:
            try:
                raw_content = line.split("예상 영양성분:")[1]
                sub_parts = raw_content.split("|")
                for part in sub_parts:
                    if "칼로리" in part: num_kcal = part.split(":")[1].strip()
                    elif "탄수화물" in part: num_carbo = part.split(":")[1].strip()
                    elif "단백질" in part: num_protein = part.split(":")[1].strip()
                    elif "지방" in part: num_fat = part.split(":")[1].strip()
            except:
                pass
            break

    # 📊 시각적인 영양성분 대시보드 배치
    st.markdown("### 📊 추천 요리 예상 영양성분 대시보드")
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    metric_col1.metric("🔥 칼로리", num_kcal)
    metric_col2.metric("🍞 탄수화물", num_carbo)
    metric_col3.metric("🥩 단백질", num_protein)
    metric_col4.metric("🥑 지방", num_fat)
    st.markdown("---")
    
    with st.container():
        st.info(st.session_state.recipe)
        
        # 🔊 메인 레시피 음성 듣기 기능
        if st.button("🔊 AI 셰프 목소리로 레시피 듣기", use_container_width=True):
            with st.spinner("목소리를 생성하고 있습니다..."):
                try:
                    speech_response = client.audio.speech.create(
                        model="tts-1",
                        voice="alloy",
                        input=st.session_state.recipe
                    )
                    st.audio(speech_response.content, format="audio/mp3")
                except Exception as e:
                    st.error(f"음성 생성 실패: {e}")

        st.markdown("<br>", unsafe_allow_html=True)

        # 하단 기능 버튼 레이아웃
        col_yt, col_dl = st.columns(2)
        with col_yt:
            youtube_url = f"https://www.youtube.com/results?search_query={st.session_state.search_query} 만들기"
            st.link_button(f"📺 유튜브 영상 검색", youtube_url, use_container_width=True)
        with col_dl:
            st.download_button(
                label="💾 이 레시피 파일로 저장하기 (.txt)",
                data=st.session_state.recipe,
                file_name=f"{st.session_state.search_query}_레시피.txt",
                mime="text/plain",
                use_container_width=True
            )

    st.markdown("---")
    st.subheader("💬 AI 셰프와 대화하기 (음성/텍스트 모두 가능)")

    # 추가 질문 대화 내역 출력
    for msg in st.session_state.chat_history[1:]:
        role = "ai" if msg["role"] == "assistant" else "user"
        with st.chat_message(role):
            st.markdown(msg["content"])

    # 🎙️ [핵심 추가] 마이크 음성 입력 위젯 배치
    voice_file = st.audio_input("🎙️ 말로 질문하기 (마이크 버튼을 누르고 말씀하세요)")
    
    active_question = None

    # 새로운 음성 녹음 데이터가 들어왔을 때 Whisper API로 텍스트화
    if voice_file and voice_file != st.session_state.last_processed_voice:
        st.session_state.last_processed_voice = voice_file
        with st.spinner("사용자님의 음성을 인식하는 중입니다..."):
            try:
                transcription = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=voice_file
                )
                active_question = transcription.text
            except Exception as e:
                st.error(f"음성 인식에 실패했습니다: {e}")
    else:
        # 음성 입력이 없을 때는 기존의 텍스트 입력창 활성화
        active_question = st.chat_input("또는 여기에 질문을 타이핑하세요...")

    # 질문 처리 로직 (음성이든 텍스트든 질문이 활성화되면 작동)
    if active_question:
        with st.chat_message("user"):
            st.markdown(active_question)
        st.session_state.chat_history.append({"role": "user", "content": active_question})

        with st.chat_message("ai"):
            with st.spinner("AI 셰프가 답변을 작성 중입니다..."):
                chat_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=st.session_state.chat_history
                )
                bot_reply = chat_response.choices[0].message.content
                st.markdown(bot_reply)
                
                # 답변을 자동으로 음성 변환하여 플레이어 출력
                try:
                    chat_speech = client.audio.speech.create(
                        model="tts-1",
                        voice="alloy",
                        input=bot_reply
                    )
                    st.audio(chat_speech.content, format="audio/mp3")
                except:
                    pass

        st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})

# 7. 요리 기록장
st.markdown("---")
st.subheader("📝 나만의 요리 기록장")
st.caption("오늘 추천받아 만든 요리를 기록해 보세요!")

default_dish = st.session_state.search_query if st.session_state.search_query else ""
record_dish_name = st.text_input("🍲 요리 이름", value=default_dish, placeholder="예: 대패삼겹 두부김치")

col_date, col_star = st.columns(2)

with col_date:
    selected_date = st.date_input("📅 요리한 날짜 선택")

with col_star:
    star_rating = st.selectbox("⭐ 요리 만족도 별점", ["⭐⭐⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐", "⭐⭐", "⭐"])

user_review = st.text_input("✍️ 맛 평가 및 한줄평을 적어주세요", placeholder="예: 진짜 백종원 맛이 나요! 최고최고")

if st.button("💾 요리 기록 저장", use_container_width=True):
    if not record_dish_name.strip():
        st.warning("요리 이름을 입력해 주세요!")
    else:
        try:
            new_data = {
                "날짜": str(selected_date),
                "요리이름": record_dish_name,
                "별점": star_rating,
                "한줄평": user_review
            }
            updated_df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            updated_df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")
            st.success(f"🎉 '{record_dish_name}' 기록이 저장되었습니다!")
            st.rerun()
        except Exception as e:
            st.error(f"저장 실패: {e}")

# 8. 히스토리 출력
if os.path.exists(CSV_FILE):
    history_df = pd.read_csv(CSV_FILE)
    if not history_df.empty:
        st.markdown("---")
        st.markdown("### 📚 나의 누적 요리 히스토리")
        for _, row in history_df.iloc[::-1].iterrows():
            st.markdown(f"**[{row['날짜']}] {row['요리이름']}** | {row['별점']}")
            st.markdown(f"> {row['한줄평']}")
            st.markdown("<br>", unsafe_allow_html=True)

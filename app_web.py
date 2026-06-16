import streamlit as st
import google.generativeai as genai

# 1. 화면 기본 설정 (브라우저 탭 이름과 넓은 레이아웃 설정)
st.set_page_config(page_title="냉파 AI 셰프", page_icon="🍳", layout="centered")

# 2. Gemini API 키 설정 (본인의 키를 넣어주세요)
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

# 3. 메인 타이틀 및 헤더 (상단 영역)
st.title("🍳 나만의 맞춤형 냉파 AI 셰프")
st.markdown("냉장고에 남은 재료를 입력하면, AI가 당신의 상황에 딱 맞는 **현실적인 레시피**를 추천합니다.")
st.markdown("---") # 시각적 구분을 위한 가로선

# 4. 입력 영역: 화면을 2개의 단(Column)으로 나누기
col1, col2 = st.columns([2, 1]) # 왼쪽이 조금 더 넓게 배치됩니다.

with col1:
    st.subheader("🛒 남은 재료 입력")
    user_ingredients = st.text_input("어떤 재료가 있나요?", placeholder="예: 삼겹살, 신김치, 대파, 두부")

with col2:
    st.subheader("🔥 요리 스타일")
    # AI의 답변을 더 흥미롭게 만들어줄 옵션 UI 추가
    cooking_style = st.selectbox(
        "어떤 스타일을 원하시나요?", 
        ["초간단 자취생 요리", "건강한 다이어트식", "매콤한 술안주", "든든한 밥도둑"]
    )

st.markdown("---")

# 5. 실행 버튼 (중앙 배치 효과)
_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    # use_container_width=True 로 버튼을 꽉 차고 예쁘게 만듭니다.
    submit_button = st.button("✨ 추천 레시피 탐색 시작", use_container_width=True)

# 6. 결과 출력 영역
if submit_button:
    if user_ingredients:
        # AI가 생각하는 동안 예쁜 로딩 표시 띄우기
        with st.spinner(f"AI 셰프가 '{cooking_style}' 레시피를 고민 중입니다..."):
            try:
                # 모델 설정
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                # 사용자가 선택한 '요리 스타일'을 프롬프트에 추가로 반영!
                prompt = f"""
                너는 대중적이고 검증된 한식 요리 전문가야. 
                사용자가 제시한 재료 [{user_ingredients}]를 바탕으로, 
                반드시 [{cooking_style}] 스타일에 어울리는 레시피를 추천해줘.

                [엄격한 규칙]
                1. 절대로 존재하지 않는 창의적인 요리나 실험적인 괴식을 만들어내지 마십시오.
                2. 일반적인 가정집이나 식당에서 실제로 흔히 해 먹는 대중적인 레시피만 추천하십시오.
                3. 제시된 재료 외에 소금, 설탕, 간장, 식용유, 마늘 같은 '기본 양념 및 조미료'는 집에 있다고 가정해도 됩니다.
                4. 출력 형식은 아래 형식을 엄격히 따르십시오.

                [출력 형식]
                - 요리 이름: 
                - 추천 이유: 
                - 필요한 추가 기본 양념: 
                - 조리 순서: 
                """
                
                response = model.generate_content(prompt)
                
                # 결과 출력 UI (시각적으로 돋보이게 처리)
                st.success("🎉 완벽한 레시피를 찾았습니다!")
                with st.container():
                    # 사용자의 입력을 한 번 더 확인시켜주는 센스 있는 배치
                    st.markdown(f"> **✓ 선택한 재료:** {user_ingredients} | **✓ 스타일:** {cooking_style}")
                    # 파란색 정보 상자 안에 레시피 출력
                    st.info(response.text)
                
            except Exception as e:
                st.error(f"에러가 발생했습니다: {e}")
    else:
        st.warning("요리할 재료를 최소 한 개 이상 입력해 주세요!")
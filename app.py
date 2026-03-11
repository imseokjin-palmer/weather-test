import streamlit as st
import google.generativeai as genai
import random

# 1. 페이지 설정
st.set_page_config(page_title="여행 계획 AI 비서 서비스", page_icon="✈️")

# 2. 보안 정보 로드 및 AI 설정
try:
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('models/gemini-flash-latest')
except Exception as e:
    st.error(f"설정 불러오기 실패: {e}")

# 3. 세션 상태 초기화
if 'group' not in st.session_state:
    st.session_state.group = random.choice(["Positive", "Negative"])
    st.session_state.step = 'intro'  # 시작 단계를 'intro'로 설정
    st.session_state.chat_history = [] # 대화 기록 저장용

# --- [1페이지] 도입 안내 화면 ---
if st.session_state.step == 'intro':
    st.markdown("### 1 페이지")
    with st.container(border=True):
        st.write("")
        st.write("안녕하세요.")
        st.write("본 설문은 생성형 AI가 제공하는 정보의 표현 방식이 사용자 인식과 평가에 어떤 영향을 미치는지 알아보기 위한 연구입니다. 방금 경험하신 AI 서비스에 대해 느낀 점을 바탕으로 응답해 주시면 됩니다. 정답은 없으며, 솔직한 의견이 가장 중요합니다.")
        st.write("응답 내용은 연구 목적 외에는 사용되지 않으며, 모든 정보는 익명으로 처리됩니다.")
        st.write("참여해 주셔서 감사합니다.")
        st.write("")
        
        if st.button("시작하기", use_container_width=True):
            st.session_state.step = 'chat'
            st.rerun()

# --- [2페이지] AI 대화 화면 ---
elif st.session_state.step == 'chat':
    st.markdown("### 2 페이지")
    
    # 교수님 요청 프레이밍 메시지 (배경색으로 강조)
    if st.session_state.group == "Positive":
        st.success("✨ **AI에게 날씨 및 여행 정보를 물어보면 빠르게 필요한 정보를 얻을 수 있습니다.**")
    else:
        st.error("⚠️ **AI에게 날씨 및 여행 정보를 묻지 않으면 필요한 정보를 확인할 수 없습니다.**")

    with st.container(border=True):
        st.write("당신은 3박 4일 여행을 계획하고 있습니다.")
        st.write("여행지는 자유롭게 선택할 수 있으며, 일정·숙소·예산을 스스로 결정해야 합니다.")
        st.write("여행 준비 과정에서 다양한 정보를 탐색하고 비교하여 합리적인 선택을 내려야 하는 상황입니다.")
        st.write("이제 생성형 AI 챗봇과 함께 여행 계획을 수립해 보십시오.")
        st.write("")
        st.write("AI 챗봇은 여행 일정 구성, 예산 계획, 숙소 및 이동 수단 선택 등에 관한 정보를 제공합니다.")
        st.write("여행과 관련하여 자유롭게 질문하거나 계획을 요청할 수 있습니다.")
        st.write("충분히 대화를 진행하셨다고 판단되면 **“대화 종료”** 버튼을 눌러 주십시오.")
        st.write("이후 AI 서비스에 대한 설문이 진행됩니다.")
        st.write("")
        st.write(":blue[**여행에 대해서 물어보세요.**]")

        # 대화 내용 표시
        for chat in st.session_state.chat_history:
            with st.chat_message(chat["role"]):
                st.write(chat["content"])

        # 질문 입력창
        question = st.text_input("질문을 입력하세요", placeholder="예) 스위스 3박 4일 여행 일정 짜줘", label_visibility="collapsed")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("AI 답변듣기", use_container_width=True):
                if question:
                    # 프롬프트에 그룹 톤 반영
                    prompt = f"당신은 {st.session_state.group} 톤의 여행 전문가입니다. '{question}'에 대해 친절하게 답해주세요."
                    response = model.generate_content(prompt)
                    
                    # 대화 기록 저장
                    st.session_state.chat_history.append({"role": "user", "content": question})
                    st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                    st.rerun()
                else:
                    st.warning("질문을 입력해주세요.")
        
        with col2:
            if st.button("대화종료", use_container_width=True, type="primary"):
                if len(st.session_state.chat_history) > 0:
                    st.session_state.step = 'survey'
                    st.rerun()
                else:
                    st.warning("최소 한 번 이상 AI와 대화한 후 종료해 주세요.")

# --- [3단계] 설문 연결 화면 ---
elif st.session_state.step == 'survey':
    st.title("📋 서비스 만족도 조사")
    st.subheader("연구 데이터 수집을 위한 마지막 단계입니다.")
    
    # 구글 폼 주소 (기존 주소 유지)
    base_url = "https://docs.google.com/forms/d/e/1FAIpQLSdCiF4lzxN5NRaOWIrgLsW9Tphs99FmtS6mLXAlCEKs75udXg/viewform?entry.41790104="
    final_form_url = base_url + st.session_state.group
    
    st.info(f"시스템 확인이 완료되었습니다. 현재 할당된 그룹은 **{st.session_state.group}**입니다.")
    
    st.link_button("🚀 설문 참여하고 완료하기", final_form_url, use_container_width=True)
    
    if st.button("처음으로 돌아가기"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

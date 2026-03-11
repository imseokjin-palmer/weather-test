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
    st.session_state.step = 'intro'
    st.session_state.chat_history = []
    st.session_state.temp_input = "" # 임시 입력창 상태

# 질문 제출 함수 (입력창 비우기 포함)
def submit_question():
    user_input = st.session_state.widget_input
    if user_input:
        try:
            # 프롬프트 구성 및 답변 생성
            prompt = f"당신은 {st.session_state.group} 톤의 여행 전문가입니다. '{user_input}'에 대해 친절하게 답해주세요."
            response = model.generate_content(prompt)
            
            # 대화 기록 저장
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            st.session_state.chat_history.append({"role": "assistant", "content": response.text})
            
            # [핵심] 입력창 비우기
            st.session_state.widget_input = ""
        except Exception as e:
            st.error(f"AI 호출 오류: {e}")
    else:
        st.warning("질문을 입력해주세요.")

# --- [1페이지] 도입 안내 화면 ---
if st.session_state.step == 'intro':
    st.markdown("### 1 페이지")
    with st.container(border=True):
        st.write("안녕하세요.")
        st.write("본 연구는 AI 정보 제공 방식에 따른 사용자 인식을 알아보기 위한 연구입니다. 모든 정보는 익명으로 처리됩니다.")
        
        if st.button("시작하기", use_container_width=True):
            st.session_state.step = 'chat'
            st.rerun()

# --- [2페이지] AI 대화 화면 ---
elif st.session_state.step == 'chat':
    st.markdown("### 2 페이지")
    
    if st.session_state.group == "Positive":
        st.success("✨ **AI에게 날씨 및 여행 정보를 물어보면 빠르게 필요한 정보를 얻을 수 있습니다.**")
    else:
        st.error("⚠️ **AI에게 날씨 및 여행 정보를 묻지 않으면 필요한 정보를 확인할 수 없습니다.**")

    with st.container(border=True):
        st.write("당신은 3박 4일 여행을 계획하고 있습니다. 자유롭게 질문해 보세요.")
        st.write(":blue[**여행에 대해서 물어보세요.**]")

        # 대화 기록 표시
        for chat in st.session_state.chat_history:
            with st.chat_message(chat["role"]):
                st.write(chat["content"])

        # [수정된 부분] 입력창 설정: key를 부여하고 엔터키 입력 시 submit_question 실행
        st.text_input("질문을 입력하세요", 
                      key="widget_input", 
                      placeholder="예) 스위스 3박 4일 여행 일정 짜줘", 
                      label_visibility="collapsed",
                      on_change=submit_question)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            # 버튼 클릭 시에도 동일하게 작동하도록 함수 호출
            if st.button("AI 답변듣기", use_container_width=True):
                submit_question()
                st.rerun()
        
        with col2:
            if st.button("대화종료", use_container_width=True, type="primary"):
                if len(st.session_state.chat_history) > 0:
                    st.session_state.step = 'survey'
                    st.rerun()
                else:
                    st.warning("최소 한 번 이상 대화한 후 종료해 주세요.")

# --- [3단계] 설문 연결 화면 ---
elif st.session_state.step == 'survey':
    st.title("📋 서비스 만족도 조사")
    base_url = "https://docs.google.com/forms/d/e/1FAIpQLSdCiF4lzxN5NRaOWIrgLsW9Tphs99FmtS6mLXAlCEKs75udXg/viewform?entry.41790104="
    final_form_url = base_url + st.session_state.group
    
    st.info(f"시스템 확인이 완료되었습니다. 그룹: {st.session_state.group}")
    st.link_button("🚀 설문 참여하고 완료하기", final_form_url, use_container_width=True)

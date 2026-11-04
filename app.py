import streamlit as st​

​

st.title("🎈 나의 첫 Streamlit 앱")​

st.write("Streamlit 은 파이썬 코드만으로​

          웹 화면을 만듭니다.")​

​

nickname = st.text_input("별명을 입력하세요")​

​

if st.button("인사하기"):​

    st.success(f"{nickname} 님, 반가워요!")​

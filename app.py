if "count" not in st.session_state:​

    st.session_state.count = 0      # 처음 열 때만​

​

if st.button("+1"):​

    st.session_state.count = st.session_state.count + 1​

​

if st.button("처음으로"):​

    st.session_state.count = 0​

​

st.metric("누른 횟수", st.session_state.count)​

import streamlit as st
from knowledge_bot_v2 import ask  # 导入上面的函数

st.title("📚 我的知识库问答助手")

question = st.text_input("请输入你的问题：")

if question:
    with st.spinner("思考中..."):
        answer = ask(question)
    st.write(answer)
# -*- coding: utf-8 -*-
"""
네이버 블로그 검색 데이터 분석 페이지

사용자가 입력한 검색어들의 블로그 발행 추이와 텍스트 핵심 단어 빈도,
영향력 있는 블로거 비중을 시각화 분석합니다.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import re
from collections import Counter
import utils

st.title("📝 네이버 블로그 검색 데이터 분석")
st.markdown("네이버 블로그 검색 결과를 분석하여 최신 트렌드 키워드, 블로거 분포 및 작성 추이를 시각화합니다.")

# API 키 확인
if not st.session_state.get("client_id") or not st.session_state.get("client_secret"):
    st.warning("👈 왼쪽 사이드바에서 NAVER API Client ID와 Client Secret을 먼저 입력해 주세요.")
else:
    client_id = st.session_state["client_id"]
    client_secret = st.session_state["client_secret"]
    
    # 입력 폼 레이아웃
    with st.form("blog_form"):
        col1, col2 = st.columns([2, 1])
        with col1:
            keyword_input = st.text_input(
                "검색어 입력 (쉼표로 구분, 최대 3개)",
                value="아이폰 16, 갤럭시 s25",
                help="쉼표로 구분해 여러 키워드를 입력하면 검색어별 블로그 성향을 비교합니다."
            )
        with col2:
            display_num = st.slider("수집할 블로그 수", min_value=10, max_value=100, value=50, step=10)
            
        col3, col4 = st.columns(2)
        with col3:
            sort_type = st.selectbox(
                "정렬 기준",
                options=["sim", "date"],
                format_func=lambda x: "정확도순" if x == "sim" else "날짜순"
            )
        with col4:
            st.markdown("<br>", unsafe_allow_html=True)
            # 빈 열 공간 확보용
            
        submitted = st.form_submit_button("블로그 데이터 분석 실행")
        
    if submitted:
        keywords = utils.parse_keywords(keyword_input)
        if not keywords:
            st.error("분석할 블로그 키워드를 입력해 주세요.")
        elif len(keywords) > 3:
            st.error("블로그 비교는 동시에 최대 3개까지만 가능합니다.")
        else:
            all_blogs = []
            
            with st.spinner("네이버 블로그 API로부터 데이터를 수집하는 중입니다..."):
                try:
                    for kw in keywords:
                        res = utils.cached_search_blog(
                            client_id=client_id,
                            client_secret=client_secret,
                            query=kw,
                            display=display_num,
                            sort=sort_type
                        )
                        
                        items = res.get("items", [])
                        for item in items:
                            title_cleaned = item["title"].replace("<b>", "").replace("</b>", "")
                            desc_cleaned = item["description"].replace("<b>", "").replace("</b>", "")
                            
                            # 날짜 형식 변환 (yyyyMMdd -> yyyy-MM-dd)
                            post_date = item["postdate"]
                            try:
                                formatted_date = datetime.strptime(post_date, "%Y%m%d").strftime("%Y-%m-%d")
                            except:
                                formatted_date = post_date
                                
                            all_blogs.append({
                                "검색키워드": kw,
                                "제목": title_cleaned,
                                "설명": desc_cleaned,
                                "블로거명": item["bloggername"],
                                "블로그링크": item["bloggerlink"],
                                "작성일": formatted_date,
                                "게시글링크": item["link"]
                            })
                            
                    if not all_blogs:
                        st.info("검색된 블로그 데이터가 없습니다.")
                    else:
                        df = pd.DataFrame(all_blogs)
                        
                        st.markdown("### 📊 수집 데이터 분석 요약")
                        
                        # 1. 시계열 발행량 분석
                        st.markdown("### 📅 날짜별 블로그 발행 추이")
                        date_df = df.groupby(["작성일", "검색키워드"]).size().reset_index(name="발행량")
                        fig_line = px.line(
                            date_df,
                            x="작성일",
                            y="발행량",
                            color="검색키워드",
                            title="일자별 블로그 게시글 수 추이",
                            markers=True
                        )
                        st.plotly_chart(fig_line, use_container_width=True)
                        
                        # 2. 텍스트 분석 (주요 언급 단어 추출)
                        st.markdown("### 🔤 블로그 제목 내 주요 언급 단어 (단어 빈도 분석)")
                        col_chart1, col_chart2 = st.columns(2)
                        
                        # 키워드별 언급 빈도 계산 함수
                        def get_top_nouns(text_list, num=10):
                            words = []
                            for text in text_list:
                                # 특수문자 제거 및 한글/영어/숫자 2글자 이상 추출
                                w_list = re.findall(r'[a-zA-Z0-9가-힣]{2,}', text)
                                for w in w_list:
                                    # 불용어 처리 (일반적인 단어 및 검색어 자체 제외)
                                    if w not in ["블로그", "포스팅", "정보", "리뷰", "후기", "추천", "오늘", "사용"]:
                                        words.append(w)
                            return Counter(words).most_common(num)
                        
                        with col_chart1:
                            st.markdown(f"**🟢 {keywords[0]} 블로그 주요 키워드**")
                            kw0_texts = df[df["검색키워드"] == keywords[0]]["제목"].tolist()
                            top_kw0 = get_top_nouns(kw0_texts)
                            if top_kw0:
                                top_kw0_df = pd.DataFrame(top_kw0, columns=["단어", "빈도수"])
                                fig_bar1 = px.bar(
                                    top_kw0_df,
                                    x="빈도수",
                                    y="단어",
                                    orientation="h",
                                    title=f"'{keywords[0]}' 관련 연관 키워드 TOP 10",
                                    color="빈도수",
                                    color_continuous_scale="Purples"
                                )
                                fig_bar1.update_layout(yaxis={'categoryorder':'total ascending'})
                                st.plotly_chart(fig_bar1, use_container_width=True)
                            else:
                                st.info("분석할 단어 데이터가 부족합니다.")
                                
                        with col_chart2:
                            if len(keywords) > 1:
                                st.markdown(f"**🟢 {keywords[1]} 블로그 주요 키워드**")
                                kw1_texts = df[df["검색키워드"] == keywords[1]]["제목"].tolist()
                                top_kw1 = get_top_nouns(kw1_texts)
                                if top_kw1:
                                    top_kw1_df = pd.DataFrame(top_kw1, columns=["단어", "빈도수"])
                                    fig_bar2 = px.bar(
                                        top_kw1_df,
                                        x="빈도수",
                                        y="단어",
                                        orientation="h",
                                        title=f"'{keywords[1]}' 관련 연관 키워드 TOP 10",
                                        color="빈도수",
                                        color_continuous_scale="Oranges"
                                    )
                                    fig_bar2.update_layout(yaxis={'categoryorder':'total ascending'})
                                    st.plotly_chart(fig_bar2, use_container_width=True)
                                else:
                                    st.info("분석할 단어 데이터가 부족합니다.")
                            else:
                                st.info("비교할 두 번째 키워드가 없습니다.")
                                
                        # 3. 데이터 테이블 및 다운로드
                        st.markdown("### 📋 수집된 블로그 포스트 리스트")
                        st.dataframe(df.drop(columns=["게시글링크", "블로그링크"]), use_container_width=True)
                        
                        csv = df.to_csv(index=False).encode('utf-8-sig')
                        st.download_button(
                            label="📥 블로그 수집 데이터 다운로드",
                            data=csv,
                            file_name=f"naver_blog_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
                except Exception as e:
                    st.error(f"블로그 데이터 조회 중 오류가 발생했습니다: {str(e)}")

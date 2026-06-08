# -*- coding: utf-8 -*-
"""
네이버 카페글 검색 데이터 분석 페이지

사용자가 입력한 검색어들의 네이버 카페 게시글 데이터를 수집하고,
게시글이 많이 작성된 주요 카페 분포와 키워드 빈도를 시각화 분석합니다.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import re
from collections import Counter
import utils

st.title("👥 네이버 카페글 검색 데이터 분석")
st.markdown("네이버 카페 검색 결과를 분석하여 주요 커뮤니티(카페명) 분포 및 연관 검색어 키워드를 파악합니다.")

# API 키 확인
if not st.session_state.get("client_id") or not st.session_state.get("client_secret"):
    st.warning("👈 왼쪽 사이드바에서 NAVER API Client ID와 Client Secret을 먼저 입력해 주세요.")
else:
    client_id = st.session_state["client_id"]
    client_secret = st.session_state["client_secret"]
    
    # 입력 폼 레이아웃
    with st.form("cafe_form"):
        col1, col2 = st.columns([2, 1])
        with col1:
            keyword_input = st.text_input(
                "검색어 입력 (쉼표로 구분, 최대 3개)",
                value="중고차 직거래, 셀프 세차",
                help="쉼표로 구분해 여러 키워드를 입력하면 검색어별 활성화된 카페 및 트렌드를 비교합니다."
            )
        with col2:
            display_num = st.slider("수집할 카페글 수", min_value=10, max_value=100, value=50, step=10)
            
        col3, col4 = st.columns(2)
        with col3:
            sort_type = st.selectbox(
                "정렬 기준",
                options=["sim", "date"],
                format_func=lambda x: "정확도순" if x == "sim" else "날짜순"
            )
        with col4:
            st.markdown("<br>", unsafe_allow_html=True)
            
        submitted = st.form_submit_button("카페 데이터 분석 실행")
        
    if submitted:
        keywords = utils.parse_keywords(keyword_input)
        if not keywords:
            st.error("분석할 카페 키워드를 입력해 주세요.")
        elif len(keywords) > 3:
            st.error("카페 게시글 비교는 동시에 최대 3개까지만 가능합니다.")
        else:
            all_cafes = []
            
            with st.spinner("네이버 카페 API로부터 데이터를 수집하는 중입니다..."):
                try:
                    for kw in keywords:
                        res = utils.cached_search_cafe(
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
                            
                            all_cafes.append({
                                "검색키워드": kw,
                                "제목": title_cleaned,
                                "설명": desc_cleaned,
                                "카페명": item["cafename"],
                                "카페주소": item["cafeurl"],
                                "게시글링크": item["link"]
                            })
                            
                    if not all_cafes:
                        st.info("검색된 카페 데이터가 없습니다.")
                    else:
                        df = pd.DataFrame(all_cafes)
                        
                        st.markdown("### 📊 수집 데이터 분석 요약")
                        
                        col_c1, col_c2 = st.columns(2)
                        
                        # 1. 카페별 점유율 분석
                        with col_c1:
                            st.markdown("### 🏬 언급이 많은 상위 카페 분포")
                            cafe_count_df = df.groupby(["카페명", "검색키워드"]).size().reset_index(name="게시글수")
                            # 상위 카페 정렬
                            cafe_count_df = cafe_count_df.sort_values(by="게시글수", ascending=False).head(10)
                            
                            fig_bar = px.bar(
                                cafe_count_df,
                                x="게시글수",
                                y="카페명",
                                color="검색키워드",
                                orientation="h",
                                title="가장 게시글이 많이 등록된 카페 순위 (TOP 10)",
                                labels={"게시글수": "수집된 글 수"}
                            )
                            fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
                            st.plotly_chart(fig_bar, use_container_width=True)
                            
                        # 2. 텍스트 분석 (카페글 핵심 단어 분석)
                        with col_c2:
                            st.markdown("### 🔤 카페글 제목 내 연관 단어 빈도")
                            
                            words = []
                            for title in df["제목"].tolist():
                                w_list = re.findall(r'[a-zA-Z0-9가-힣]{2,}', title)
                                for w in w_list:
                                    if w not in ["카페", "질문", "후기", "추천", "공유", "정보", "관련", "가입", "등등"]:
                                        words.append(w)
                                        
                            top_words = Counter(words).most_common(10)
                            if top_words:
                                words_df = pd.DataFrame(top_words, columns=["단어", "빈도수"])
                                fig_pie = px.pie(
                                    words_df,
                                    values="빈도수",
                                    names="단어",
                                    title="전체 카페글 제목 핵심 연관 키워드 비중",
                                    hole=0.3
                                )
                                st.plotly_chart(fig_pie, use_container_width=True)
                            else:
                                st.info("분석할 단어 데이터가 부족합니다.")
                                
                        # 3. 데이터 테이블 및 다운로드
                        st.markdown("### 📋 수집된 카페 게시글 리스트")
                        st.dataframe(df.drop(columns=["게시글링크", "카페주소"]), use_container_width=True)
                        
                        csv = df.to_csv(index=False).encode('utf-8-sig')
                        st.download_button(
                            label="📥 카페글 수집 데이터 다운로드",
                            data=csv,
                            file_name=f"naver_cafe_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
                except Exception as e:
                    st.error(f"카페 데이터 조회 중 오류가 발생했습니다: {str(e)}")

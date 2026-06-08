# -*- coding: utf-8 -*-
"""
네이버 뉴스 검색 데이터 분석 페이지

사용자가 입력한 검색어들의 뉴스 보도 데이터를 수집하고,
보도량 추이, 원문 도메인(언론사) 분석 및 핵심 연관 단어 분포를 시각화합니다.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from urllib.parse import urlparse
import re
from collections import Counter
import utils

st.title("📰 네이버 뉴스 검색 데이터 분석")
st.markdown("네이버 뉴스 검색 결과를 분석하여 일자별 보도량 추이, 주요 보도 매체(도메인) 및 연관 키워드를 시각화합니다.")

# API 키 확인
if not st.session_state.get("client_id") or not st.session_state.get("client_secret"):
    st.warning("👈 왼쪽 사이드바에서 NAVER API Client ID와 Client Secret을 먼저 입력해 주세요.")
else:
    client_id = st.session_state["client_id"]
    client_secret = st.session_state["client_secret"]
    
    # 입력 폼 레이아웃
    with st.form("news_form"):
        col1, col2 = st.columns([2, 1])
        with col1:
            keyword_input = st.text_input(
                "검색어 입력 (쉼표로 구분, 최대 3개)",
                value="네이버, 카카오",
                help="쉼표로 구분해 여러 키워드를 입력하면 검색어별 뉴스 보도 트렌드를 비교합니다."
            )
        with col2:
            display_num = st.slider("수집할 뉴스 수", min_value=10, max_value=100, value=50, step=10)
            
        col3, col4 = st.columns(2)
        with col3:
            sort_type = st.selectbox(
                "정렬 기준",
                options=["sim", "date"],
                format_func=lambda x: "정확도순" if x == "sim" else "날짜순"
            )
        with col4:
            st.markdown("<br>", unsafe_allow_html=True)
            
        submitted = st.form_submit_button("뉴스 데이터 분석 실행")
        
    if submitted:
        keywords = utils.parse_keywords(keyword_input)
        if not keywords:
            st.error("분석할 뉴스 키워드를 입력해 주세요.")
        elif len(keywords) > 3:
            st.error("뉴스 비교는 동시에 최대 3개까지만 가능합니다.")
        else:
            all_news = []
            
            with st.spinner("네이버 뉴스 API로부터 데이터를 수집하는 중입니다..."):
                try:
                    for kw in keywords:
                        res = utils.cached_search_news(
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
                            
                            # 날짜 형식 파싱 (Mon, 08 Jun 2026 09:00:00 +0900 등 RFC 822 포맷)
                            pub_date = item["pubDate"]
                            try:
                                # 간소화된 날짜 파싱 (예: "08 Jun 2026" 부분만 추출)
                                date_match = re.search(r'\d{2}\s[a-zA-Z]{3}\s\d{4}', pub_date)
                                if date_match:
                                    parsed_date = datetime.strptime(date_match.group(), "%d %b %Y").strftime("%Y-%m-%d")
                                else:
                                    parsed_date = datetime.now().strftime("%Y-%m-%d")
                            except:
                                parsed_date = datetime.now().strftime("%Y-%m-%d")
                                
                            # 원문 도메인 추출 (언론사 대용)
                            orig_link = item["originallink"]
                            domain = "기타"
                            if orig_link:
                                try:
                                    parsed_uri = urlparse(orig_link)
                                    domain = parsed_uri.netloc.replace("www.", "")
                                except:
                                    pass
                                    
                            all_news.append({
                                "검색키워드": kw,
                                "제목": title_cleaned,
                                "설명": desc_cleaned,
                                "보도일": parsed_date,
                                "원문도메인": domain,
                                "원문링크": orig_link,
                                "네이버뉴스링크": item["link"]
                            })
                            
                    if not all_news:
                        st.info("검색된 뉴스 데이터가 없습니다.")
                    else:
                        df = pd.DataFrame(all_news)
                        
                        st.markdown("### 📊 수집 데이터 분석 요약")
                        
                        # 1. 일자별 뉴스 발행량 추이
                        st.markdown("### 📅 일자별 뉴스 보도 추이")
                        date_df = df.groupby(["보도일", "검색키워드"]).size().reset_index(name="보도건수")
                        fig_line = px.line(
                            date_df,
                            x="보도일",
                            y="보도건수",
                            color="검색키워드",
                            title="일자별 뉴스 발행 추이",
                            markers=True
                        )
                        st.plotly_chart(fig_line, use_container_width=True)
                        
                        # 2. 보도 매체(도메인) 및 연관 키워드 분포
                        col_n1, col_n2 = st.columns(2)
                        
                        with col_n1:
                            st.markdown("### 🏛️ 주요 보도 매체(도메인) TOP 10")
                            domain_df = df.groupby("원문도메인").size().reset_index(name="보도건수").sort_values(by="보도건수", ascending=False).head(10)
                            fig_bar = px.bar(
                                domain_df,
                                x="보도건수",
                                y="원문도메인",
                                color="보도건수",
                                orientation="h",
                                title="상위 언론사 도메인별 보도 점유율",
                                color_continuous_scale="Viridis"
                            )
                            fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
                            st.plotly_chart(fig_bar, use_container_width=True)
                            
                        with col_n2:
                            st.markdown("### 🔤 뉴스 제목 내 다빈도 키워드")
                            words = []
                            for title in df["제목"].tolist():
                                w_list = re.findall(r'[a-zA-Z0-9가-힣]{2,}', title)
                                for w in w_list:
                                    if w not in ["뉴스", "보도", "기사", "출시", "선정", "개최", "진행", "발표", "계획"]:
                                        words.append(w)
                                        
                            top_words = Counter(words).most_common(10)
                            if top_words:
                                words_df = pd.DataFrame(top_words, columns=["단어", "빈도수"])
                                fig_pie = px.pie(
                                    words_df,
                                    values="빈도수",
                                    names="단어",
                                    title="전체 뉴스 제목 연관 핵심 키워드",
                                    hole=0.4
                                )
                                st.plotly_chart(fig_pie, use_container_width=True)
                            else:
                                st.info("분석할 단어 데이터가 부족합니다.")
                                
                        # 3. 데이터 테이블 및 다운로드
                        st.markdown("### 📋 수집된 뉴스 리스트")
                        st.dataframe(df.drop(columns=["원문링크", "네이버뉴스링크"]), use_container_width=True)
                        
                        csv = df.to_csv(index=False).encode('utf-8-sig')
                        st.download_button(
                            label="📥 뉴스 수집 데이터 다운로드",
                            data=csv,
                            file_name=f"naver_news_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
                except Exception as e:
                    st.error(f"뉴스 데이터 조회 중 오류가 발생했습니다: {str(e)}")

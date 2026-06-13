# -*- coding: utf-8 -*-
"""
네이버 소셜 버즈 통합 분석 페이지

사용자가 쉼표로 구분하여 입력한 다수의 검색어들에 대하여
네이버 블로그, 카페글, 뉴스 API 검색 데이터를 일괄 수집하여
발행량 비교 추이, 채널별 핵심 언급 키워드(텍스트 분석) 및 수집 데이터를 종합적으로 분석합니다.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import re
from collections import Counter
import utils

st.title("🔗 네이버 소셜 버즈 통합 분석 (뉴스·블로그·카페)")
st.markdown("쉼표로 구분된 다수의 키워드에 대해 뉴스, 블로그, 카페 검색 데이터를 통합 수집하여 비교 분석합니다.")

# API 키 확인
if not st.session_state.get("client_id") or not st.session_state.get("client_secret"):
    st.warning("👈 왼쪽 사이드바에서 NAVER API 설정 상태를 확인해 주세요. .env 파일에 키를 지정해야 작동합니다.")
else:
    client_id = st.session_state["client_id"]
    client_secret = st.session_state["client_secret"]
    
    # 폼 레이아웃 설정
    with st.form("social_integration_form"):
        col1, col2 = st.columns([3, 1])
        with col1:
            keyword_input = st.text_input(
                "분석할 검색어 입력 (쉼표로 구분)",
                value="아이폰, 갤럭시",
                help="쉼표로 구분하여 여러 키워드를 입력할 수 있습니다."
            )
        with col2:
            display_num = st.slider("채널별 수집 개수 (1개 키워드 기준)", min_value=10, max_value=100, value=30, step=10)
            
        submitted = st.form_submit_button("통합 소셜 분석 실행")
        
    if submitted:
        keywords = utils.parse_keywords(keyword_input)
        if not keywords:
            st.error("분석할 검색 키워드를 입력해 주세요.")
        else:
            all_data = []
            
            with st.spinner("네이버 뉴스·블로그·카페 API로부터 데이터를 수집하고 있습니다..."):
                try:
                    for kw in keywords:
                        # 1. 블로그 데이터 수집
                        try:
                            blog_res = utils.cached_search_blog(
                                client_id=client_id,
                                client_secret=client_secret,
                                query=kw,
                                display=display_num,
                                sort="sim"
                            )
                            for item in blog_res.get("items", []):
                                title = item["title"].replace("<b>", "").replace("</b>", "")
                                desc = item["description"].replace("<b>", "").replace("</b>", "")
                                post_date = item.get("postdate", "")
                                try:
                                    formatted_date = datetime.strptime(post_date, "%Y%m%d").strftime("%Y-%m-%d")
                                except:
                                    formatted_date = datetime.today().strftime("%Y-%m-%d")
                                    
                                all_data.append({
                                    "검색키워드": kw,
                                    "채널": "블로그",
                                    "제목": title,
                                    "설명": desc,
                                    "출처/작성자": item.get("bloggername", "네이버 블로그"),
                                    "작성일": formatted_date,
                                    "링크": item.get("link", "")
                                })
                        except Exception as e:
                            st.warning(f"'{kw}' 블로그 수집 중 오류: {str(e)}")
                            
                        # 2. 카페글 데이터 수집
                        try:
                            cafe_res = utils.cached_search_cafe(
                                client_id=client_id,
                                client_secret=client_secret,
                                query=kw,
                                display=display_num,
                                sort="sim"
                            )
                            for item in cafe_res.get("items", []):
                                title = item["title"].replace("<b>", "").replace("</b>", "")
                                desc = item["description"].replace("<b>", "").replace("</b>", "")
                                # 카페는 작성일 형식이 다양할 수 있어 오늘 날짜 처리 혹은 생략
                                all_data.append({
                                    "검색키워드": kw,
                                    "채널": "카페",
                                    "제목": title,
                                    "설명": desc,
                                    "출처/작성자": item.get("cafename", "네이버 카페"),
                                    "작성일": datetime.today().strftime("%Y-%m-%d"),
                                    "링크": item.get("link", "")
                                })
                        except Exception as e:
                            st.warning(f"'{kw}' 카페글 수집 중 오류: {str(e)}")
                            
                        # 3. 뉴스 데이터 수집
                        try:
                            news_res = utils.cached_search_news(
                                client_id=client_id,
                                client_secret=client_secret,
                                query=kw,
                                display=display_num,
                                sort="sim"
                            )
                            for item in news_res.get("items", []):
                                title = item["title"].replace("<b>", "").replace("</b>", "")
                                desc = item["description"].replace("<b>", "").replace("</b>", "")
                                pub_date = item.get("pubDate", "")
                                try:
                                    # 예: Wed, 10 Jun 2026 12:00:00 +0900
                                    formatted_date = datetime.strptime(pub_date[:25].strip(), "%a, %d %b %Y %H:%M:%S").strftime("%Y-%m-%d")
                                except:
                                    formatted_date = datetime.today().strftime("%Y-%m-%d")
                                    
                                all_data.append({
                                    "검색키워드": kw,
                                    "채널": "뉴스",
                                    "제목": title,
                                    "설명": desc,
                                    "출처/작성자": "언론사 뉴스",
                                    "작성일": formatted_date,
                                    "링크": item.get("link", "")
                                })
                        except Exception as e:
                            st.warning(f"'{kw}' 뉴스 수집 중 오류: {str(e)}")
                            
                    if not all_data:
                        st.info("검색된 소셜 버즈 데이터가 없습니다.")
                    else:
                        df = pd.DataFrame(all_data)
                        
                        # 지표 요약
                        st.markdown("### 📊 채널별 수집 건수 요약")
                        summary_df = df.groupby(["검색키워드", "채널"]).size().reset_index(name="수집건수")
                        st.dataframe(summary_df, use_container_width=True)
                        
                        col_chart1, col_chart2 = st.columns(2)
                        
                        with col_chart1:
                            st.markdown("#### 📢 채널별 점유율 비율")
                            fig_pie = px.pie(
                                df,
                                names="채널",
                                color="채널",
                                color_discrete_map={"뉴스": "#EF553B", "블로그": "#636EFA", "카페": "#00CC96"},
                                hole=0.4
                            )
                            st.plotly_chart(fig_pie, use_container_width=True)
                            
                        with col_chart2:
                            st.markdown("#### 📈 키워드별 채널 언급 분포")
                            fig_bar = px.bar(
                                summary_df,
                                x="검색키워드",
                                y="수집건수",
                                color="채널",
                                barmode="group",
                                color_discrete_map={"뉴스": "#EF553B", "블로그": "#636EFA", "카페": "#00CC96"}
                            )
                            st.plotly_chart(fig_bar, use_container_width=True)
                            
                        # 단어 추출 및 단순 불용어 처리 함수
                        def get_top_words(text_list, num=15):
                            words = []
                            for text in text_list:
                                w_list = re.findall(r'[a-zA-Z0-9가-힣]{2,}', text)
                                for w in w_list:
                                    if w not in ["블로그", "포스팅", "정보", "리뷰", "후기", "추천", "오늘", "사용", "뉴스", "카페"]:
                                        words.append(w)
                            return Counter(words).most_common(num)
                            
                        # 키워드별 분석 탭
                        st.markdown("### 🔤 키워드별 텍스트 핵심 언급 단어")
                        tabs = st.tabs(keywords)
                        for idx, tab in enumerate(tabs):
                            current_kw = keywords[idx]
                            with tab:
                                col_t1, col_t2, col_t3 = st.columns(3)
                                channels = [("뉴스", col_t1), ("블로그", col_t2), ("카페", col_t3)]
                                for ch_name, col_obj in channels:
                                    with col_obj:
                                        st.markdown(f"**{ch_name} 채널 내 키워드**")
                                        ch_texts = df[(df["검색키워드"] == current_kw) & (df["채널"] == ch_name)]["제목"].tolist()
                                        top_nouns = get_top_words(ch_texts)
                                        if top_nouns:
                                            nouns_df = pd.DataFrame(top_nouns, columns=["단어", "빈도"])
                                            fig = px.bar(
                                                nouns_df,
                                                x="빈도",
                                                y="단어",
                                                orientation="h",
                                                color="빈도",
                                                color_continuous_scale="Viridis",
                                                title=f"'{current_kw}' {ch_name} 단어 TOP 15"
                                            )
                                            fig.update_layout(yaxis={'categoryorder':'total ascending'})
                                            st.plotly_chart(fig, use_container_width=True)
                                        else:
                                            st.info("데이터가 부족합니다.")
                                            
                        # 데이터 목록 제공
                        st.markdown("### 📋 통합 버즈 상세 데이터 목록")
                        st.dataframe(df.drop(columns=["링크"]), use_container_width=True)
                        
                        # 다운로드
                        csv_data = df.to_csv(index=False).encode("utf-8-sig")
                        st.download_button(
                            label="📥 통합 소셜 데이터 다운로드",
                            data=csv_data,
                            file_name=f"naver_social_integration_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
                except Exception as e:
                    st.error(f"통합 분석 과정 중 오류가 발생했습니다: {str(e)}")

# -*- coding: utf-8 -*-
"""
네이버 쇼핑 검색 결과 분석 페이지

사용자가 입력한 검색어들의 네이버 쇼핑 상품 데이터를 수집하여
가격 분포, 쇼핑몰 점유율, 브랜드 분포 등의 다차원 분석 대시보드를 제공합니다.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import utils

st.title("🛒 네이버 쇼핑 검색 결과 분석")
st.markdown("네이버 쇼핑에 등록된 상품 데이터의 가격 분포, 쇼핑몰 비중, 브랜드 현황을 비교 분석합니다.")

# API 키 확인
if not st.session_state.get("client_id") or not st.session_state.get("client_secret"):
    st.warning("👈 왼쪽 사이드바에서 NAVER API Client ID와 Client Secret을 먼저 입력해 주세요.")
else:
    client_id = st.session_state["client_id"]
    client_secret = st.session_state["client_secret"]
    
    # 입력 폼 레이아웃
    with st.form("shopping_form"):
        col1, col2 = st.columns([2, 1])
        with col1:
            keyword_input = st.text_input(
                "검색 상품 입력 (쉼표로 구분, 최대 3개)",
                value="갤럭시 s24, 아이폰 15",
                help="쉼표로 구분해 여러 상품을 입력하면 가격 및 브랜드 분포를 교차 비교합니다."
            )
        with col2:
            display_num = st.slider("수집할 상품 수", min_value=10, max_value=100, value=30, step=10)
            
        col3, col4 = st.columns(2)
        with col3:
            sort_type = st.selectbox(
                "정렬 기준",
                options=["sim", "date", "asc", "dsc"],
                format_func=lambda x: {
                    "sim": "정확도순", "date": "최신등록순",
                    "asc": "가격 낮은순", "dsc": "가격 높은순"
                }[x]
            )
        with col4:
            filter_pay = st.checkbox("네이버페이 구매 가능 상품만 필터링", value=False)
            
        # 제외 상품 선택
        exclude_options = st.multiselect(
            "제외할 상품 유형 (선택)",
            options=["used", "rental", "cbshop"],
            format_func=lambda x: {"used": "중고 상품 제외", "rental": "렌탈 상품 제외", "cbshop": "해외직구 제외"}[x]
        )
        
        submitted = st.form_submit_button("쇼핑 데이터 분석 실행")
        
    if submitted:
        keywords = utils.parse_keywords(keyword_input)
        if not keywords:
            st.error("분석할 상품 키워드를 입력해 주세요.")
        elif len(keywords) > 3:
            st.error("상품 비교는 동시에 최대 3개까지만 가능합니다.")
        else:
            filter_val = "naverpay" if filter_pay else ""
            exclude_val = ":".join(exclude_options) if exclude_options else ""
            
            all_products = []
            
            with st.spinner("네이버 쇼핑 API로부터 상품 데이터를 수집하는 중입니다..."):
                try:
                    for kw in keywords:
                        res = utils.cached_search_shop(
                            client_id=client_id,
                            client_secret=client_secret,
                            query=kw,
                            display=display_num,
                            sort=sort_type,
                            filter_type=filter_val,
                            exclude=exclude_val
                        )
                        
                        items = res.get("items", [])
                        for item in items:
                            # <b> 태그 제거 유틸
                            title_cleaned = item["title"].replace("<b>", "").replace("</b>", "")
                            # 가격 정보 형변환
                            lprice = int(item["lprice"]) if item["lprice"] else 0
                            hprice = int(item["hprice"]) if item["hprice"] else 0
                            
                            all_products.append({
                                "검색키워드": kw,
                                "상품명": title_cleaned,
                                "최저가": lprice,
                                "최고가": hprice,
                                "쇼핑몰": item["mallName"] if item["mallName"] else "기타",
                                "브랜드": item["brand"] if item["brand"] else "미지정",
                                "제조사": item["maker"] if item["maker"] else "미지정",
                                "카테고리": f"{item['category1']} > {item['category2']}",
                                "링크": item["link"]
                            })
                            
                    if not all_products:
                        st.info("검색된 상품 데이터가 없습니다.")
                    else:
                        df = pd.DataFrame(all_products)
                        
                        # 0원 가격 제외 (비정상 데이터 처리)
                        df = df[df["최저가"] > 0]
                        
                        # 대시보드 시각화
                        st.markdown("### 📊 수집 데이터 개요")
                        
                        # 주요 통계 요약 (Metric Cards)
                        metric_cols = st.columns(len(keywords))
                        for idx, kw in enumerate(keywords):
                            kw_df = df[df["검색키워드"] == kw]
                            if not kw_df.empty:
                                median_price = kw_df["최저가"].median()
                                mean_price = kw_df["최저가"].mean()
                                product_count = len(kw_df)
                                
                                with metric_cols[idx]:
                                    st.markdown(f"**🟢 {kw}** (수집: {product_count}건)")
                                    st.metric(label="중앙 가격", value=f"{int(median_price):,}원")
                                    st.metric(label="평균 가격", value=f"{int(mean_price):,}원")
                                    
                        # 1. 가격 분포 비교 (Box Plot)
                        st.markdown("### 📈 상품 가격 분포 비교 (Box Plot)")
                        st.write("이상치(극단값) 식별 및 사분위수(IQR) 파악에 용이합니다.")
                        fig_box = px.box(
                            df, 
                            x="검색키워드", 
                            y="최저가", 
                            color="검색키워드",
                            points="all",
                            title="검색어별 상품 가격 분포 및 아웃라이어 분석",
                            labels={"최저가": "상품 가격 (원)"}
                        )
                        st.plotly_chart(fig_box, use_container_width=True)
                        
                        # 2. 쇼핑몰 및 브랜드 점유율 분석
                        st.markdown("### 🏬 주요 쇼핑몰 및 브랜드 비중")
                        col_chart1, col_chart2 = st.columns(2)
                        
                        with col_chart1:
                            # 쇼핑몰 TOP 7 비중
                            mall_df = df.groupby("쇼핑몰").size().reset_index(name="상품수").sort_values(by="상품수", ascending=False).head(7)
                            fig_pie = px.pie(
                                mall_df,
                                values="상품수",
                                names="쇼핑몰",
                                title="전체 상품 등록 쇼핑몰 점유율 (TOP 7)",
                                hole=0.4
                            )
                            st.plotly_chart(fig_pie, use_container_width=True)
                            
                        with col_chart2:
                            # 브랜드별 평균 가격 비교
                            brand_df = df[df["브랜드"] != "미지정"].groupby("브랜드").agg(
                                상품수=("최저가", "count"),
                                평균가격=("최저가", "mean")
                            ).reset_index()
                            # 상품수 많은 브랜드 TOP 7
                            brand_df = brand_df.sort_values(by="상품수", ascending=False).head(7)
                            
                            fig_brand = px.bar(
                                brand_df,
                                x="브랜드",
                                y="평균가격",
                                color="브랜드",
                                text="상품수",
                                title="상위 브랜드별 평균 가격 (그래프 위 숫자는 등록 상품 수)",
                                labels={"평균가격": "평균 가격 (원)"}
                            )
                            fig_brand.update_traces(texttemplate='%{text}개', textposition='outside')
                            st.plotly_chart(fig_brand, use_container_width=True)
                            
                        # 3. 데이터 테이블 및 다운로드
                        st.markdown("### 📋 수집된 상품 목록")
                        # 가독성을 위해 링크 클릭 가능하도록 포맷팅
                        display_df = df.copy()
                        st.dataframe(display_df.drop(columns=["링크"]), use_container_width=True)
                        
                        # 다운로드
                        csv = df.to_csv(index=False).encode('utf-8-sig')
                        st.download_button(
                            label="📥 쇼핑 수집 데이터 다운로드",
                            data=csv,
                            file_name=f"naver_shopping_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
                except Exception as e:
                    st.error(f"쇼핑 데이터 조회 중 오류가 발생했습니다: {str(e)}")

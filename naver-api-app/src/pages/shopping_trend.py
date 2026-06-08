# -*- coding: utf-8 -*-
"""
네이버 쇼핑 트렌드(쇼핑인사이트) 분석 페이지

선택한 쇼핑 카테고리 내 입력된 키워드들의 네이버쇼핑 검색 클릭 트렌드를
수집하고 비교 분석하는 대시보드를 제공합니다.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import utils

st.title("🛍️ 네이버 쇼핑 트렌드 분석 (쇼핑인사이트)")
st.markdown("네이버 쇼핑 영역에서 특정 카테고리 내 키워드들의 검색 클릭 트렌드를 비교 시각화합니다.")

# API 키 확인
if not st.session_state.get("client_id") or not st.session_state.get("client_secret"):
    st.warning("👈 왼쪽 사이드바에서 NAVER API Client ID와 Client Secret을 먼저 입력해 주세요.")
else:
    client_id = st.session_state["client_id"]
    client_secret = st.session_state["client_secret"]
    
    # 대표 카테고리 맵핑 정보
    categories = {
        "패션의류": "50000000",
        "패션잡화": "50000001",
        "화장품/미용": "50000002",
        "디지털/가전": "50000003",
        "가구/인테리어": "50000004",
        "출산/육아": "50000005",
        "식품": "50000006",
        "스포츠/레저": "50000007",
        "생활/건강": "50000008",
        "여가/생활편의": "50000009",
        "도서": "50000010"
    }
    
    # 입력 폼 레이아웃
    with st.form("shop_trend_form"):
        col1, col2 = st.columns([2, 1])
        with col1:
            keyword_input = st.text_input(
                "분석 키워드 입력 (쉼표로 구분, 최대 5개)",
                value="노트북, 태블릿, 모니터",
                help="쉼표로 구분해 여러 쇼핑 키워드를 입력하세요."
            )
        with col2:
            time_unit = st.selectbox(
                "조회 단위",
                options=["date", "week", "month"],
                format_func=lambda x: "일간" if x == "date" else "주간" if x == "week" else "월간"
            )
            
        col3, col4 = st.columns(2)
        with col3:
            selected_cat_name = st.selectbox(
                "대표 쇼핑 카테고리 선택",
                options=list(categories.keys())
            )
        with col4:
            # 사용자가 카테고리 코드를 직접 수동 입력할 수 있도록 지원
            custom_cat_code = st.text_input(
                "직접 카테고리 코드 입력 (선택)",
                value=categories[selected_cat_name],
                help="특정 하위 카테고리 코드를 알고 있다면 입력하세요. 기본값은 위에서 선택한 코드입니다."
            )
            
        col5, col6 = st.columns(2)
        with col5:
            start_date, end_date = utils.get_default_dates()
            sel_start_date = st.date_input("시작일", start_date)
        with col6:
            sel_end_date = st.date_input("종료일", end_date)
            
        # 추가 상세 필터
        with st.expander("🔍 상세 조건 필터 (선택사항)"):
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                device = st.selectbox("검색 기기", ["", "pc", "mo"], format_func=lambda x: "전체 기기" if x == "" else x.upper())
            with col_f2:
                gender = st.selectbox("검색 사용자 성별", ["", "m", "f"], format_func=lambda x: "전체 성별" if x == "" else ("남성" if x == "m" else "여성"))
            with col_f3:
                ages = st.multiselect(
                    "검색 사용자 연령대",
                    options=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"],
                    format_func=lambda x: {
                        "1": "0∼12세", "2": "13∼18세", "3": "19∼24세", "4": "25∼29세",
                        "5": "30∼34세", "6": "35∼39세", "7": "40∼44세", "8": "45∼49세",
                        "9": "50∼54세", "10": "55∼59세", "11": "60세 이상"
                    }[x]
                )
                
        submitted = st.form_submit_button("쇼핑 클릭 트렌드 분석")
        
    if submitted:
        keywords = utils.parse_keywords(keyword_input)
        cat_code = custom_cat_code if custom_cat_code else categories[selected_cat_name]
        
        if not keywords:
            st.error("분석할 쇼핑 키워드를 입력해 주세요.")
        elif len(keywords) > 5:
            st.error("키워드는 최대 5개까지만 입력 가능합니다.")
        elif not cat_code.isdigit():
            st.error("올바른 카테고리 코드를 입력해 주세요 (숫자만 입력 가능).")
        elif sel_start_date > sel_end_date:
            st.error("시작일이 종료일보다 늦을 수 없습니다.")
        else:
            # API 요청 포맷 생성 (쇼핑인사이트는 keyword 하위에 name과 param을 쌍으로 보냄)
            api_keywords = [{"name": kw, "param": [kw]} for kw in keywords]
            
            with st.spinner("네이버 쇼핑인사이트 API로부터 데이터를 수집하는 중입니다..."):
                try:
                    res = utils.cached_get_shopping_trend(
                        client_id=client_id,
                        client_secret=client_secret,
                        start_date=sel_start_date.strftime("%Y-%m-%d"),
                        end_date=sel_end_date.strftime("%Y-%m-%d"),
                        time_unit=time_unit,
                        category=cat_code,
                        keywords=api_keywords,
                        device=device,
                        gender=gender,
                        ages=ages if ages else None
                    )
                    
                    results = res.get("results", [])
                    if not results or not results[0].get("data"):
                        st.info("해당 조건에 대한 데이터 검색 결과가 없습니다.")
                    else:
                        # 시계열 데이터 파싱
                        all_data = []
                        for group in results:
                            title = group["title"]
                            for item in group["data"]:
                                all_data.append({
                                    "날짜": pd.to_datetime(item["period"]),
                                    "클릭비율": float(item["ratio"]),
                                    "키워드": title
                                })
                        df = pd.DataFrame(all_data)
                        
                        st.markdown("### 📊 쇼핑 키워드 클릭 트렌드")
                        
                        # Plotly 라인 차트
                        fig = px.line(
                            df, 
                            x="날짜", 
                            y="클릭비율", 
                            color="키워드", 
                            title=f"선택 카테고리(코드: {cat_code}) 내 키워드 검색 클릭 트렌드",
                            labels={"클릭비율": "상대적 클릭 비율 (%)"}
                        )
                        fig.update_layout(hovermode="x unified")
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # 기술 통계량 분석 (Metric Card)
                        st.markdown("### 📈 키워드별 기술 통계 요약")
                        stats_cols = st.columns(len(keywords))
                        
                        for idx, kw in enumerate(keywords):
                            kw_df = df[df["키워드"] == kw]
                            if not kw_df.empty:
                                mean_val = kw_df["클릭비율"].mean()
                                max_val = kw_df["클릭비율"].max()
                                min_val = kw_df["클릭비율"].min()
                                
                                with stats_cols[idx]:
                                    st.markdown(f"**🟢 {kw}**")
                                    st.metric(label="평균 클릭 비율", value=f"{mean_val:.2f}%")
                                    st.metric(label="최대 클릭 비율", value=f"{max_val:.2f}%")
                                    st.metric(label="최소 클릭 비율", value=f"{min_val:.2f}%")
                                    
                        # 데이터 테이블 표시 및 다운로드
                        st.markdown("### 📋 수집된 상세 데이터")
                        pivot_df = df.pivot(index="날짜", columns="키워드", values="클릭비율").reset_index()
                        st.dataframe(pivot_df, use_container_width=True)
                        
                        # 다운로드
                        csv = pivot_df.to_csv(index=False).encode('utf-8-sig')
                        st.download_button(
                            label="📥 CSV 데이터 다운로드",
                            data=csv,
                            file_name=f"naver_shopping_trend_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
                except Exception as e:
                    st.error(f"쇼핑 트렌드 데이터 수집 중 오류가 발생했습니다: {str(e)}")

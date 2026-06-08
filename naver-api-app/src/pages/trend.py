# -*- coding: utf-8 -*-
"""
네이버 검색어 트렌드 분석 페이지

사용자가 입력한 검색어들의 네이버 통합검색 트렌드 추이를 수집하고
Plotly 인터랙티브 차트 및 기술 통계를 통해 시각화합니다.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import utils

st.title("📈 네이버 검색어 트렌드 분석")
st.markdown("여러 검색어들의 네이버 통합검색 내 검색량 추이를 비교하고 시각화합니다.")

# API 키 확인
if not st.session_state.get("client_id") or not st.session_state.get("client_secret"):
    st.warning("👈 왼쪽 사이드바에서 NAVER API Client ID와 Client Secret을 먼저 입력해 주세요.")
else:
    client_id = st.session_state["client_id"]
    client_secret = st.session_state["client_secret"]
    
    # 입력 폼 레이아웃
    with st.form("trend_form"):
        col1, col2 = st.columns([2, 1])
        with col1:
            keyword_input = st.text_input(
                "검색어 입력 (쉼표로 구분, 최대 5개)",
                value="인공지능, 메타버스, 자율주행",
                help="예: 인공지능, 메타버스, 자율주행 (최대 5개의 주제어를 쉼표로 구분해 입력하세요)"
            )
        with col2:
            time_unit = st.selectbox(
                "조회 단위",
                options=["date", "week", "month"],
                format_func=lambda x: "일간" if x == "date" else "주간" if x == "week" else "월간"
            )
            
        col3, col4 = st.columns(2)
        with col3:
            start_date, end_date = utils.get_default_dates()
            sel_start_date = st.date_input("시작일", start_date)
        with col4:
            sel_end_date = st.date_input("종료일", end_date)
            
        # 추가 필터 (기기, 성별, 연령)
        with st.expander("🔍 상세 필터 설정 (선택사항)"):
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
                
        submitted = st.form_submit_button("트렌드 분석 실행")
        
    if submitted:
        keywords = utils.parse_keywords(keyword_input)
        if not keywords:
            st.error("분석할 검색어를 입력해 주세요.")
        elif len(keywords) > 5:
            st.error("주제어는 최대 5개까지만 입력 가능합니다.")
        elif sel_start_date > sel_end_date:
            st.error("시작일이 종료일보다 늦을 수 없습니다.")
        else:
            # API 호출 파라미터 구성
            keyword_groups = [{"groupName": kw, "keywords": [kw]} for kw in keywords]
            
            with st.spinner("네이버 데이터랩 API로부터 데이터를 수집하는 중입니다..."):
                try:
                    res = utils.cached_get_search_trend(
                        client_id=client_id,
                        client_secret=client_secret,
                        start_date=sel_start_date.strftime("%Y-%m-%d"),
                        end_date=sel_end_date.strftime("%Y-%m-%d"),
                        time_unit=time_unit,
                        keyword_groups=keyword_groups,
                        device=device,
                        gender=gender,
                        ages=ages if ages else None
                    )
                    
                    # 데이터 프레임 변환 및 전처리
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
                                    "검색량비율": float(item["ratio"]),
                                    "주제어": title
                                })
                        df = pd.DataFrame(all_data)
                        
                        # 대시보드 시각화 및 분석 리포트
                        st.markdown("### 📊 트렌드 추이 분석")
                        
                        # Plotly 라인 차트
                        fig = px.line(
                            df, 
                            x="날짜", 
                            y="검색량비율", 
                            color="주제어", 
                            title="네이버 통합검색 상대적 검색량 추이 (최대값 100 기준)",
                            labels={"검색량비율": "상대적 검색량 비율 (%)"}
                        )
                        fig.update_layout(hovermode="x unified")
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # 기술 통계량 분석 (Metric Card)
                        st.markdown("### 📈 주제어별 기술 통계 요약")
                        stats_cols = st.columns(len(keywords))
                        
                        for idx, kw in enumerate(keywords):
                            kw_df = df[df["주제어"] == kw]
                            if not kw_df.empty:
                                mean_val = kw_df["검색량비율"].mean()
                                max_val = kw_df["검색량비율"].max()
                                min_val = kw_df["검색량비율"].min()
                                
                                with stats_cols[idx]:
                                    st.markdown(f"**🟢 {kw}**")
                                    st.metric(label="평균 검색 비율", value=f"{mean_val:.2f}%")
                                    st.metric(label="최대 검색 비율", value=f"{max_val:.2f}%")
                                    st.metric(label="최소 검색 비율", value=f"{min_val:.2f}%")
                                    
                        # 데이터 테이블 표시 및 다운로드
                        st.markdown("### 📋 수집된 상세 데이터")
                        pivot_df = df.pivot(index="날짜", columns="주제어", values="검색량비율").reset_index()
                        st.dataframe(pivot_df, use_container_width=True)
                        
                        # 다운로드 버튼
                        csv = pivot_df.to_csv(index=False).encode('utf-8-sig')
                        st.download_button(
                            label="📥 CSV 데이터 다운로드",
                            data=csv,
                            file_name=f"naver_trend_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
                except Exception as e:
                    st.error(f"데이터 수집 중 오류가 발생했습니다: {str(e)}")

# -*- coding: utf-8 -*-
"""
Streamlit 대시보드 공통 유틸리티 모듈

이 모듈은 대시보드 테마 설정, 공통 사이드바 렌더링, Plotly 레이아웃 설정
및 캐싱이 적용된 API 호출 함수를 제공합니다.
"""
import streamlit as st
import plotly.io as pio
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, Any, List
import naver_api

# Plotly 공통 디자인 템플릿 설정
def set_plotly_theme():
    """Plotly의 기본 디자인 테마를 설정합니다."""
    pio.templates["custom_theme"] = go.layout.Template(
        layout=go.Layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E0E0E0", family="Pretendard, sans-serif"),
            xaxis=dict(
                gridcolor="#2D2D2D",
                linecolor="#444444",
                zerolinecolor="#444444",
                showgrid=True
            ),
            yaxis=dict(
                gridcolor="#2D2D2D",
                linecolor="#444444",
                zerolinecolor="#444444",
                showgrid=True
            ),
            colorway=["#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#19D3F3", "#FF6692"]
        )
    )
    pio.templates.default = "custom_theme"

def render_sidebar() -> bool:
    """공통 사이드바를 렌더링하고 API 키 입력 여부를 반환합니다."""
    st.sidebar.markdown("### 🔑 NAVER API 설정")
    
    # Session State 초기화
    if "client_id" not in st.session_state:
        st.session_state["client_id"] = ""
    if "client_secret" not in st.session_state:
        st.session_state["client_secret"] = ""
        
    client_id = st.sidebar.text_input(
        "Client ID",
        value=st.session_state["client_id"],
        type="password",
        help="네이버 개발자 센터에서 발급받은 Client ID를 입력하세요."
    )
    client_secret = st.sidebar.text_input(
        "Client Secret",
        value=st.session_state["client_secret"],
        type="password",
        help="네이버 개발자 센터에서 발급받은 Client Secret을 입력하세요."
    )
    
    st.session_state["client_id"] = client_id
    st.session_state["client_secret"] = client_secret
    
    if not client_id or not client_secret:
        st.sidebar.warning("API 인증 키를 입력해 주세요.")
        return False
    
    st.sidebar.success("API 인증 키가 준비되었습니다.")
    return True

def parse_keywords(keyword_str: str) -> List[str]:
    """쉼표로 구분된 키워드 문자열을 리스트로 변환합니다."""
    if not keyword_str:
        return []
    return [k.strip() for k in keyword_str.split(",") if k.strip()]

def get_default_dates():
    """기본 검색 시작일(한 달 전)과 종료일(오늘)을 반환합니다."""
    end_date = datetime.today()
    start_date = end_date - timedelta(days=30)
    return start_date.date(), end_date.date()

# API 호출 캐싱 처리 (Client ID/Secret 및 입력값 기준 캐싱)
@st.cache_data(show_spinner=False)
def cached_get_search_trend(client_id: str, client_secret: str, **kwargs) -> Dict[str, Any]:
    return naver_api.get_search_trend(client_id, client_secret, **kwargs)

@st.cache_data(show_spinner=False)
def cached_get_shopping_trend(client_id: str, client_secret: str, **kwargs) -> Dict[str, Any]:
    return naver_api.get_shopping_trend(client_id, client_secret, **kwargs)

@st.cache_data(show_spinner=False)
def cached_search_blog(client_id: str, client_secret: str, **kwargs) -> Dict[str, Any]:
    return naver_api.search_blog(client_id, client_secret, **kwargs)

@st.cache_data(show_spinner=False)
def cached_search_news(client_id: str, client_secret: str, **kwargs) -> Dict[str, Any]:
    return naver_api.search_news(client_id, client_secret, **kwargs)

@st.cache_data(show_spinner=False)
def cached_search_cafe(client_id: str, client_secret: str, **kwargs) -> Dict[str, Any]:
    return naver_api.search_cafe(client_id, client_secret, **kwargs)

@st.cache_data(show_spinner=False)
def cached_search_shop(client_id: str, client_secret: str, **kwargs) -> Dict[str, Any]:
    return naver_api.search_shop(client_id, client_secret, **kwargs)

# -*- coding: utf-8 -*-
"""
네이버 API 통합 분석 대시보드 메인 엔트리포인트

이 파일은 Streamlit 멀티페이지 앱의 공통 설정을 초기화하고,
사이드바에서의 API 키 획득 및 st.navigation을 통한 페이지 전환 관리를 수행합니다.
"""
import streamlit as st
import utils

# 페이지 기본 설정
st.set_page_config(
    page_title="NAVER API 통합 분석 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Plotly 디자인 테마 설정
utils.set_plotly_theme()

# 공통 사이드바 렌더링 (API Client ID/Secret 설정)
has_keys = utils.render_sidebar()

def show_home():
    """대시보드 메인 소개 화면을 렌더링합니다."""
    st.markdown("# 🚀 NAVER API 통합 분석 대시보드")
    st.markdown("네이버 개발자 API를 활용하여 통합 검색 트렌드, 쇼핑 트렌드 및 분야별 검색 결과 데이터를 다각도로 분석하는 프리미엄 대시보드입니다.")
    st.write("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💡 주요 제공 기능")
        st.markdown(
            """
            *   **데이터랩 검색어 트렌드**: 최대 5개 검색어의 네이버 검색 추이를 연령/성별/기기별로 상세 분석합니다.
            *   **쇼핑 트렌드 (쇼핑인사이트)**: 네이버 쇼핑 카테고리 내에서 키워드별 클릭 점유율 트렌드를 추적합니다.
            *   **쇼핑 검색 결과 분석**: 검색 상품의 가격 분포(Box Plot) 및 브랜드/쇼핑몰 비중을 비교합니다.
            *   **블로그/카페/뉴스 검색 분석**: 텍스트 데이터 마이닝을 통해 주요 연관 키워드, 매체 점유율 및 작성 추이를 분석합니다.
            """
        )
        
    with col2:
        st.markdown("### 🔑 사용 가이드")
        st.info(
            """
            1.  **네이버 개발자 센터**에서 비로그인 방식 API 권한이 포함된 애플리케이션을 등록합니다.
            2.  발급받은 **Client ID**와 **Client Secret**을 왼쪽 메뉴의 비밀번호 입력창에 입력합니다.
            3.  상단 카테고리 분류에서 원하는 분석 대시보드를 선택해 실행합니다.
            4.  분석 실행 후, 각 차트의 인터랙티브 기능 및 데이터 다운로드 기능을 사용해 보세요.
            """
        )
        
    st.write("---")
    if has_keys:
        st.success("✅ API 키 인증이 완료되었습니다! 왼쪽 메뉴의 데이터랩 또는 검색 데이터 분석 대시보드 페이지를 선택하여 분석을 시작하세요.")
    else:
        st.warning("⚠️ 현재 API 키가 비어있거나 올바르지 않습니다. 왼쪽 메뉴에서 API 인증 키를 입력하시면 분석 기능이 활성화됩니다.")

# 멀티페이지 구조 정의 (st.navigation)
pg = st.navigation({
    "안내": [
        st.Page(show_home, title="대시보드 소개", icon="🏠")
    ],
    "데이터랩 트렌드 분석": [
        st.Page("pages/trend.py", title="검색어 트렌드 분석", icon="📈"),
        st.Page("pages/shopping_trend.py", title="쇼핑 트렌드 분석", icon="🛍️")
    ],
    "검색 데이터 다차원 분석": [
        st.Page("pages/shopping.py", title="쇼핑 검색 분석", icon="🛒"),
        st.Page("pages/blog.py", title="블로그 검색 분석", icon="📝"),
        st.Page("pages/cafe.py", title="카페글 검색 분석", icon="👥"),
        st.Page("pages/news.py", title="뉴스 검색 분석", icon="📰")
    ]
})

# 애플리케이션 실행
pg.run()

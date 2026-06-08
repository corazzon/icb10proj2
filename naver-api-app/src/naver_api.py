# -*- coding: utf-8 -*-
"""
네이버 오픈 API 통신 모듈

이 모듈은 네이버 검색어 트렌드, 쇼핑인사이트 키워드 트렌드, 블로그 검색,
뉴스 검색, 카페글 검색, 쇼핑 검색 API의 요청 및 응답 처리를 담당합니다.
"""
import requests
import urllib.parse
from typing import Dict, Any, List

def get_headers(client_id: str, client_secret: str) -> Dict[str, str]:
    """네이버 API 요청을 위한 헤더를 반환합니다."""
    return {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
        "Content-Type": "application/json"
    }

def handle_response(response: requests.Response) -> Dict[str, Any]:
    """API 응답을 처리하고 오류 발생 시 예외를 던집니다."""
    if response.status_code == 200:
        return response.json()
    else:
        try:
            err_data = response.json()
            err_msg = err_data.get("errorMessage", response.text)
            err_code = err_data.get("errorCode", str(response.status_code))
            raise ValueError(f"[{err_code}] {err_msg}")
        except Exception as e:
            if not isinstance(e, ValueError):
                raise ValueError(f"HTTP {response.status_code}: {response.text}")
            raise e

def get_search_trend(
    client_id: str,
    client_secret: str,
    start_date: str,
    end_date: str,
    time_unit: str,
    keyword_groups: List[Dict[str, Any]],
    device: str = "",
    gender: str = "",
    ages: List[str] = None
) -> Dict[str, Any]:
    """네이버 통합 검색어 트렌드 API를 호출합니다."""
    url = "https://openapi.naver.com/v1/datalab/search"
    headers = get_headers(client_id, client_secret)
    
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": time_unit,
        "keywordGroups": keyword_groups
    }
    if device:
        body["device"] = device
    if gender:
        body["gender"] = gender
    if ages:
        body["ages"] = ages
        
    response = requests.post(url, json=body, headers=headers)
    return handle_response(response)

def get_shopping_trend(
    client_id: str,
    client_secret: str,
    start_date: str,
    end_date: str,
    time_unit: str,
    category: str,
    keywords: List[Dict[str, Any]],
    device: str = "",
    gender: str = "",
    ages: List[str] = None
) -> Dict[str, Any]:
    """네이버 데이터랩 쇼핑인사이트 키워드별 트렌드 API를 호출합니다."""
    url = "https://openapi.naver.com/v1/datalab/shopping/category/keywords"
    headers = get_headers(client_id, client_secret)
    
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": time_unit,
        "category": category,
        "keyword": keywords
    }
    if device:
        body["device"] = device
    if gender:
        body["gender"] = gender
    if ages:
        body["ages"] = ages
        
    response = requests.post(url, json=body, headers=headers)
    return handle_response(response)

def search_blog(
    client_id: str,
    client_secret: str,
    query: str,
    display: int = 10,
    start: int = 1,
    sort: str = "sim"
) -> Dict[str, Any]:
    """네이버 블로그 검색 API를 호출합니다."""
    url = "https://openapi.naver.com/v1/search/blog.json"
    headers = get_headers(client_id, client_secret)
    params = {
        "query": query,
        "display": display,
        "start": start,
        "sort": sort
    }
    response = requests.get(url, params=params, headers=headers)
    return handle_response(response)

def search_news(
    client_id: str,
    client_secret: str,
    query: str,
    display: int = 10,
    start: int = 1,
    sort: str = "sim"
) -> Dict[str, Any]:
    """네이버 뉴스 검색 API를 호출합니다."""
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = get_headers(client_id, client_secret)
    params = {
        "query": query,
        "display": display,
        "start": start,
        "sort": sort
    }
    response = requests.get(url, params=params, headers=headers)
    return handle_response(response)

def search_cafe(
    client_id: str,
    client_secret: str,
    query: str,
    display: int = 10,
    start: int = 1,
    sort: str = "sim"
) -> Dict[str, Any]:
    """네이버 카페글 검색 API를 호출합니다."""
    url = "https://openapi.naver.com/v1/search/cafearticle.json"
    headers = get_headers(client_id, client_secret)
    params = {
        "query": query,
        "display": display,
        "start": start,
        "sort": sort
    }
    response = requests.get(url, params=params, headers=headers)
    return handle_response(response)

def search_shop(
    client_id: str,
    client_secret: str,
    query: str,
    display: int = 10,
    start: int = 1,
    sort: str = "sim",
    filter_type: str = "",
    exclude: str = ""
) -> Dict[str, Any]:
    """네이버 쇼핑 검색 API를 호출합니다."""
    url = "https://openapi.naver.com/v1/search/shop.json"
    headers = get_headers(client_id, client_secret)
    params = {
        "query": query,
        "display": display,
        "start": start,
        "sort": sort
    }
    if filter_type:
        params["filter"] = filter_type
    if exclude:
        params["exclude"] = exclude
        
    response = requests.get(url, params=params, headers=headers)
    return handle_response(response)

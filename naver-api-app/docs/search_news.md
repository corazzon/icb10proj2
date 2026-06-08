# 네이버 검색 - 뉴스 검색 API 명세

네이버 뉴스 검색 결과를 JSON 또는 XML 형식으로 조회하는 RESTful API 명세입니다.

---

## 1. API 기본 정보

* **요청 URL**:
  * **JSON**: `https://openapi.naver.com/v1/search/news.json`
  * **XML**: `https://openapi.naver.com/v1/search/news.xml`
* **프로토콜**: HTTPS
* **HTTP 메서드**: `GET`
* **일일 호출 한도**: 25,000회 (전체 검색 API 총합 한도)
* **인증 방식**: 비로그인 방식 (HTTP 헤더에 `X-Naver-Client-Id` 및 `X-Naver-Client-Secret` 필수 제공)

---

## 2. 요청 파라미터 (Query String)

| 파라미터 | 타입 | 필수 여부 | 기본값 | 허용 범위 및 설명 |
| :--- | :--- | :---: | :---: | :--- |
| `query` | string | **Y** | - | **검색어**: 검색하고자 하는 키워드이며, 반드시 UTF-8로 URL 인코딩하여 전송해야 합니다. |
| `display` | integer | N | 10 | **검색 결과 개수**: 한 번에 표시할 결과 수 (최대 100) |
| `start` | integer | N | 1 | **검색 시작 위치**: 검색 시작 순서 (최대 1000) |
| `sort` | string | N | sim | **결과 정렬 방식**<br>- `sim`: 정확도순 내림차순 정렬<br>- `date`: 날짜순 내림차순 정렬 |

### 요청 예시 (curl)
```bash
curl -G "https://openapi.naver.com/v1/search/news.json" \
  --data-urlencode "query=금리 인상" \
  -d "display=10" \
  -d "start=1" \
  -d "sort=date" \
  -H "X-Naver-Client-Id: YOUR_CLIENT_ID" \
  -H "X-Naver-Client-Secret: YOUR_CLIENT_SECRET"
```

---

## 3. 응답 데이터 명세 (JSON 기준)

| 필드 | 타입 | 설명 |
| :--- | :--- | :--- |
| `lastBuildDate` | string | 검색 결과를 생성한 시간 (RFC 822 형식) |
| `total` | integer | 총 검색 결과 개수 |
| `start` | integer | 검색 시작 위치 |
| `display` | integer | 한 번에 표시된 검색 결과 개수 |
| `items` | array(JSON) | 개별 검색 결과 목록 |
| `items.title` | string | 뉴스 기사의 제목. 검색어 매칭 영역은 `<b>...</b>` 태그로 감싸져 반환됩니다. |
| `items.originallink` | string | 언론사 공식 웹사이트의 원문 뉴스 URL |
| `items.link` | string | 해당 기사의 네이버 뉴스 URL. 네이버에 제공되지 않은 경우 원문 주소와 동일할 수 있습니다. |
| `items.description` | string | 뉴스 기사 내용을 요약한 텍스트. 검색어 매칭 영역은 `<b>...</b>` 태그로 감싸집니다. |
| `items.pubDate` | string | 뉴스 기사가 네이버에 노출되거나 원문이 배포된 날짜 및 시간 (RFC 822 형식) |

### 응답 JSON 예시
```json
{
  "lastBuildDate": "Mon, 08 Jun 2026 20:00:00 +0900",
  "total": 5678,
  "start": 1,
  "display": 1,
  "items": [
    {
      "title": "한국은행, 기준<b>금리 인상</b> 여부 동결 가닥",
      "originallink": "https://www.newsplatform.com/news/12345",
      "link": "https://n.news.naver.com/mnews/article/001/0012345",
      "description": "한국은행 금융통화위원회가 이번 정기 회의에서 기준 <b>금리 인상</b> 여부를 다각도로 검토하고...",
      "pubDate": "Mon, 08 Jun 2026 09:00:00 +0900"
    }
  ]
}
```

---

## 4. 관련 에러 코드
* **SE01** (HTTP 400): 잘못된 쿼리 요청 (인코딩 에러 및 파라미터 규격 불일치)
* **SE02** (HTTP 400): `display` 파라미터 범위 이탈
* **SE03** (HTTP 400): `start` 파라미터 범위 이탈
* **SE04** (HTTP 400): `sort` 파라미터 값 설정 오류
* **SE06** (HTTP 400): 잘못된 형식의 인코딩 (UTF-8 인코딩이 아닌 경우)

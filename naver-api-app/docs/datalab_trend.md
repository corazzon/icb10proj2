# 네이버 데이터랩 - 통합 검색어 트렌드 API 명세

주제어 및 그 하위 검색어들에 대한 네이버 통합검색 내 검색 추이 데이터를 조회할 수 있는 RESTful API 명세입니다.

---

## 1. API 기본 정보

* **요청 URL**: `https://openapi.naver.com/v1/datalab/search`
* **프로토콜**: HTTPS
* **HTTP 메서드**: `POST`
* **Content-Type**: `application/json`
* **일일 호출 한도**: 1,000회
* **인증 방식**: 비로그인 방식 (HTTP 헤더에 `X-Naver-Client-Id` 및 `X-Naver-Client-Secret` 필수 제공)

---

## 2. 요청 파라미터 (Request Body JSON)

| 파라미터 | 타입 | 필수 여부 | 설명 |
| :--- | :--- | :---: | :--- |
| `startDate` | string | **Y** | 조회 기간 시작 날짜 (`yyyy-mm-dd` 형식, 2016-01-01부터 지원) |
| `endDate` | string | **Y** | 조회 기간 종료 날짜 (`yyyy-mm-dd` 형식) |
| `timeUnit` | string | **Y** | 데이터 추출 구간 단위 (`date`: 일간, `week`: 주간, `month`: 월간) |
| `keywordGroups` | array(JSON) | **Y** | 주제어와 주제어에 포함될 세부 검색어 쌍의 배열 (최대 5개 그룹 설정 가능) |
| `keywordGroups.groupName` | string | **Y** | 주제어명 (그룹을 대표하는 이름) |
| `keywordGroups.keywords` | array(string) | **Y** | 주제어에 속하는 검색어 목록 (그룹별 최대 20개) |
| `device` | string | N | 검색 기기 필터링 (`pc`: PC 검색량만, `mo`: 모바일 검색량만, 미지정 시 전체 기기) |
| `gender` | string | N | 검색 성별 필터링 (`m`: 남성, `f`: 여성, 미지정 시 전체) |
| `ages` | array(string) | N | 검색 연령대 필터링 (미지정 시 전체 연령. `1`: 0~12세, `2`: 13~18세, `3`: 19~24세, `4`: 25~29세, `5`: 30~34세, `6`: 35~39세, `7`: 40~44세, `8`: 45~49세, `9`: 50~54세, `10`: 55~59세, `11`: 60세 이상) |

### 요청 JSON 예시
```json
{
  "startDate": "2023-01-01",
  "endDate": "2023-12-31",
  "timeUnit": "month",
  "keywordGroups": [
    {
      "groupName": "인공지능",
      "keywords": ["AI", "인공지능", "Artificial Intelligence"]
    },
    {
      "groupName": "메타버스",
      "keywords": ["메타버스", "metaverse"]
    }
  ],
  "device": "pc",
  "gender": "f",
  "ages": ["3", "4"]
}
```

---

## 3. 응답 데이터 명세 (Response Body JSON)

조회가 성공하면 상대적 비율로 환산된 데이터셋을 반환합니다. 비율(ratio)은 조회 기간 및 그룹 결과 중 최댓값을 100으로 기준하여 산정됩니다.

| 필드 | 타입 | 설명 |
| :--- | :--- | :--- |
| `startDate` | string | 조회 기간의 시작 날짜 (`yyyy-mm-dd` 형식) |
| `endDate` | string | 조회 기간의 종료 날짜 (`yyyy-mm-dd` 형식) |
| `timeUnit` | string | 데이터 추출 구간 단위 |
| `results` | array(JSON) | 주제어별 조회 결과 그룹 |
| `results.title` | string | 주제어명 |
| `results.keywords` | array(string) | 주제어 아래 포함된 검색어 리스트 |
| `results.data` | array(JSON) | 시계열 통계 데이터 목록 |
| `results.data.period` | string | 해당 구간의 시작 날짜 (`yyyy-mm-dd` 형식) |
| `results.data.ratio` | number | 해당 구간의 상대적 검색량 비율 (0.0 ~ 100.0) |

### 응답 JSON 예시
```json
{
  "startDate": "2023-01-01",
  "endDate": "2023-03-31",
  "timeUnit": "month",
  "results": [
    {
      "title": "인공지능",
      "keywords": ["AI", "인공지능", "Artificial Intelligence"],
      "data": [
        { "period": "2023-01-01", "ratio": 45.12 },
        { "period": "2023-02-01", "ratio": 100.00 },
        { "period": "2023-03-01", "ratio": 88.45 }
      ]
    }
  ]
}
```

---

## 4. API 에러 및 특이사항
* **403 Forbidden**: 네이버 개발자 센터에서 '데이터랩(검색어트렌드)' API 권한을 활성화했는지 확인해야 합니다.
* **400 Bad Request**: 파라미터 날짜 규격(`yyyy-mm-dd`)이 올바른지, keywordGroups의 개수 및 내부 배열이 필수 조건을 충족하는지 확인이 필요합니다.

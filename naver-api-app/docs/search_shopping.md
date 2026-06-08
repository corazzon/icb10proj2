# 네이버 검색 - 쇼핑 검색 API 명세

네이버 쇼핑 상품 검색 결과를 JSON 또는 XML 형식으로 조회하는 RESTful API 명세입니다.

---

## 1. API 기본 정보

* **요청 URL**:
  * **JSON**: `https://openapi.naver.com/v1/search/shop.json`
  * **XML**: `https://openapi.naver.com/v1/search/shop.xml`
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
| `sort` | string | N | sim | **결과 정렬 방식**<br>- `sim`: 정확도순 내림차순 정렬<br>- `date`: 날짜순 내림차순 정렬<br>- `asc`: 가격순 오름차순 정렬 (최저가순)<br>- `dsc`: 가격순 내림차순 정렬 (최고가순) |
| `filter` | string | N | - | **상품 유형 필터**<br>- `naverpay`: 네이버페이 연동 상품만 노출 |
| `exclude` | string | N | - | **제외할 상품 유형**: `{option}:{option}` 형태로 복수 설정 가능 (예: `exclude=used:cbshop`) <br>- `used`: 중고 상품 제외<br>- `rental`: 렌탈 상품 제외<br>- `cbshop`: 해외직구/구매대행 상품 제외 |

### 요청 예시 (curl)
```bash
curl -G "https://openapi.naver.com/v1/search/shop.json" \
  --data-urlencode "query=무선 이어폰" \
  -d "display=20" \
  -d "sort=asc" \
  -d "exclude=used" \
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
| `items.title` | string | 상품 이름. 검색어 매칭 영역은 `<b>...</b>` 태그로 감싸져 반환됩니다. |
| `items.link` | string | 상품 구매 또는 상세 보기 페이지 URL |
| `items.image` | string | 상품 섬네일 이미지 주소 URL |
| `items.lprice` | integer | 최저가 (최저가 정보가 없을 경우 0 반환, 가격비교가 불가한 경우 상품 자체 가격을 의미) |
| `items.hprice` | integer | 최고가 (최고가 정보가 없거나 가격비교가 안 되는 경우 0 반환) |
| `items.mallName` | string | 상품을 판매하는 쇼핑몰명 (쇼핑몰명이 제공되지 않으면 '네이버' 반환) |
| `items.productId` | integer | 네이버 쇼핑 상품 ID |
| `items.productType` | integer | 상품군 및 가격비교 매칭 타입 (1 ~ 12)<br>- `1`: 일반상품 (가격비교 매칭)<br>- `2`: 일반상품 (가격비교 비매칭 일반상품)<br>- `3`: 일반상품 (가격비교 매칭 일반상품)<br>- `4`~`6`: 중고 상품 관련 타입<br>- `7`~`9`: 단종 상품 관련 타입<br>- `10`~`12`: 판매 예정 상품 관련 타입 |
| `items.maker` | string | 제조사명 |
| `items.brand` | string | 브랜드명 |
| `items.category1` | string | 상품 대분류 카테고리 |
| `items.category2` | string | 상품 중분류 카테고리 |
| `items.category3` | string | 상품 소분류 카테고리 |
| `items.category4` | string | 상품 세분류 카테고리 |

### 응답 JSON 예시
```json
{
  "lastBuildDate": "Mon, 08 Jun 2026 20:00:00 +0900",
  "total": 98765,
  "start": 1,
  "display": 1,
  "items": [
    {
      "title": "A사 <b>무선 이어폰</b> 프로 노이즈캔슬링",
      "link": "https://search.shopping.naver.com/catalog/12345678",
      "image": "https://shopping-phinf.pstatic.net/main_1234567/12345678.jpg",
      "lprice": 189000,
      "hprice": 220000,
      "mallName": "네이버 쇼핑윈도",
      "productId": 12345678,
      "productType": 1,
      "maker": "A사",
      "brand": "A사",
      "category1": "디지털/가전",
      "category2": "음향가전",
      "category3": "이어폰",
      "category4": "무선이어폰"
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

FastAPI 프로젝트 폴더 구조는 규모와 복잡도에 따라 달라질 수 있지만, 일반적으로 아래와 같은 폴더 구조가 유지 관리와 확장성에 좋습니다. 각 폴더의 역할과 기본적인 구조를 예시로 보여드리겠습니다.

1. 기본 폴더 구조
plaintext
코드 복사

my_fastapi_project/
├── app/
│   ├── __init__.py
│   ├── main.py                   
│   ├── api/                      
│   │   ├── __init__.py
│   │   ├── api_v1/               
│   │   │    ├── __init__.py
│   │   │    ├── endpoints/        
│   │   │    │   ├── __init__.py
│   │   │    │   └── users.py      
│   │   │    └── dependencies.py   
│   ├── core/                    
│   │   ├── __init__.py
│   │   ├── config.py             
│   │   └── security.py           
│   ├── crud/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── db/                       
│   │   ├── __init__.py
│   │   ├── base.py               
│   │   └── session.py             
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── schemas/                  
│   │   ├── __init__.py
│   │   └── user.py               
│   ├── utils/                    
│   │   ├── __init__.py
│   │   ├── dependencies.py  
│   │   └── helpers.py            
└── tests/                        
    ├── __init__.py
    ├── test_main.py              
    └── api/                      
        ├── __init__.py
        └── test_users.py         


my_fastapi_project/
├── app/
│   ├── __init__.py
│   ├── main.py                   # FastAPI 앱의 진입점
│   ├── api/                      # 라우트 관리
│   │   ├── __init__.py
│   │   ├── api_v1/               # API 버전 1 (v1)
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/        # 엔드포인트 폴더
│   │   │   │   ├── __init__.py
│   │   │   │   └── users.py      # 사용자 관련 엔드포인트 예시
│   │   │   └── dependencies.py   # 종속성 및 공통 의존성 관리
│   ├── core/                     # 설정 및 핵심 기능
│   │   ├── __init__.py
│   │   ├── config.py             # 환경 설정 및 환경 변수 로드
│   │   └── security.py           # 인증 및 보안 관련 기능
│   ├── db/                       # 데이터베이스 관련 모듈
│   │   ├── __init__.py
│   │   ├── base.py               # 데이터베이스 연결 설정 및 세션 관리
│   │   ├── models.py             # 데이터베이스 모델 정의
│   │   └── crud.py               # CRUD 기능 정의
│   ├── schemas/                  # 데이터 스키마
│   │   ├── __init__.py
│   │   └── user.py               # 사용자 관련 스키마 예시
│   ├── services/                 # 서비스 레이어
│   │   ├── __init__.py
│   │   └── user_service.py       # 사용자 관련 비즈니스 로직
│   ├── utils/                    # 유틸리티 함수
│   │   ├── __init__.py
│   │   └── helpers.py            # 헬퍼 함수들
└── tests/                        # 테스트 파일
    ├── __init__.py
    ├── test_main.py              # 기본 테스트
    └── api/                      # API 별 테스트 모듈
        ├── __init__.py
        └── test_users.py         # 사용자 엔드포인트 테스트
2. 폴더별 역할 설명
app/main.py: FastAPI 앱의 진입점 파일입니다. uvicorn으로 이 파일을 실행해 서버를 시작합니다.

app/api/: API 라우트를 모아 관리합니다. 각 라우트를 별도의 파일로 관리하는 것이 좋으며, 여러 버전의 API가 필요한 경우 api_v1, api_v2 식으로 폴더를 분리해 사용할 수 있습니다.

app/core/: 앱의 설정 및 핵심적인 기능을 다룹니다. 예를 들어, config.py에는 환경 변수나 설정 파일을 로드하는 기능을 넣고, security.py에는 인증 관련 기능(JWT 토큰 생성 등)을 넣습니다.

app/db/: 데이터베이스 연결 및 관리와 관련된 코드를 둡니다. models.py에 SQLAlchemy 등으로 데이터베이스 모델을 정의하고, crud.py에 CRUD 기능을 정의합니다. 데이터베이스 연결 설정은 base.py에서 처리합니다.

app/schemas/: Pydantic을 이용한 데이터 검증 및 직렬화 스키마를 정의합니다. 예를 들어, user.py 파일에 사용자의 요청 및 응답 스키마를 정의합니다.

app/services/: 비즈니스 로직을 포함한 서비스 레이어입니다. 예를 들어 user_service.py에서는 사용자 등록, 비밀번호 검증 등의 로직을 처리합니다. 서비스 레이어는 엔드포인트에서 직접적인 비즈니스 로직을 분리하는 데 유용합니다.

app/utils/: 프로젝트 전반에서 재사용될 수 있는 헬퍼 함수들을 둡니다. 예를 들어, 날짜 포맷 변경, 문자열 변환 등의 유틸리티 함수를 여기에 정의할 수 있습니다.

tests/: 테스트 파일을 모아 두는 폴더입니다. API 엔드포인트, 모델, 서비스 등의 유닛 테스트를 각 기능별로 나눠 작성하여 유지보수에 유리하게 구성할 수 있습니다.

### 파일서버 nginx 설정 site-available 폴더에 다음과 같이 설정합니다.
server {
        listen 1021 default_server;
        listen [::]:1021 default_server;
        server_name api2410.ebesesk.synology.me;

        location / {
                #include proxy_params;
                #limit_except GET POST {
                #        deny all;
                #}
                #add_header 'Access-Control-Allow-Origin' '*';
                proxy_pass http://localhost:8000;
                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection upgrade;
                proxy_set_header Host $host;
                proxy_set_header Accept-Encoding gzip;
                proxy_set_header X-Forwarded-Proto $scheme;
        }

        # 이미지 파일 제공 설정
        location /images/ {
                auth_request /auth/nginxauth;
                alias /home/manga/;
                #proxy_pass http://localhost:8000;
                # 클라이언트의 Authorization 헤더를 FastAPI 인증 엔드포인트로 전달
                proxy_set_header Authorization $http_authorization;
                #autoindex on;  # 디버깅용으로, 실제 사용 시 제거 가능

                # 모든 요청에 대해 CORS 헤더 추가
                add_header 'Access-Control-Allow-Origin' 'https://k2410.ebesesk.syn>
                add_header 'Access-Control-Allow-Methods' 'GET, OPTIONS' always;
                add_header 'Access-Control-Allow-Headers' 'Authorization, Content-T>

                # 프리플라이트 요청에 대한 응답 설정
                if ($request_method = 'OPTIONS') {
                        add_header 'Access-Control-Allow-Origin' 'https://k2410.ebe>
                        add_header 'Access-Control-Allow-Methods' 'GET, OPTIONS' al>
                        add_header 'Access-Control-Allow-Headers' 'Authorization, C>
                        add_header 'Access-Control-Max-Age' 86400 always;
                        return 204;
                }
        }



        # JWT 검증 요청을 FastAPI의 /auth 엔드포인트로 전달
        location = /auth/nginxauth {
                internal;
                proxy_pass http://localhost:8000/auth/nginxauth;
                proxy_set_header Host $host;
                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection upgrade;
                proxy_set_header Accept-Encoding gzip;
                proxy_set_header X-Forwarded-Proto $scheme;

                #proxy_method   GET;
                #proxy_pass http://localhost:8000/auth/nginxauth;
                #proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                #proxy_set_header X-Forwarded-Proto $scheme;


        }
}

### manga 데이터 베이스

id
folder
tags
images_path
create_date
file_daate
update_date

page
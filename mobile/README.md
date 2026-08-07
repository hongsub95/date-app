# 나의 일기(내일) 모바일

Expo 기반 React Native 앱입니다. 백엔드 계약은 `../docs/API_SPEC.md`를 따르며,
구현된 API의 최종 기준은 실행 중인 서버의 `/openapi.json`입니다.

## 실행

1. `.env.example`을 `.env.local`로 복사합니다.
2. 실행 기기에 맞게 `EXPO_PUBLIC_API_BASE_URL`을 설정합니다.
3. 백엔드 서버를 실행합니다.
4. `npm.cmd start`를 실행합니다.

| 실행 환경 | API 호스트 |
|---|---|
| Android 에뮬레이터 | `http://10.0.2.2:8000/api/v1` |
| iOS 시뮬레이터 | `http://localhost:8000/api/v1` |
| 실제 기기 | `http://{PC의 공유기 IP}:8000/api/v1` |

앱 인증은 `/auth/*` JWT만 사용합니다. access/refresh token은 SecureStore에 저장하며,
`401 + UNAUTHORIZED` 응답에서 refresh token을 회전한 뒤 원래 요청을 한 번 재시도합니다.

현재 인증과 메뉴는 실제 API를 호출합니다. 스페이스·일정·장소·일기·사진은 백엔드 구현
전까지 `docs/API_SPEC.md` 응답 형태를 따르는 mock repository를 사용합니다.

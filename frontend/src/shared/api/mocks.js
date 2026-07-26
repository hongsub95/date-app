export const MOCK_USER = {
  id: '1',
  nickname: '홍길동',
  email: 'test@example.com',
}

export const MOCK_SCHEDULES = [
  {
    id: '1',
    title: '한강 피크닉',
    start_at: '2026-07-26T14:00:00',
    end_at: '2026-07-26T18:00:00',
    status: 'planned',
    places: [
      { id: '1', sort_order: 1, name: '여의도 한강공원', address: '서울 영등포구 여의동로 330', memo: '돗자리 챙기기', visited: false },
      { id: '2', sort_order: 2, name: '더현대 서울', address: '서울 영등포구 여의대로 108', memo: '', visited: false },
    ],
    diary: null,
  },
  {
    id: '2',
    title: '성수 카페 투어',
    start_at: '2026-07-20T12:00:00',
    end_at: '2026-07-20T17:00:00',
    status: 'completed',
    places: [
      { id: '3', sort_order: 1, name: '어니언 성수', address: '서울 성동구 아차산로9길 8', memo: '사진 많이 찍기', visited: true },
      { id: '4', sort_order: 2, name: '블루보틀 성수', address: '서울 성동구 왕십리로2길 20-12', memo: '', visited: true },
    ],
    diary: {
      content: '오늘 성수 카페 투어 너무 좋았다. 어니언은 역시 분위기 최고!',
      mood: '😊',
    },
  },
  {
    id: '3',
    title: '북촌 한옥마을 산책',
    start_at: '2026-07-15T10:00:00',
    end_at: '2026-07-15T14:00:00',
    status: 'completed',
    places: [
      { id: '5', sort_order: 1, name: '북촌 한옥마을', address: '서울 종로구 북촌로', memo: '', visited: true },
      { id: '6', sort_order: 2, name: '삼청동 카페거리', address: '서울 종로구 삼청동', memo: '', visited: true },
    ],
    diary: {
      content: '한옥마을 골목길이 너무 예뻤다. 다음엔 가을에 오고 싶다.',
      mood: '😌',
    },
  },
  {
    id: '4',
    title: '강남 맛집 탐방',
    start_at: '2026-08-03T18:00:00',
    end_at: '2026-08-03T21:00:00',
    status: 'planned',
    places: [
      { id: '7', sort_order: 1, name: '봉피양 강남점', address: '서울 강남구 테헤란로 151', memo: '예약 확인하기', visited: false },
    ],
    diary: null,
  },
]

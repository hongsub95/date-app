import { useMemo, useState } from 'react'
import {
  ArrowPathIcon,
  CalendarDaysIcon,
  CameraIcon,
  CheckCircleIcon,
  ClockIcon,
  MapPinIcon,
  PencilSquareIcon,
  PlusIcon,
  Squares2X2Icon,
  UserGroupIcon,
} from '@heroicons/react/24/outline'
import {
  CheckCircleIcon as CheckCircleSolidIcon,
  MapPinIcon as MapPinSolidIcon,
} from '@heroicons/react/24/solid'
import '../../App.css'

const schedules = [
  {
    id: 1,
    date: '07.26',
    weekday: '일',
    title: '성수 카페 투어',
    time: '13:00 - 18:30',
    status: '오늘',
    mood: '기록 대기',
    participants: ['나', '민지'],
    places: [
      { name: '오르에르 성수', time: '13:00', note: '창가 자리 요청', done: true },
      { name: '서울숲 산책로', time: '15:10', note: '사진 스팟 저장', done: false },
      { name: '누데이크 성수', time: '17:00', note: '케이크 포장', done: false },
    ],
    diary: '카페 동선은 좋았고 서울숲에서 사진을 더 남기면 좋겠다.',
  },
  {
    id: 2,
    date: '07.29',
    weekday: '수',
    title: '한남 저녁 약속',
    time: '18:30 - 21:30',
    status: '예정',
    mood: '장소 확정',
    participants: ['나', '준호'],
    places: [
      { name: '파이프그라운드', time: '18:30', note: '예약 확인', done: false },
      { name: '리움 미술관 앞', time: '20:20', note: '야간 산책', done: false },
    ],
    diary: '',
  },
  {
    id: 3,
    date: '07.21',
    weekday: '화',
    title: '북촌 기록 산책',
    time: '10:30 - 15:00',
    status: '완료',
    mood: '일기 완료',
    participants: ['나'],
    places: [
      { name: '북촌 한옥마을', time: '10:30', note: '골목 사진', done: true },
      { name: '어니언 안국', time: '13:00', note: '빵 사진 첨부', done: true },
    ],
    diary: '혼자 걷기 좋은 날이었다. 다음에는 평일 오전에 다시 가기.',
  },
]

const calendarDays = [
  ['20', '기록 1'],
  ['21', '완료 1'],
  ['22', ''],
  ['23', ''],
  ['24', ''],
  ['25', ''],
  ['26', '오늘 1'],
  ['27', ''],
  ['28', ''],
  ['29', '예정 1'],
  ['30', ''],
  ['31', ''],
]

const metrics = [
  { label: '이번 달 일정', value: '12', trend: '+3' },
  { label: '저장 장소', value: '46', trend: '+8' },
  { label: '작성 일기', value: '9', trend: '+2' },
  { label: '공유 일정', value: '4', trend: '+1' },
]

export default function PrototypePage() {
  const [mode, setMode] = useState('mobile')
  const [selectedId, setSelectedId] = useState(1)
  const selected = useMemo(
    () => schedules.find((schedule) => schedule.id === selectedId),
    [selectedId],
  )

  return (
    <main className="min-h-screen bg-[#f7f4ef] text-stone-950">
      <div className="mx-auto flex min-h-screen w-full max-w-7xl flex-col px-4 py-4 sm:px-6 lg:px-8">
        <Header mode={mode} onModeChange={setMode} />
        {mode === 'mobile' ? (
          <MobilePrototype selected={selected} onSelect={setSelectedId} />
        ) : (
          <WebPrototype selected={selected} onSelect={setSelectedId} />
        )}
      </div>
    </main>
  )
}

function Header({ mode, onModeChange }) {
  return (
    <header className="mb-4 flex flex-col gap-4 rounded-lg border border-stone-200 bg-white px-4 py-3 shadow-sm sm:flex-row sm:items-center sm:justify-between">
      <div>
        <p className="text-sm font-semibold text-emerald-700">나의 일기(내일)</p>
        <h1 className="text-xl font-bold sm:text-2xl">앱/웹 시연 프로토타입</h1>
      </div>
      <div className="grid grid-cols-2 rounded-lg bg-stone-100 p-1 text-sm font-semibold">
        <button
          className={`rounded-md px-4 py-2 transition ${mode === 'mobile' ? 'bg-white text-stone-950 shadow-sm' : 'text-stone-500'}`}
          onClick={() => onModeChange('mobile')}
          type="button"
        >
          모바일 앱
        </button>
        <button
          className={`rounded-md px-4 py-2 transition ${mode === 'web' ? 'bg-white text-stone-950 shadow-sm' : 'text-stone-500'}`}
          onClick={() => onModeChange('web')}
          type="button"
        >
          웹 버전
        </button>
      </div>
    </header>
  )
}

function MobilePrototype({ selected, onSelect }) {
  return (
    <section className="grid flex-1 gap-5 lg:grid-cols-[420px_1fr]">
      <div className="mx-auto w-full max-w-[420px] rounded-[34px] border-[10px] border-stone-900 bg-stone-900 shadow-2xl">
        <div className="h-[760px] overflow-hidden rounded-[24px] bg-[#fbfaf7]">
          <MobileTopBar />
          <div className="h-[708px] overflow-y-auto px-4 pb-6">
            <TodayCard selected={selected} />
            <CalendarStrip selected={selected} onSelect={onSelect} />
            <PlaceTimeline places={selected.places} />
            <DiaryComposer selected={selected} />
            <MobileNav />
          </div>
        </div>
      </div>
      <DesignNotes />
    </section>
  )
}

function MobileTopBar() {
  return (
    <div className="flex items-center justify-between border-b border-stone-200 bg-white px-4 py-3">
      <div>
        <p className="text-xs font-semibold text-stone-500">2026년 7월</p>
        <p className="text-lg font-bold">내일 준비하기</p>
      </div>
      <button className="grid h-10 w-10 place-items-center rounded-full bg-emerald-700 text-white" type="button">
        <PlusIcon className="h-5 w-5" />
      </button>
    </div>
  )
}

function TodayCard({ selected }) {
  return (
    <article className="mt-4 overflow-hidden rounded-lg border border-stone-200 bg-white shadow-sm">
      <div className="relative h-36 bg-stone-800">
        <div className="absolute inset-0 map-visual" />
        <div className="absolute left-4 top-4 rounded-md bg-white px-3 py-2 shadow-sm">
          <p className="text-xs font-semibold text-stone-500">선택한 일정</p>
          <h2 className="text-lg font-bold">{selected.title}</h2>
        </div>
        <div className="absolute bottom-4 left-4 right-4 flex items-center justify-between rounded-md bg-stone-950/80 px-3 py-2 text-white">
          <span className="text-sm font-semibold">{selected.time}</span>
          <span className="rounded bg-amber-300 px-2 py-1 text-xs font-bold text-stone-950">{selected.status}</span>
        </div>
      </div>
      <div className="grid grid-cols-3 divide-x divide-stone-200 text-center">
        <SummaryCell label="장소" value={`${selected.places.length}곳`} />
        <SummaryCell label="참여" value={`${selected.participants.length}명`} />
        <SummaryCell label="상태" value={selected.mood} />
      </div>
    </article>
  )
}

function SummaryCell({ label, value }) {
  return (
    <div className="px-2 py-3">
      <p className="text-xs font-semibold text-stone-500">{label}</p>
      <p className="mt-1 truncate text-sm font-bold">{value}</p>
    </div>
  )
}

function CalendarStrip({ selected, onSelect }) {
  return (
    <section className="mt-5">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-base font-bold">캘린더</h2>
        <button className="text-sm font-semibold text-emerald-700" type="button">월 보기</button>
      </div>
      <div className="grid grid-cols-4 gap-2">
        {schedules.map((schedule) => (
          <button
            className={`rounded-lg border px-3 py-3 text-left transition ${
              selected.id === schedule.id
                ? 'border-emerald-700 bg-emerald-700 text-white'
                : 'border-stone-200 bg-white text-stone-800'
            }`}
            key={schedule.id}
            onClick={() => onSelect(schedule.id)}
            type="button"
          >
            <p className="text-xs font-semibold opacity-80">{schedule.weekday}</p>
            <p className="mt-1 text-lg font-bold">{schedule.date}</p>
            <p className="mt-2 truncate text-xs font-semibold">{schedule.status}</p>
          </button>
        ))}
      </div>
    </section>
  )
}

function PlaceTimeline({ places }) {
  return (
    <section className="mt-5 rounded-lg border border-stone-200 bg-white p-4 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-base font-bold">장소 순서</h2>
        <button className="grid h-9 w-9 place-items-center rounded-md border border-stone-200" type="button">
          <ArrowPathIcon className="h-5 w-5" />
        </button>
      </div>
      <div className="space-y-3">
        {places.map((place, index) => (
          <div className="grid grid-cols-[32px_1fr] gap-3" key={place.name}>
            <div className="flex flex-col items-center">
              <div className={`grid h-8 w-8 place-items-center rounded-full ${place.done ? 'bg-emerald-700 text-white' : 'bg-stone-100 text-stone-500'}`}>
                {place.done ? <CheckCircleSolidIcon className="h-5 w-5" /> : <span className="text-sm font-bold">{index + 1}</span>}
              </div>
              {index < places.length - 1 && <div className="mt-2 h-10 w-px bg-stone-200" />}
            </div>
            <div className="min-w-0 rounded-md bg-stone-50 px-3 py-2">
              <div className="flex items-center justify-between gap-2">
                <p className="truncate font-bold">{place.name}</p>
                <p className="shrink-0 text-xs font-semibold text-stone-500">{place.time}</p>
              </div>
              <p className="mt-1 truncate text-sm text-stone-500">{place.note}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

function DiaryComposer({ selected }) {
  return (
    <section className="mt-5 rounded-lg border border-stone-200 bg-white p-4 shadow-sm">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-base font-bold">오늘의 일기</h2>
        <button className="flex items-center gap-1 rounded-md bg-stone-900 px-3 py-2 text-xs font-bold text-white" type="button">
          <CameraIcon className="h-4 w-4" />
          사진
        </button>
      </div>
      <p className="min-h-[76px] rounded-md bg-[#f7f4ef] p-3 text-sm leading-6 text-stone-700">
        {selected.diary || '약속이 끝나면 사진과 글로 하루를 기록하세요.'}
      </p>
      <div className="mt-3 grid grid-cols-3 gap-2">
        <div className="photo-tile bg-[#d9eadf]" />
        <div className="photo-tile bg-[#e8d7c4]" />
        <div className="photo-tile bg-[#cfd8e3]" />
      </div>
    </section>
  )
}

function MobileNav() {
  const items = [
    ['캘린더', CalendarDaysIcon],
    ['장소', MapPinIcon],
    ['기록', PencilSquareIcon],
    ['설정', Squares2X2Icon],
  ]

  return (
    <nav className="sticky bottom-0 mt-5 grid grid-cols-4 rounded-lg border border-stone-200 bg-white p-2 shadow-lg">
      {items.map(([label, Icon], index) => (
        <button className={`flex flex-col items-center gap-1 rounded-md py-2 text-xs font-semibold ${index === 0 ? 'bg-emerald-50 text-emerald-800' : 'text-stone-500'}`} key={label} type="button">
          <Icon className="h-5 w-5" />
          {label}
        </button>
      ))}
    </nav>
  )
}

function DesignNotes() {
  return (
    <aside className="rounded-lg border border-stone-200 bg-white p-5 shadow-sm">
      <h2 className="text-xl font-bold">모바일 앱 구성</h2>
      <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-1">
        <Note icon={CalendarDaysIcon} title="캘린더 중심 진입" text="오늘, 예정, 완료 일정을 날짜 기준으로 빠르게 전환합니다." />
        <Note icon={MapPinIcon} title="장소 기반 일정" text="한 일정 안에 여러 장소를 사용자 순서대로 저장하고 방문 상태를 표시합니다." />
        <Note icon={CameraIcon} title="사진과 일기" text="완료된 하루를 사진, 장소 메모, 일기 본문으로 남깁니다." />
        <Note icon={UserGroupIcon} title="혼자/함께 사용" text="MVP에서는 참여자 표시까지 두고 초대 편집은 이후 단계로 확장합니다." />
      </div>
    </aside>
  )
}

function Note({ icon: Icon, title, text }) {
  return (
    <div className="rounded-lg border border-stone-200 bg-stone-50 p-4">
      <Icon className="h-6 w-6 text-emerald-700" />
      <p className="mt-3 font-bold">{title}</p>
      <p className="mt-1 text-sm leading-6 text-stone-600">{text}</p>
    </div>
  )
}

function WebPrototype({ selected, onSelect }) {
  return (
    <section className="grid flex-1 gap-4 lg:grid-cols-[240px_1fr]">
      <WebSidebar />
      <div className="grid gap-4 xl:grid-cols-[1fr_380px]">
        <div className="space-y-4">
          <MetricGrid />
          <WebCalendar onSelect={onSelect} selected={selected} />
          <WebMap selected={selected} />
        </div>
        <WebDetail selected={selected} />
      </div>
    </section>
  )
}

function WebSidebar() {
  const items = [
    ['대시보드', Squares2X2Icon],
    ['캘린더', CalendarDaysIcon],
    ['장소 관리', MapPinIcon],
    ['기록 관리', PencilSquareIcon],
  ]

  return (
    <aside className="rounded-lg border border-stone-200 bg-white p-4 shadow-sm">
      <div className="mb-6 rounded-lg bg-stone-900 p-4 text-white">
        <p className="text-sm font-semibold text-emerald-200">내일 workspace</p>
        <p className="mt-2 text-lg font-bold">홍섭님의 일정</p>
      </div>
      <nav className="space-y-1">
        {items.map(([label, Icon], index) => (
          <button className={`flex w-full items-center gap-3 rounded-md px-3 py-3 text-left text-sm font-semibold ${index === 0 ? 'bg-emerald-50 text-emerald-800' : 'text-stone-600 hover:bg-stone-50'}`} key={label} type="button">
            <Icon className="h-5 w-5" />
            {label}
          </button>
        ))}
      </nav>
    </aside>
  )
}

function MetricGrid() {
  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {metrics.map((metric) => (
        <article className="rounded-lg border border-stone-200 bg-white p-4 shadow-sm" key={metric.label}>
          <p className="text-sm font-semibold text-stone-500">{metric.label}</p>
          <div className="mt-3 flex items-end justify-between">
            <p className="text-3xl font-bold">{metric.value}</p>
            <p className="rounded bg-emerald-50 px-2 py-1 text-xs font-bold text-emerald-800">{metric.trend}</p>
          </div>
        </article>
      ))}
    </div>
  )
}

function WebCalendar({ selected, onSelect }) {
  return (
    <section className="rounded-lg border border-stone-200 bg-white p-5 shadow-sm">
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm font-semibold text-stone-500">월간 일정</p>
          <h2 className="text-xl font-bold">2026년 7월</h2>
        </div>
        <button className="flex w-fit items-center gap-2 rounded-md bg-emerald-700 px-4 py-2 text-sm font-bold text-white" type="button">
          <PlusIcon className="h-5 w-5" />
          일정 추가
        </button>
      </div>
      <div className="grid grid-cols-2 gap-2 md:grid-cols-6">
        {calendarDays.map(([day, label]) => {
          const matched = schedules.find((schedule) => schedule.date.endsWith(day))
          const isSelected = matched?.id === selected.id
          return (
            <button
              className={`min-h-[96px] rounded-lg border p-3 text-left transition ${
                isSelected ? 'border-emerald-700 bg-emerald-50' : 'border-stone-200 bg-stone-50 hover:bg-white'
              }`}
              disabled={!matched}
              key={day}
              onClick={() => matched && onSelect(matched.id)}
              type="button"
            >
              <p className="text-sm font-bold">{day}</p>
              {label && <p className="mt-6 rounded bg-white px-2 py-1 text-xs font-bold text-stone-700 shadow-sm">{label}</p>}
            </button>
          )
        })}
      </div>
    </section>
  )
}

function WebMap({ selected }) {
  return (
    <section className="grid gap-4 rounded-lg border border-stone-200 bg-white p-5 shadow-sm lg:grid-cols-[1fr_280px]">
      <div>
        <div className="mb-4 flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold text-stone-500">지도 미리보기</p>
            <h2 className="text-xl font-bold">{selected.title}</h2>
          </div>
          <button className="grid h-10 w-10 place-items-center rounded-md border border-stone-200" type="button">
            <MapPinIcon className="h-5 w-5" />
          </button>
        </div>
        <div className="relative h-[320px] overflow-hidden rounded-lg bg-stone-800">
          <div className="absolute inset-0 web-map-visual" />
          {selected.places.map((place, index) => (
            <div
              className="absolute flex items-center gap-2 rounded-full bg-white px-3 py-2 text-sm font-bold shadow-lg"
              key={place.name}
              style={{ left: `${18 + index * 22}%`, top: `${26 + (index % 2) * 28}%` }}
            >
              <MapPinSolidIcon className="h-5 w-5 text-emerald-700" />
              {place.name}
            </div>
          ))}
        </div>
      </div>
      <div className="rounded-lg bg-stone-50 p-4">
        <p className="font-bold">장소 관리</p>
        <div className="mt-4 space-y-3">
          {selected.places.map((place, index) => (
            <div className="rounded-md bg-white p-3 shadow-sm" key={place.name}>
              <div className="flex items-center justify-between gap-3">
                <p className="truncate font-bold">{index + 1}. {place.name}</p>
                {place.done && <CheckCircleIcon className="h-5 w-5 shrink-0 text-emerald-700" />}
              </div>
              <p className="mt-1 text-sm text-stone-500">{place.time} · {place.note}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

function WebDetail({ selected }) {
  return (
    <aside className="rounded-lg border border-stone-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-semibold text-stone-500">일정 상세</p>
          <h2 className="mt-1 text-2xl font-bold">{selected.title}</h2>
          <p className="mt-2 text-sm font-semibold text-emerald-700">{selected.date} · {selected.time}</p>
        </div>
        <span className="rounded-md bg-amber-100 px-3 py-2 text-xs font-bold text-amber-900">{selected.status}</span>
      </div>
      <div className="mt-6 grid grid-cols-2 gap-3">
        <InfoBox icon={ClockIcon} label="시간" value={selected.time} />
        <InfoBox icon={UserGroupIcon} label="참여자" value={selected.participants.join(', ')} />
      </div>
      <section className="mt-6">
        <h3 className="font-bold">일기 본문</h3>
        <p className="mt-3 rounded-lg bg-[#f7f4ef] p-4 text-sm leading-6 text-stone-700">
          {selected.diary || '아직 작성된 일기가 없습니다. 완료 후 사진과 글을 추가합니다.'}
        </p>
      </section>
      <section className="mt-6">
        <h3 className="font-bold">사진</h3>
        <div className="mt-3 grid grid-cols-2 gap-3">
          <div className="photo-tile large bg-[#d9eadf]" />
          <div className="photo-tile large bg-[#cfd8e3]" />
          <div className="photo-tile large bg-[#e8d7c4]" />
          <button className="grid aspect-square place-items-center rounded-lg border border-dashed border-stone-300 bg-stone-50 text-stone-500" type="button">
            <PlusIcon className="h-6 w-6" />
          </button>
        </div>
      </section>
    </aside>
  )
}

function InfoBox({ icon: Icon, label, value }) {
  return (
    <div className="min-w-0 rounded-lg border border-stone-200 p-3">
      <Icon className="h-5 w-5 text-emerald-700" />
      <p className="mt-2 text-xs font-semibold text-stone-500">{label}</p>
      <p className="mt-1 truncate text-sm font-bold">{value}</p>
    </div>
  )
}

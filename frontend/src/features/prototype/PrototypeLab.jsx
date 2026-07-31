import { useMemo, useState } from 'react'
import {
  AdjustmentsHorizontalIcon, CalendarDaysIcon, CameraIcon, CheckIcon,
  ChevronLeftIcon, ChevronRightIcon, ClockIcon, ListBulletIcon, MapIcon,
  MapPinIcon, PencilSquareIcon, PlusIcon, UserCircleIcon,
} from '@heroicons/react/24/outline'
import './PrototypeLab.css'

const screens = [
  ['calendar', '캘린더', CalendarDaysIcon], ['schedule', '일정 목록', ListBulletIcon],
  ['detail', '일정 상세', MapIcon], ['diary', '일기 기록', PencilSquareIcon],
]
const themes = [
  ['로즈', '#F43F5E', '#BE123C', '#FFF1F2'], ['오렌지', '#F97316', '#C2410C', '#FFF7ED'],
  ['에메랄드', '#059669', '#047857', '#ECFDF5'], ['인디고', '#4F46E5', '#4338CA', '#EEF2FF'],
]
const schedules = [
  ['31', '금', '성수 전시와 저녁', '14:00 – 20:30', '그라운드시소 → 서울숲 → 작은식당', '오늘'],
  ['02', '일', '북촌 기록 산책', '11:00 – 16:00', '안국역 → 북촌한옥마을 → 카페', '예정'],
  ['27', '월', '한강 피크닉', '17:30 – 21:00', '여의나루 → 한강공원', '완료'],
]
const days = Array.from({ length: 35 }, (_, index) => index - 2)

export default function PrototypeLab() {
  const [platform, setPlatform] = useState('app')
  const [screen, setScreen] = useState('calendar')
  const [theme, setTheme] = useState(themes[0])
  const [radius, setRadius] = useState(16)
  const [spacing, setSpacing] = useState(16)
  const [map, setMap] = useState(true)
  const style = useMemo(() => ({
    '--p': theme[1], '--pd': theme[2], '--ps': theme[3],
    '--r': `${radius}px`, '--s': `${spacing}px`,
  }), [theme, radius, spacing])

  return <main className="prototype-lab" style={style}>
    <header className="lab-top">
      <div><b>나의 일기 · 내일</b><h1>웹·앱 디자인 플레이그라운드</h1><p>화면과 스타일을 바꾸며 실제 구현 방향을 비교해 보세요.</p></div>
      <a href="/calendar">서비스 화면으로</a>
    </header>
    <div className="lab-grid">
      <aside className="lab-panel">
        <h2><AdjustmentsHorizontalIcon />디자인 조절</h2>
        <Field label="플랫폼"><Segment value={platform} set={setPlatform} items={[['app', '모바일 앱'], ['web', '웹']]} /></Field>
        <Field label="화면"><div className="screen-picker">{screens.map(([id, label, Icon]) => <button className={screen === id ? 'on' : ''} key={id} onClick={() => setScreen(id)} type="button"><Icon />{label}</button>)}</div></Field>
        <Field label="주요 색상"><div className="color-picker">{themes.map((item) => <button aria-label={item[0]} className={theme[0] === item[0] ? 'on' : ''} key={item[0]} onClick={() => setTheme(item)} style={{ background: item[1] }} type="button">{theme[0] === item[0] && <CheckIcon />}</button>)}</div></Field>
        <Range label="카드 곡률" value={radius} set={setRadius} min={4} max={28} />
        <Range label="화면 여백" value={spacing} set={setSpacing} min={10} max={24} />
        <label className="switch"><span>지도 영역 표시</span><input checked={map} onChange={(event) => setMap(event.target.checked)} type="checkbox" /></label>
        <div className="help"><b>조절 방법</b><p>선택값은 미리보기에 즉시 반영됩니다. 마음에 드는 조합을 알려주면 운영 화면에 적용할 수 있어요.</p></div>
      </aside>
      <section className={`stage ${platform}`}>
        <div className="stage-meta"><span>{platform === 'app' ? '390 × 844 모바일 기준' : '1440px 웹 기준'}</span><span>{screens.find(([id]) => id === screen)?.[1]}</span></div>
        {platform === 'app' ? <Phone screen={screen} map={map} /> : <Desktop screen={screen} map={map} />}
      </section>
    </div>
  </main>
}

function Field({ label, children }) { return <div className="field"><label>{label}</label>{children}</div> }
function Segment({ value, set, items }) { return <div className="segment">{items.map(([id, label]) => <button className={value === id ? 'on' : ''} key={id} onClick={() => set(id)} type="button">{label}</button>)}</div> }
function Range({ label, value, set, min, max }) { return <label className="range"><span><b>{label}</b><em>{value}px</em></span><input min={min} max={max} onChange={(event) => set(Number(event.target.value))} type="range" value={value} /></label> }

function Phone({ screen, map }) {
  return <div className="phone"><i /><div className="phone-inner"><PreviewHeader compact /><div className="phone-body"><View screen={screen} map={map} mobile /></div><BottomNav screen={screen} /></div></div>
}
function Desktop({ screen, map }) {
  return <div className="desktop"><aside className="side"><div className="brand"><b>내</b><strong>나의 일기</strong></div><nav>{screens.map(([id, label, Icon]) => <div className={screen === id ? 'on' : ''} key={id}><Icon />{label}</div>)}</nav><div className="profile"><UserCircleIcon /><p><b>홍섭님</b><span>오늘도 기록해요</span></p></div></aside><div className="workspace"><PreviewHeader /><div className="work-body"><View screen={screen} map={map} /></div></div></div>
}
function PreviewHeader({ compact = false }) {
  return <header className={`preview-head ${compact ? 'compact' : ''}`}><div><span>2026년 7월 31일</span><b>좋은 오후예요, 홍섭님</b></div><button type="button"><PlusIcon />{!compact && '새 일정'}</button></header>
}
function View({ screen, map, mobile = false }) {
  if (screen === 'schedule') return <ScheduleList mobile={mobile} />
  if (screen === 'detail') return <Detail mobile={mobile} map={map} />
  if (screen === 'diary') return <Diary mobile={mobile} />
  return <Calendar mobile={mobile} />
}

function Calendar({ mobile }) {
  return <div className={`calendar-view ${mobile ? 'mobile-view' : ''}`}><section className="card calendar-card"><Title eyebrow="나의 일정" title="2026년 7월"><div className="month-buttons"><button type="button"><ChevronLeftIcon /></button><button type="button">오늘</button><button type="button"><ChevronRightIcon /></button></div></Title><div className="week">{['일','월','화','수','목','금','토'].map((d) => <span key={d}>{d}</span>)}</div><div className="month">{days.map((day, index) => <button className={`${day === 31 ? 'selected' : ''} ${day < 1 || day > 31 ? 'muted' : ''}`} key={`${day}-${index}`} type="button"><span>{day > 0 && day <= 31 ? day : ''}</span>{[7,12,18,21,27,31].includes(day) && <i />}</button>)}</div></section><aside className="card agenda"><Title eyebrow="선택한 날짜" title="7월 31일 금요일" /><Schedule item={schedules[0]} /><div className="empty"><CalendarDaysIcon /><p>이날의 다음 일정은 없어요.</p><button type="button">일정 추가하기</button></div></aside></div>
}
function ScheduleList({ mobile }) {
  return <section><div className="page-title"><div><b>나의 시간</b><h2>일정 목록</h2><p>앞으로의 계획과 지나간 기록을 한눈에 확인하세요.</p></div>{!mobile && <button className="primary" type="button"><PlusIcon />새 일정</button>}</div><div className="filters"><button className="on" type="button">전체</button><button type="button">예정</button><button type="button">완료</button></div><div className="schedule-list">{schedules.map((item) => <Schedule item={item} key={item[2]} />)}</div></section>
}
function Schedule({ item }) {
  return <article className={`schedule ${item[5] === '완료' ? 'done' : ''}`}><div className="date"><b>{item[0]}</b><span>{item[1]}</span></div><div className="schedule-text"><div><i>{item[5]}</i><h3>{item[2]}</h3></div><p><ClockIcon />{item[3]}</p><p><MapPinIcon />{item[4]}</p></div><ChevronRightIcon /></article>
}
function Detail({ mobile, map }) {
  const places = ['그라운드시소 성수', '서울숲 산책길', '작은식당 성수점']
  return <div className={`detail ${mobile ? 'mobile-view' : ''}`}><section><div className="hero"><i>오늘</i><h2>성수 전시와 저녁</h2><p><ClockIcon />7월 31일 금요일 · 14:00 – 20:30</p></div>{map && <MapBox places={places} />}<section className="card places"><Title eyebrow="이동 순서" title="오늘 갈 장소"><button type="button">순서 편집</button></Title>{places.map((place, index) => <div className="place" key={place}><i>{index ? index + 1 : <CheckIcon />}</i><p><b>{place}</b><span>{['14:00 · 전시 관람','17:00 · 산책과 사진','19:00 · 저녁 예약'][index]}</span></p></div>)}</section></section><aside className="card memory"><b>하루의 기록</b><h2>오늘을 남겨보세요</h2><p>사진과 글은 일정이 끝난 뒤에도 장소와 함께 기억됩니다.</p><Photos /><button className="primary" type="button"><PencilSquareIcon />일기 작성하기</button></aside></div>
}
function MapBox({ places }) { return <div className="mapbox"><div className="route" />{places.map((place, index) => <i className={`pin p${index + 1}`} key={place}>{index + 1}</i>)}<p><b>3개 장소</b><span>예상 이동 5.4km</span></p></div> }
function Diary({ mobile }) {
  return <div className={`diary ${mobile ? 'mobile-view' : ''}`}><section className="card editor"><div className="page-title"><div><b>7월 27일 월요일</b><h2>한강 피크닉의 기록</h2><p>그날의 감정과 기억을 편안하게 남겨보세요.</p></div></div><label>오늘의 기분<div className="moods"><button type="button">😊</button><button className="on" type="button">🥰</button><button type="button">😌</button><button type="button">😴</button></div></label><label>일기<textarea defaultValue="노을이 생각보다 오래 남아 있어서 천천히 걸었다. 다음에는 돗자리와 따뜻한 차도 챙겨오고 싶다." /></label><div className="actions"><button type="button">임시 저장</button><button className="primary" type="button">기록 저장</button></div></section><aside className="card photo-side"><Title eyebrow="사진" title="오늘의 장면" /><div className="big-photo" /><Photos /></aside></div>
}
function Title({ eyebrow, title, children }) { return <div className="title"><div><b>{eyebrow}</b><h2>{title}</h2></div>{children}</div> }
function Photos() { return <div className="photos"><div /><div /><button type="button"><CameraIcon /><span>추가</span></button></div> }
function BottomNav({ screen }) { return <nav className="bottom">{screens.map(([id, label, Icon]) => <button className={screen === id ? 'on' : ''} key={id} type="button"><Icon /><span>{label.replace(' 목록','').replace(' 상세','').replace(' 기록','')}</span></button>)}</nav> }

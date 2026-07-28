import { useParams, useNavigate } from 'react-router-dom'
import { Icon } from '../../shared/components/Icon'
import arrowLeftRaw from '../../assets/icons/arrow-left.svg?raw'
import pencilRaw from '../../assets/icons/pencil.svg?raw'
import { useSchedule } from '../../shared/api/queries'
import './schedules.css'

const DAYS = ['일', '월', '화', '수', '목', '금', '토']

function formatFullDate(dateStr) {
  const d = new Date(dateStr)
  return `${d.getFullYear()}년 ${d.getMonth() + 1}월 ${d.getDate()}일 (${DAYS[d.getDay()]})`
}

function formatTime(dateStr) {
  const d = new Date(dateStr)
  const h = d.getHours()
  const m = d.getMinutes()
  const ampm = h < 12 ? '오전' : '오후'
  return `${ampm} ${h % 12 || 12}:${String(m).padStart(2, '0')}`
}

export default function ScheduleDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { data: schedule, isLoading } = useSchedule(id)

  if (isLoading) return <div className="sdetail-loading">로딩 중...</div>
  if (!schedule) return <div className="sdetail-loading">일정을 찾을 수 없어요</div>

  return (
    <div className="sdetail-page">
      <div className="sdetail-header">
        <div className="sdetail-header__row">
          <button onClick={() => navigate(-1)} className="sdetail-back-btn">
            <Icon raw={arrowLeftRaw} size={20} />
          </button>
          <h1 className="sdetail-header__title">{schedule.title}</h1>
          <span className={`sdetail-header__badge sdetail-header__badge--${schedule.status}`}>
            {schedule.status === 'completed' ? '완료' : '예정'}
          </span>
        </div>
        <p className="sdetail-header__time">
          {formatFullDate(schedule.start_at)} · {formatTime(schedule.start_at)} – {formatTime(schedule.end_at)}
        </p>
      </div>

      <div className="sdetail-body">
        {/* Places */}
        <section className="sdetail-section">
          <div className="sdetail-section__header">
            <h2 className="sdetail-section__title">장소</h2>
          </div>
          <div className="sdetail-places">
            {schedule.places.map((p) => (
              <div key={p.id} className="sdetail-place">
                <div className="sdetail-place__order">{p.sort_order}</div>
                <div className="sdetail-place__info">
                  <div className="sdetail-place__name-row">
                    <p className={`sdetail-place__name${p.visited ? ' sdetail-place__name--visited' : ''}`}>
                      {p.name}
                    </p>
                    {p.visited && <span className="sdetail-place__check">✓</span>}
                  </div>
                  <p className="sdetail-place__address">{p.address}</p>
                  {p.memo && <p className="sdetail-place__memo">{p.memo}</p>}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Diary */}
        <section className="sdetail-section">
          <div className="sdetail-section__header">
            <h2 className="sdetail-section__title">일기</h2>
            {schedule.diary && (
              <button className="sdetail-section__edit">
                <Icon raw={pencilRaw} size={14} />
                수정
              </button>
            )}
          </div>
          {schedule.diary ? (
            <div className="sdetail-diary">
              {schedule.diary.mood && (
                <p className="sdetail-diary__mood">{schedule.diary.mood}</p>
              )}
              <p className="sdetail-diary__content">{schedule.diary.content}</p>
            </div>
          ) : (
            <div className="sdetail-diary-empty">
              <p>아직 일기가 없어요</p>
              <button className="sdetail-diary-empty__btn">일기 쓰기</button>
            </div>
          )}
        </section>
      </div>
    </div>
  )
}

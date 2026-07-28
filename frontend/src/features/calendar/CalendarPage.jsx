import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Icon } from '../../shared/components/Icon'
import chevronLeftRaw from '../../assets/icons/chevron-left.svg?raw'
import chevronRightRaw from '../../assets/icons/chevron-right.svg?raw'
import plusRaw from '../../assets/icons/plus.svg?raw'
import { useSchedules } from '../../shared/api/queries'
import './calendar.css'

const WEEKDAYS = ['일', '월', '화', '수', '목', '금', '토']

function formatDateKey(year, month, day) {
  return `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
}

function formatTime(dateStr) {
  const d = new Date(dateStr)
  const h = d.getHours()
  const m = d.getMinutes()
  const ampm = h < 12 ? '오전' : '오후'
  return `${ampm} ${h % 12 || 12}:${String(m).padStart(2, '0')}`
}

export default function CalendarPage() {
  const today = new Date()
  const [viewDate, setViewDate] = useState(new Date(today.getFullYear(), today.getMonth(), 1))
  const [selectedDay, setSelectedDay] = useState(today.getDate())
  const navigate = useNavigate()
  const { data: schedules = [] } = useSchedules()

  const year = viewDate.getFullYear()
  const month = viewDate.getMonth()

  const prevMonth = () => {
    setViewDate(new Date(year, month - 1, 1))
    setSelectedDay(1)
  }
  const nextMonth = () => {
    setViewDate(new Date(year, month + 1, 1))
    setSelectedDay(1)
  }

  const schedulesByDay = schedules.reduce((acc, s) => {
    const d = new Date(s.start_at)
    if (d.getFullYear() === year && d.getMonth() === month) {
      const day = d.getDate()
      if (!acc[day]) acc[day] = []
      acc[day].push(s)
    }
    return acc
  }, {})

  const firstDayOfWeek = new Date(year, month, 1).getDay()
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const cells = [...Array(firstDayOfWeek).fill(null), ...Array.from({ length: daysInMonth }, (_, i) => i + 1)]
  while (cells.length % 7 !== 0) cells.push(null)

  const selectedDateKey = formatDateKey(year, month, selectedDay)
  const selectedSchedules = schedules.filter((s) => s.start_at.startsWith(selectedDateKey))

  const isToday = (day) =>
    year === today.getFullYear() && month === today.getMonth() && day === today.getDate()

  return (
    <div className="calendar-page">
      <div className="calendar-header">
        <div className="calendar-header__top">
          <h2 className="calendar-header__title">
            {year}년 {month + 1}월
          </h2>
          <div className="calendar-header__nav">
            <button onClick={prevMonth} className="calendar-nav-btn">
              <Icon raw={chevronLeftRaw} size={20} />
            </button>
            <button onClick={nextMonth} className="calendar-nav-btn">
              <Icon raw={chevronRightRaw} size={20} />
            </button>
          </div>
        </div>

        <div className="calendar-weekdays">
          {WEEKDAYS.map((d, i) => (
            <span key={d} className={`calendar-weekday${i === 0 ? ' calendar-weekday--sun' : i === 6 ? ' calendar-weekday--sat' : ''}`}>
              {d}
            </span>
          ))}
        </div>

        <div className="calendar-grid">
          {cells.map((day, idx) => {
            if (!day) return <div key={`e-${idx}`} />
            const col = idx % 7
            const hasSchedule = !!schedulesByDay[day]
            const selected = day === selectedDay
            const today_ = isToday(day)
            return (
              <button
                key={day}
                onClick={() => setSelectedDay(day)}
                className="calendar-day"
              >
                <span className={[
                  'calendar-day__num',
                  selected ? 'calendar-day__num--selected' : '',
                  !selected && today_ ? 'calendar-day__num--today' : '',
                  !selected && col === 0 ? 'calendar-day__num--sun' : '',
                  !selected && col === 6 ? 'calendar-day__num--sat' : '',
                ].filter(Boolean).join(' ')}>
                  {day}
                </span>
                <span className={`calendar-day__dot${hasSchedule ? ' calendar-day__dot--visible' : ''}`} />
              </button>
            )
          })}
        </div>
      </div>

      <div className="calendar-body">
        <div className="calendar-body__header">
          <span className="calendar-body__date-label">
            {month + 1}월 {selectedDay}일
          </span>
          <button onClick={() => navigate('/schedules/new')} className="calendar-body__add-btn">
            <Icon raw={plusRaw} size={16} />
            새 일정
          </button>
        </div>

        {selectedSchedules.length === 0 ? (
          <div className="calendar-empty">
            <span className="calendar-empty__icon">📅</span>
            <p>이 날은 일정이 없어요</p>
          </div>
        ) : (
          <div className="schedule-list">
            {selectedSchedules.map((s) => (
              <button
                key={s.id}
                onClick={() => navigate(`/schedules/${s.id}`)}
                className="schedule-card"
              >
                <div className="schedule-card__content">
                  <span className={`schedule-card__badge schedule-card__badge--${s.status}`}>
                    {s.status === 'completed' ? '완료' : '예정'}
                  </span>
                  <p className="schedule-card__title">{s.title}</p>
                  <p className="schedule-card__meta">
                    {formatTime(s.start_at)} · {s.places.length}개 장소
                  </p>
                </div>
                <Icon raw={chevronRightRaw} size={16} className="schedule-card__arrow" />
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

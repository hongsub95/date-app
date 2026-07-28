import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Icon } from '../../shared/components/Icon'
import arrowLeftRaw from '../../assets/icons/arrow-left.svg?raw'
import './schedules.css'

export default function ScheduleNewPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    title: '',
    date: new Date().toISOString().slice(0, 10),
    start_time: '12:00',
    end_time: '15:00',
    memo: '',
  })

  const set = (key, val) => setForm((f) => ({ ...f, [key]: val }))

  const handleSubmit = (e) => {
    e.preventDefault()
    // API 연동 전 mock: 캘린더로 이동
    navigate('/calendar')
  }

  return (
    <div className="snew-page">
      <div className="snew-header">
        <button onClick={() => navigate(-1)} className="sdetail-back-btn">
          <Icon raw={arrowLeftRaw} size={20} />
        </button>
        <h1 className="snew-header__title">새 일정</h1>
      </div>

      <form onSubmit={handleSubmit} className="snew-form">
        <div className="snew-form__field">
          <label className="snew-form__label">제목 *</label>
          <input
            type="text"
            value={form.title}
            onChange={(e) => set('title', e.target.value)}
            className="snew-form__input"
            placeholder="일정 이름을 입력하세요"
            required
          />
        </div>

        <div className="snew-form__field">
          <label className="snew-form__label">날짜 *</label>
          <input
            type="date"
            value={form.date}
            onChange={(e) => set('date', e.target.value)}
            className="snew-form__input"
            required
          />
        </div>

        <div className="snew-form__row">
          <div className="snew-form__field">
            <label className="snew-form__label">시작 시간</label>
            <input
              type="time"
              value={form.start_time}
              onChange={(e) => set('start_time', e.target.value)}
              className="snew-form__input"
            />
          </div>
          <div className="snew-form__field">
            <label className="snew-form__label">종료 시간</label>
            <input
              type="time"
              value={form.end_time}
              onChange={(e) => set('end_time', e.target.value)}
              className="snew-form__input"
            />
          </div>
        </div>

        <div className="snew-form__field">
          <label className="snew-form__label">메모</label>
          <textarea
            value={form.memo}
            onChange={(e) => set('memo', e.target.value)}
            className="snew-form__input snew-form__textarea"
            placeholder="메모를 입력하세요 (선택)"
            rows={4}
          />
        </div>

        <button type="submit" className="snew-form__submit">일정 추가하기</button>
      </form>
    </div>
  )
}

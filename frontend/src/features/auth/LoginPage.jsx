import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../shared/contexts/AuthContext'
import { MOCK_USER } from '../../shared/api/mocks'
import './auth.css'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!form.email || !form.password) {
      setError('이메일과 비밀번호를 입력해주세요.')
      return
    }
    login({ ...MOCK_USER, email: form.email })
    navigate('/calendar')
  }

  const set = (key, val) => setForm((f) => ({ ...f, [key]: val }))

  return (
    <div className="auth-page">
      <div className="auth-page__hero">
        <h1 className="auth-page__title">나의 일기</h1>
        <p className="auth-page__subtitle">내일의 나를 위한 기록</p>
      </div>

      <form onSubmit={handleSubmit} className="auth-form">
        <div className="auth-form__field">
          <label className="auth-form__label">이메일</label>
          <input
            type="email"
            value={form.email}
            onChange={(e) => set('email', e.target.value)}
            className="auth-form__input"
            placeholder="example@email.com"
          />
        </div>
        <div className="auth-form__field">
          <label className="auth-form__label">비밀번호</label>
          <input
            type="password"
            value={form.password}
            onChange={(e) => set('password', e.target.value)}
            className="auth-form__input"
            placeholder="비밀번호"
          />
        </div>
        {error && <p className="auth-form__error">{error}</p>}
        <button type="submit" className="auth-form__submit">로그인</button>
      </form>

      <p className="auth-page__footer">
        계정이 없으신가요?{' '}
        <Link to="/register" className="auth-page__link">회원가입</Link>
      </p>
    </div>
  )
}

import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../shared/contexts/AuthContext'
import './auth.css'

export default function RegisterPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ nickname: '', email: '', password: '', confirm: '' })
  const [error, setError] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!form.nickname || !form.email || !form.password) {
      setError('모든 항목을 입력해주세요.')
      return
    }
    if (form.password !== form.confirm) {
      setError('비밀번호가 일치하지 않아요.')
      return
    }
    login({ id: '1', nickname: form.nickname, email: form.email })
    navigate('/calendar')
  }

  const set = (key, val) => setForm((f) => ({ ...f, [key]: val }))

  return (
    <div className="auth-page">
      <div className="auth-page__hero">
        <h1 className="auth-page__title">회원가입</h1>
        <p className="auth-page__subtitle">나의 일기를 시작해요</p>
      </div>

      <form onSubmit={handleSubmit} className="auth-form">
        <div className="auth-form__field">
          <label className="auth-form__label">닉네임</label>
          <input
            type="text"
            value={form.nickname}
            onChange={(e) => set('nickname', e.target.value)}
            className="auth-form__input"
            placeholder="닉네임을 입력하세요"
          />
        </div>
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
        <div className="auth-form__field">
          <label className="auth-form__label">비밀번호 확인</label>
          <input
            type="password"
            value={form.confirm}
            onChange={(e) => set('confirm', e.target.value)}
            className="auth-form__input"
            placeholder="비밀번호 다시 입력"
          />
        </div>
        {error && <p className="auth-form__error">{error}</p>}
        <button type="submit" className="auth-form__submit">가입하기</button>
      </form>

      <p className="auth-page__footer">
        이미 계정이 있으신가요?{' '}
        <Link to="/login" className="auth-page__link">로그인</Link>
      </p>
    </div>
  )
}

import { useNavigate } from 'react-router-dom'
import { Icon } from '../../shared/components/Icon'
import userRaw from '../../assets/icons/user.svg?raw'
import logoutRaw from '../../assets/icons/logout.svg?raw'
import chevronRightRaw from '../../assets/icons/chevron-right.svg?raw'
import { useAuth } from '../../shared/contexts/AuthContext'
import './settings.css'

const MENU_ITEMS = ['프로필 수정', '알림 설정', '개인정보 처리방침', '서비스 이용약관']

export default function SettingsPage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="settings-page">
      <div className="settings-page__header">
        <h1 className="settings-page__heading">설정</h1>
      </div>

      <div className="settings-page__body">
        {/* Profile card */}
        <section className="settings-profile">
          <div className="settings-profile__avatar">
            <Icon raw={userRaw} size={32} className="settings-profile__avatar-icon" />
          </div>
          <div>
            <p className="settings-profile__name">{user?.nickname}</p>
            <p className="settings-profile__email">{user?.email}</p>
          </div>
        </section>

        {/* Menu */}
        <section className="settings-menu">
          {MENU_ITEMS.map((item, i) => (
            <div key={item}>
              <button className="settings-menu__item">
                <span>{item}</span>
                <Icon raw={chevronRightRaw} size={16} className="settings-menu__arrow" />
              </button>
              {i < MENU_ITEMS.length - 1 && <div className="settings-menu__divider" />}
            </div>
          ))}
        </section>

        {/* Logout */}
        <button onClick={handleLogout} className="settings-logout">
          <Icon raw={logoutRaw} size={20} className="settings-logout__icon" />
          로그아웃
        </button>
      </div>
    </div>
  )
}

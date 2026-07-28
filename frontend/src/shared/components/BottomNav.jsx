import { NavLink } from 'react-router-dom'
import { Icon } from './Icon'
import calendarRaw from '../../assets/icons/calendar.svg?raw'
import listRaw from '../../assets/icons/list.svg?raw'
import settingsRaw from '../../assets/icons/settings.svg?raw'
import './BottomNav.css'

const NAV_ITEMS = [
  { to: '/calendar', label: '캘린더', raw: calendarRaw },
  { to: '/schedules', label: '일정', raw: listRaw },
  { to: '/settings', label: '설정', raw: settingsRaw },
]

export default function BottomNav() {
  return (
    <nav className="bottom-nav">
      {NAV_ITEMS.map(({ to, label, raw }) => (
        <NavLink
          key={to}
          to={to}
          className={({ isActive }) => `bottom-nav__item${isActive ? ' bottom-nav__item--active' : ''}`}
        >
          <Icon raw={raw} size={24} className="bottom-nav__icon" />
          <span className="bottom-nav__label">{label}</span>
        </NavLink>
      ))}
    </nav>
  )
}

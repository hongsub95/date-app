export function Icon({ raw, size = 24, className = '', style = {} }) {
  return (
    <span
      className={className}
      style={{ display: 'inline-flex', width: size, height: size, flexShrink: 0, ...style }}
      dangerouslySetInnerHTML={{ __html: raw }}
    />
  )
}

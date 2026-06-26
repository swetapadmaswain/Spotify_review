interface Props {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
  glow?: boolean;
}

export default function Card({ children, className = '', onClick, glow }: Props) {
  return (
    <div
      onClick={onClick}
      className={`glass-card p-5 ${glow ? 'glow-spotify' : ''} ${onClick ? 'cursor-pointer hover:border-spotify/30 transition-colors' : ''} ${className}`}
    >
      {children}
    </div>
  );
}

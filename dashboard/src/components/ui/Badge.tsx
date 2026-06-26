interface Props {
  label: string;
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info';
}

const styles = {
  default: 'bg-white/10 text-white',
  success: 'bg-spotify/20 text-spotify',
  warning: 'bg-yellow-500/20 text-yellow-400',
  danger: 'bg-red-500/20 text-red-400',
  info: 'bg-blue-500/20 text-blue-400',
};

export default function Badge({ label, variant = 'default' }: Props) {
  return (
    <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${styles[variant]}`}>
      {label}
    </span>
  );
}

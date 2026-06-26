interface Props {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  loading?: boolean;
  className?: string;
  onClick?: () => void;
  disabled?: boolean;
}

const variants = {
  primary: 'btn-primary',
  secondary: 'btn-secondary',
  ghost: 'btn-ghost',
  danger: 'px-4 py-2 rounded-lg bg-red-500/20 text-red-400 font-medium text-sm hover:bg-red-500/30 border border-red-500/30 transition-all',
};

export default function Button({
  children, variant = 'secondary', loading, className = '', onClick, disabled,
}: Props) {
  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      className={`${variants[variant]} inline-flex items-center gap-2 ${className}`}
    >
      {loading && (
        <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
      )}
      {children}
    </button>
  );
}

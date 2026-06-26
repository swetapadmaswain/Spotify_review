interface Props {
  findings: string[];
}

export default function KeyFindingsList({ findings }: Props) {
  return (
    <div className="bg-card rounded-xl p-5 border border-white/10">
      <h3 className="text-lg font-semibold mb-4">Key Findings</h3>
      {findings.length === 0 ? (
        <p className="text-muted">No findings yet.</p>
      ) : (
        <ul className="space-y-2">
          {findings.map((f, i) => (
            <li key={i} className="flex gap-3 text-sm">
              <span className="text-spotify font-bold">{i + 1}.</span>
              <span>{f}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

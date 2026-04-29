export default function ProfileCard({ name, subtitle, accent, buttonLabel, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="w-full rounded-[1.5rem] border border-slate-200 bg-white p-5 text-left shadow-sm transition hover:border-rose-200 hover:bg-rose-50 hover:shadow-md"
    >
      <div className="flex items-start justify-between gap-4">
        <div className={`h-12 w-12 rounded-2xl ${accent}`} />
        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-500">
          Click
        </span>
      </div>
      <h3 className="mt-4 text-lg font-semibold text-slate-900">{name}</h3>
      <p className="mt-2 text-sm leading-6 text-slate-600">{subtitle}</p>
      <div className="mt-4">
        <span className="button-secondary inline-flex">
          {buttonLabel || 'Choose'}
        </span>
      </div>
    </button>
  );
}

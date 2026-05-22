export default function StatsSection() {
  return (
    <section className="px-4 py-16 sm:py-20">
      <div className="mx-auto max-w-5xl">
        <div className="grid gap-6 text-center sm:grid-cols-4">
          <div>
            <p className="text-3xl font-bold text-zinc-900">300 000+</p>
            <p className="mt-1 text-sm text-zinc-500">parents inscrits</p>
          </div>
          <div>
            <p className="text-3xl font-bold text-zinc-900">600 000+</p>
            <p className="mt-1 text-sm text-zinc-500">encadreurs disponibles</p>
          </div>
          <div>
            <p className="text-3xl font-bold text-zinc-900">Partout</p>
            <p className="mt-1 text-sm text-zinc-500">en Côte d&apos;Ivoire</p>
          </div>
          <div>
            <p className="text-3xl font-bold text-zinc-900">0 %</p>
            <p className="mt-1 text-sm text-zinc-500">commission sur les cours</p>
          </div>
        </div>
      </div>
    </section>
  );
}

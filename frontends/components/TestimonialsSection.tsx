const TESTIMONIALS = [
  {
    name: "Aminata K.",
    role: "Parent, Abidjan",
    text: "J'ai trouvé un répétiteur de maths pour mon fils en 2 jours. Le paiement unique de 1 000 F est vraiment abordable.",
  },
  {
    name: "Franck D.",
    role: "Encadreur, Korhogo",
    text: "MYCD m'a permis de trouver des élèves sans payer de plateforme. Je reçois des demandes chaque semaine.",
  },
  {
    name: "Marie-Louise B.",
    role: "Parent, Bouaké",
    text: "La recherche par quartier m'a aidée à trouver quelqu'un de confiance près de chez moi. Je recommande !",
  },
];

export default function TestimonialsSection() {
  return (
    <section className="bg-zinc-50 px-4 py-16 sm:py-20">
      <div className="mx-auto max-w-5xl">
        <h2 className="text-center text-2xl font-bold text-zinc-900 sm:text-3xl">
          Ils nous font confiance
        </h2>
        <div className="mt-10 grid gap-6 sm:grid-cols-3">
          {TESTIMONIALS.map((t) => (
            <div key={t.name} className="rounded-xl bg-white p-6 shadow-sm">
              <p className="text-sm leading-relaxed text-zinc-600 italic">
                &ldquo;{t.text}&rdquo;
              </p>
              <div className="mt-4 border-t border-zinc-100 pt-3">
                <p className="text-sm font-semibold text-zinc-900">{t.name}</p>
                <p className="text-xs text-zinc-400">{t.role}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

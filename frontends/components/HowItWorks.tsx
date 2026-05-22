const STEPS = [
  {
    number: "1",
    title: "Créez votre compte",
    desc: "Inscription en 30 secondes. Nom, email, téléphone et vous êtes prêt.",
  },
  {
    number: "2",
    title: "Trouvez l'encadreur idéal",
    desc: "Filtrez par matière, ville et quartier. Parcourez les profils et comparez.",
  },
  {
    number: "3",
    title: "Contactez-le",
    desc: "1 000 F pour contacter jusqu'à 3 encadreurs. Messages gratuits et illimités ensuite.",
  },
];

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="bg-zinc-50 px-4 py-16 sm:py-20">
      <div className="mx-auto max-w-5xl">
        <h2 className="text-center text-2xl font-bold text-zinc-900 sm:text-3xl">
          Comment ça marche
        </h2>
        <div className="mt-10 grid gap-6 sm:grid-cols-3">
          {STEPS.map((step) => (
            <div key={step.number} className="rounded-xl bg-white p-6 text-center shadow-sm">
              <div className="mx-auto mb-4 flex h-10 w-10 items-center justify-center rounded-full bg-zinc-900 text-sm font-bold text-white">
                {step.number}
              </div>
              <h3 className="text-lg font-semibold text-zinc-900">{step.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-zinc-500">{step.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

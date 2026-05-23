import Link from "next/link";

export default function HeroSection() {
  return (
    <section className="flex flex-col items-center px-4 pt-20 pb-16 text-center sm:pt-28 sm:pb-20">
      <h1 className="max-w-2xl text-3xl font-bold leading-tight tracking-tight text-zinc-900 sm:text-4xl sm:leading-tight">
        Trouvez le meilleur encadreur pour votre enfant
      </h1>
      <p className="mt-4 max-w-lg text-base leading-relaxed text-zinc-500 sm:text-lg">
        Répétiteurs, maîtres de maison, professeurs particuliers — partout en Côte d&apos;Ivoire.
        Pas d&apos;abonnement, pas de commission. Payez uniquement pour contacter.
      </p>
      <div className="mt-8 flex flex-col gap-3 sm:flex-row">
        <Link
          href="/register?role=parent"
          className="rounded-xl bg-zinc-900 px-6 py-3 text-sm font-medium text-white hover:bg-zinc-800"
        >
          Je suis un parent
        </Link>
        <Link
          href="/register?role=encadreur"
          className="rounded-xl border border-zinc-300 px-6 py-3 text-sm font-medium text-zinc-700 hover:bg-zinc-50"
        >
          Je suis un encadreur
        </Link>
      </div>
    </section>
  );
}

import Link from "next/link";

export default function CTASection() {
  return (
    <section className="px-4 py-16 text-center sm:py-20">
      <h2 className="text-2xl font-bold text-zinc-900 sm:text-3xl">
        Prêt à trouver votre encadreur ?
      </h2>
      <p className="mt-3 text-base text-zinc-500">
        Rejoignez des milliers de parents et d&apos;encadreurs dès aujourd&apos;hui.
      </p>
      <Link
        href="/register"
        className="mt-6 inline-block rounded-xl bg-zinc-900 px-8 py-3 text-sm font-medium text-white hover:bg-zinc-800"
      >
        Créer un compte gratuit
      </Link>
    </section>
  );
}

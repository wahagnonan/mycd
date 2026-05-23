export default function Footer() {
  return (
    <footer className="border-t border-zinc-200 bg-white px-4 py-8">
      <div className="mx-auto flex max-w-5xl flex-col items-center justify-between gap-4 text-sm text-zinc-500 sm:flex-row">
        <p>&copy; {new Date().getFullYear()} MYCD. Tous droits réservés.</p>
        <nav className="flex gap-4">
          <a href="#" className="hover:text-zinc-900">CGU</a>
          <a href="#" className="hover:text-zinc-900">Confidentialité</a>
          <a href="#" className="hover:text-zinc-900">Contact</a>
        </nav>
      </div>
    </footer>
  );
}

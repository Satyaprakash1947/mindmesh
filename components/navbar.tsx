
import Link from "next/link";

export default function Navbar() {
  return (
    <header className="w-full bg-[#080808] px-4 pt-2">
      <nav className="mx-auto flex max-w-[1440px] items-center justify-between rounded-[22px] border border-[#292929] bg-[#0c0c0c] px-6 py-4 sm:px-8">

        {/* Brand */}
        <Link href="/" className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-orange-500 text-xl font-bold text-white">
            M
          </div>
          <span className="text-xl font-semibold tracking-tight text-white">
            MindMesh
          </span>
        </Link>

        {/* Navigation */}
        <div className="flex items-center gap-5 sm:gap-8">
          <Link
            href="#how-it-works"
            className="hidden text-sm text-gray-300 transition-colors hover:text-white sm:block"
          >
            How it works
          </Link>

          <Link
            href="#features"
            className="hidden text-sm text-gray-300 transition-colors hover:text-white sm:block"
          >
            Features
          </Link>

          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 rounded-xl border border-[#353535] bg-[#191919] px-4 py-3 text-sm font-medium text-gray-200 shadow-sm transition hover:border-[#505050] hover:bg-[#222222]"
          >
            <span aria-hidden="true">★</span>
            <span>Star on GitHub</span>
          </a>
        </div>
      </nav>
    </header>
  );
}

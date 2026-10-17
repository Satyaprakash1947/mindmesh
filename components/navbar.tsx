
import Link from "next/link";

export default function Navbar() {
  return (
    <header className="w-full bg-[#080808] px-4 pt-3">
      <nav
        className="relative mx-auto flex max-w-[1440px] items-center
        justify-between rounded-[22px] border border-white/[0.12]
        bg-gradient-to-b from-white/[0.09] via-[#111111]/95 to-[#090909]
        px-5 py-4 shadow-[0_8px_32px_rgba(0,0,0,0.4),inset_0_1px_0_rgba(255,255,255,0.12)]
        backdrop-blur-2xl sm:px-7"
      >
    
        <div className="pointer-events-none absolute inset-x-8 top-0 h-px bg-gradient-to-r from-transparent via-white/30 to-transparent" />

        <Link href="/" className="relative z-10 flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-orange-300/30 bg-gradient-to-br from-orange-400 via-orange-500 to-orange-600 text-xl font-bold text-white shadow-[0_3px_15px_rgba(249,115,22,0.25),inset_0_1px_1px_rgba(255,255,255,0.35)]">
            M
          </div>

          <span className="text-xl font-semibold tracking-tight text-white">
            MindMesh
          </span>
        </Link>

      
        <div className="absolute left-1/2 flex -translate-x-1/2 items-center gap-5 sm:gap-8">
          <Link
            href="#how-it-works"
            className="whitespace-nowrap text-sm text-gray-300 transition-colors duration-200 hover:text-white"
          >
            How it works
          </Link>

          <Link
            href="#get-started"
            className="whitespace-nowrap rounded-xl border border-white/[0.12] bg-white/[0.05] px-4 py-2.5 text-sm font-medium text-gray-200 shadow-[inset_0_1px_0_rgba(255,255,255,0.08)] transition duration-200 hover:border-white/25 hover:bg-white/10 hover:text-white sm:px-5"
          >
            Get Started <span className="ml-1">↗</span>
          </Link>
        </div>

       
        <a
          href="https://github.com"
          target="_blank"
          rel="noopener noreferrer"
          className="relative z-10 flex items-center gap-2 rounded-xl border border-white/[0.16] bg-gradient-to-b from-[#303030] via-[#1e1e1e] to-[#151515] px-3 py-3 text-sm font-medium text-gray-100 shadow-[0_3px_12px_rgba(0,0,0,0.3),inset_0_1px_0_rgba(255,255,255,0.18)] transition duration-200 hover:border-white/30 hover:from-[#3a3a3a] hover:to-[#202020] hover:shadow-[0_4px_20px_rgba(255,255,255,0.06),inset_0_1px_0_rgba(255,255,255,0.25)] sm:px-5"
        >
          <span className="text-base text-yellow-400 drop-shadow-[0_0_5px_rgba(250,204,21,0.35)]">
            ★
          </span>
          <span className="hidden sm:inline">Star on GitHub</span>
          <span className="sm:hidden">GitHub</span>
        </a>
      </nav>
    </header>
  );
}

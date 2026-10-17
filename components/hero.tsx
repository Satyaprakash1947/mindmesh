
import Link from "next/link";

export default function HeroSection() {
  return (
    <section className="relative isolate flex min-h-[650px] items-center justify-center overflow-hidden bg-[#080808] px-6 py-24">

      <div
        className="pointer-events-none absolute inset-0 -z-10"
        style={{
          backgroundImage: `
            linear-gradient(to right, rgba(255,255,255,0.055) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(255,255,255,0.055) 1px, transparent 1px)
          `,
          backgroundSize: "52px 52px",
          maskImage:
            "linear-gradient(to bottom, black 0%, black 65%, transparent 100%)",
        }}
      />

      {/* Subtle orange glow */}
      <div className="pointer-events-none absolute left-1/2 top-20 -z-10 h-72 w-72 -translate-x-1/2 rounded-full bg-orange-500/[0.10] blur-[120px]" />

      {/* Hero content */}
      <div className="mx-auto flex max-w-4xl flex-col items-center text-center">
        <div className="mb-8 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-4 py-2 text-sm text-gray-300 shadow-[inset_0_1px_0_rgba(255,255,255,0.06)]">
          <span className="h-2 w-2 rounded-full bg-orange-400 shadow-[0_0_10px_rgba(251,146,60,0.7)]" />
          A new way to learn with AI
        </div>

        <h1 className="text-4xl font-semibold leading-[1.12] tracking-tight text-white sm:text-6xl lg:text-7xl">
          Don&apos;t just get answers.
          <span className="mt-2 block bg-gradient-to-r from-orange-300 via-orange-400 to-orange-600 bg-clip-text text-transparent">
            Understand the why.
          </span>
        </h1>

        <p className="mt-7 max-w-2xl text-base leading-8 text-gray-400 sm:text-lg">
          MindMesh maps what you know, discovers the concepts you&apos;re missing,
          and guides you through them — so you can build real understanding,
          not just collect answers.
        </p>

        <div className="mt-10 flex flex-col items-center gap-4 sm:flex-row">
          <Link
            href="#get-started"
            className="group inline-flex items-center justify-center gap-2 rounded-xl border border-orange-300/30 bg-gradient-to-b from-orange-400 to-orange-600 px-7 py-3.5 text-sm font-semibold text-white shadow-[0_4px_24px_rgba(249,115,22,0.18),inset_0_1px_0_rgba(255,255,255,0.25)] transition hover:-translate-y-0.5 hover:shadow-[0_8px_30px_rgba(249,115,22,0.25)]"
          >
            Explore your knowledge
            <span className="transition-transform group-hover:translate-x-1">
              →
            </span>
          </Link>


        </div>

        <p className="mt-6 text-xs tracking-wide text-gray-600">
          Learn the connections. Close the gaps. Think for yourself.
        </p>
      </div>
    </section>
  );
}

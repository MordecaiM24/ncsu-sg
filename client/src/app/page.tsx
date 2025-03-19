"use client";

export default function Landing() {
  return (
    <div className="relative flex w-full items-center py-10 md:py-20">
      {/* Gradient Background */}
      <div className="gradient absolute inset-0 top-1/2 left-1/2 -z-10 h-3/4 w-3/4 -translate-x-1/2 -translate-y-1/2 blur-[10rem]"></div>

      {/* Container */}
      <div className="bg-opacity-50 ring-foreground/20 -m-2 rounded-xl p-2 ring-1 backdrop-blur-3xl ring-inset lg:-m-4 lg:rounded-2xl">
        {/* Black Rectangle */}
        <div className="bg-black w-[1200px] h-[1200px] ring-border rounded-md ring-1 shadow-2xl lg:rounded-xl"></div>

        {/* Animated Border */}
        <div
          style={{
            "--size": 250,
            "--duration": "12s",
            "--anchor": 90,
            "--border-width": 1.5,
            "--color-from": "#ffaa40",
            "--color-to": "#9c40ff",
            "--delay": "-9s",
          }}
          className="pointer-events-none absolute inset-0 rounded-[inherit] [border:calc(var(--border-width)*1px)_solid_transparent] [mask-clip:padding-box,border-box] [mask-composite:intersect] [mask:linear-gradient(transparent,transparent),linear-gradient(white,white)] after:animate-border-beam after:absolute after:aspect-square after:w-[calc(var(--size)*1px)] after:[animation-delay:var(--delay)] after:[background:linear-gradient(to_left,var(--color-from),var(--color-to),transparent)] after:[offset-anchor:calc(var(--anchor)*1%)_50%] after:[offset-path:rect(0_auto_auto_0_round_calc(var(--size)*1px))]"
        />
      </div>
    </div>
  );
}

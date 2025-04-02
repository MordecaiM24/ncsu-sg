"use client";
import { Open_Sans } from "next/font/google";
import { cn } from "@/lib/utils";
import { useRouter } from "next/navigation";

const openSans = Open_Sans({
  weight: "600",
  subsets: ["latin"],
  display: "swap",
});

export default function Logo() {
  const router = useRouter();

  return (
    <div
      className={cn(
        `absolute left-12 top-4 cursor-pointer p-4 text-3xl text-white`,
        openSans.className,
      )}
      onClick={() => {
        router.push("/");
      }}
    >
      Transpare
      <span className="inline-block cursor-pointer bg-gradient-to-r from-[#C00] to-[#F33] bg-clip-text font-bold text-transparent">
        NC
      </span>
    </div>
  );
}

"use client";
import React, { useEffect, useState } from "react";
import { Search, PenLine, FileText, Layers, ArrowUp } from "lucide-react";
import { cn } from "@/lib/utils";
import { useRouter } from "next/navigation";
import { v4 } from "uuid";

const HomeUI = () => {
  const [docSearch, setDocSearch] = useState(false);
  const [prompt, setPrompt] = useState("");

  const router = useRouter();

  useEffect(() => {
    const existingPrompt = window.localStorage.getItem("prompt");
    console.log(existingPrompt);

    if (existingPrompt !== "" && existingPrompt !== null) {
      setPrompt(existingPrompt);
    }
  }, []);

  async function onSubmit() {
    window.localStorage.setItem("prompt", "");
    window.localStorage.setItem("transferPrompt", prompt);
    const uuid = v4();
    router.push(`c/${uuid}`);
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-black p-4 pb-20 text-white">
      <div className="mt-16 flex w-full max-w-3xl flex-col items-center">
        <h1 className="mb-8 text-3xl font-bold">What do you want to know?</h1>

        <div className="mb-6 w-full">
          <form
            className="flex items-center rounded-full bg-zinc-900 p-3 pl-6"
            onSubmit={(e) => {
              e.preventDefault();
              console.log("submitted");
              onSubmit();
            }}
          >
            <input
              autoFocus
              type="text"
              placeholder="Ask anything"
              className="flex-grow bg-transparent px-2 text-white outline-none"
              value={prompt}
              onChange={(e) => {
                setPrompt(e.target.value);
                window.localStorage.setItem("prompt", e.target.value);
              }}
            />

            <div className="flex items-center space-x-2">
              <button
                type="button"
                className={cn(
                  "flex items-center space-x-1 rounded-full bg-zinc-800 px-3 py-2 duration-75",
                  docSearch
                    ? "border border-blue-500 bg-blue-500/50 text-blue-100"
                    : "border border-zinc-800 bg-zinc-800",
                )}
                onClick={() => setDocSearch((docSearch) => !docSearch)}
              >
                <FileText size={16} />
                <span className="text-sm">Document Search</span>
              </button>

              <button
                disabled={!prompt.trim()}
                type="submit"
                className="flex items-center rounded-full bg-white p-2 text-black transition-all hover:cursor-pointer hover:bg-slate-200 active:bg-slate-300 disabled:cursor-default disabled:text-slate-500 disabled:opacity-25"
              >
                <ArrowUp size={18} />
              </button>
            </div>
          </form>
        </div>

        <div className="flex flex-wrap justify-center gap-2">
          <button
            className="flex items-center space-x-2 rounded-full bg-zinc-900 px-4 py-2 hover:bg-zinc-800"
            onClick={() => {
              setPrompt("What bills talk about DEI?");
            }}
          >
            <FileText size={18} className="text-orange-500" />
            <span className="text-sm">What bills talk about DEI?</span>
          </button>
          <button
            className="flex items-center space-x-2 rounded-full bg-zinc-900 px-4 py-2 hover:bg-zinc-800"
            onClick={() => {
              setPrompt("What are the requirements for senators?");
            }}
          >
            <Layers size={18} className="text-blue-500" />
            <span className="text-sm">
              What are the requirements for senators?
            </span>
          </button>
          <button
            className="flex items-center space-x-2 rounded-full bg-zinc-900 px-4 py-2 hover:bg-zinc-800"
            onClick={() => {
              setPrompt("Who voted for R29?");
            }}
          >
            <PenLine size={18} className="text-purple-500" />
            <span className="text-sm">Who voted for R29?</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default HomeUI;

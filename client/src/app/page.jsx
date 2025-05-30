"use client";
import React, { useEffect, useState } from "react";
import { PenLine, FileText, Layers, ArrowUp, Clock, Trash } from "lucide-react";
import { cn } from "@/lib/utils";
import { useRouter } from "next/navigation";
import { v4 } from "uuid";
import { getAllChats, deleteChat } from "@/lib/db";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const HomeUI = () => {
  const [docSearch, setDocSearch] = useState(false);
  const [prompt, setPrompt] = useState("");
  const [topK, setTopK] = useState(2);
  const [pastChats, setPastChats] = useState([]);
  const [showPastChats, setShowPastChats] = useState(false);
  const [searchType, setSearchType] = useState("legislation");

  const arr = [1, 2, 3, 4, 5, 6, 7, 8, 9];

  const router = useRouter();

  useEffect(() => {
    const existingPrompt = window.localStorage.getItem("prompt");
    if (existingPrompt !== "" && existingPrompt !== null) {
      setPrompt(existingPrompt);
    }

    loadPastChats();
  }, []);

  const loadPastChats = async () => {
    try {
      const chats = await getAllChats();

      const sortedChats = chats.sort((a, b) => b.timestamp - a.timestamp);
      setPastChats(sortedChats);
    } catch (error) {
      console.error("Error loading past chats:", error);
    }
  };

  const handleDeleteChat = async (e, chatId) => {
    e.stopPropagation();
    try {
      await deleteChat(chatId);

      loadPastChats();
    } catch (error) {
      console.error("Error deleting chat:", error);
    }
  };

  async function onSubmit() {
    window.localStorage.setItem("prompt", "");
    window.sessionStorage.setItem("transferPrompt", prompt);

    if (docSearch) {
      window.sessionStorage.setItem("top_k", String(topK));
      window.sessionStorage.setItem("type", "docSearch");
      window.sessionStorage.setItem("search_type", searchType);
    }

    const uuid = v4();
    router.push(`c/${uuid}`);
  }

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const getChatTitle = (chat) => {
    if (chat.messages && chat.messages.length > 0) {
      const firstUserMessage = chat.messages.find((msg) => msg.role === "user");
      if (firstUserMessage) {
        return firstUserMessage.content.length > 30
          ? firstUserMessage.content.substring(0, 30) + "..."
          : firstUserMessage.content;
      }
    }
    return "Untitled Chat";
  };

  const toggleSearchType = (type) => {
    // Only allow setting legislation type, statutes is disabled
    if (type === "legislation") {
      // Toggle legislation on/off if it's already selected
      if (docSearch && searchType === "legislation") {
        setDocSearch(false);
      } else {
        setSearchType(type);
        setDocSearch(true);
      }
    } else if (type === "statutes") {
      toast.info("Statutes search coming soon!", {
        position: "bottom-right",
        autoClose: 1500,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
        theme: "dark",
      });
      // Don't change any state when statutes is clicked
    }
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-black p-4 pb-20 text-white">
      <div className="mt-16 flex w-full max-w-3xl flex-col items-center justify-between">
        <div></div>

        <h1 className="mb-8 text-3xl font-bold">What do you want to know?</h1>

        <div className="mb-6 w-full">
          <div className="relative inline-flex w-full overflow-hidden rounded-full p-[1px] focus-within:outline-none focus-within:ring-slate-400 focus-within:ring-offset-2 focus-within:ring-offset-slate-50">
            <span className="absolute inset-[-1000%] animate-[spin_2s_linear_infinite] bg-[conic-gradient(from_90deg_at_50%_50%,#C00_0%,#F66_50%,#C00_100%)]" />
            <form
              className="relative flex w-full items-center rounded-full bg-zinc-900 p-3 pl-6"
              onSubmit={(e) => {
                e.preventDefault();
                onSubmit();
              }}
            >
              <input
                autoFocus
                type="text"
                placeholder={
                  docSearch ? `Search for ${searchType}...` : "Ask anything"
                }
                className="flex-grow bg-transparent px-2 text-white outline-none"
                value={prompt}
                onChange={(e) => {
                  setPrompt(e.target.value);
                  window.localStorage.setItem("prompt", e.target.value);
                }}
              />
              <div className="flex items-center space-x-2">
                {docSearch && (
                  <select
                    className="text rounded border border-zinc-700 bg-zinc-900 p-1 text-white outline-none"
                    value={topK}
                    onChange={(e) => setTopK(Number(e.target.value))}
                  >
                    {arr.map((n) => (
                      <option key={n} value={n}>
                        {n}
                      </option>
                    ))}
                  </select>
                )}

                <button
                  type="button"
                  className="flex cursor-not-allowed items-center space-x-1 rounded-full border border-zinc-700 bg-zinc-800 px-3 py-2 text-gray-400 opacity-60"
                  onClick={() => toggleSearchType("statutes")}
                >
                  <FileText size={16} />
                  <span className="text-sm">Statutes</span>
                </button>

                <button
                  type="button"
                  className={cn(
                    "flex items-center space-x-1 rounded-full bg-zinc-800 px-3 py-2 duration-75",
                    docSearch && searchType === "legislation"
                      ? "border border-blue-500 bg-blue-500/50 text-blue-100"
                      : "border border-zinc-800 bg-zinc-800",
                  )}
                  onClick={() => toggleSearchType("legislation")}
                >
                  <FileText size={16} />
                  <span className="text-sm">Legislation</span>
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
        </div>

        <div className="mb-6 flex w-full flex-wrap justify-between gap-2">
          <button
            className="flex items-center space-x-2 rounded-full bg-zinc-900 px-4 py-2 hover:bg-zinc-800"
            onClick={() => {
              setPrompt("What bills talk about DEI?");
              setDocSearch(true);
              setSearchType("legislation");
            }}
          >
            <FileText size={18} className="text-orange-500" />
            <span className="text-sm">What bills talk about DEI?</span>
          </button>
          <button
            className="flex items-center space-x-2 rounded-full bg-zinc-900 px-4 py-2 hover:bg-zinc-800"
            onClick={() => {
              setPrompt("Why is reapportionment necessary?");
              setDocSearch(false);
            }}
          >
            <Layers size={18} className="text-blue-500" />
            <span className="text-sm">Why is reapportionment necessary?</span>
          </button>
          <button
            className="flex items-center space-x-2 rounded-full bg-zinc-900 px-4 py-2 hover:bg-zinc-800"
            onClick={() => {
              setPrompt("What was R29 about?");
              setDocSearch(true);
              setSearchType("legislation");
            }}
          >
            <PenLine size={18} className="text-purple-500" />
            <span className="text-sm">What was R29 about?</span>
          </button>

          <button
            className={cn(
              "ml-auto flex items-center space-x-1 rounded-full px-4 py-2 duration-75",
              showPastChats
                ? "border border-green-500 bg-green-500/50 text-green-100"
                : "border border-zinc-800 bg-zinc-900 hover:bg-zinc-800",
            )}
            onClick={() => {
              setShowPastChats(!showPastChats);
              if (!showPastChats) loadPastChats(); // Refresh the list when opening
            }}
          >
            <Clock size={16} />
            <span className="text-sm">Past Chats</span>
          </button>
        </div>

        {/* Show past chats if toggled */}
        {showPastChats && (
          <div className="w-full">
            <h2 className="mb-4 text-xl font-semibold">Past Conversations</h2>

            {pastChats.length > 0 ? (
              <div className="grid max-h-96 gap-3 overflow-y-auto md:grid-cols-2">
                {pastChats.map((chat) => (
                  <div
                    key={chat.id}
                    className="cursor-pointer rounded-lg border border-zinc-700 bg-zinc-800 p-4 hover:bg-zinc-700"
                    onClick={() => router.push(`/c/${chat.id}`)}
                  >
                    <div className="flex items-center justify-between">
                      <h3 className="mb-2 font-medium">{getChatTitle(chat)}</h3>
                      <button
                        className="rounded-full p-1 text-gray-400 hover:bg-red-500/20 hover:text-red-400"
                        onClick={(e) => handleDeleteChat(e, chat.id)}
                      >
                        <Trash size={16} />
                      </button>
                    </div>
                    <div className="flex items-center justify-between text-sm text-gray-400">
                      <div className="flex items-center gap-2">
                        <span>{chat.messages?.length || 0} messages</span>
                        {chat.activeDocIds?.length > 0 && (
                          <span className="rounded bg-blue-900/30 px-1.5 py-0.5 text-xs text-blue-300">
                            {chat.activeDocIds.length} document
                            {chat.activeDocIds.length > 1 ? "s" : ""}
                          </span>
                        )}
                      </div>
                      <span>{formatDate(chat.timestamp)}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="rounded-lg border border-zinc-700 bg-zinc-800 p-6 text-center text-gray-400">
                <p>No conversation history yet.</p>
                <p className="mt-2 text-sm">Start a new chat to see it here!</p>
              </div>
            )}
          </div>
        )}
      </div>
      <ToastContainer className="text-sm" />
    </div>
  );
};

export default HomeUI;

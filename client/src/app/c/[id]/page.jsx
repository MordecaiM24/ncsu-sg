"use client";
import React, { useState, useRef, useEffect } from "react";
import { Search, FileText, ArrowUp, Calendar, Users } from "lucide-react";
import { cn } from "@/lib/utils";

const ChatUI = () => {
  const [docSearch, setDocSearch] = useState(false);
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([]);

  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    const existingPrompt = window.localStorage.getItem("transferPrompt");
    window.localStorage.setItem("transferPrompt", "");
    if (existingPrompt !== null && existingPrompt !== "") {
      setLoading(true);

      setMessages([{ role: "user", content: existingPrompt }]);

      getDocuments(existingPrompt);

      setLoading(false);
    }
  }, []);

  async function handleSubmit() {
    if (!prompt.trim()) return;

    setMessages((prev) => [...prev, { role: "user", content: prompt }]);

    setPrompt("");
    setLoading(true);

    getDocuments(prompt);

    setLoading(false);
  }

  async function getDocuments(query) {
    try {
      const res = await fetch("http://localhost:8000/doc-retrieval", {
        method: "POST",
        body: JSON.stringify({ query, top_k: 4 }),
        headers: {
          "Content-Type": "application/json",
        },
      });

      const response = await res.json();

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: response,
        },
      ]);
    } catch (error) {
      console.error("Error fetching documents:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Sorry, there was an error retrieving documents. Please try again later.",
        },
      ]);
    }
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-between bg-black p-4 text-white">
      <div className="flex min-h-full w-full max-w-3xl flex-col gap-y-8">
        {messages.map((message, idx) => {
          return message.role === "user" ? (
            <UserMessage content={message.content} key={idx} />
          ) : (
            <AssistantMessage content={message.content} key={idx} />
          );
        })}
        <div ref={messagesEndRef} />
      </div>
      <div className="mt-16 flex w-full max-w-3xl flex-col items-center">
        <div className="mb-6 w-full">
          <form
            className="sitcky flex items-center rounded-full bg-zinc-900 p-3 pl-6"
            onSubmit={(e) => {
              e.preventDefault();
              console.log("submitted");
              handleSubmit();
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
                console.log(prompt);
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
                disabled={loading || !prompt.trim()}
                type="submit"
                className="flex items-center rounded-full bg-white p-2 text-black transition-all hover:cursor-pointer hover:bg-slate-200 active:bg-slate-300 disabled:cursor-default disabled:text-slate-500 disabled:opacity-25"
              >
                <ArrowUp size={18} />
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

function UserMessage({ content }) {
  return (
    <div className="ml-auto max-w-[66.666667%] rounded-xl rounded-br-none bg-zinc-800/50 p-4 text-white">
      <p className="whitespace-normal break-words">{content}</p>
    </div>
  );
}

function AssistantMessage({ content }) {
  const isJsonContent = typeof content === "object" && content !== null;

  if (isJsonContent && content.result) {
    return (
      <div className="max-w-full rounded p-4 text-white">
        <div className="mb-4">
          <p className="mb-2 text-sm text-gray-400">
            Found {content.result.length} relevant documents:
          </p>
          <div className="grid grid-cols-2 gap-4">
            {content.result.map((doc, index) => (
              <DocumentCard key={index} document={doc} />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-[66.666667%] rounded p-4 text-white">
      <p className="whitespace-normal break-words">
        {typeof content === "string" ? content : JSON.stringify(content)}
      </p>
    </div>
  );
}
const DocumentCard = ({ document }) => {
  const { id, metadata, page_content, type } = document;

  const documentUrl = `https://ncsu-sg.s3.us-east-1.amazonaws.com/${id}.pdf`;

  const truncateText = (text, maxLength) => {
    if (text && text.length > maxLength) {
      return text.substring(0, maxLength) + "...";
    }
    return text || "";
  };

  const sponsorsArray = metadata.sponsors
    ? typeof metadata.sponsors === "string"
      ? JSON.parse(metadata.sponsors.replace(/'/g, '"'))
      : metadata.sponsors
    : [];

  return (
    <a
      href={documentUrl}
      target="_blank"
      rel="noopener noreferrer"
      className="hover:scale-102 mb-4 block w-full max-w-sm cursor-pointer transition-all duration-200 hover:shadow-lg"
    >
      <div className="overflow-hidden rounded-xl border border-zinc-700 bg-zinc-800">
        <div className="flex items-center justify-between bg-zinc-700 p-3">
          <div className="flex items-center">
            <FileText size={18} className="mr-2 text-blue-400" />
            <span className="font-medium">{metadata.short_title || id}</span>
          </div>
          <div className="rounded bg-zinc-600 px-2 py-1 text-xs">
            {type || "Document"}
          </div>
        </div>

        <div className="p-4">
          <h3 className="mb-2 text-sm font-bold text-gray-300">
            {truncateText(metadata.long_title, 100)}
          </h3>
          <p className="mb-3 text-xs text-gray-400">
            {truncateText(page_content, 180)}
          </p>

          <div className="mt-4 border-t border-zinc-700 pt-3">
            {metadata.first_reading && (
              <div className="mb-2 flex items-center text-xs text-gray-400">
                <Calendar size={14} className="mr-2 text-gray-500" />
                <span>First Reading: {metadata.first_reading}</span>
              </div>
            )}
            {sponsorsArray.length > 0 && (
              <div className="flex items-center text-xs text-gray-400">
                <Users size={14} className="mr-2 text-gray-500" />
                <span>
                  Sponsors: {truncateText(sponsorsArray.join(", "), 60)}
                </span>
              </div>
            )}
          </div>
        </div>

        <div className="bg-zinc-900 p-2 text-center text-xs text-gray-400">
          <span>PDF Document</span>
        </div>
      </div>
    </a>
  );
};

export default ChatUI;

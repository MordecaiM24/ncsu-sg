"use client";
import React, { useState, useRef, useEffect } from "react";
import { FileText, ArrowUp, Calendar, Users } from "lucide-react";
import { cn } from "@/lib/utils";
import ReactMarkdown from "react-markdown";
import { useRouter, useParams } from "next/navigation";
import { saveChat, getChat } from "@/lib/db";

function ChatUI() {
  const [docSearch, setDocSearch] = useState(false);
  const [topK, setTopK] = useState(2);
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([]);
  const [hiddenContext, setHiddenContext] = useState("");
  const [savedDocuments, setSavedDocuments] = useState([]);

  const arr = [1, 2, 3, 4, 5, 6, 7, 8, 9];

  const messagesEndRef = useRef(null);

  const router = useRouter();
  const params = useParams();
  const chatId = params?.id;

  useEffect(() => {
    const loadChatData = async () => {
      if (chatId) {
        try {
          const chatData = await getChat(chatId);
          if (chatData) {
            setMessages(chatData.messages || []);
            setHiddenContext(chatData.hiddenContext || "");
            setSavedDocuments(chatData.documents || []);
          }
        } catch (error) {
          console.error("Error loading chat:", error);
        }
      }
    };

    loadChatData();
  }, [chatId]);

  useEffect(() => {
    const saveChatData = async () => {
      if (
        chatId &&
        (messages.length > 0 || hiddenContext || savedDocuments.length > 0)
      ) {
        try {
          await saveChat(chatId, {
            messages,
            hiddenContext,
            documents: savedDocuments,
          });
        } catch (error) {
          console.error("Error saving chat:", error);
        }
      }
    };

    saveChatData();
  }, [chatId, messages, hiddenContext, savedDocuments]);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        router.push("/");
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [router]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    const existingPrompt = window.sessionStorage.getItem("transferPrompt");
    const type = window.sessionStorage.getItem("type");

    if (existingPrompt === null || existingPrompt === "") {
      return;
    }

    setLoading(true);
    setMessages([{ role: "user", content: existingPrompt }]);

    if (type !== null && type == "docSearch") {
      const k = window.sessionStorage.getItem("top_k");
      getDocuments(existingPrompt, k);
    } else {
      sendToClaude(existingPrompt);
    }

    window.sessionStorage.removeItem("top_k");
    window.sessionStorage.removeItem("transferPrompt");
    window.sessionStorage.removeItem("type");

    setLoading(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleSubmit() {
    if (!prompt.trim()) return;
    setMessages((prev) => [...prev, { role: "user", content: prompt }]);
    setPrompt("");
    setLoading(true);

    if (docSearch) {
      await getDocuments(prompt, topK);
    } else {
      await sendToClaude(prompt);
    }

    setLoading(false);
  }

  async function getDocuments(query, top_k) {
    setDocSearch(false);

    try {
      const res = await fetch("http://localhost:8000/doc-retrieval", {
        method: "POST",
        body: JSON.stringify({ query, top_k }),
        headers: {
          "Content-Type": "application/json",
        },
      });

      const response = await res.json();

      setSavedDocuments((prev) => [...prev, ...response.result]);

      const newContext = response.result.reduce((acc, doc) => {
        return doc.full_text ? acc + doc.full_text + "\n" : acc;
      }, "");
      setHiddenContext((prev) => prev + newContext);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: response,
        },
      ]);
    } catch (error) {
      console.error("error fetching documents:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "sorry, there was an error retrieving documents. please try again later.",
        },
      ]);
    }
  }

  async function sendToClaude(query) {
    let combinedPrompt;

    if (hiddenContext.length !== 0) {
      combinedPrompt = `Context: ${hiddenContext}\n\n${query}`;
    } else {
      combinedPrompt = query;
    }

    try {
      let streamedContent = "";

      setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

      const response = await fetch("http://localhost:8000/claude-stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: [{ role: "user", content: combinedPrompt }],
        }),
      });

      if (!response.body) throw new Error("no body in stream");

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const text = decoder.decode(value, { stream: true });
        streamedContent += text;
        setMessages((prev) => [
          ...prev.slice(0, -1),
          { role: "assistant", content: streamedContent },
        ]);
      }
    } catch (err) {
      console.error("error calling claude:", err);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "yeah so claude's not vibing rn. try again later.",
        },
      ]);
    }
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-between bg-black p-4 pt-16 text-white">
      <div className="flex min-h-full w-full max-w-3xl flex-col gap-y-8 pb-20">
        {messages.map((message, idx) => {
          return message.role === "user" ? (
            <UserMessage content={message.content} key={idx} />
          ) : (
            <AssistantMessage
              content={message.content}
              documents={savedDocuments}
              key={idx}
            />
          );
        })}
        <div ref={messagesEndRef} />
      </div>
      <div className="fixed bottom-0 left-0 right-0 z-10 bg-black/80 px-4 py-4 backdrop-blur-sm">
        <div className="mx-auto max-w-3xl">
          <form
            className="flex items-center rounded-full bg-zinc-900 p-3 pl-6"
            onSubmit={(e) => {
              e.preventDefault();
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
}

function UserMessage({ content }) {
  return (
    <div className="ml-auto max-w-[66.666667%] rounded-xl rounded-br-none bg-zinc-800/50 p-4 py-3 text-lg text-white">
      <p className="whitespace-normal break-words">{content}</p>
    </div>
  );
}

function AssistantMessage({ content }) {
  const isJsonContent = typeof content === "object" && content !== null;
  const isLoadingMessage =
    content === "Getting more information to answer your question...\n\n";

  if (isLoadingMessage) {
    return (
      <div className="max-w-[66.666667%] rounded p-4 text-white">
        <p
          className="animate-shimmer whitespace-normal break-words bg-gradient-to-r from-transparent via-white/80 via-50% to-transparent bg-[length:400px_100%] bg-clip-text bg-[0_0] text-white/50"
          style={{ "--shimmer-width": "400px" }}
        >
          {content}
        </p>
      </div>
    );
  }

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
    <div className="max-w-full rounded p-4 text-gray-100">
      <div className="text-lg">
        <ReactMarkdown
          components={{
            ul: ({ ...props }) => (
              <ul
                style={{
                  display: "block",
                  listStyleType: "disc",
                  paddingInlineStart: "40px",
                }}
                {...props}
              />
            ),
            ol: ({ ...props }) => (
              <ol
                style={{
                  display: "block",
                  listStyleType: "decimal",
                  paddingInlineStart: "40px",
                }}
                {...props}
              />
            ),
          }}
        >
          {typeof content === "string" ? content : JSON.stringify(content)}
        </ReactMarkdown>
      </div>
    </div>
  );
}

const DocumentCard = ({ document }) => {
  const { id, metadata, page_content } = document;

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
            {"Legislation"}
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
          <span>PDF </span>
        </div>
      </div>
    </a>
  );
};

export default ChatUI;

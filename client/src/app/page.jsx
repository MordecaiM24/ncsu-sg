"use client";

import React, { useState, useEffect } from "react";
import {
  Search,
  FileText,
  MessageSquare,
  ChevronDown,
  ArrowRight,
  Sparkles,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

const LegislativeTransparencyTool = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchMode, setSearchMode] = useState("chat"); // 'chat' or 'documents'
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [activeView, setActiveView] = useState("landing"); // 'landing', 'chat', 'documents'
  const [messages, setMessages] = useState([]);
  const [documents, setDocuments] = useState([]);

  const ncsuRed = "#C00";

  const suggestions = [
    "What's the budget for student organizations?",
    "How does the election process work?",
    "Recent resolutions on sustainability",
  ];

  const handleSearch = () => {
    if (!searchQuery.trim()) return;

    setIsLoading(true);

    // Simulate API call
    setTimeout(() => {
      if (searchMode === "documents") {
        setDocuments([
          {
            id: 1,
            title: "Budget Allocation FY2024-25",
            section: "Article II, Sections 3-7",
            snippet:
              "Funds shall be distributed based on demonstrated need and historical precedent...",
          },
          {
            id: 2,
            title: "SG Constitution",
            section: "Article IV",
            snippet:
              "The legislative authority shall be vested in the Student Senate...",
          },
          {
            id: 3,
            title: "Resolution 47",
            section: "Full Document",
            snippet:
              "Whereas the student body has expressed interest in expanding sustainable practices...",
          },
        ]);
        setActiveView("documents");
      } else {
        setMessages([
          { id: 1, sender: "user", text: searchQuery },
          {
            id: 2,
            sender: "bot",
            text: "Based on the current legislative documents, the budget allocation process works through the Student Senate Finance Committee. They review applications in February and make recommendations to the full Senate by March.",
            citations: [
              {
                id: 1,
                title: "Budget Allocation FY2024-25",
                section: "Article II, Section 4",
              },
              {
                id: 2,
                title: "SG Constitution",
                section: "Article IV, Section 8",
              },
            ],
          },
        ]);
        setActiveView("chat");
      }
      setIsLoading(false);
    }, 1500);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      handleSearch();
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setSearchQuery(suggestion);
    handleSearch();
  };

  const handleModeChange = (mode) => {
    setSearchMode(mode);
    setIsDropdownOpen(false);
  };

  // Rotating border animation for suggestions
  useEffect(() => {
    if (activeView !== "landing") return;

    const rotateGlow = () => {
      const suggestions = document.querySelectorAll(".suggestion-card");
      suggestions.forEach((card) => {
        const border = card.querySelector(".rotating-border");
        if (border) {
          let rotation = 0;
          setInterval(() => {
            rotation = (rotation + 1) % 360;
            border.style.transform = `rotate(${rotation}deg)`;
          }, 50);
        }
      });
    };

    rotateGlow();
  }, [activeView]);

  return (
    <div className="flex flex-col min-h-screen bg-black text-white">
      {/* Header */}
      <header className="w-full py-4 px-6 flex justify-between items-center z-10 bg-black">
        <h1 className="text-xl font-bold flex items-center">
          <Sparkles size={20} className="mr-2" style={{ color: ncsuRed }} />
          <span>LegisLight</span>
          <span className="text-sm ml-2 bg-gray-800 px-2 py-0.5 rounded-full text-gray-400">
            NCSU
          </span>
        </h1>
        <Button
          variant="outline"
          size="sm"
          className="border-gray-700 hover:border-red-500 hover:text-red-500 bg-transparent"
        >
          Sign In
        </Button>
      </header>

      {/* Main Content */}
      <main className="flex-1 w-full max-w-4xl mx-auto p-4 md:p-8 flex flex-col">
        {activeView === "landing" && (
          <div className="w-full flex flex-col items-center mt-8 md:mt-16">
            <div className="text-center mb-12">
              <h2 className="text-4xl md:text-5xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-white to-red-500">
                Campus Policy, Simplified
              </h2>
              <p className="text-xl text-gray-400">
                Find and understand student government documents instantly
              </p>
            </div>

            {/* Search Box and Dropdown */}
            <div className="w-full max-w-xl mb-12 relative">
              <div className="flex shadow-lg rounded-xl overflow-hidden ring-1 ring-gray-800 hover:ring-red-800 transition-all">
                <Input
                  type="text"
                  placeholder="Ask about NCSU student government..."
                  className="flex-1 p-4 h-14 text-lg bg-gray-900 border-none focus:ring-0 focus-visible:ring-0 focus-visible:ring-offset-0"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={handleKeyDown}
                />

                <div className="relative">
                  <Button
                    className="h-14 px-3 border-none rounded-none bg-gray-800 hover:bg-gray-700"
                    onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                  >
                    {searchMode === "chat" ? (
                      <MessageSquare size={18} />
                    ) : (
                      <FileText size={18} />
                    )}
                    <ChevronDown size={16} className="ml-1" />
                  </Button>

                  {isDropdownOpen && (
                    <div className="absolute right-0 mt-1 bg-gray-800 border border-gray-700 rounded-lg shadow-lg z-10 w-48 overflow-hidden">
                      <button
                        className="w-full px-4 py-3 text-left hover:bg-gray-700 flex items-center border-b border-gray-700"
                        onClick={() => handleModeChange("chat")}
                      >
                        <MessageSquare size={16} className="mr-2" />
                        <span>Explanation</span>
                      </button>
                      <button
                        className="w-full px-4 py-3 text-left hover:bg-gray-700 flex items-center"
                        onClick={() => handleModeChange("documents")}
                      >
                        <FileText size={16} className="mr-2" />
                        <span>Documents</span>
                      </button>
                    </div>
                  )}
                </div>

                <Button
                  className="h-14 w-14 flex justify-center items-center"
                  style={{ backgroundColor: ncsuRed }}
                  onClick={handleSearch}
                >
                  <Search size={20} />
                </Button>
              </div>
            </div>

            {/* Suggested Queries with Glowing Border */}
            <div className="w-full max-w-xl grid grid-cols-1 gap-6 mb-16">
              {suggestions.map((suggestion, index) => (
                <div key={index} className="relative suggestion-card">
                  {/* Rotating border */}
                  <div
                    className="absolute -inset-0.5 bg-red-500 rounded-lg opacity-70 rotating-border"
                    style={{
                      background: `linear-gradient(90deg, ${ncsuRed}, transparent, ${ncsuRed})`,
                      backgroundSize: "200% 100%",
                      zIndex: -1,
                    }}
                  ></div>
                  <Button
                    variant="outline"
                    className="w-full p-5 h-auto bg-gray-900 border-none hover:bg-gray-800 transition-all flex justify-between items-center relative z-10"
                    onClick={() => handleSuggestionClick(suggestion)}
                  >
                    <span className="text-base font-normal text-left">
                      {suggestion}
                    </span>
                    <ArrowRight size={16} className="opacity-70" />
                  </Button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Loading Screen */}
        {isLoading && (
          <div className="w-full h-64 flex flex-col items-center justify-center">
            <div className="relative w-24 h-24 mb-6">
              <div className="absolute inset-0 rounded-full bg-gray-800"></div>
              <div
                className="absolute inset-0 rounded-full bg-gradient-to-r from-gray-800 via-red-500 to-gray-800 bg-[length:200%_100%] animate-shimmer"
                style={{
                  WebkitMaskImage:
                    "linear-gradient(90deg, transparent 40%, #000 50%, transparent 60%)",
                  maskImage:
                    "linear-gradient(90deg, transparent 40%, #000 50%, transparent 60%)",
                  animationDuration: "1.5s",
                  animationIterationCount: "infinite",
                }}
              ></div>
              <div className="absolute inset-0 flex items-center justify-center">
                <Sparkles size={40} style={{ color: ncsuRed }} />
              </div>
            </div>
            <p className="text-lg font-medium">Analyzing documents...</p>
          </div>
        )}

        {/* Chat View */}
        {activeView === "chat" && !isLoading && (
          <div className="w-full h-full flex flex-col gap-4 mt-4">
            {/* Chat Messages */}
            <div className="flex-1 border border-gray-800 rounded-xl overflow-hidden bg-gray-900">
              <div className="p-4 bg-gray-900 border-b border-gray-800 flex justify-between items-center">
                <h3 className="font-medium flex items-center">
                  <MessageSquare
                    size={18}
                    className="mr-2"
                    style={{ color: ncsuRed }}
                  />
                  AI Assistant
                </h3>
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-gray-400 hover:text-white"
                  onClick={() => setActiveView("landing")}
                >
                  New Search
                </Button>
              </div>

              <div className="h-96 overflow-y-auto p-4 space-y-6">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${
                      message.sender === "user"
                        ? "justify-end"
                        : "justify-start"
                    }`}
                  >
                    <div
                      className={`max-w-3/4 p-4 rounded-xl ${
                        message.sender === "user"
                          ? "bg-red-900 text-white"
                          : "bg-gray-800 border border-gray-700"
                      }`}
                    >
                      <p className="leading-relaxed">{message.text}</p>
                      {message.citations && (
                        <div className="mt-3 pt-3 border-t border-gray-700 text-sm text-gray-400">
                          <p className="font-medium text-white">Sources:</p>
                          <ul className="mt-2 space-y-1">
                            {message.citations.map((citation) => (
                              <li
                                key={citation.id}
                                className="flex items-start"
                              >
                                <span className="inline-block w-1 h-1 rounded-full bg-red-500 mt-2 mr-2"></span>
                                {citation.title} - {citation.section}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              <div className="p-4 border-t border-gray-800 flex">
                <Input
                  type="text"
                  placeholder="Ask a follow-up question..."
                  className="flex-1 bg-gray-800 border-gray-700 focus:border-red-500"
                />
                <Button className="ml-2" style={{ backgroundColor: ncsuRed }}>
                  <Search size={18} />
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* Documents View */}
        {activeView === "documents" && !isLoading && (
          <div className="w-full mt-4">
            <div className="mb-6 flex justify-between items-center">
              <h3 className="text-xl font-medium flex items-center">
                <FileText
                  size={20}
                  className="mr-2"
                  style={{ color: ncsuRed }}
                />
                Document Results
              </h3>
              <Button
                variant="outline"
                size="sm"
                className="border-gray-700 hover:border-red-500 text-gray-400 hover:text-white"
                onClick={() => setActiveView("landing")}
              >
                New Search
              </Button>
            </div>

            <div className="space-y-4">
              {documents.map((doc) => (
                <Card
                  key={doc.id}
                  className="bg-gray-900 border-gray-800 hover:border-red-900 transition-all overflow-hidden"
                >
                  <CardHeader>
                    <CardTitle className="text-lg">{doc.title}</CardTitle>
                    <CardDescription className="text-gray-400">
                      {doc.section}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-300">{doc.snippet}</p>
                  </CardContent>
                  <CardFooter className="bg-gray-800 flex justify-end">
                    <Button
                      style={{ backgroundColor: ncsuRed }}
                      size="sm"
                      className="flex items-center"
                    >
                      View Full Document
                      <ArrowRight size={16} className="ml-2" />
                    </Button>
                  </CardFooter>
                </Card>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="w-full py-4 px-6 mt-6 border-t border-gray-800 text-gray-400">
        <div className="max-w-4xl mx-auto flex justify-between items-center">
          <div className="flex items-center">
            <Sparkles size={16} className="mr-2" style={{ color: ncsuRed }} />
            <span className="font-medium text-white">LegisLight</span>
          </div>
          <div className="text-sm">© 2025 NCSU Student Initiative</div>
        </div>
      </footer>
    </div>
  );
};

export default LegislativeTransparencyTool;

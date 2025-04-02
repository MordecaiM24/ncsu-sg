"use client";

const DB_NAME = "chatHistoryDB";
const DB_VERSION = 1;
const CHATS_STORE = "chats";

// Initialize the database
export const initDB = () => {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onupgradeneeded = (event) => {
      const db = event.target.result;

      if (!db.objectStoreNames.contains(CHATS_STORE)) {
        const store = db.createObjectStore(CHATS_STORE, { keyPath: "id" });

        store.createIndex("timestamp", "timestamp", { unique: false });
      }
    };

    request.onsuccess = (event) => {
      resolve(event.target.result);
    };

    request.onerror = (event) => {
      console.error("Database error:", event.target.error);
      reject(event.target.error);
    };
  });
};

export const saveChat = async (chatId, data) => {
  const db = await initDB();
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([CHATS_STORE], "readwrite");
    const store = transaction.objectStore(CHATS_STORE);

    const chatData = {
      id: chatId,
      messages: data.messages || [],
      hiddenContext: data.hiddenContext || "",
      documents: data.documents || [],
      timestamp: Date.now(),
    };

    const request = store.put(chatData);

    request.onsuccess = () => resolve(chatData);
    request.onerror = (event) => reject(event.target.error);
  });
};

export const getChat = async (chatId) => {
  const db = await initDB();
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([CHATS_STORE], "readonly");
    const store = transaction.objectStore(CHATS_STORE);
    const request = store.get(chatId);

    request.onsuccess = () => resolve(request.result);
    request.onerror = (event) => reject(event.target.error);
  });
};

export const getAllChats = async () => {
  const db = await initDB();
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([CHATS_STORE], "readonly");
    const store = transaction.objectStore(CHATS_STORE);
    const index = store.index("timestamp");
    const request = index.getAll();

    request.onsuccess = () => resolve(request.result);
    request.onerror = (event) => reject(event.target.error);
  });
};

export const deleteChat = async (chatId) => {
  const db = await initDB();
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([CHATS_STORE], "readwrite");
    const store = transaction.objectStore(CHATS_STORE);
    const request = store.delete(chatId);

    request.onsuccess = () => resolve(true);
    request.onerror = (event) => reject(event.target.error);
  });
};

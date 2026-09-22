const API_BASE_URL = "http://localhost:8000";


// ========================================
// STATE
// ========================================

let currentChatId = null;


// ========================================
// ELEMENTS
// ========================================

const newChatBtn =
    document.getElementById("newChatBtn");

const uploadBtn =
    document.getElementById("uploadBtn");

const pdfInput =
    document.getElementById("pdfInput");

const uploadStatus =
    document.getElementById("uploadStatus");

const chatIdElement =
    document.getElementById("chatId");

const chatList =
    document.getElementById("chatList");

const messagesContainer =
    document.getElementById("messages");

const messageInput =
    document.getElementById("messageInput");

const sendBtn =
    document.getElementById("sendBtn");


// ========================================
// PAGE LOAD
// ========================================
//
// When the chatbot opens:
//
// GET /all_users
//
// Expected response:
//
// {
//     "users": [
//         "user_id_1",
//         "user_id_2",
//         "user_id_3"
//     ]
// }
//
// ========================================

document.addEventListener(
    "DOMContentLoaded",
    loadAllChats
);


// ========================================
// LOAD ALL PREVIOUS CHATS
// GET /all_users
// ========================================

async function loadAllChats() {

    try {

        chatList.innerHTML =
            `<div class="chat-list-loading">
                Loading chats...
            </div>`;


        const response = await fetch(
            `${API_BASE_URL}/all_users`
        );


        if (!response.ok) {

            throw new Error(
                "Could not load previous chats."
            );
        }


        const data = await response.json();

        console.log(
            "All users response:",
            data
        );


        /*
         * Expected:
         *
         * {
         *     "users": [
         *         "abc",
         *         "def",
         *         "xyz"
         *     ]
         * }
         */

        const users = data.users || [];


        displayChatList(users);


    } catch (error) {

        console.error(
            "Error loading chats:",
            error
        );


        chatList.innerHTML =
            `<div class="no-chats">
                Could not load previous chats.
            </div>`;
    }
}


// ========================================
// DISPLAY CHAT LIST
// ========================================

function displayChatList(users) {

    chatList.innerHTML = "";


    if (!users || users.length === 0) {

        chatList.innerHTML =
            `<div class="no-chats">
                No previous chats.
            </div>`;

        return;
    }


    users.forEach(userId => {

        const chatRow = document.createElement("div")
        chatRow.className = "chat-row"

        const chatButton =
            document.createElement("button");


        chatButton.className =
            "chat-item";


        chatButton.textContent =
            userId;


        chatButton.title =
            userId;

        const deleteButton = document.createElement("button");
        deleteButton.className = "chat-dlt";
        deleteButton.title = "🗑️"
        deleteButton.textContent = "🗑️"



        /*
         * When a previous chat is clicked,
         * load its history.
         */

        chatButton.addEventListener(
            "click",
            () => {

                selectChat(
                    userId,
                    chatButton
                );

            }
        );
        deleteButton.addEventListener(
            "click",
            (event) => {
                event.stopPropagation();
                deleteChat(
                    userId,
                    chatRow
                )
            }
        )


        chatRow.appendChild(
            chatButton
        );
        chatRow.appendChild(
            deleteButton
        );
        chatList.appendChild(chatRow);

    });
}


// ========================================
// DELETE CHAT
// DELETE /delete_chat?userid=...
// ========================================

async function deleteChat(userId, chatRow) {

    if (!confirm("Delete this chat?")) {
        return;
    }

    try {
        const response = await fetch(
            `${API_BASE_URL}/delete_chat?userid=${encodeURIComponent(userId)}`,
            {
                method: "DELETE"
            }
        );

        const data = await response.json();

        if (!response.ok || data.error) {
            throw new Error(data.detail || data.error || "Could not delete chat.");
        }

        chatRow.remove();

        if (currentChatId === userId) {
            currentChatId = null;
            chatIdElement.textContent = "";
            messagesContainer.innerHTML = "";
            uploadStatus.textContent = "";
            pdfInput.value = "";
        }

        if (!chatList.querySelector(".chat-row")) {
            chatList.innerHTML = `<div class="no-chats">No previous chats.</div>`;
        }
    } catch (error) {
        console.error("Delete chat error:", error);
        alert(error.message || "Could not delete chat.");
    }
}


// ========================================
// SELECT PREVIOUS CHAT
// ========================================
//
// 1. Set currentChatId
// 2. Highlight selected chat
// 3. Call /history
// 4. Display history
//
// ========================================

async function selectChat(
    userId,
    selectedButton
) {

    currentChatId = userId;


    // Update current chat display

    chatIdElement.textContent =
        currentChatId;


    // Remove active state

    const allChatButtons =
        document.querySelectorAll(
            ".chat-item"
        );


    allChatButtons.forEach(button => {

        button.classList.remove(
            "active"
        );

    });


    // Highlight selected chat

    if (selectedButton) {

        selectedButton.classList.add(
            "active"
        );

    }


    // Clear current messages

    messagesContainer.innerHTML = "";


    uploadStatus.textContent = "";


    // Load history

    await loadHistory(
        currentChatId
    );
}


// ========================================
// LOAD CHAT HISTORY
// GET /history?user_id=...
// ========================================
//
// Expected response:
//
// [
//     {
//         "query": "What is AI?",
//         "answer": "AI means...",
//         "timestamp": "..."
//     },
//     {
//         "query": "What is RAG?",
//         "answer": "RAG means...",
//         "timestamp": "..."
//     }
// ]
//
// The API already returns the list in order,
// so we simply display it in that order.
//
// ========================================

async function loadHistory(userId) {

    try {

        const response = await fetch(
            `/history?user_id=${encodeURIComponent(userId)}`
        );


        if (!response.ok) {

            throw new Error(
                "Could not load chat history."
            );
        }


        const history =
            await response.json();


        console.log(
            "Chat history:",
            history
        );


        messagesContainer.innerHTML = "";


        if (
            !Array.isArray(history) ||
            history.length === 0
        ) {

            addBotMessage(
                "No messages in this chat yet."
            );

            return;
        }


        /*
         * The API returns:
         *
         * [
         *   {
         *      query,
         *      answer,
         *      timestamp
         *   }
         * ]
         *
         * Display them in the same order.
         */

        history.forEach(item => {


            // User's question

            if (item.query) {

                addUserMessage(
                    item.query,
                    item.timestamp
                );

            }


            // Bot's answer

            if (item.answer) {

                addBotMessage(
                    item.answer,
                    false,
                    item.timestamp
                );

            }

        });


        scrollToBottom();


    } catch (error) {

        console.error(
            "History error:",
            error
        );


        messagesContainer.innerHTML = "";


        addBotMessage(
            "Could not load the chat history."
        );

    }
}


// ========================================
// NEW CHAT
// POST /new_user
// ========================================

newChatBtn.addEventListener(
    "click",
    createNewChat
);


async function createNewChat() {

    try {

        newChatBtn.disabled = true;


        const response = await fetch(
            `${API_BASE_URL}/new_user`,
            {
                method: "POST"
            }
        );


        if (!response.ok) {

            throw new Error(
                "Could not create a new chat."
            );
        }


        const data =
            await response.json();


        console.log(
            "New chat response:",
            data
        );


        /*
         * Expected:
         *
         * {
         *     "user_id": "abc123"
         * }
         */

        currentChatId =
            data.user_id ||
            data.id ||
            data.userId;


        if (!currentChatId) {

            alert(
                "New chat was created, but the API did not return a user ID."
            );

            return;
        }


        // Update current chat

        chatIdElement.textContent =
            currentChatId;


        // Clear messages

        messagesContainer.innerHTML = "";


        // Clear upload

        uploadStatus.textContent = "";

        pdfInput.value = "";


        // Add welcome message

        addBotMessage(
            "New chat created. Please upload a PDF to get started."
        );


        /*
         * Add the newly created chat to the
         * previous chat list immediately.
         */

        addNewChatToList(
            currentChatId
        );


        // Highlight new chat

        highlightChat(
            currentChatId
        );


    } catch (error) {

        console.error(error);


        alert(
            "Unable to create a new chat. Please try again."
        );


    } finally {

        newChatBtn.disabled = false;
    }
}


// ========================================
// ADD NEW CHAT TO SIDEBAR
// ========================================

function addNewChatToList(userId) {

    /*
     * Remove "No previous chats" message
     */

    const noChats =
        chatList.querySelector(
            ".no-chats"
        );


    if (noChats) {
        noChats.remove();
    }


    /*
     * Avoid duplicate chat IDs
     */

    const existing =
        Array.from(
            chatList.querySelectorAll(
                ".chat-item"
            )
        ).find(
            button =>
                button.textContent === userId
        );


    if (existing) {
        return;
    }

    const chatRow = document.createElement("div")
    chatRow.className = "chat-row"

    const chatButton =
        document.createElement("button");


    chatButton.className =
        "chat-item";


    chatButton.textContent =
        userId;


    chatButton.title =
        userId;

    const deleteButton = document.createElement("button");
    deleteButton.className = "chat-dlt";
    deleteButton.title = "🗑️"
    deleteButton.textContent = "🗑️"


    chatButton.addEventListener(
        "click",
        () => {

            selectChat(
                userId,
                chatButton
            );

        }
    );
    deleteButton.addEventListener(
        "click",
        (event) => {
            event.stopPropagation();
            deleteChat(
                userId,
                chatRow
            )
        }
    )
    chatRow.appendChild(
        chatButton
    );
    chatRow.appendChild(
        deleteButton
    );

    /*
     * Put the newest chat at the top.
     */

    chatList.prepend(
        chatRow
    );
}


// ========================================
// HIGHLIGHT CHAT
// ========================================

function highlightChat(userId) {

    const buttons =
        document.querySelectorAll(
            ".chat-item"
        );


    buttons.forEach(button => {

        if (
            button.textContent === userId
        ) {

            button.classList.add(
                "active"
            );

        } else {

            button.classList.remove(
                "active"
            );

        }

    });
}


// ========================================
// UPLOAD PDF
// POST /upload?user_id=...
// ========================================

uploadBtn.addEventListener(
    "click",
    uploadPDF
);


async function uploadPDF() {

    if (!currentChatId) {

        alert(
            "Please create a new chat first."
        );

        return;
    }


    const file =
        pdfInput.files[0];


    if (!file) {

        alert(
            "Please select a PDF file first."
        );

        return;
    }


    // Validate PDF

    if (
        file.type !== "application/pdf" &&
        !file.name
            .toLowerCase()
            .endsWith(".pdf")
    ) {

        alert(
            "Please upload a PDF file."
        );

        return;
    }


    const formData =
        new FormData();


    formData.append(
        "file",
        file
    );


    try {

        uploadBtn.disabled = true;


        uploadStatus.textContent =
            "Uploading PDF...";


        const response =
            await fetch(
                `/upload?user_id=${encodeURIComponent(currentChatId)}`,
                {
                    method: "POST",
                    body: formData
                }
            );


        const data =
            await response.json();


        console.log(
            "Upload response:",
            data
        );


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "PDF upload failed."
            );
        }


        uploadStatus.textContent =
            `Uploaded: ${file.name}`;


        addBotMessage(
            `PDF "${file.name}" uploaded successfully. You can now ask questions.`
        );


    } catch (error) {

        console.error(error);


        uploadStatus.textContent =
            "Upload failed.";


        alert(
            error.message ||
            "Could not upload the PDF."
        );


    } finally {

        uploadBtn.disabled = false;
    }
}


// ========================================
// SEND MESSAGE
// POST /send?user_id=...&query=...
// ========================================

sendBtn.addEventListener(
    "click",
    sendMessage
);


async function sendMessage() {

    const query =
        messageInput.value.trim();


    if (!query) {
        return;
    }


    if (!currentChatId) {

        alert(
            "Please create a new chat first."
        );

        return;
    }


    // Show user message

    addUserMessage(
        query
    );


    messageInput.value = "";


    sendBtn.disabled = true;


    // Show loading

    const loadingMessage =
        addBotMessage(
            "Thinking...",
            true
        );


    try {

        const url =
            `/send?user_id=${encodeURIComponent(currentChatId)}` +
            `&query=${encodeURIComponent(query)}`;


        const response =
            await fetch(
                url,
                {
                    method: "POST"
                }
            );


        const data =
            await response.json();


        console.log(
            "Send response:",
            data
        );


        // ====================================
        // PDF NOT UPLOADED
        // ====================================

        if (
            data.error &&
            data.error
                .toLowerCase()
                .includes("upload a pdf")
        ) {

            loadingMessage.remove();


            alert(
                "Please upload a PDF first."
            );


            addBotMessage(
                "Please upload a PDF before asking questions."
            );


            return;
        }


        if (!response.ok) {

            loadingMessage.remove();


            alert(
                data.detail ||
                "Something went wrong while processing your question."
            );


            return;
        }


        // Remove loading

        loadingMessage.remove();


        // Get answer

        const answer =
            data.answer ||
            data.response ||
            data.message ||
            data.result;


        if (answer) {

            addBotMessage(
                answer
            );

        } else {

            addBotMessage(
                JSON.stringify(
                    data,
                    null,
                    2
                )
            );
        }


    } catch (error) {

        console.error(error);


        loadingMessage.remove();


        alert(
            "Could not connect to the chatbot server."
        );


    } finally {

        sendBtn.disabled = false;

        messageInput.focus();
    }
}


// ========================================
// ADD USER MESSAGE
// ========================================

function addUserMessage(
    text,
    timestamp = null
) {

    const message =
        document.createElement("div");


    message.className =
        "message user-message";


    message.textContent =
        text;


    if (timestamp) {

        addTimestamp(
            message,
            timestamp
        );

    }


    messagesContainer.appendChild(
        message
    );


    scrollToBottom();


    return message;
}


// ========================================
// ADD BOT MESSAGE
// ========================================

function addBotMessage(
    text,
    loading = false,
    timestamp = null
) {

    const message =
        document.createElement("div");


    message.className =
        "message bot-message";


    if (loading) {

        message.classList.add(
            "loading"
        );

    }


    message.textContent =
        text;


    if (timestamp) {

        addTimestamp(
            message,
            timestamp
        );

    }


    messagesContainer.appendChild(
        message
    );


    scrollToBottom();


    return message;
}


// ========================================
// ADD TIMESTAMP
// ========================================

function addTimestamp(
    messageElement,
    timestamp
) {

    const time =
        document.createElement("span");


    time.className =
        "message-time";


    time.textContent =
        formatTimestamp(timestamp);


    messageElement.appendChild(
        time
    );
}


// ========================================
// FORMAT TIMESTAMP
// ========================================

function formatTimestamp(timestamp) {

    if (!timestamp) {
        return "";
    }


    try {

        const date =
            new Date(timestamp);


        if (isNaN(date.getTime())) {

            return timestamp;
        }


        return date.toLocaleString();


    } catch {

        return timestamp;
    }
}


// ========================================
// SCROLL TO BOTTOM
// ========================================

function scrollToBottom() {

    messagesContainer.scrollTop =
        messagesContainer.scrollHeight;
}


// ========================================
// ENTER KEY
// ========================================

messageInput.addEventListener(
    "keydown",
    function(event) {

        if (
            event.key === "Enter"
        ) {

            event.preventDefault();

            sendMessage();
        }

    }
);


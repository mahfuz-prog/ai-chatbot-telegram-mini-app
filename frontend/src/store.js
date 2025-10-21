import { reactive, readonly } from "vue"

// for development, in production state will be empty string
const useFakeUser = import.meta.env.VITE_USE_FAKE_USER === 'true'

const authState = reactive({
  SERVER_ADDR: import.meta.env.VITE_SERVER_ADDR,
  userName: useFakeUser ? import.meta.env.VITE_USER_NAME : "",
  firstName: useFakeUser ? import.meta.env.VITE_FIRST_NAME : "",
  lastName: useFakeUser ? import.meta.env.VITE_LAST_NAME : "",
  profilePic: useFakeUser ? import.meta.env.VITE_PROFILE_PIC : "",
})

const authActions = {
    setAuthInfo(auth) {
        authState.userName = auth.username
        authState.firstName = auth.first_name
        authState.lastName = auth.last_name
        authState.profilePic = auth.photo_url
    },

    resetAuth() {
        authState.userName = ""
        authState.firstName = ""
        authState.lastName = ""
        authState.profilePic = ""
    }
}


// ========================================
// chat info
// pagination = { "currentPage": "", "hasPrev": "", "hasNext": "", "pageList": [] } 
// chats = [{'id': 1, 'title': 'New Chat', 'created_at': '2025-07-30T18:02:14.125628Z', 'updated_at': '2025-07-30T18:02:14.125628Z'}]

const chatState = reactive({
    pagination: {},
    chatList: new Map()  // ordered map
})

const chatActions = {
    resetChats() {
        chatState.pagination = {}
        chatState.chatList.clear()
    },

    // add a chat at beginning of chatList
    addChatAtBeginning(newChat) {
        const tempMap = new Map()
        tempMap.set(newChat.id, newChat)

        chatState.chatList.forEach((chat, id) => {
            tempMap.set(id, chat)
        })

        chatState.chatList = tempMap
    },


    // populate chatList
    setChats(data) {
        // reset chatList
        chatActions.resetChats()
        data.forEach(chat => {
            chatState.chatList.set(chat.id, chat)
        })
    },

    // delete a single chat
    deleteChat(chatId) {
        chatState.chatList.delete(chatId)
    },
}


// =================================================
// active conversation/chat
const activeChatState = reactive({
    id : "",
    title : "",
    uniqueHexId : "",
    messages : new Map()  // ordered map
})

const activeChatActions = {
    resetActiveChat() {
        activeChatState.id = ""
        activeChatState.title = ""
        activeChatState.uniqueHexId = ""
        activeChatState.messages.clear()
    },

    setActiveChat(chat) {
        activeChatActions.resetActiveChat()

        activeChatState.id = chat.id
        activeChatState.title = chat.title
        activeChatState.uniqueHexId = chat.uniqueHexId

        chat.messages.forEach(message => {
            activeChatState.messages.set(message.id, message)
        })
    },

    addMessage(newMessage) {
        activeChatState.messages.set(newMessage.id, newMessage)
    },

    removeMessageById(messageId) {
        activeChatState.messages.delete(messageId)
    }
}

export default {
	authState: readonly(authState),
	authActions,

    chatState: readonly(chatState),
    chatActions,

    activeChatState: readonly(activeChatState),
    activeChatActions
}
<template>
  <div class="admin-chat">
    <h2>Chat with Users</h2>
    <div class="chat-container">
      <div class="chat-messages">
        <div v-for="message in messages" :key="message.id" class="message">
          <span class="sender">{{ message.sender_name }}:</span>
          <span class="content">{{ message.message }}</span>
          <span class="timestamp">{{ formatTimestamp(message.timestamp) }}</span>
        </div>
      </div>
      <div class="chat-input">
        <input type="text" v-model="newMessage" @keyup.enter="sendMessage" placeholder="Type your message...">
        <button @click="sendMessage">Send</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { io } from 'socket.io-client';

const socket = ref(null);
const messages = ref([]);
const newMessage = ref('');

const isAdmin = computed(() => {
  const role = localStorage.getItem('role');
  return role === 'admin';
});

onMounted(() => {
  if (!isAdmin.value) {
    // Redirect if not admin
    window.location.href = '/admin/dashboard';
    return;
  }

  const token = localStorage.getItem('auth_token');

  // Initialize the socket connection with WebSocket transport and auth token
  socket.value = io('http://localhost:5000/chat', {
    transports: ['websocket'],  // Force WebSocket transport
    auth: {
      token: token  // Send the token with the auth object
    }
  });

  socket.value.on('connect', () => {
    console.log('Connected to chat');

    // Set up a keep-alive ping to be sent every 25 seconds
    const pingInterval = setInterval(() => {
      console.log('Sending ping to keep the connection alive');
      socket.value.emit('ping');  // Emit the ping message to the server
    }, 25000);  // Ping every 25 seconds

    // Clear the interval when the socket disconnects
    socket.value.on('disconnect', () => {
      console.log('Disconnected from chat');
      clearInterval(pingInterval);  // Stop the ping when disconnected
    });
  });

  socket.value.on('new_message', (message) => {
    messages.value.push(message);
  });

  socket.value.on('disconnect', () => {
    console.log('Disconnected from chat');
  });
});

onUnmounted(() => {
  if (socket.value) {
    socket.value.disconnect();
  }
});

const sendMessage = () => {
  if (newMessage.value.trim() !== '') {
    socket.value.emit('new_message', { 
      message: newMessage.value, 
      room: 'admin_chat'  // Replace with your actual room name or logic
    });
    newMessage.value = '';
  }
};

const formatTimestamp = (timestamp) => {
  const options = { hour: 'numeric', minute: 'numeric', second: 'numeric' };
  return new Date(timestamp).toLocaleTimeString(undefined, options);
};
</script>

<style scoped>
.admin-chat {
  padding: 20px;
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 400px;
  border: 1px solid #ccc;
}

.chat-messages {
  flex-grow: 1;
  overflow-y: auto;
  padding: 10px;
}

.message {
  margin-bottom: 10px;
}

.sender {
  font-weight: bold;
}

.timestamp {
  font-size: smaller;
  color: gray;
  margin-left: 10px;
}

.chat-input {
  display: flex;
  padding: 10px;
}

.chat-input input {
  flex-grow: 1;
  margin-right: 10px;
  padding: 5px;
  border: 1px solid #ccc;
}
</style>

<template>
  <div class="user-dashboard">
    <h2>User Dashboard</h2>
    <div class="subjects">
      <h3>Subjects</h3>
      <ul>
        <li v-for="subject in subjects" :key="subject.id">
          <RouterLink :to="`/user/subjects/${subject.id}/chapters`">
            {{ subject.name }}
          </RouterLink>
        </li>
      </ul>
    </div>
    <p v-if="userRole">Your Role: {{ userRole }}</p>

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
        <button :disabled="newMessage.trim() === ''" @click="sendMessage">Send</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { io } from 'socket.io-client';

const router = useRouter();
const subjects = ref([]);
const userRole = ref(null);
const socket = ref(null);
const messages = ref([]);
const newMessage = ref('');
const userId = ref(null);

const isLoggedIn = computed(() => {
  return !!localStorage.getItem('auth_token');
});

onMounted(async () => {
  if (isLoggedIn.value) {
    fetchSubjects();
    userRole.value = localStorage.getItem('role');
    userId.value = await getCurrentUserId();  // Cache the userId
    connectToChat();
  } else {
    router.push('/login');
  }
});

const connectToChat = () => {
  socket.value = io('http://localhost:5000/chat', {
    transports: ['websocket'],  // Force WebSocket transport
    auth: {
      token: localStorage.getItem('auth_token')
    }
  });

  socket.value.on('connect', async () => {
    console.log('Connected to chat');

    // Get the userId using the async getCurrentUserId function
    const userId = await getCurrentUserId();

    socket.value.emit('join', { room: `user_${userId}_admin` });

    // Set up a keep-alive ping to be sent every 25 seconds
    const pingInterval = setInterval(() => {
      console.log('Sending ping to keep the connection alive');
      socket.value.emit('ping');  // Emit the ping message to the server
    }, 25000);  // Ping every 25 seconds

    // Clear the interval when the socket disconnects to prevent memory leaks
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
};

onUnmounted(async () => {
  if (socket.value) {
    if (userId.value) {
      socket.value.emit('leave', { room: `user_${userId.value}_admin` });
    }
    socket.value.disconnect();
  }
});

const sendMessage = async () => {
  if (newMessage.value.trim() !== '') {
    if (userId.value) {
      socket.value.emit('new_message', {
        message: newMessage.value,
        room: `user_${userId.value}_admin`
      });
      newMessage.value = '';
    }
  }
};

const formatTimestamp = (timestamp) => {
  const options = { hour: 'numeric', minute: 'numeric', second: 'numeric' };
  return new Date(timestamp).toLocaleTimeString(undefined, options);
};

const getCurrentUserId = async () => {
  try {
    const token = localStorage.getItem('auth_token');
    const response = await fetch('http://127.0.0.1:5000/api/user/current_user_id', {
      headers: {
        'Authentication-Token': token,
      },
    });
    if (!response.ok) {
      console.error('Error fetching user ID:', response.status);
      return null;
    }
    const data = await response.json();
    return data.user_id;
  } catch (error) {
    console.error('Error fetching user ID:', error);
    return null;
  }
};

const fetchSubjects = async () => {
  try {
    const token = localStorage.getItem('auth_token');
    const response = await fetch('http://127.0.0.1:5000/api/user/subjects', {
      headers: {
        'Authentication-Token': token,
      },
    });
    if (!response.ok) {
      console.error('Error fetching subjects:', response.status);
      return;
    }
    subjects.value = await response.json();
  } catch (error) {
    console.error('Error fetching subjects:', error);
  }
};
</script>

<style scoped>
.user-dashboard {
  padding: 20px;
}

.subjects {
  margin-top: 20px;
}

.subjects ul {
  list-style: none;
  padding: 0;
}

.subjects li {
  margin-bottom: 10px;
}

.subjects a {
  text-decoration: none;
  color: #007bff; 
}

.subjects a:hover {
  text-decoration: underline;
}
.user-dashboard {
  padding: 20px;
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 300px; 
  border: 1px solid #ccc;
  margin-top: 20px; 
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

.content {
  /* Add styles for the message content */
  margin-left: 10px;  /* Add some space between the sender name and the message */
  word-break: break-word; /* Allow long words to break and wrap */
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
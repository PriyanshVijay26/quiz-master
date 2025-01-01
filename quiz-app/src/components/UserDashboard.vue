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
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const subjects = ref([]);
const userRole = ref(null); 

// Check if the user is logged in
const isLoggedIn = computed(() => {
  return !!localStorage.getItem('auth_token'); 
});

onMounted(async () => {
  if (isLoggedIn.value) {
    fetchSubjects();
    userRole.value = localStorage.getItem('role'); 
  } else {
    router.push('/login'); 
  }
});

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
      // Handle the error, e.g., display an error message or redirect to login
      return; 
    }
    subjects.value = await response.json();
  } catch (error) {
    console.error('Error fetching subjects:', error);
    // Handle the error, e.g., display an error message
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
</style>
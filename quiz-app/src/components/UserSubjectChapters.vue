<template>
  <div class="user-subject-chapters">
    <h2>{{ subject?.name ?? '' }} - Chapters</h2>
    <ul>
      <li v-for="chapter in chapters" :key="chapter.id">
        <RouterLink :to="`/user/subjects/${subjectId}/chapters/${chapter.id}/quizzes`">
          {{ chapter.name }}
        </RouterLink>
      </li>
    </ul>
    <p v-if="userRole">Your Role: {{ userRole }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const subjectId = parseInt(route.params.subjectId, 10);
const subject = ref(null);
const chapters = ref([]);
const userRole = ref(null); // Add ref to store the role

const isLoggedIn = computed(() => {
  return !!localStorage.getItem('auth_token');
});

onMounted(async () => {
  if (isLoggedIn.value) {
    await fetchSubject();
    fetchChapters();
    userRole.value = localStorage.getItem('role'); // Fetch the role from localStorage
  } else {
    // Redirect to login if not logged in (you'll need to adjust the path)
    window.location.href = '/login';
  }
});

const fetchSubject = async () => {
  try {
    const token = localStorage.getItem('auth_token');
    const response = await fetch(`http://127.0.0.1:5000/api/user/subjects/${subjectId}`, {  // Updated API endpoint
      headers: {
        'Authentication-Token': token,
      },
    });
    if (!response.ok) {
      console.error('Error fetching subject:', response.status);
      return;
    }
    subject.value = await response.json();
    console.log('Subject:', subject.value);
  } catch (error) {
    console.error('Error fetching subject:', error);
  }
};

const fetchChapters = async () => {
  try {
    const token = localStorage.getItem('auth_token');
    const response = await fetch(`http://127.0.0.1:5000/api/user/subjects/${subjectId}/chapters`, {
      headers: {
        'Authentication-Token': token,
      },
    });
    if (!response.ok) {
      console.error('Error fetching chapters:', response.status);
      return;
    }
    chapters.value = await response.json();
    console.log('Chapters:', chapters.value);
  } catch (error) {
    console.error('Error fetching chapters:', error);
  }
};
</script>

<style scoped>
.user-subject-chapters {
  padding: 20px;
}

.user-subject-chapters ul {
  list-style: none;
  padding: 0;
}

.user-subject-chapters li {
  margin-bottom: 10px;
}
</style>
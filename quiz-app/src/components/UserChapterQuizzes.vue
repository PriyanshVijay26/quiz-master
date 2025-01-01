<template>
  <div class="user-chapter-quizzes">
    <h2>{{ subject?.name ?? '' }} - {{ chapter?.name ?? '' }} - Quizzes</h2>
    <ul>
      <li v-for="quiz in quizzes" :key="quiz.id">
        {{ quiz.name }} ({{ quiz.date_of_quiz }}) 
        <button @click="startQuiz(quiz.id)" class="btn btn-primary">
          Start Test
        </button>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();
const subjectId = parseInt(route.params.subjectId, 10);
const chapterId = parseInt(route.params.chapterId, 10);
const subject = ref(null); 
const chapter = ref(null); 
const quizzes = ref([]);

const isLoggedIn = computed(() => {
  return !!localStorage.getItem('auth_token');
});

onMounted(async () => {
  if (isLoggedIn.value) {
    await fetchSubject(); 
    await fetchChapter(); 
    fetchQuizzes();
  } else {
    window.location.href = '/login'; 
  }
});

const fetchSubject = async () => {
  try {
    const token = localStorage.getItem('auth_token');
    const response = await fetch(`http://127.0.0.1:5000/api/user/subjects/${subjectId}`, {
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

const fetchChapter = async () => {
  try {
    const token = localStorage.getItem('auth_token');
    const response = await fetch(`http://127.0.0.1:5000/api/user/subjects/${subjectId}/chapters/${chapterId}`, {
      headers: {
        'Authentication-Token': token,
      },
    });
    if (!response.ok) {
      console.error('Error fetching chapter:', response.status);
      return;
    }
    chapter.value = await response.json();
    console.log('Chapter:', chapter.value);
  } catch (error) {
    console.error('Error fetching chapter:', error);
  }
};


const fetchQuizzes = async () => {
  try {
    const token = localStorage.getItem('auth_token');
    const response = await fetch(`http://127.0.0.1:5000/api/user/subjects/${subjectId}/chapters/${chapterId}/quizzes`, {
      headers: {
        'Authentication-Token': token,
      },
    });
    if (!response.ok) {
      console.error('Error fetching quizzes:', response.status);
      return;
    }
    quizzes.value = await response.json();
    console.log('Quizzes:', quizzes.value);
  } catch (error) {
    console.error('Error fetching quizzes:', error);
  }
};

const startQuiz = (quizId) => {
  router.push(`/user/subjects/${subjectId}/chapters/${chapterId}/quizzes/${quizId}`);
};
</script>
  <style scoped>
  .user-chapter-quizzes {
    padding: 20px;
  }
  
  .user-chapter-quizzes ul {
    list-style: none;
    padding: 0;
  }
  
  .user-chapter-quizzes li {
    margin-bottom: 10px;
  }
  
  .btn-primary {
    background-color: #007bff;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    margin-left: 10px; /* Add some space between the quiz info and the button */
  }
  </style>
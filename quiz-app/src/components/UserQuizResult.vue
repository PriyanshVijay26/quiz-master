<template>
  <div class="user-quiz-result" v-if="result">
    <h2>Quiz Result</h2>
    <p><strong>Quiz:</strong> {{ result.quiz_name }}</p>
    <p><strong>Date and Time of Attempt:</strong> {{ formatDateTime(result.time_stamp_of_attempt) }}</p>
    <p><strong>Score:</strong> {{ result.total_scored }} / {{ result.total_marks }}</p>
    <p><strong>Tab Changes:</strong> {{ result.tab_changes }}</p>
    <p><strong>Time Taken:</strong> {{ formatTime(result.time_taken) }}</p>
    <div v-if="result.recording_url">
      <h3>Recording</h3>
      <p v-for="(url, type) in recordingUrls" :key="type"> 
        <a :href="url" target="_blank">Download {{ type }}</a> 
  
      </p>
      
    </div>
  </div>
  <div v-else>Loading result...</div>
</template>
  
  <script setup>
  import { ref, onMounted, computed } from "vue";
  import { useRoute } from "vue-router";
  
  const route = useRoute();
  const subjectId = parseInt(route.params.subjectId, 10);
  const chapterId = parseInt(route.params.chapterId, 10);
  const quizId = parseInt(route.params.quizId, 10);
  const result = ref(null);
  
  const isLoggedIn = computed(() => {
    return !!localStorage.getItem('auth_token');
  });
  
  onMounted(async () => {
    if (isLoggedIn.value) {
      fetchResult();
    } else {
      window.location.href = '/login'; 
    }
  });
  
  const fetchResult = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`http://127.0.0.1:5000/api/user/subjects/${subjectId}/chapters/${chapterId}/quizzes/${quizId}/result`, {
        headers: {
          'Authentication-Token': token,
        },
      });
      if (!response.ok) {
        console.error('Error fetching result:', response.status);
        return;
      }
      result.value = await response.json();
      console.log('Result:', result.value);
    } catch (error) {
      console.error('Error fetching result:', error);
    }
  };
  
  // Helper function to format date and time
  const formatDateTime = (dateTimeString) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric', hour: 'numeric', minute: 'numeric', second: 'numeric' };
    return new Date(dateTimeString).toLocaleDateString(undefined, options);
  };
  
  // Helper function to format time in minutes and seconds
  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes} minutes ${remainingSeconds} seconds`;
  };
  
  // Helper function to extract recording URLs
  
  const recordingUrls = computed(() => {
  if (result.value.recording_url) {
    const urls = {};
    // Split by comma only, then extract type and link
    result.value.recording_url.split(',').forEach(url => {  
      const parts = url.split(':');
      const type = parts[0]; 
      const link = parts.slice(1).join(':'); // Join remaining parts in case of multiple colons
      urls[type] = link;
    });
    return urls;
  }
  return {};
});
  </script>
  
  <style scoped>
  .user-quiz-result {
    padding: 20px;
  }
  </style>
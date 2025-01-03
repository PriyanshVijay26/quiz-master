<template>
    <div class="admin-user-scores">
      <h2>User Scores</h2>
      <table>
        <thead>
          <tr>
            <th>Quiz</th>
            <th>User</th>
            <th>Date and Time</th>
            <th>Score</th>
            <th>Total Marks</th>
            <th>Tab Changes</th>
            <th>Time Taken</th>
            <th>Recording</th>
            <th>Actions</th> 
          </tr>
        </thead>
        <tbody>
          <tr v-for="score in scores" :key="score.id">
            <td>{{ score.quiz_name }}</td>
            <td>{{ score.user_email }}</td>
            <td>{{ formatDateTime(score.time_stamp_of_attempt) }}</td> 
            <td>{{ score.total_scored }}</td>
            <td>{{ score.total_marks }}</td>
            <td>{{ score.tab_changes }}</td>
            <td>{{ formatTime(score.time_took_to_attempt_test) }}</td> 
            <td>
                <div v-if="score.recording_url">
                <p v-for="(url, type) in getRecordingUrls(score.recording_url)" :key="type">
                    <a :href="url" target="_blank">Download {{ type }}</a> 
                </p>
                </div>
            </td>
            <td>
              <button @click="toggleFlag(score)"> 
                {{ score.flagged ? 'Unflag' : 'Flag' }} 
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, computed } from "vue";
  
  const scores = ref([]);
  
  const isAdmin = computed(() => {
    const role = localStorage.getItem('role');
    return role === 'admin';
  });
  
  onMounted(async () => {
    if (isAdmin.value) {
      fetchScores();
    } else {
      // Redirect if not admin
      window.location.href = '/admin/dashboard'; 
    }
  });
  
  const fetchScores = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch('http://127.0.0.1:5000/api/admin/scores', {
        headers: {
          'Authentication-Token': token,
        },
      });
      if (!response.ok) {
        console.error('Error fetching scores:', response.status);
        return;
      }
      scores.value = await response.json();
      console.log('Scores:', scores.value);
    } catch (error) {
      console.error('Error fetching scores:', error);
    }
  };
  
  const formatDateTime = (dateTimeString) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric', hour: 'numeric', minute: 'numeric', second: 'numeric' };
    return new Date(dateTimeString).toLocaleDateString(undefined, options);
  };
  
  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes} minutes ${remainingSeconds} seconds`;
  };
  
  const getRecordingUrls = (recordingUrl) => {
  if (recordingUrl) {
    const urls = {};
    recordingUrl.split(',').forEach(url => {
      const parts = url.split(':'); 
      const type = parts[0];
      const link = parts.slice(1).join(':'); // Join all parts after the first colon
      urls[type] = link;
    });
    return urls;
  }
  return {};
};
  
  const toggleFlag = async (score) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`http://127.0.0.1:5000/api/admin/scores/${score.id}/flag`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authentication-Token': token,
        },
        body: JSON.stringify({ flag: !score.flagged }), 
      });
  
      if (!response.ok) {
        console.error('Error toggling flag:', response.status);
        // Handle error, e.g., display an error message
      } else {
        score.flagged = !score.flagged; // Update the flag status in the UI
      }
    } catch (error) {
      console.error('Error toggling flag:', error);
    }
  };
  </script>
  
  <style scoped>
  .admin-user-scores {
    padding: 20px;
  }
  
  table {
    width: 100%;
    border-collapse: collapse;
  }
  
  th, td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
  }
  </style>
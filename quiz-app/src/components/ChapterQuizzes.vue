<template>
  <div class="chapter-quizzes">
    <h2>{{ subject?.name ?? '' }} - {{ chapter?.name ?? '' }} - Quizzes</h2> 
    <ul>
      <li v-for="quiz in quizzes" :key="quiz.id" class="quiz-item">
        <RouterLink :to="`/admin/subjects/${subjectId}/chapters/${chapterId}/quizzes/${quiz.id}/questions`">
          {{ quiz.time_duration }} ({{ quiz.date_of_quiz }}) - {{ quiz.remarks }} 
        </RouterLink>
        <button @click="showUpdateQuizModal(quiz)">Update</button>
        <button @click="deleteQuiz(quiz.id)">Delete</button>
      </li>
    </ul>
    <button @click="addQuiz">Add Quiz</button>

        <div v-if="showQuizModalFlag" class="modal">
      <div class="modal-content">
        <span class="close" @click="closeQuizModal">&times;</span>
        <h3>{{ modalMode === 'Add' ? 'Add Quiz' : 'Update Quiz' }}</h3>
        <form @submit.prevent="saveQuiz">
          <div class="form-group">
            <label for="quizDate">Date:</label>
            <input type="date" id="quizDate" v-model="currentQuiz.date_of_quiz" required>
          </div>
          <div class="form-group">
            <label for="quizTimeDuration">Time Duration (HH:MM):</label> 
            <input type="text" id="quizTimeDuration" v-model="currentQuiz.time_duration" required>
          </div>
          <div class="form-group">
            <label for="quizRemarks">Remarks:</label>
            <textarea id="quizRemarks" v-model="currentQuiz.remarks"></textarea>
          </div>
          <button type="submit">{{ modalMode === 'Add' ? 'Add' : 'Update' }}</button>
        </form>
      </div>
    </div>
  </div>
</template>


<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const subjectId = parseInt(route.params.subjectId, 10);
const chapterId = parseInt(route.params.chapterId, 10);
const subject = ref(null);
const chapter = ref(null);
const quizzes = ref([]);
const showQuizModalFlag = ref(false);
const modalMode = ref('Add'); 
const currentQuiz = ref({ 
  date_of_quiz: null, 
  time_duration: '', 
  remarks: '' 
});


const isAdmin = computed(() => {
  const role = localStorage.getItem('role');
  return role === 'admin';
});

onMounted(async () => {
  if (isAdmin.value) {
    await fetchSubject(); 
    await fetchChapter(); 
    fetchQuizzes();
  }
});
const fetchSubject = async () => {
  try {
    const token = localStorage.getItem('auth_token');
    const response = await fetch(`http://127.0.0.1:5000/api/subjects/${subjectId}`, {
      headers: {
        'Authentication-Token': token,
      },
    });
    if (!response.ok) {
      console.error('Error fetching subject:', response.status);
      return; 
    }
    subject.value = await response.json(); 
    console.log('Subject:', subject.value);  // Log the subject data
  } catch (error) {
    console.error('Error fetching subject:', error);
  }
};

const fetchChapter = async () => {
  try {
    const token = localStorage.getItem('auth_token');
    const response = await fetch(`http://127.0.0.1:5000/api/subjects/${subjectId}/chapters/${chapterId}`, { 
      headers: {
        'Authentication-Token': token,
      },
    });
    if (!response.ok) {
      console.error('Error fetching chapter:', response.status);
      return;
    }
    chapter.value = await response.json(); 
    console.log('Chapter:', chapter.value);  // Log the chapter data
  } catch (error) {
    console.error('Error fetching chapter:', error);
  }
};



const fetchQuizzes = async () => {
  try {
    const token = localStorage.getItem('auth_token');
    const response = await fetch(`http://127.0.0.1:5000/api/subjects/${subjectId}/chapters/${chapterId}/quizzes`, { 
      headers: {
        'Authentication-Token': token,
      },
    });
    if (!response.ok) {
      console.error('Error fetching quizzes:', response.status);
      // Handle the error, e.g., display an error message to the user
      return; 
    }
    quizzes.value = await response.json();
  } catch (error) {
    console.error('Error fetching quizzes:', error);
    // Handle the error, e.g., display an error message to the user
  }
};

const addQuiz = () => {
  modalMode.value = 'Add';
  currentQuiz.value = { 
    name: '', 
    date_of_quiz: null, 
    time_duration: '',  // Set to empty string for new quiz
    remarks: '' 
  };
  showQuizModalFlag.value = true;
};

const showUpdateQuizModal = (quiz) => {
  modalMode.value = 'Update';

  // Format the date before assigning it to currentQuiz
  const formattedDate = new Date(quiz.date_of_quiz).toISOString().split('T')[0]; 

  currentQuiz.value = { ...quiz, date_of_quiz: formattedDate }; 
  showQuizModalFlag.value = true;
};

const closeQuizModal = () => {
  showQuizModalFlag.value = false;
};

const saveQuiz = () => {
  if (modalMode.value === 'Add') {
    createQuiz();
  } else {
    updateQuiz();
  }
};

const createQuiz = () => {
  const token = localStorage.getItem("auth_token");
  fetch(`http://127.0.0.1:5000/api/subjects/${subjectId}/chapters/${chapterId}/quizzes`, {
    method: "POST",
    headers: {
      'Authentication-Token': token,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      date_of_quiz: currentQuiz.value.date_of_quiz,
      time_duration: currentQuiz.value.time_duration,
      remarks: currentQuiz.value.remarks,
    }),
  })
    .then((response) => {
      if (!response.ok) {
        console.error("Error creating quiz:", response.status);
        throw new Error("Failed to create quiz");
      }
      return response.json();
    })
    .then(() => {
      fetchQuizzes(); 
      closeQuizModal(); 
    })
    .catch((error) => {
      console.error("Error creating quiz:", error);
    });
};

const updateQuiz = () => {
  const quizId = currentQuiz.value.id;
  const token = localStorage.getItem("auth_token");
  fetch(`http://127.0.0.1:5000/api/subjects/${subjectId}/chapters/${chapterId}/quizzes/${quizId}`, { 
    method: "PUT",
    headers: {
      'Authentication-Token': token,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(currentQuiz.value), 
  })
    .then((response) => {
      if (!response.ok) {
        console.error("Error updating quiz:", response.status);
        throw new Error("Failed to update quiz");
      }
      return response.json();
    })
    .then(() => {
      fetchQuizzes(); 
      closeQuizModal(); 
    })
    .catch((error) => {
      console.error("Error updating quiz:", error);
    });
};


const deleteQuiz = (quizId) => {
  if (confirm("Are you sure you want to delete this quiz?")) {
    const token = localStorage.getItem("auth_token");
    fetch(`http://127.0.0.1:5000/api/subjects/${subjectId}/chapters/${chapterId}/quizzes/${quizId}`, { 
      method: "DELETE",
      headers: {
        'Authentication-Token': token,
      },
    })
      .then((response) => {
        if (!response.ok) {
          console.error("Error deleting quiz:", response.status);
          throw new Error("Failed to delete quiz");
        }
        return response.json();
      })
      .then(() => {
        fetchQuizzes(); 
      })
      .catch((error) => {
        console.error("Error deleting quiz:", error);
      });
  }
};
</script>

<style scoped>
.chapter-quizzes {
  padding: 20px;
}

.chapter-quizzes ul {
  list-style: none;
  padding: 0;
}

.chapter-quizzes li {
  margin-bottom: 10px;
}

.quiz-item {
  display: flex;
  align-items: center; 
}

.quiz-item button {
  margin-left: 10px; 
}

.modal {
  position: fixed;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-content {
  background-color: #fefefe;
  margin: 15% auto;
  padding: 20px;
  border: 1px solid #888;
  width: 30%;
}

.close {
  color: #aaa;
  float: right;
  font-size: 28px;
  font-weight: bold;
}

.close:hover,
.close:focus {
  color: black;
  text-decoration: none;
  cursor: pointer;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
}
</style>
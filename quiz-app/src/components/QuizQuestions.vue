<template>
  <div class="quiz-questions">
    <h2>{{ subject?.name ?? '' }} - {{ chapter?.name ?? '' }} - {{ quiz?.name ?? '' }} - Questions</h2>
    <ul>
      <li v-for="(question, index) in questions" :key="question.id">
        <p><strong>{{ index + 1 }}. {{ question.question_statement }}</strong></p>
        <img v-if="question.photo_url" :src="baseUrl + question.photo_url" alt="Question Image" /> 
        <ul>
          <li>{{ question.option1 }}</li>
          <li>{{ question.option2 }}</li>
          <li>{{ question.option3 }}</li>
          <li>{{ question.option4 }}</li>
        </ul>
        <p><strong>Correct Answer:</strong> {{ question.correct_option }}</p> 
        <button @click="showUpdateQuestionModal(question)">Update</button>
        <button @click="deleteQuestion(question.id)">Delete</button>
      </li>
    </ul>
    <button @click="addQuestion">Add Question</button>

    <div v-if="showQuestionModalFlag" class="modal">
      <div class="modal-content">
        <span class="close" @click="closeQuestionModal">&times;</span>
        <h3>{{ modalMode === 'Add' ? 'Add Question' : 'Update Question' }}</h3>
        <form @submit.prevent="saveQuestion" enctype="multipart/form-data"> 
          <div class="form-group">
            <label for="questionText">Question Text:</label>
            <input type="text" id="questionText" v-model="currentQuestion.question_statement" required>
          </div>
          <div class="form-group">
            <label for="option1">Option 1:</label>
            <input type="text" id="option1" v-model="currentQuestion.option1" required>
          </div>
          <div class="form-group">
            <label for="option2">Option 2:</label>
            <input type="text" id="option2" v-model="currentQuestion.option2" required>
          </div>
          <div class="form-group">
            <label for="option3">Option 3:</label>
            <input type="text" id="option3" v-model="currentQuestion.option3" required>
          </div>
          <div class="form-group">
            <label for="option4">Option 4:</label>
            <input type="text" id="option4" v-model="currentQuestion.option4" required>
          </div>
          <div class="form-group">
            <label for="correctOption">Correct Option (1-4):</label>
            <input type="number" id="correctOption" v-model="currentQuestion.correct_option" min="1" max="4" required>
          </div>
          <div class="form-group">
            <label for="questionImage">Image:</label> 
            <input type="file" id="questionImage" @change="handleImageUpload" accept="image/*"> 
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


const baseUrl = 'http://127.0.0.1:5000';
const route = useRoute();
const subjectId = parseInt(route.params.subjectId, 10);
const chapterId = parseInt(route.params.chapterId, 10);
const quizId = parseInt(route.params.quizId, 10);
const subject = ref(null);
const chapter = ref(null);
const quiz = ref(null);
const questions = ref([]);
const showQuestionModalFlag = ref(false);
const modalMode = ref('Add');
const currentQuestion = ref({
  question_statement: '',
  option1: '',
  option2: '',
  option3: '',
  option4: '',
  correct_option: null,
  photo_url: null,  // Add photo_url to currentQuestion
});

const isAdmin = computed(() => {
  const role = localStorage.getItem('role');
  return role === 'admin';
});

onMounted(async () => {
  if (isAdmin.value) {
    await fetchSubject();
    await fetchChapter();
    await fetchQuiz(); 
    fetchQuestions();
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
    console.log('Subject:', subject.value);
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
    console.log('Chapter:', chapter.value);
  } catch (error) {
    console.error('Error fetching chapter:', error);
  }
};

const fetchQuiz = async () => {
  try {
    const token = localStorage.getItem('auth_token');
    const response = await fetch(`http://127.0.0.1:5000/api/subjects/${subjectId}/chapters/${chapterId}/quizzes/${quizId}`, { 
      headers: {
        'Authentication-Token': token,
      },
    });
    if (!response.ok) {
      console.error('Error fetching quiz:', response.status);
      return; 
    }
    quiz.value = await response.json(); 
    console.log('Quiz:', quiz.value); 
  } catch (error) {
    console.error('Error fetching quiz:', error);
  }
};

const fetchQuestions = async () => {
  try {
    const token = localStorage.getItem('auth_token');
    const response = await fetch(`http://127.0.0.1:5000/api/subjects/${subjectId}/chapters/${chapterId}/quizzes/${quizId}/questions`, { 
      headers: {
        'Authentication-Token': token,
      },
    });
    if (!response.ok) {
      console.error('Error fetching questions:', response.status);
      return; 
    }
    questions.value = await response.json();
    console.log('Questions:', questions.value);
    
  } catch (error) {
    console.error('Error fetching questions:', error);
  }
};

const addQuestion = () => {
  modalMode.value = 'Add';
  currentQuestion.value = {
    question_statement: '',
    option1: '',
    option2: '',
    option3: '',
    option4: '',
    correct_option: null,
    photo_url: null, // Reset photo_url when adding a new question
  };
  showQuestionModalFlag.value = true;
};

const showUpdateQuestionModal = (question) => {
  modalMode.value = 'Update';
  currentQuestion.value = { ...question };
  showQuestionModalFlag.value = true;
};

const closeQuestionModal = () => {
  showQuestionModalFlag.value = false;
  currentQuestion.value.photo_url = null; // Reset photo_url when closing the modal
};

const saveQuestion = () => {
  if (modalMode.value === 'Add') {
    createQuestion();
  } else {
    updateQuestion();
  }
};

const handleImageUpload = (event) => {
  const file = event.target.files[0];
  if (file) {
    currentQuestion.value.photo_url = URL.createObjectURL(file); 
  } else {
    currentQuestion.value.photo_url = null; 
  }
};

const createQuestion = async () => {
  try {
    const token = localStorage.getItem("auth_token");

    const formData = new FormData(); 
    formData.append('question_statement', currentQuestion.value.question_statement);
    formData.append('option1', currentQuestion.value.option1);
    formData.append('option2', currentQuestion.value.option2);
    formData.append('option3', currentQuestion.value.option3);
    formData.append('option4', currentQuestion.value.option4);
    formData.append('correct_option', currentQuestion.value.correct_option);

    if (currentQuestion.value.photo_url) {
      const fileInput = document.getElementById('questionImage'); 
      const file = fileInput.files[0];
      if (file) {
        formData.append('file', file);
      }
    }

    const response = await fetch(`http://127.0.0.1:5000/api/subjects/${subjectId}/chapters/${chapterId}/quizzes/${quizId}/questions`, {
      method: "POST",
      headers: {
        'Authentication-Token': token,
      },
      body: formData, 
    });

    if (!response.ok) {
      const errorData = await response.json(); 
      console.error("Error creating question:", response.status, errorData); 
      throw new Error("Failed to create question");
    }

    fetchQuestions();
    closeQuestionModal();
  } catch (error) {
    console.error("Error creating question:", error);
  }
};

const updateQuestion = async () => {
  try {
    const questionId = currentQuestion.value.id;
    const token = localStorage.getItem("auth_token");

    const formData = new FormData();
    formData.append('question_statement', currentQuestion.value.question_statement);
    formData.append('option1', currentQuestion.value.option1);
    formData.append('option2', currentQuestion.value.option2);
    formData.append('option3', currentQuestion.value.option3);
    formData.append('option4', currentQuestion.value.option4);
    formData.append('correct_option', currentQuestion.value.correct_option);

    if (currentQuestion.value.photo_url) {
      const fileInput = document.getElementById('questionImage');
      const file = fileInput.files[0];
      if (file) {
        formData.append('file', file);
      }
    }

    const response = await fetch(`http://127.0.0.1:5000/api/subjects/${subjectId}/chapters/${chapterId}/quizzes/${quizId}/questions/${questionId}`, {
      method: "PUT",
      headers: {
        'Authentication-Token': token,
      },
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error("Error updating question:", response.status, errorData);
      throw new Error("Failed to update question");
    }

    fetchQuestions();
    closeQuestionModal();
  } catch (error) {
    console.error("Error updating question:", error);
  }
};

const deleteQuestion = (questionId) => {
  if (confirm("Are you sure you want to delete this question?")) {
    const token = localStorage.getItem("auth_token");
    fetch(`http://127.0.0.1:5000/api/subjects/${subjectId}/chapters/${chapterId}/quizzes/${quizId}/questions/${questionId}`, { 
      method: "DELETE",
      headers: {
        'Authentication-Token': token,
      },
    })
      .then((response) => {
        if (!response.ok) {
          console.error("Error deleting question:", response.status);
          throw new Error("Failed to delete question");
        }
        return response.json();
      })
      .then(() => {
        fetchQuestions(); 
      })
      .catch((error) => {
        console.error("Error deleting question:", error);
      });
  }
};
</script>

<style scoped>
.quiz-questions {
  padding: 20px;
}

.quiz-questions ul {
  list-style: none;
  padding: 0;
}

.quiz-questions li {
  margin-bottom: 20px;
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
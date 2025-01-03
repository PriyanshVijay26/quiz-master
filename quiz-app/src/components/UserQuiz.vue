<template>
  <div class="user-quiz">
    <div class="quiz-header">
      <h2>{{ quiz?.remarks ?? '' }}</h2> 
      <div class="timer">Time Left: {{ formattedTimeLeft }}</div>
      <div>Tab Changes: {{ tabChanges }}</div> 
    </div>

    <div class="video-container" v-if="screenStream && cameraStream">
      <video :srcObject="screenStream" autoplay muted></video>
      <video :srcObject="cameraStream" autoplay muted class="flipped-video"></video> 
    </div>

    <div v-if="questions.length > 0">
      <div
        v-for="(question, index) in questions"
        :key="question.id"
        class="question"
        :class="{
          answered: selectedAnswers[question.id],
          'marked-for-review': markedForReview[question.id],
        }"
      >
        <p class="question-text">
          {{ index + 1 }}. {{ question.question_statement }}
        </p>
        <img v-if="question.photo_url" :src="baseUrl + question.photo_url" alt="Question Image" /> 
        <div class="options">
          <label
            v-for="(option, optionIndex) in ['option1', 'option2', 'option3', 'option4']"
            :key="optionIndex"
            class="option"
            :class="{
              selected: selectedAnswers[question.id] === optionIndex + 1, 
              correct: showAnswers && question.correct_option === optionIndex + 1, 
              incorrect:
                showAnswers &&
                selectedAnswers[question.id] === optionIndex + 1 && 
                question.correct_option !== optionIndex + 1, 
            }"
          >
            <input
              type="radio"
              :name="`question-${question.id}`"
              :value="optionIndex + 1" 
              v-model="selectedAnswers[question.id]"
            />
            {{ question[option] }}
          </label>
        </div>
        <div class="question-actions">
          <button @click="markForReview(question.id)">Mark for Review</button>
          <button @click="clearAnswer(question.id)">Clear Answer</button>
        </div>
      </div>
      <button @click="submitQuiz" class="btn btn-primary">Submit Quiz</button>
    </div>
    <div v-else>Loading questions...</div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

const baseUrl = 'http://127.0.0.1:5000'; 
const route = useRoute();
const router = useRouter();
const subjectId = parseInt(route.params.subjectId, 10);
const chapterId = parseInt(route.params.chapterId, 10);
const quizId = parseInt(route.params.quizId, 10);
const subject = ref(null);
const chapter = ref(null);
const quiz = ref(null);
const questions = ref([]);
const selectedAnswers = ref({});
const markedForReview = ref({});
const timeLeft = ref(0);
const tabChanges = ref(0);
const showAnswers = ref(false);
const mediaRecorder = ref(null);
const recordedChunks = ref([]);
const audioChunks = ref([]);
const screenStream = ref(null);
const cameraStream = ref(null);

let windowFocused = true; 
let lastVisibilityState = document.visibilityState;

const isLoggedIn = computed(() => {
  return !!localStorage.getItem('auth_token');
});

onMounted(async () => {
  if (!isLoggedIn.value) {
    window.location.href = '/login'; 
    return; 
  }

  try {
    await fetchSubject();
    await fetchChapter();
    await fetchQuiz();
    await fetchQuestions();

    const [hours, minutes] = quiz.value.time_duration.split(':');
    timeLeft.value = (parseInt(hours) * 60 + parseInt(minutes)) * 60; 

    const timerInterval = setInterval(() => {
      timeLeft.value--;
      if (timeLeft.value <= 0) {
        clearInterval(timerInterval);
        submitQuiz(); 
      }
    }, 1000);

    screenStream.value = await navigator.mediaDevices.getDisplayMedia({
      video: true,
    });
    cameraStream.value = await navigator.mediaDevices.getUserMedia({
      video: true,
    });
    const audioStream = await navigator.mediaDevices.getUserMedia({
      audio: true,
    });

    const combinedStream = new MediaStream([
      ...screenStream.value.getVideoTracks(),
      ...cameraStream.value.getVideoTracks(),
      ...audioStream.getAudioTracks(),
    ]);

    mediaRecorder.value = new MediaRecorder(combinedStream);

    mediaRecorder.value.ondataavailable = (event) => {
      if (event.data.type.startsWith("video")) {
        recordedChunks.value.push(event.data);
      } else if (event.data.type.startsWith("audio")) {
        audioChunks.value.push(event.data);
      }
    };

    mediaRecorder.value.onstop = async () => {
      const videoBlob = new Blob(recordedChunks.value, { type: "video/webm" });
      const audioBlob = new Blob(audioChunks.value, { type: "audio/webm" });

      try {
        const token = localStorage.getItem('auth_token');
        const formData = new FormData();
        formData.append('video', videoBlob, 'video.webm'); 
        formData.append('audio', audioBlob, 'audio.webm'); 

        const uploadResponse = await fetch(`http://127.0.0.1:5000/api/user/subjects/${subjectId}/chapters/${chapterId}/quizzes/${quizId}/recording`, {
          method: "POST",
          headers: {
            'Authentication-Token': token,
          },
          body: formData,
        });

        if (!uploadResponse.ok) {
          console.error('Error uploading recording:', uploadResponse.status);
        } else {
          console.log('Recording uploaded successfully!');
        }
      } catch (error) {
        console.error("Error uploading recording:", error);
      }
    };

    mediaRecorder.value.start();

    // Ensure event listeners are attached after mediaRecorder starts
    document.addEventListener("visibilitychange", handleVisibilityChange);
    window.addEventListener('blur', handleWindowBlur);
    window.addEventListener('focus', handleWindowFocus); 
  } catch (error) {
    console.error("Error initializing quiz:", error);
  }
});

onUnmounted(() => {
  if (mediaRecorder.value) {
    mediaRecorder.value.stop();
  }
  document.removeEventListener("visibilitychange", handleVisibilityChange);
  window.removeEventListener('blur', handleWindowBlur);
  window.removeEventListener('focus', handleWindowFocus); 
});

const handleVisibilityChange = () => {
  console.log("Visibility changed:", document.visibilityState);

  if (document.visibilityState === 'hidden') {
    tabChanges.value++;
    console.log("Tab changes incremented:", tabChanges.value);
  }
};

const handleWindowBlur = () => {
  windowFocused = false;
};

const handleWindowFocus = () => {
  windowFocused = true;
};



const formattedTimeLeft = computed(() => {
  const minutes = Math.floor(timeLeft.value / 60);
  const seconds = timeLeft.value % 60;
  return `${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
});

const submitQuiz = async () => {
  if (mediaRecorder.value) {
    mediaRecorder.value.stop(); 
  }

  try {
    const token = localStorage.getItem('auth_token');
    const totalQuestions = questions.value.length;
    let correctAnswers = 0;
    const [hours, minutes] = quiz.value.time_duration.split(':'); 
    const totalQuizSeconds = (parseInt(hours) * 60 + parseInt(minutes)) * 60;
    const timeTaken = Math.max(0, totalQuizSeconds - timeLeft.value);


    for (const question of questions.value) {
      if (selectedAnswers.value[question.id] === question.correct_option) {
        correctAnswers++;
      }
    }

    const score = correctAnswers;

    const scoreResponse = await fetch(`http://127.0.0.1:5000/api/user/subjects/${subjectId}/chapters/${chapterId}/quizzes/${quizId}/score`, {
      method: "POST",
      headers: {
        'Content-Type': 'application/json',
        'Authentication-Token': token,
      },
      body: JSON.stringify({
        total_scored: score, 
        total_marks: totalQuestions, 
        remarks: JSON.stringify(selectedAnswers.value), 
        tab_changes: tabChanges.value,
        time_took_to_attempt_test: timeTaken, 
        duration_quiz: totalQuizSeconds,  
      }),
    });

    if (!scoreResponse.ok) {
      console.error('Error storing score:', scoreResponse.status);
    }

    showAnswers.value = true;
    router.push(`/user/subjects/${subjectId}/chapters/${chapterId}/quizzes`);
  } catch (error) {
    console.error("Error submitting quiz:", error);
  }
};

const markForReview = (questionId) => {
  markedForReview.value[questionId] = !markedForReview.value[questionId];
};

const clearAnswer = (questionId) => {
  selectedAnswers.value[questionId] = null;
  markedForReview.value[questionId] = false;
};

watch(selectedAnswers, () => {
  console.log("Selected answers changed:", selectedAnswers.value);
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

const fetchQuiz = async () => {
  try {
    const token = localStorage.getItem('auth_token');
    const response = await fetch(`http://127.0.0.1:5000/api/user/subjects/${subjectId}/chapters/${chapterId}/quizzes/${quizId}`, {
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
    const response = await fetch(`http://127.0.0.1:5000/api/user/subjects/${subjectId}/chapters/${chapterId}/quizzes/${quizId}/questions`, {
      headers: {
        'Authentication-Token': token,
      },
    });
    if (!response.ok) {
      console.error('Error fetching questions:', response.status);
      return;
    }
    questions.value = await response.json();

    questions.value.forEach(question => {
      if (question.photo_url) {
        question.photo_url = '/' + question.photo_url; 
      }
    });

    console.log('Questions:', questions.value);
  } catch (error) {
    console.error('Error fetching questions:', error);
  }
};
</script>
<style scoped>
.user-quiz {
  padding: 20px;
}

.quiz-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.question {
  margin-bottom: 30px;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.question.answered {
  border-left: 4px solid #28a745; /* Green for answered */
}

.question.marked-for-review {
  border-left: 4px solid #6f42c1; /* Purple for marked for review */
}

.question-text {
  font-weight: bold;
  margin-bottom: 10px;
}

.options {
  display: flex;
  flex-direction: column;
}

.option {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-bottom: 5px;
  cursor: pointer;
}

.option:hover {
  background-color: #f5f5f5;
}

.option.selected {
  background-color: #d4edda; /* Green for selected */
  border-color: #c3e6cb;
}

.option.correct {
  background-color: #d4edda; /* Green for correct */
  border-color: #c3e6cb;
}

.option.incorrect {
  background-color: #f8d7da; /* Red for incorrect */
  border-color: #f5c6cb;
}

.question-actions {
  margin-top: 10px;
}
.flipped-video {
  transform: scaleX(-1); /* Flip the video horizontally */
}
.question-actions button {
  margin-right: 5px;
  padding: 5px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #f8f9fa;
  cursor: pointer;
}

.btn-primary {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1em;
}

.video-container {
  display: flex; /* Use flexbox to arrange videos side by side */
  gap: 20px; /* Add some space between the videos */
  margin-bottom: 20px;
}

.video-container video {
  width: 320px;
  height: 240px;
  border: 1px solid #ccc;
}
</style>
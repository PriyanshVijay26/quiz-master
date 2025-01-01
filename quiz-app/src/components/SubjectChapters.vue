<template>
  <div class="subject-chapters">
    <h2 v-if="subject">{{ subject.name }} - Chapters</h2> 
    <ul>
      <li v-for="chapter in chapters" :key="chapter.id" class="chapter-item">
        <RouterLink :to="`/admin/subjects/${subjectId}/chapters/${chapter.id}/quizzes`">
          {{ chapter.name }}
        </RouterLink>
        <button @click="showUpdateChapterModal(chapter)">Update</button>
        <button @click="deleteChapter(chapter.id)">Delete</button>
      </li>
    </ul>
    <button @click="addChapter">Add Chapter</button>

    <div v-if="showChapterModalFlag" class="modal">
      <div class="modal-content">
        <span class="close" @click="closeChapterModal">&times;</span>
        <h3>{{ modalMode === 'Add' ? 'Add Chapter' : 'Update Chapter' }}</h3>
        <form @submit.prevent="saveChapter">
          <div class="form-group">
            <label for="chapterName">Name:</label>
            <input type="text" id="chapterName" v-model="currentChapter.name" required>
          </div>
          <div class="form-group">
            <label for="chapterDescription">Description:</label>
            <textarea id="chapterDescription" v-model="currentChapter.description" required></textarea>
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
const subject = ref(null); 
const chapters = ref([]);
const showChapterModalFlag = ref(false);
const modalMode = ref('Add'); // Can be 'Add' or 'Update'
const currentChapter = ref({ name: '', description: '' }); 

const isAdmin = computed(() => {
  const role = localStorage.getItem('role');
  return role === 'admin';
});

onMounted(async () => {
  if (isAdmin.value) {
    await fetchSubject(); 
    fetchChapters();
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
  } catch (error) {
    console.error('Error fetching subject:', error);
  }
};


const fetchChapters = async () => {
  try {
    const token = localStorage.getItem('auth_token');
    const response = await fetch(`http://127.0.0.1:5000/api/subjects/${subjectId}/chapters`, {
      headers: {
        'Authentication-Token': token,
      },
    });
    if (!response.ok) {
      console.error('Error fetching chapters:', response.status);
      return; 
    }
    chapters.value = await response.json();
  } catch (error) {
    console.error('Error fetching chapters:', error);
  }
};

const addChapter = () => {
  modalMode.value = 'Add';
  currentChapter.value = { name: '', description: '' }; 
  showChapterModalFlag.value = true;
};

const showUpdateChapterModal = (chapter) => {
  modalMode.value = 'Update';
  currentChapter.value = { ...chapter };
  showChapterModalFlag.value = true;
};

const closeChapterModal = () => {
  showChapterModalFlag.value = false;
};

const saveChapter = () => {
  if (modalMode.value === 'Add') {
    createChapter();
  } else {
    updateChapter();
  }
};

const createChapter = () => {
  const token = localStorage.getItem("auth_token");
  fetch(`http://127.0.0.1:5000/api/subjects/${subjectId}/chapters`, { 
    method: "POST",
    headers: {
      'Authentication-Token': token,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      subject_id: subjectId, 
      name: currentChapter.value.name,
      description: currentChapter.value.description,
    }),
  })
    .then((response) => {
      if (!response.ok) {
        console.error("Error creating chapter:", response.status);
        throw new Error("Failed to create chapter");
      }
      return response.json();
    })
    .then(() => {
      fetchChapters(); 
      closeChapterModal(); 
    })
    .catch((error) => {
      console.error("Error creating chapter:", error);
    });
};


const updateChapter = () => {
  const chapterId = currentChapter.value.id;
  const token = localStorage.getItem("auth_token");
  fetch(`http://127.0.0.1:5000/api/subjects/${subjectId}/chapters/${chapterId}`, {
    method: "PUT",
    headers: {
      'Authentication-Token': token,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(currentChapter.value), 
  })
    .then((response) => {
      if (!response.ok) {
        console.error("Error updating chapter:", response.status);
        throw new Error("Failed to update chapter");
      }
      return response.json();
    })
    .then(() => {
      fetchChapters(); 
      closeChapterModal(); 
    })
    .catch((error) => {
      console.error("Error updating chapter:", error);
    });
};

const deleteChapter = (chapterId) => {
  if (confirm("Are you sure you want to delete this chapter?")) {
    const token = localStorage.getItem("auth_token");
    fetch(`http://127.0.0.1:5000/api/subjects/${subjectId}/chapters/${chapterId}`, {
      method: "DELETE",
      headers: {
        'Authentication-Token': token,
      },
    })
      .then((response) => {
        if (!response.ok) {
          console.error("Error deleting chapter:", response.status);
          throw new Error("Failed to delete chapter");
        }
        return response.json();
      })
      .then(() => {
        fetchChapters(); 
      })
      .catch((error) => {
        console.error("Error deleting chapter:", error);
      });
  }
};
</script>

<style scoped>
.subject-chapters {
  padding: 20px;
}

.subject-chapters ul {
  list-style: none;
  padding: 0;
}

.subject-chapters li {
  margin-bottom: 10px;
}

.chapter-item {
  display: flex;
  align-items: center;
}

.chapter-item button {
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
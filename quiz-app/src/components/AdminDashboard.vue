<template>
  <div class="admin-dashboard">
    <h2>Admin Dashboard</h2>
    <button @click="goToScores">View User Scores</button> <div v-if="isAdmin" class="subjects"></div>
    <button @click="goToChat">Chat with Users</button> 
    <div v-if="isAdmin" class="subjects">
      <h3>Subjects</h3>
      <ul>
        <li v-for="subject in subjects" :key="subject.id" class="subject-item"> 
          <RouterLink :to="`/admin/subjects/${subject.id}/chapters`">
            {{ subject.name }}
          </RouterLink>
          <button @click="showUpdateModal(subject)">Update</button>
          <button @click="deleteSubject(subject.id)">Delete</button>
        </li>
      </ul>
      <button @click="addSubject">Add Subject</button>
    </div>
    <div v-else>
      <p>You do not have permission to access this page.</p>
    </div>

    <div v-if="showUpdateModalFlag" class="modal">
      <div class="modal-content">
        <span class="close" @click="closeUpdateModal">&times;</span>
        <h3>Update Subject</h3>
        <form @submit.prevent="updateSubject"> 
          <div class="form-group">
            <label for="updatedName">Name:</label>
            <input type="text" id="updatedName" v-model="updatedSubject.name" required>
          </div>
          <div class="form-group">
            <label for="updatedDescription">Description:</label>
            <textarea id="updatedDescription" v-model="updatedSubject.description" required></textarea>
          </div>
          <button type="submit">Update</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const subjects = ref([]);
const role = localStorage.getItem('role');
const showUpdateModalFlag = ref(false); 
const updatedSubject = ref({ name: '', description: '' });

const isAdmin = computed(() => {
  return role === 'admin';
});


onMounted(async () => {
  if (isAdmin.value) { 
    fetchSubjects();
  }
});

const fetchSubjects = async () => {
  try {
    const token = localStorage.getItem('auth_token');
    const response = await fetch('http://127.0.0.1:5000/api/subjects', {
      headers: {
        'Authentication-Token': token,
      },
    });
    if (!response.ok) {
      // Handle error, maybe redirect to login
      console.error('Error fetching subjects:', response.status); 
      return;
    }
    subjects.value = await response.json();
  } catch (error) {
    console.error('Error fetching subjects:', error);
  }
};
const showUpdateModal = (subject) => {
  updatedSubject.value = { ...subject }; 
  showUpdateModalFlag.value = true;
};

const closeUpdateModal = () => {
  showUpdateModalFlag.value = false;
};const updateSubject = () => {
  const subjectId = updatedSubject.value.id; 
  const token = localStorage.getItem("auth_token");
  fetch(`http://127.0.0.1:5000/api/subjects/${subjectId}`, {
    method: "PUT",
    headers: {
      'Authentication-Token': token,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(updatedSubject.value), 
  })
    .then((response) => {
      if (!response.ok) {
        console.error("Error updating subject:", response.status);
        throw new Error("Failed to update subject");
      }
      return response.json();
    })
    .then(() => {
      fetchSubjects();
      closeUpdateModal(); 
    })
    .catch((error) => {
      console.error("Error updating subject:", error);
    });
};

const deleteSubject = (subjectId) => {
  if (confirm("Are you sure you want to delete this subject?")) { 
    const token = localStorage.getItem("auth_token");
    fetch(`http://127.0.0.1:5000/api/subjects/${subjectId}`, {
      method: "DELETE",
      headers: {
        'Authentication-Token': token,
      },
    })
      .then((response) => {
        if (!response.ok) {
          console.error("Error deleting subject:", response.status);
          throw new Error("Failed to delete subject");
        }
        return response.json();
      })
      .then(() => {
        fetchSubjects(); 
      })
      .catch((error) => {
        console.error("Error deleting subject:", error);
      });
  }
};
const goToScores = () => {
  router.push('/admin/scores'); // Navigate to the user scores page
};
const goToChat = () => {
  router.push('/admin/chat');  // Navigate to the admin chat page
};

const addSubject = () => {
  const newSubjectName = prompt("Enter the name of the new subject:");
  const newSubjectDescription = prompt("Enter the description:");

  if (newSubjectName && newSubjectDescription) {
    const token = localStorage.getItem("auth_token");
    fetch("http://127.0.0.1:5000/api/subjects", {
      method: "POST",
      headers: {
        'Authentication-Token': token,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        name: newSubjectName,
        description: newSubjectDescription,
      }),
    })
      .then((response) => {
        if (!response.ok) {
          // Handle error (e.g., display an error message)
          console.error("Error adding subject:", response.status); 
          throw new Error("Failed to add subject"); 
        }
        return response.json();
      })
      .then(() => {
        // Refresh the subject list after successful addition
        fetchSubjects(); 
      })
      .catch((error) => {
        console.error("Error adding subject:", error);
        // Handle the error (e.g., display an error message to the user)
      });
  }
};
</script> 

<style scoped>
.admin-dashboard {
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

.subjects a { /* Style the links */
  text-decoration: none;
  color: #007bff; /* Blue color */
}

.subjects a:hover {
  text-decoration: underline;
}


.subject-item {
  display: flex;
  align-items: center; 
}

.subject-item button {
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
<template>
  <div class="login-page">
    <div class="container">
      <h2 class="heading">Login</h2>
      <form @submit.prevent="login">
        <div class="form-group">
          <label for="email">Email:</label>
          <input type="email" id="email" v-model="email" required />
        </div>
        <div class="form-group">
          <label for="password">Password:</label>
          <input type="password" id="password" v-model="password" required />
        </div>
        <button type="submit" class="btn btn-primary">Login</button>
        <div v-if="error" class="error-message">{{ error }}</div>
      </form>
      <div class="register-link">
        <p>Not registered yet? <RouterLink to="/register">Register here</RouterLink></p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const email = ref("");
const password = ref("");
const error = ref("");

const login = async () => {
  try {
    const response = await fetch("http://127.0.0.1:5000/api/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: email.value,
        password: password.value,
      }),
    });

    if (!response.ok) {
      const data = await response.json();
      error.value = data.message || "Login failed";
      return;
    }

    const data = await response.json();
    localStorage.setItem('auth_token', data.token);
    // Store the user's roles in localStorage
    localStorage.setItem('role', data.roles[0]); 

    if (data.roles.includes("admin")) {
      router.push("/admin/dashboard");
    } else {
      router.push("/user/dashboard");
    }
  } catch (err) {
    error.value = "An error occurred";
    console.error(err);
  }
};
</script>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f8f9fa;
}

.container {
  background-color: #ffffff;
  padding: 50px; /* Increased padding */
  border-radius: 10px; /* Slightly larger border radius */
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2); /* More pronounced shadow */
  width: 500px; /* Increased width */
}

.heading {
  text-align: center;
  margin-bottom: 20px;
  font-size: 2.5em; /* Increased font size */
}

.form-group {
  margin-bottom: 20px; /* Increased margin */
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-size: 1.2em; /* Increased font size */
}

.form-group input {
  width: 100%;
  padding: 12px; /* Increased padding */
  border: 1px solid #ced4da;
  border-radius: 4px;
  box-sizing: border-box;
  font-size: 1em; /* Increased font size */
}

.btn-primary {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 12px 24px; /* Increased padding */
  border-radius: 4px;
  cursor: pointer;
  font-size: 1.2em; /* Increased font size */
}

.error-message {
  color: #dc3545;
  margin-top: 10px;
  font-size: 1em; /* Increased font size */
}

.register-link {
  text-align: center;
  margin-top: 20px;
}
</style>
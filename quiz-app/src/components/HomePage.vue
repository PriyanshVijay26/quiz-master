<template>
    <div class="home-page">
      <div class="container">
        <h1 class="main-heading">Quiz Master App</h1>
        <p class="catchy-line">Test your knowledge, conquer your exams.</p>
        <p class="motivational-text">
          This is the place to hone your skills, boost your confidence, and
          become a quiz master!
        </p>
        <RouterLink to="/login" class="btn btn-primary">Get Started</RouterLink>
      </div>
    </div>
  </template>
  
  <script setup>
  import { RouterLink } from 'vue-router';
  </script>
  
  <style scoped>
  .home-page {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background-color: #f8f9fa; /* Light gray background */
  }
  
  .container {
    text-align: center;
  }
  
  .main-heading {
    font-size: 3rem;
    margin-bottom: 1rem;
  }
  
  .catchy-line {
    font-size: 1.5rem;
    margin-bottom: 2rem;
  }
  
  .motivational-text {
    font-size: 1.2rem;
    margin-bottom: 3rem;
  }
  </style>
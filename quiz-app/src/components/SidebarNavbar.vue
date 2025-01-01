<template>
    <div class="sidebar-navbar">
      <div class="sidebar">
        <ul>
          <li>
            <RouterLink to="/">Home</RouterLink>
          </li>
          <li>
            <RouterLink to="/login">Login</RouterLink>
          </li>
        </ul>
      </div>
     
    </div>
  </template>
  
  <style scoped>
  .sidebar-navbar {
    display: flex;
  }
  
  .sidebar {
    width: 250px;
    background-color: #343a40;
    color: white;
    padding: 20px;
    position: fixed; /* Fixed positioning */
    left: 0; /* Stick to the left */
    top: 0;
    height: 100vh;
  }
  
  .sidebar ul {
    list-style: none;
    padding: 0;
  }
  
  .sidebar li {
    margin-bottom: 10px;
  }
  
  .sidebar a {
    color: white;
    text-decoration: none;
    display: block;
    padding: 10px;
  }
  
  .sidebar a:hover {
    background-color: #495057; /* Slightly darker background on hover */
  }
  
  .content {
    flex-grow: 1;
    padding: 20px;
    margin-left: 250px; /* Adjust for sidebar width */
    overflow-y: auto; /* Enable vertical scrolling if needed */
  }
  </style>
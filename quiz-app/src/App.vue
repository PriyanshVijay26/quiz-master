<template>
  <div id="app">
    <SidebarNavbar class="sidebar" />
    <div class="main-content">
      <router-view />
    </div>
  </div>
</template>

<script>
import SidebarNavbar from './components/SidebarNavbar.vue';

export default {
  components: {
    SidebarNavbar,
  },
};
</script>

<style scoped>
#app {
  display: flex;
  height: 100vh; /* Use full height of the viewport */
  width: 100vw; /* Use full width of the viewport */
  overflow: hidden; /* Prevent the overall app from scrolling */
}

.sidebar {
  width: 250px; /* Fixed width for the sidebar */
  background-color: #343a40; /* Dark background for the sidebar */
  color: white;
  display: flex;
  flex-direction: column; /* Stack sidebar items */
  height: 100%; /* Full height */
  overflow-y: auto; /* Allow scrolling inside the sidebar if content overflows */
}

.main-content {
  flex-grow: 1; /* Take up the remaining space */
  height: 100%; /* Full height */
  background-color: #f8f9fa; /* Light background for the content area */
  padding: 20px; /* Padding around the content */
  overflow-y: auto; /* Allow scrolling inside the content area */
  display: flex;
  justify-content: center; /* Center content horizontally */
  align-items: center; /* Center content vertically */
}
</style>

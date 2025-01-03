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
  height: 100vh; /* Full height */
  width: 100vw;  /* Full width */
  overflow: hidden; 
}

.sidebar {
  width: 250px; 
  background-color: #343a40; 
  color: white;
  display: flex;
  flex-direction: column; 
  height: 100%; 
  overflow-y: auto; 
  position: fixed; 
  left: 0;        
  top: 0;        
  z-index: 10;   
}

.main-content {
  margin-left: 250px; /* Align to the right of the sidebar */
  width: calc(100vw - 250px); /* Take the full remaining width */
  padding: 20px;
  background-color: #f8f9fa; 
  height: 100vh; /* Full height of the viewport */
  overflow-y: auto; 
  display: flex;
  flex-direction: column;
}
</style>

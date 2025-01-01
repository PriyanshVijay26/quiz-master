// router/index.js

import { createRouter, createWebHistory } from 'vue-router';
import HomePage from '../components/HomePage.vue';
import LoginPage from '../components/LoginPage.vue'; 
import RegisterPage from '../components/RegisterPage.vue';
import AdminDashboard from '../components/AdminDashboard.vue'; // Import AdminDashboard
import SubjectChapters from '../components/SubjectChapters.vue'; // Import the component
import ChapterQuizzes from '../components/ChapterQuizzes.vue'; // Import the new component
import QuizQuestions from '../components/QuizQuestions.vue'; // Import the new component
import UserDashboard from '../components/UserDashboard.vue';
import UserSubjectChapters from '../components/UserSubjectChapters.vue'; // Import the new component
import UserChapterQuizzes from '../components/UserChapterQuizzes.vue'; 

import UserQuiz from '../components/UserQuiz.vue'; // Import the new component


const routes = [
  { path: '/', component: HomePage },
  { path: '/login', component: LoginPage },
  { path: '/register', component: RegisterPage },
  { path: '/admin/dashboard', component: AdminDashboard }, // Admin dashboard route
  { path: '/admin/subjects/:subjectId/chapters', component: SubjectChapters },
  { path: '/admin/subjects/:subjectId/chapters/:chapterId/quizzes', component: ChapterQuizzes },
  { path: '/admin/subjects/:subjectId/chapters/:chapterId/quizzes/:quizId/questions', component: QuizQuestions },
  { path: '/user/dashboard', component: UserDashboard }, // User dashboard route
  { path: '/user/subjects/:subjectId/chapters', component: UserSubjectChapters }, // User subject chapters route
  // ... other routes
  { path: '/user/subjects/:subjectId/chapters/:chapterId/quizzes', component: UserChapterQuizzes },
  { path: '/user/subjects/:subjectId/chapters/:chapterId/quizzes/:quizId', component: UserQuiz },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
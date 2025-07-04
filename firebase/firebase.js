// src/firebase/firebase.js

import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyA4ueTgu5Mu3B2amhLToz8mbrlRnJM8AVs",
  authDomain: "visionalert-8130a.firebaseapp.com",
  projectId: "visionalert-8130a",
  storageBucket: "visionalert-8130a.appspot.com",
  messagingSenderId: "931272854811",
  appId: "1:931272854811:web:863d80002f5b5d2cf557be",
  measurementId: "G-NVBK4J5H8Y"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

// Export if needed in other files
export { app, analytics };

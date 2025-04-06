// Importation des modules Firebase
import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";
import { getFirestore } from "firebase/firestore";
import { getStorage } from "firebase/storage";

// Configuration Firebase
const firebaseConfig = {
    apiKey: "AIzaSyBJKNdFFtN6BmoeQd1gRrhBS1GiM2Y_3Ls",
    authDomain: "explore-morocco-a831d.firebaseapp.com",
    projectId: "explore-morocco-a831d",
    storageBucket: "explore-morocco-a831d.firebasestorage.app",
    messagingSenderId: "488123061161",
    appId: "1:488123061161:web:a939f91065b2cb8e4aeab8",
    measurementId: "G-408NNB5TEE"
};

// Initialisation de Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();
const db = getFirestore(app);
const storage = getStorage(app);

export { auth, provider, db, storage };
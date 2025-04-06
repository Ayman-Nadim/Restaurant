import React, { useState } from "react";
import { auth, provider } from "./firebase/firebaseConfig";
import { signInWithPopup } from "firebase/auth";

const Signin = () => {
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleGoogleSignin = async () => {
    try {
      await signInWithPopup(auth, provider);
      setSuccess("Connexion réussie ! Bienvenue.");
      setError(null);
    } catch (error) {
      setError(error.message);
      setSuccess(null);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-lg w-96 text-center">
        <h2 className="text-2xl font-bold mb-4">Connexion</h2>
        {error && <p className="text-red-500">{error}</p>}
        {success && <p className="text-green-500">{success}</p>}
        <button 
          onClick={handleGoogleSignin} 
          className="w-full bg-red-500 text-white py-2 rounded-md hover:bg-red-600 transition duration-300"
        >
          Se connecter avec Google
        </button>
      </div>
    </div>
  );
};

export default Signin;
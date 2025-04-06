import React, { useState } from "react";
import axios from "axios";
import { FiSearch, FiMapPin, FiStar, FiExternalLink, FiPhone, FiGlobe } from "react-icons/fi";
import { motion, AnimatePresence } from "framer-motion";

function App(){
  const [prompt, setPrompt] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedPlace, setSelectedPlace] = useState(null);

  const handleSearch = async () => {
    if (!prompt.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const response = await axios.post("http://127.0.0.1:8000/get-recommendations/", {
        prompt: prompt.trim(),
      });

      setResults(response.data.results);
    } catch (error) {
      console.error("Error fetching recommendations:", error);
      setError("Failed to get recommendations. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      handleSearch();
    }
  };

  const openGoogleMaps = (lat, lng) => {
    window.open(`https://www.google.com/maps/search/?api=1&query=${lat},${lng}`, "_blank");
  };

  const getFallbackImage = (name) => {
    const colors = [
      "from-blue-500 to-blue-700",
      "from-green-500 to-green-700",
      "from-purple-500 to-purple-700",
    ];
    const index = name.length % colors.length;
    return (
      <div className={`w-full h-full bg-gradient-to-r ${colors[index]} flex items-center justify-center`}>
        <span className="text-white text-xl font-bold text-center px-4">{name}</span>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-300 to-green-300 flex flex-col items-center p-6 md:p-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full mb-8 text-center"
      >
        {/* Ajout de l'image PNG avant le titre */}
        <div className="mb-4">
        <img
          src={require('./AgentGuide.png')}  // Remplacez par le chemin de votre image PNG
          alt="Logo"
          className="mx-auto h-80 w-80 object-contain" // Classes mises à jour pour augmenter la taille de l'image
        />
      </div>

      <div className="text-center mt-8">
        <h1 className="text-4xl font-bold text-white opacity-0 animate-fadeIn duration-1000">
          Welcome to ExploreMorocco!
        </h1>
        <p className="text-lg text-gray-700 mt-4 opacity-0 animate-fadeIn duration-1000 delay-500">
          My name is Houssam, and I am an AI AGENT that will help you to explore Morocco.
        </p>
      </div>

      </motion.div>
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4, delay: 0.2 }}
        className="w-full max-w-2xl mb-8"
      >
        <div className="relative flex items-center shadow-lg rounded-xl overflow-hidden bg-white">
          <input
            type="text"
            placeholder="What would you like to explore in Morocco?" 
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyPress={handleKeyPress}
            className="w-full p-4 pr-16 text-gray-700 focus:outline-none rounded-xl"
          />
          <button
            onClick={handleSearch}
            disabled={loading}
            className={`absolute right-2 p-2 rounded-lg ${loading ? 'text-blue-300' : 'text-blue-600 hover:text-blue-800'}`}
          >
            {loading ? (
              <svg className="animate-spin h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : (
              <FiSearch className="h-6 w-6" />
            )}
          </button>
        </div>
      </motion.div>

      {/* Results section */}
      <div className="w-full">
        {loading && (
          <div className="flex justify-center my-12">
            <div className="flex flex-col items-center">
              <svg className="animate-spin h-12 w-12 text-blue-500 mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <p className="text-gray-600">Finding the perfect sushi spots...</p>
            </div>
          </div>
        )}

        <AnimatePresence>
          {results.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
            >
              {results.map((place, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.1 }}
                  whileHover={{ y: -5 }}
                  className="w-full bg-white rounded-2xl shadow-md overflow-hidden hover:shadow-xl transition-all duration-300 cursor-pointer"
                  onClick={() => setSelectedPlace(place)}
                >
                <div className="h-48 relative overflow-hidden">
                  {place.photos && place.photos.length > 0 ? (
                    <img
                      src={place.photos[0]}
                      alt={place.name}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        e.target.onerror = null;
                        e.target.src = "https://via.placeholder.com/400x300?text=Image+Not+Available";
                      }}
                    />
                  ) : (
                    getFallbackImage(place.name) // Applique le fond dégradé ici si aucune image
                  )}
                </div>

                  <div className="p-4">
                    <h2 className="text-xl font-semibold mb-2">{place.name}</h2>
                    <div className="flex items-center text-gray-600">
                      <FiMapPin className="mr-2" />
                      <span>{place.address}</span>
                    </div>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>


      {/* Place details modal */}
      <AnimatePresence>
        {selectedPlace && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4"
            onClick={() => setSelectedPlace(null)}
          >
            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: 20, opacity: 0 }}
              className="bg-white rounded-2xl shadow-lg p-6 w-[65%] max-h-[75vh] overflow-y-auto scrollbar-thin scrollbar-thumb-gray-400 scrollbar-track-gray-100"
              onClick={(e) => e.stopPropagation()}
            >
              <div>
                <h2 className="text-2xl font-semibold mb-4">{selectedPlace.name}</h2>
                <div className="flex items-center text-gray-600 mb-2">
                  <FiMapPin className="mr-2" />
                  <span>{selectedPlace.address}</span>
                </div>

                {selectedPlace.rating && (
                  <div className="flex items-center text-gray-600 mb-2">
                    <FiStar className="mr-2 text-yellow-500" />
                    <span>{selectedPlace.rating}</span>
                  </div>
                )}

                {selectedPlace.types && (
                  <div className="text-gray-600 mb-2">
                    <strong>Types:</strong> {selectedPlace.types.join(", ")}
                  </div>
                )}

                {selectedPlace.phone && (
                  <div className="flex items-center text-gray-600 mb-2">
                    <FiPhone className="mr-2" />
                    <span>{selectedPlace.phone}</span>
                  </div>
                )}

                {selectedPlace.website && (
                  <div className="flex items-center text-blue-600 mb-2">
                    <FiGlobe className="mr-2" />
                    <a href={selectedPlace.website} target="_blank" rel="noopener noreferrer" className="hover:underline">
                      Website
                    </a>
                  </div>
                )}

                {selectedPlace.reviews && selectedPlace.reviews.length > 0 && (
                  <div className="text-gray-600 mt-4">
                    <strong>Reviews:</strong>
                    <div className="mt-2 space-y-4">
                      {selectedPlace.reviews.map((review, reviewIndex) => (
                        <div key={reviewIndex} className="p-4 rounded-lg bg-gray-100">
                          <div className="flex items-center mb-2">
                            <strong className="mr-2">{review.author_name}</strong>
                            <div className="flex items-center">
                              {[...Array(review.rating)].map((_, i) => (
                                <FiStar key={i} className="text-yellow-500" />
                              ))}
                            </div>
                          </div>
                          <p>{review.text}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {selectedPlace.photos && selectedPlace.photos.length > 0 && (
                  <div className="mt-4">
                    <div className="flex overflow-x-auto snap-x">
                      {selectedPlace.photos.map((photoUrl, photoIndex) => (
                        <img
                          key={photoIndex}
                          src={photoUrl || "https://www.century21casa.immo/wp-content/uploads/2021/12/empty.jpg"}
                          alt={`${selectedPlace.name} - Photo ${photoIndex + 1}`}
                          className="w-full h-48 object-cover snap-center flex-shrink-0 mr-2"
                          onError={(e) => {
                            e.target.onerror = null;
                            e.target.src = "https://via.placeholder.com/400x300?text=Image+Not+Available";
                          }}
                        />
                      ))}
                    </div>
                  </div>
                )}

                <button
                  onClick={() => openGoogleMaps(selectedPlace.location.lat, selectedPlace.location.lng)}
                  className="flex items-center text-blue-600 hover:text-blue-800 mt-4"
                >
                  <FiExternalLink className="mr-2" />
                  <span>View on Google Maps</span>
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

    </div>
  );
}

export default App;
// import React from "react";
// import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
// import Signup from "./signUp";
// import SignIn from "./SignIn";

// const App = () => {
//   return (
//     <Router>
//       <div>
//         <h1>Bienvenue sur mon application</h1>
//         <Routes>
//           <Route path="/signup" element={<Signup />} />
//           <Route path="/signIn" element={<SignIn />} />
//         </Routes>
//       </div>
//     </Router>
//   );
// };

// export default App;
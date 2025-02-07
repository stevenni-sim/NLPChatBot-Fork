import React, { useState, useEffect } from 'react';
import Footer from '../../component/footer';
import UserHeader from '../../component/userHeader';
import Chat from '../../component/Chat';
import axios from 'axios';
import { BASE_URL } from '../../service/config';


const Dashboard: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [userLocation, setUserLocation] = useState<{ lat: number; lng: number } | null>(null);
  const [userId, setUserId] = useState<string | null>(null);





  const getLocation = (): Promise<{ lat: number; lng: number }> => {
    return new Promise((resolve, reject) => {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            resolve({
              lat: position.coords.latitude,
              lng: position.coords.longitude,
            });
          },
          (error) => reject(error),
          { timeout: 10000 }
        );
      } else {
        reject("Geolocation is not supported by this browser.");
      }
    });
  };

  const fetchResults = async (query: string, lat: number, lng: number) => {
    setLoading(true);
    try {
      const response = await axios.post(`${BASE_URL}/nearbyLocation/`, {
        mode: 'search',
        latitude: lat, // Updated key to match the backend
        longitude: lng, // Updated key to match the backend
        inputText: query || 'cafe',
      });
      setResults(response.data.results);
    } catch (error: any) {
      console.error('Error fetching data:', error.response?.data || error.message);
    } finally {
      setLoading(false);
    }
  };
  

  useEffect(() => {

    const storedUserId = sessionStorage.getItem('userId');
    if (storedUserId) {
      setUserId(storedUserId);
    }

  
    getLocation()
      .then((location) => {
        setUserLocation(location);
        fetchResults('cafe', location.lat, location.lng);
      })
      .catch((error) => {
        console.error("Error getting location:", error);
        fetchResults('cafe', 1.3521, 103.8198);
      });
  }, [userId]);


  const handleSearch = () => {
    if (userLocation) {
      fetchResults(searchQuery, userLocation.lat, userLocation.lng);
    }
  };

  return (
    <>
      <UserHeader />
      <main style={{ flex: '1' }}>

        {/* Main Dashboard Content */}
        <div style={{ padding: '20px', textAlign: 'center' }}>
          {/* Search bar and results */}
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search for places (e.g., cafe, restaurant)"
            style={{
              padding: '10px',
              width: '300px',
              fontSize: '16px',
              marginRight: '10px',
              borderRadius: '5px',
              border: '1px solid #ccc',
            }}
          />
          <button
            onClick={handleSearch}
            style={{
              padding: '10px 20px',
              fontSize: '16px',
              cursor: 'pointer',
              backgroundColor: '#007BFF',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
            }}
          >
            Search
          </button>

          {loading ? (
            <p>Loading...</p>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', padding: '20px' }}>
              {results.length > 0 ? (
                results.map((place) => (
                  <div
                    key={place.fsq_id}
                    style={{
                      border: '1px solid #ddd',
                      borderRadius: '10px',
                      padding: '10px',
                      textAlign: 'center',
                      boxShadow: '0 2px 5px rgba(0,0,0,0.1)',
                    }}
                  >
                    <h4>{place.name}</h4>
                    <img
                      src={`${place.categories[0].icon.prefix}bg_64${place.categories[0].icon.suffix}`}
                      alt={place.categories[0].name}
                      style={{ width: '50px', height: '50px', marginBottom: '10px' }}
                    />
                    <p>{place.location.formatted_address}</p>
                    <p>{place.distance} meters away</p>
                  </div>
                ))
              ) : (
                <p>No results found.</p>
              )}
            </div>
          )}
        </div>
      </main>
      <Chat />
      <Footer />
    </>
  );
};

export default Dashboard;

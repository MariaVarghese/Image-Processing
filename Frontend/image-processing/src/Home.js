import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Carousel } from 'react-responsive-carousel';
import 'react-responsive-carousel/lib/styles/carousel.min.css';
import './Home.css';

function HomePage() {
  const [images, setImages] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch images from API
    axios.get('https://o7re24ge39.execute-api.ap-south-1.amazonaws.com/default/fetchImage')
      .then(response => {
        console.log(response.data.result)
        setImages(response.data.result);
      })
      .catch(error => {
        setError(error.message);
      });
  }, []);

  return (
    <div>
      {error ? (
        <p>Error: {error}</p>
      ) : (
        <Carousel>
          {images.map((image, index) => (
            <div key={index}>
              <img src={`data:image/jpeg;base64,${image.image}`} alt={image.metadata.description} />
              <p className="legend">
                Author: {image.metadata.artist_name} <br />
                Description: {image.metadata.description} <br />
                Copyright: {image.metadata.copyright}
              </p>
            </div>
          ))}
        </Carousel>
      )}
    </div>
  );
}

export default HomePage;
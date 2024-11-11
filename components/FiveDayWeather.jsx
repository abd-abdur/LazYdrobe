import React, { useEffect, useState } from 'react';

const FiveDayWeather = ({ location }) => {
  const [forecast, setForecast] = useState([]);
  const apiKey = process.env.REACT_APP_VISUAL_CROSSING_API_KEY;

  useEffect(() => {
    if (location) {
      const fetchWeather = async () => {
        try {
          const response = await fetch(
            `https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/${location}/next5days?key=${apiKey}&unitGroup=us&iconSet=icons2`
          );
          const data = await response.json();
          setForecast(data.days.slice(0, 5)); // Get the next 5 days, including today
        } catch (error) {
          console.error('Error fetching weather data:', error);
        }
      };
      fetchWeather();
    }
  }, [location, apiKey]);

  return (
    <div style={{ display: 'flex', justifyContent: 'space-around', padding: '10px', background: '#e0f7fa', borderRadius: '10px' }}>
      {forecast.length > 0 ? (
        forecast.map((day, index) => (
          <div key={index} style={{ textAlign: 'center' }}>
            <div>{new Date(day.datetime).toLocaleDateString('en-US', { weekday: 'short' })}</div>
            {day.icon && (
              <img src={`https://raw.githubusercontent.com/visualcrossing/WeatherIcons/refs/heads/main/PNG/1st%20Set%20-%20Color/${day.icon}.png`} alt={day.icon} style={{ width: '40px', height: '40px' }} />
            )}
            <div>{Math.round(day.tempmin)}° / {Math.round(day.tempmax)}°F</div>
          </div>
        ))
      ) : (
        <p>Please enter a valid location to view the weather forecast.</p>
      )}
    </div>
  );
};

export default FiveDayWeather;

import {useEffect, useState} from 'react';
import axios from "axios"
import {format} from "date-fns";

import './App.css';

const baseURL = "http://localhost:1000"

function App() {
  const [description, setDescription] = useState("");

  const fetchEvents = async () => {
    const data = await axios.get(`${baseURL}/events/weather_data/Boston`);
    console.log("DATA: ", data);
  }

  const handleChange = e => {
    setDescription(e.target.value);
    console.log(description);
  }

  const handleSubmit = e => {
    e.preventDefault();
  }

  useEffect(() => {
    fetchEvents();
  }, [])
  return (
    <div className="App">
      <header className="App-header">
        <form onSubmit={handleSubmit}>
          <label htmlFor='description'>Description</label>
          <input onChange={handleChange} type="text" name="description" id="description" value={description}>
          </input>
          <button type="submit">Submit</button>
        </form>
      </header>
    </div>
  );
}

export default App;

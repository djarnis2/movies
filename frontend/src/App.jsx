import './css/App.css'
import { Routes, Route } from "react-router-dom"
import Home from './pages/Home';
import NotSeen from './pages/NotSeen';
import NavBar from './components/NavBar';
import Imports from './pages/Imports'
import { useState } from "react";



function App() {
  const [resetTick, setResetTick] = useState(0);

  const clearSearchEverywhere = () => {
    setResetTick(t => t + 1);
  };


  return (
    <div>
      <NavBar onClearSearch={() => clearSearchEverywhere()} />

      <main className='main-content'>
        <Routes>
          <Route
            path='/'
            element={
              <Home
                resetTick={resetTick}
              />
            }
          />
          <Route
            path='/notseen'
            element={
              <NotSeen
                resetTick={resetTick}
              />} />
          <Route
            path='/imports'
            element={
              <Imports />
            }
          />
        </Routes>
      </main>
    </div>
  );
}

export default App;
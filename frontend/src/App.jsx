import './css/App.css'
import { Routes, Route } from "react-router-dom"
import Home from './pages/Home';
import NotSeen from './pages/NotSeen';
import NavBar from './components/NavBar';



function App() {
  return (
    <div>
      <NavBar />
    <main className='main-content'>
      <Routes>
        <Route path='/' element={<Home />}></Route>
        <Route path='/notseen' element={<NotSeen />}></Route>
      </Routes>
    </main>
   </div>
  );
}

export default App
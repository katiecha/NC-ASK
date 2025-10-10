import { Routes, Route } from 'react-router-dom';
import { DarkModeProvider } from './contexts/DarkModeContext';
import Layout from './components/Layout';
import Home from './pages/Home';
import About from './pages/About';
import './styles/global.css';

function App() {
  return (
    <DarkModeProvider>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </Layout>
    </DarkModeProvider>
  );
}

export default App;
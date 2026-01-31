import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import AITree from './pages/AITree';
import { Trading, Insights, Settings } from './pages/PlaceholderPages';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="ai-tree" element={<AITree />} />
        <Route path="trading" element={<Trading />} />
        <Route path="insights" element={<Insights />} />
        <Route path="settings" element={<Settings />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}

export default App;

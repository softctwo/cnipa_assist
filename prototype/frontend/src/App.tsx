import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Provider } from 'react-redux';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import { store } from './store';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import DocumentList from './pages/DocumentList';
import DocumentDetail from './pages/DocumentDetail';
import ExaminationWorkspace from './pages/ExaminationWorkspace';
import AIAnalysis from './pages/AIAnalysis';
import Settings from './pages/Settings';
import './App.css';

function App() {
  return (
    <Provider store={store}>
      <ConfigProvider locale={zhCN}>
        <Router>
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/documents" element={<DocumentList />} />
              <Route path="/documents/:id" element={<DocumentDetail />} />
              <Route path="/examination" element={<ExaminationWorkspace />} />
              <Route path="/examination/:id" element={<ExaminationWorkspace />} />
              <Route path="/ai-analysis" element={<AIAnalysis />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </Layout>
        </Router>
      </ConfigProvider>
    </Provider>
  );
}

export default App;
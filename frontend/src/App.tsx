import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { BottomNav } from './components/BottomNav';
import { CanvasShader } from './components/CanvasShader';
import { HomePage } from './pages/HomePage';
import { DiagnosePage } from './pages/DiagnosePage';
import { DiseaseLibraryPage } from './pages/DiseaseLibraryPage';
import { DiseaseDetailPage } from './pages/DiseaseDetailPage';
import { HistoryPage } from './pages/HistoryPage';
import { CarePage } from './pages/CarePage';
import { AboutPage } from './pages/AboutPage';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<string>('home');
  const [selectedDiseaseId, setSelectedDiseaseId] = useState<string | null>(null);

  const handleSelectDisease = (id: string) => {
    setSelectedDiseaseId(id);
    setCurrentTab('disease-detail');
  };

  return (
    <div className="min-h-screen flex flex-col relative text-on-surface">
      <CanvasShader />
      
      <Navbar currentTab={currentTab} onNavigate={setCurrentTab} />

      <main className="flex-grow pt-4">
        {currentTab === 'home' && <HomePage onNavigate={setCurrentTab} />}
        {currentTab === 'diagnose' && <DiagnosePage onNavigate={setCurrentTab} />}
        {currentTab === 'diseases' && <DiseaseLibraryPage onSelectDisease={handleSelectDisease} />}
        {currentTab === 'disease-detail' && selectedDiseaseId && (
          <DiseaseDetailPage
            diseaseId={selectedDiseaseId}
            onBack={() => setCurrentTab('diseases')}
            onDiagnoseNow={() => setCurrentTab('diagnose')}
          />
        )}
        {currentTab === 'history' && <HistoryPage />}
        {currentTab === 'care' && <CarePage />}
        {currentTab === 'about' && <AboutPage />}
      </main>

      <BottomNav currentTab={currentTab} onNavigate={setCurrentTab} />
    </div>
  );
};
export default App;

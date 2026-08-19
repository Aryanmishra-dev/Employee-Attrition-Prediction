import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import MainLayout from '@/components/layout/MainLayout'
import Dashboard from '@/pages/Dashboard'
import Predict from '@/pages/Predict'
import BatchPredict from '@/pages/BatchPredict'
import Analytics from '@/pages/Analytics'
import ModelInfo from '@/pages/ModelInfo'
import EmployeeProfile from '@/pages/EmployeeProfile'

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="predict" element={<Predict />} />
          <Route path="batch-predict" element={<BatchPredict />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="model-info" element={<ModelInfo />} />
          <Route path="employee/:employeeId" element={<EmployeeProfile />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App

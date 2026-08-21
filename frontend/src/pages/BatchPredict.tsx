import React, { useState } from 'react';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { UploadCloud, FileText, CheckCircle, AlertTriangle } from 'lucide-react';

const BatchPredict: React.FC = () => {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState<File | null>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8 animate-fade-in">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-slate-900 dark:text-white">Batch Prediction</h2>
        <p className="mt-2 text-slate-600 dark:text-gray-400">Upload a CSV file containing multiple employee records for bulk scoring.</p>
      </div>

      <Card glass>
        <CardContent className="p-8">
          <div
            className={`relative border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 ${
              dragActive 
                ? 'border-primary bg-primary/5 dark:bg-primary/10' 
                : 'border-slate-300 hover:border-primary/50 dark:border-gray-600'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <input
              type="file"
              accept=".csv"
              className="absolute inset-0 h-full w-full opacity-0 cursor-pointer"
              onChange={handleChange}
            />
            
            {!file ? (
              <div className="flex flex-col items-center pointer-events-none">
                <div className="mb-4 rounded-full bg-primary/10 p-4 text-primary dark:bg-primary/20">
                  <UploadCloud className="h-8 w-8" />
                </div>
                <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Click or drag and drop to upload</h3>
                <p className="mt-2 text-sm text-slate-500 dark:text-gray-400">CSV files only. Maximum file size 5MB.</p>
                <div className="mt-6 flex items-center gap-2 text-sm text-slate-500">
                  <FileText className="h-4 w-4" />
                  <span>Download template</span>
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center pointer-events-none animate-slide-up">
                <div className="mb-4 rounded-full bg-success/10 p-4 text-success">
                  <CheckCircle className="h-8 w-8" />
                </div>
                <h3 className="text-lg font-semibold text-slate-900 dark:text-white">{file.name}</h3>
                <p className="mt-1 text-sm text-slate-500 dark:text-gray-400">{(file.size / 1024).toFixed(1)} KB</p>
                
                <Button className="mt-6 pointer-events-auto relative z-10" onClick={(e) => { e.preventDefault(); /* submit */}}>
                  Process File
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
      
      <div className="rounded-xl border border-warning/20 bg-warning-light/30 p-4 text-sm text-warning-dark dark:bg-warning-dark/10 dark:text-warning-light flex items-start">
        <AlertTriangle className="mr-3 h-5 w-5 shrink-0" />
        <p>Ensure your CSV headers match the exact format specified in the template. Missing columns will result in processing errors.</p>
      </div>
    </div>
  );
};

export default BatchPredict;

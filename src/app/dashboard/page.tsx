"use client"

import { useState, useEffect } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Upload, BarChart3, Brain, Scale, Lightbulb, BookOpen } from "lucide-react"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import DataUploadSection from "@/components/dashboard/data-upload-section"
import EDASection from "@/components/dashboard/eda-section"
import ModelPredictionSection from "@/components/dashboard/model-prediction-section"
import FairnessAuditSection from "@/components/dashboard/fairness-audit-section"
import ExplainabilitySection from "@/components/dashboard/explainability-section"

export default function DashboardPage() {
  const [uploadedData, setUploadedData] = useState<any>(null)
  const [isLoaded, setIsLoaded] = useState(false)

  // Load data from localStorage on mount
  useEffect(() => {
    const savedData = localStorage.getItem('creditScoringData')
    if (savedData) {
      try {
        setUploadedData(JSON.parse(savedData))
      } catch (e) {
        console.error('Failed to parse saved data:', e)
      }
    }
    setIsLoaded(true)
  }, [])

  // Save data to localStorage when it changes
  useEffect(() => {
    if (isLoaded) {
      if (uploadedData) {
        localStorage.setItem('creditScoringData', JSON.stringify(uploadedData))
      } else {
        localStorage.removeItem('creditScoringData')
      }
    }
  }, [uploadedData, isLoaded])

  return (
    <div className="min-h-screen bg-background">
      <div className="border-b bg-gradient-to-r from-success/5 to-transparent">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-success to-success/70 text-success-foreground shadow-lg shadow-success/20">
                <Brain className="h-6 w-6" />
              </div>
              <div>
                <h1 className="text-2xl font-bold tracking-tight">Credit Scoring Dashboard</h1>
                <p className="text-sm text-muted-foreground">
                  Data analysis, model predictions, and fairness auditing
                </p>
              </div>
            </div>
            <div className="flex gap-2">
              <Link href="/">
                <Button variant="outline" size="sm" className="border-success/20 hover:bg-success/5">
                  Home
                </Button>
              </Link>
              <Link href="/api/docs">
                <Button variant="outline" size="sm" className="gap-2 border-success/20 hover:bg-success/5">
                  <BookOpen className="h-4 w-4" />
                  API Docs
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-6">
        <Tabs defaultValue="upload" className="space-y-6">
          <TabsList className="grid w-full grid-cols-5 lg:w-auto lg:inline-grid bg-muted/50">
            <TabsTrigger value="upload" className="gap-2 data-[state=active]:bg-success data-[state=active]:text-success-foreground">
              <Upload className="h-4 w-4" />
              <span className="hidden sm:inline">Data Upload</span>
            </TabsTrigger>
            <TabsTrigger value="eda" className="gap-2 data-[state=active]:bg-success data-[state=active]:text-success-foreground">
              <BarChart3 className="h-4 w-4" />
              <span className="hidden sm:inline">EDA</span>
            </TabsTrigger>
            <TabsTrigger value="prediction" className="gap-2 data-[state=active]:bg-success data-[state=active]:text-success-foreground">
              <Brain className="h-4 w-4" />
              <span className="hidden sm:inline">Prediction</span>
            </TabsTrigger>
            <TabsTrigger value="fairness" className="gap-2 data-[state=active]:bg-success data-[state=active]:text-success-foreground">
              <Scale className="h-4 w-4" />
              <span className="hidden sm:inline">Fairness</span>
            </TabsTrigger>
            <TabsTrigger value="explainability" className="gap-2 data-[state=active]:bg-success data-[state=active]:text-success-foreground">
              <Lightbulb className="h-4 w-4" />
              <span className="hidden sm:inline">SHAP</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="upload" className="space-y-4">
            <DataUploadSection onDataUploaded={setUploadedData} />
          </TabsContent>

          <TabsContent value="eda" className="space-y-4">
            <EDASection data={uploadedData} />
          </TabsContent>

          <TabsContent value="prediction" className="space-y-4">
            <ModelPredictionSection />
          </TabsContent>

          <TabsContent value="fairness" className="space-y-4">
            <FairnessAuditSection data={uploadedData} />
          </TabsContent>

          <TabsContent value="explainability" className="space-y-4">
            <ExplainabilitySection data={uploadedData} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
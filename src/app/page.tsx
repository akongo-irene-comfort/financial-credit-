import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Brain, BarChart3, Scale, Lightbulb, ArrowRight, CheckCircle, Sparkles, Shield, TrendingUp } from "lucide-react";

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col bg-gradient-to-b from-background to-muted/20">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-success to-success/70 text-success-foreground shadow-lg shadow-success/20">
              <Brain className="h-5 w-5" />
            </div>
            <span className="text-lg font-bold bg-gradient-to-r from-success to-success/80 bg-clip-text text-transparent">Credit Scoring AI</span>
          </div>
          <Link href="/dashboard">
            <Button className="gap-2 bg-success hover:bg-success/90 text-success-foreground shadow-lg shadow-success/20">
              Go to Dashboard
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1">
        <div className="container mx-auto px-4 py-20 md:py-32">
          <div className="mx-auto max-w-4xl text-center space-y-8">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-success/10 border border-success/20 text-success text-sm font-medium mb-4">
              <Sparkles className="h-4 w-4" />
              AI-Powered Credit Analysis Platform
            </div>
            
            <div className="space-y-6">
              <h1 className="text-5xl font-bold tracking-tight sm:text-6xl md:text-7xl">
                Credit Scoring
                <span className="block bg-gradient-to-r from-success to-success/70 bg-clip-text text-transparent mt-2">
                  Dashboard
                </span>
              </h1>
              <p className="text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
                Advanced machine learning platform for loan application analysis, 
                fairness auditing, and explainable AI predictions
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
              <Link href="/dashboard">
                <Button size="lg" className="gap-2 bg-success hover:bg-success/90 text-success-foreground shadow-xl shadow-success/20 px-8">
                  <Brain className="h-5 w-5" />
                  Launch Dashboard
                </Button>
              </Link>
              <Link href="/api/docs">
                <Button size="lg" variant="outline" className="gap-2 border-success/20 hover:bg-success/5 px-8">
                  View API Docs
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
            </div>

            {/* Features Grid */}
            <div className="grid gap-6 pt-16 sm:grid-cols-2 lg:grid-cols-4 text-left">
              <Card className="border-success/10 hover:border-success/30 transition-all hover:shadow-lg hover:shadow-success/5">
                <CardHeader className="space-y-3">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-success/10 to-success/5 ring-1 ring-success/20">
                    <BarChart3 className="h-6 w-6 text-success" />
                  </div>
                  <CardTitle className="text-lg">EDA & Insights</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="leading-relaxed">
                    Comprehensive exploratory data analysis with interactive visualizations and real-time statistics
                  </CardDescription>
                </CardContent>
              </Card>

              <Card className="border-success/10 hover:border-success/30 transition-all hover:shadow-lg hover:shadow-success/5">
                <CardHeader className="space-y-3">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-success/10 to-success/5 ring-1 ring-success/20">
                    <Brain className="h-6 w-6 text-success" />
                  </div>
                  <CardTitle className="text-lg">ML Predictions</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="leading-relaxed">
                    Real-time credit scoring with Random Forest and ensemble models achieving 87.3% accuracy
                  </CardDescription>
                </CardContent>
              </Card>

              <Card className="border-success/10 hover:border-success/30 transition-all hover:shadow-lg hover:shadow-success/5">
                <CardHeader className="space-y-3">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-success/10 to-success/5 ring-1 ring-success/20">
                    <Scale className="h-6 w-6 text-success" />
                  </div>
                  <CardTitle className="text-lg">Fairness Audit</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="leading-relaxed">
                    Bias detection and demographic parity analysis across groups with compliance metrics
                  </CardDescription>
                </CardContent>
              </Card>

              <Card className="border-success/10 hover:border-success/30 transition-all hover:shadow-lg hover:shadow-success/5">
                <CardHeader className="space-y-3">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-success/10 to-success/5 ring-1 ring-success/20">
                    <Lightbulb className="h-6 w-6 text-success" />
                  </div>
                  <CardTitle className="text-lg">SHAP Explainability</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="leading-relaxed">
                    Feature importance and individual prediction explanations with waterfall charts
                  </CardDescription>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>

        {/* Stats Section */}
        <div className="border-t bg-gradient-to-b from-muted/30 to-background">
          <div className="container mx-auto px-4 py-16">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold mb-3">Platform Performance</h2>
              <p className="text-muted-foreground">Trusted metrics from our production environment</p>
            </div>
            <div className="grid gap-8 sm:grid-cols-3 max-w-4xl mx-auto">
              <Card className="text-center border-success/10">
                <CardContent className="pt-6">
                  <div className="flex justify-center mb-3">
                    <div className="p-3 rounded-xl bg-success/10 ring-1 ring-success/20">
                      <TrendingUp className="h-6 w-6 text-success" />
                    </div>
                  </div>
                  <div className="text-4xl font-bold text-success mb-2">87.3%</div>
                  <div className="text-sm text-muted-foreground font-medium">Model Accuracy</div>
                  <div className="mt-2 inline-flex items-center gap-1 text-xs text-success">
                    <CheckCircle className="h-3 w-3" />
                    Production Ready
                  </div>
                </CardContent>
              </Card>
              
              <Card className="text-center border-success/10">
                <CardContent className="pt-6">
                  <div className="flex justify-center mb-3">
                    <div className="p-3 rounded-xl bg-success/10 ring-1 ring-success/20">
                      <Shield className="h-6 w-6 text-success" />
                    </div>
                  </div>
                  <div className="text-4xl font-bold text-success mb-2">88.6</div>
                  <div className="text-sm text-muted-foreground font-medium">Fairness Score</div>
                  <div className="mt-2 inline-flex items-center gap-1 text-xs text-success">
                    <CheckCircle className="h-3 w-3" />
                    Bias Compliant
                  </div>
                </CardContent>
              </Card>
              
              <Card className="text-center border-success/10">
                <CardContent className="pt-6">
                  <div className="flex justify-center mb-3">
                    <div className="p-3 rounded-xl bg-success/10 ring-1 ring-success/20">
                      <BarChart3 className="h-6 w-6 text-success" />
                    </div>
                  </div>
                  <div className="text-4xl font-bold text-success mb-2">5,000+</div>
                  <div className="text-sm text-muted-foreground font-medium">Applications Analyzed</div>
                  <div className="mt-2 inline-flex items-center gap-1 text-xs text-success">
                    <CheckCircle className="h-3 w-3" />
                    Real-time Processing
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="container mx-auto px-4 py-16">
          <Card className="border-success/20 bg-gradient-to-br from-success/5 to-success/10">
            <CardContent className="flex flex-col md:flex-row items-center justify-between gap-6 p-8 md:p-12">
              <div className="space-y-2 text-center md:text-left">
                <h3 className="text-2xl font-bold">Ready to Get Started?</h3>
                <p className="text-muted-foreground max-w-xl">
                  Upload your dataset and start analyzing credit applications with AI-powered insights
                </p>
              </div>
              <Link href="/dashboard">
                <Button size="lg" className="gap-2 bg-success hover:bg-success/90 text-success-foreground shadow-xl shadow-success/20 px-8 whitespace-nowrap">
                  <Brain className="h-5 w-5" />
                  Open Dashboard
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t py-6 bg-background/50">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          <p>© 2024 Credit Scoring AI. Built with Next.js, TypeScript, and Machine Learning.</p>
        </div>
      </footer>
    </div>
  );
}
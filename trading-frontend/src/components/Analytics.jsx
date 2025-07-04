import { BarChart3, TrendingUp, Bot, Target } from 'lucide-react'

const Analytics = () => {
  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold text-foreground">Analytics</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-card rounded-lg p-6 border border-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Total Trades</p>
              <p className="text-2xl font-bold text-foreground">1,247</p>
            </div>
            <BarChart3 className="h-8 w-8 text-blue-500" />
          </div>
        </div>
        
        <div className="bg-card rounded-lg p-6 border border-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Win Rate</p>
              <p className="text-2xl font-bold text-foreground">78.5%</p>
            </div>
            <Target className="h-8 w-8 text-green-500" />
          </div>
        </div>
        
        <div className="bg-card rounded-lg p-6 border border-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Profit Factor</p>
              <p className="text-2xl font-bold text-foreground">2.34</p>
            </div>
            <TrendingUp className="h-8 w-8 text-purple-500" />
          </div>
        </div>
        
        <div className="bg-card rounded-lg p-6 border border-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">AI Accuracy</p>
              <p className="text-2xl font-bold text-foreground">85.2%</p>
            </div>
            <Bot className="h-8 w-8 text-orange-500" />
          </div>
        </div>
      </div>
      
      <div className="bg-card rounded-lg p-6 border border-border">
        <h2 className="text-xl font-semibold text-foreground mb-4">Performance Analytics</h2>
        <div className="text-center py-12">
          <BarChart3 className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">Advanced analytics charts coming soon</p>
        </div>
      </div>
    </div>
  )
}

export default Analytics


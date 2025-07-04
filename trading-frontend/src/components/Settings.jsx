import { Settings as SettingsIcon, User, Shield, Bell, CreditCard } from 'lucide-react'

const Settings = ({ user }) => {
  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold text-foreground">Settings</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card rounded-lg p-6 border border-border">
          <div className="flex items-center space-x-2 mb-4">
            <User className="h-5 w-5 text-blue-500" />
            <h2 className="text-xl font-semibold text-foreground">Profile Settings</h2>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-muted-foreground mb-1">
                First Name
              </label>
              <input
                type="text"
                value={user?.first_name || ''}
                className="w-full px-3 py-2 bg-background border border-border rounded-lg text-foreground"
                readOnly
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-muted-foreground mb-1">
                Last Name
              </label>
              <input
                type="text"
                value={user?.last_name || ''}
                className="w-full px-3 py-2 bg-background border border-border rounded-lg text-foreground"
                readOnly
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-muted-foreground mb-1">
                Email
              </label>
              <input
                type="email"
                value={user?.email || ''}
                className="w-full px-3 py-2 bg-background border border-border rounded-lg text-foreground"
                readOnly
              />
            </div>
          </div>
        </div>
        
        <div className="bg-card rounded-lg p-6 border border-border">
          <div className="flex items-center space-x-2 mb-4">
            <CreditCard className="h-5 w-5 text-green-500" />
            <h2 className="text-xl font-semibold text-foreground">Subscription</h2>
          </div>
          
          <div className="space-y-4">
            <div className="p-4 bg-background rounded-lg border border-border">
              <p className="font-medium text-foreground">
                {user?.subscription?.plan?.name || 'Free Trial'}
              </p>
              <p className="text-sm text-muted-foreground">
                {user?.subscription?.plan?.description || 'Basic trading features'}
              </p>
              <p className="text-sm font-medium text-green-500 mt-2">
                ${user?.subscription?.plan?.price || '0.00'}/month
              </p>
            </div>
          </div>
        </div>
        
        <div className="bg-card rounded-lg p-6 border border-border">
          <div className="flex items-center space-x-2 mb-4">
            <Bell className="h-5 w-5 text-orange-500" />
            <h2 className="text-xl font-semibold text-foreground">Notifications</h2>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-foreground">Trading Alerts</span>
              <input type="checkbox" defaultChecked className="rounded" />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-foreground">Email Notifications</span>
              <input type="checkbox" defaultChecked className="rounded" />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-foreground">AI Signal Updates</span>
              <input type="checkbox" defaultChecked className="rounded" />
            </div>
          </div>
        </div>
        
        <div className="bg-card rounded-lg p-6 border border-border">
          <div className="flex items-center space-x-2 mb-4">
            <Shield className="h-5 w-5 text-red-500" />
            <h2 className="text-xl font-semibold text-foreground">Security</h2>
          </div>
          
          <div className="space-y-4">
            <button className="w-full px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90">
              Change Password
            </button>
            <button className="w-full px-4 py-2 bg-secondary text-secondary-foreground rounded-lg hover:bg-secondary/90">
              Enable 2FA
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Settings


#!/usr/bin/env python3
import re

# Read the file
with open('./frontend/src/app/page.tsx', 'r') as f:
    content = f.read()

# Find and replace the navigation section
old_nav = r'''        {/\* Navigation \*/}
        <div className="mb-8 bg-white p-4 rounded-lg shadow">
          <div className="flex gap-4">
            <Button className="bg-blue-600 text-white">DR Planning</Button>
            <a href="/agents">
              <Button className="bg-gray-200 text-gray-800">AI Agents</Button>
            </a>
            <a href="/verification">
              <Button className="bg-gray-200 text-gray-800">API Verification</Button>
            </a>
            <a href="/history">
              <Button className="bg-gray-200 text-gray-800">History</Button>
            </a>
          </div>
        </div>'''

new_nav = '''        {/* Navigation */}
        <Navigation />

        {/* Quick Access Cards */}
        <Grid numItemsMd={4} className="gap-4 mb-6">
          <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => window.location.href='/realtime'}>
            <div className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-yellow-500" />
              <Text>Real-Time Monitoring</Text>
            </div>
            <Text className="text-xs text-gray-500 mt-2">Live grid operations center</Text>
          </Card>

          <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => window.location.href='/analytics'}>
            <div className="flex items-center gap-2">
              <Zap className="h-5 w-5 text-green-500" />
              <Text>ML Analytics</Text>
            </div>
            <Text className="text-xs text-gray-500 mt-2">AI predictions & insights</Text>
          </Card>

          <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => window.location.href='/market'}>
            <div className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-indigo-500" />
              <Text>Energy Market</Text>
            </div>
            <Text className="text-xs text-gray-500 mt-2">Trading & pricing</Text>
          </Card>

          <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => window.location.href='/topology'}>
            <div className="flex items-center gap-2">
              <CloudSun className="h-5 w-5 text-cyan-500" />
              <Text>Grid Topology</Text>
            </div>
            <Text className="text-xs text-gray-500 mt-2">Network visualization</Text>
          </Card>
        </Grid>'''

# Replace the navigation section
content = content.replace(old_nav, new_nav)

# Write back
with open('./frontend/src/app/page.tsx', 'w') as f:
    f.write(content)

print("Navigation updated successfully!")
'use client';

import { useState, useEffect } from 'react';
import { Card, Title, Text, Metric, Grid, Badge, Button, ProgressBar } from '@tremor/react';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { AlertCircle, Zap, CloudSun, Users, Activity, Send } from 'lucide-react';
import axios from 'axios';
import { format } from 'date-fns';
import Navigation from './navigation';

const API_BASE = 'http://localhost:8003/api';

export default function Dashboard() {
  const [ercotData, setErcotData] = useState<any>(null);
  const [forecast, setForecast] = useState<any>(null);
  const [cohorts, setCohorts] = useState<any[]>([]);
  const [weather, setWeather] = useState<any>(null);
  const [selectedCohorts, setSelectedCohorts] = useState<string[]>([]);
  const [strategy, setStrategy] = useState('balanced');
  const [proposedPlan, setProposedPlan] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<string>('');

  // Fetch data on mount
  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); // Refresh every 5 seconds to see real-time changes
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      // Fetch data with individual error handling
      const [ercotRes, forecastRes, cohortsRes, weatherRes] = await Promise.allSettled([
        axios.get(`${API_BASE}/ercot/current`).catch(err => ({ data: { error: 'ERCOT data unavailable', data_source: 'unavailable' } })),
        axios.get(`${API_BASE}/ercot/forecast`).catch(err => ({ data: { error: 'Forecast unavailable', data_source: 'unavailable' } })),
        axios.get(`${API_BASE}/cohorts/`).catch(err => ({ data: [] })),
        axios.get(`${API_BASE}/weather/78701`).catch(err => ({ data: { error: 'Weather unavailable' } })),
      ]);

      // Handle fulfilled promises
      if (ercotRes.status === 'fulfilled') setErcotData(ercotRes.value.data);
      if (forecastRes.status === 'fulfilled') setForecast(forecastRes.value.data);
      if (cohortsRes.status === 'fulfilled') setCohorts(cohortsRes.value.data);
      if (weatherRes.status === 'fulfilled') setWeather(weatherRes.value.data);

      setLastUpdate(new Date().toLocaleTimeString());
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const proposePlan = async () => {
    setLoading(true);
    try {
      const now = new Date();
      const windowStart = new Date(now.getTime() + 2 * 60 * 60 * 1000); // 2 hours from now
      const windowEnd = new Date(windowStart.getTime() + 2 * 60 * 60 * 1000); // 2 hour window

      const response = await axios.post(`${API_BASE}/plans/propose/`, {
        window_start: windowStart.toISOString(),
        window_end: windowEnd.toISOString(),
        strategy,
        selected_cohorts: selectedCohorts.length > 0 ? selectedCohorts : null,
        operator_id: 'operator_1'
      });

      setProposedPlan(response.data);
    } catch (error) {
      console.error('Error proposing plan:', error);
    } finally {
      setLoading(false);
    }
  };

  const approvePlan = async () => {
    if (!proposedPlan) return;

    try {
      await axios.post(`${API_BASE}/plans/${proposedPlan.id}/approve/`, {
        operator_id: 'operator_1',
        notes: 'Approved via HITL portal'
      });

      alert('Plan approved and signals dispatched!');
      setProposedPlan(null);
      setSelectedCohorts([]);
    } catch (error) {
      console.error('Error approving plan:', error);
    }
  };

  const getStressColor = (level: string) => {
    switch (level) {
      case 'critical': return 'red';
      case 'high': return 'orange';
      case 'moderate': return 'yellow';
      default: return 'green';
    }
  };

  // Prepare chart data
  const chartData = forecast?.load_forecast_mw?.map((load: number, idx: number) => ({
    hour: idx,
    load
  })) || [];

  return (
    <div className="min-h-screen p-6">
      <div className="max-w-7xl mx-auto">
        {/* Navigation */}
        <div className="mb-8 bg-white p-4 rounded-lg shadow">
          <div className="flex flex-wrap gap-3">
            <Button className="bg-blue-600 text-white">📊 DR Planning</Button>
            <a href="/der">
              <Button className="bg-green-600 text-white">⚡ DER Management</Button>
            </a>
            <a href="/verification">
              <Button className="bg-gray-200 text-gray-800">✅ API Verification</Button>
            </a>
          </div>
        </div>

        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Utility HITL Portal</h1>
          <p className="text-gray-600">Texas Grid Demand Response Coordination</p>
          <p className="text-sm text-gray-500 mt-1">
            Last updated: {lastUpdate || 'Loading...'} | Auto-refresh: 5s |
            {ercotData?.error ? (
              <span className="ml-2 text-red-600">● NO DATA - ERCOT API UNAVAILABLE</span>
            ) : ercotData?.data_source === 'ercot_dashboard_live' ? (
              <span className="ml-2 text-green-600">● LIVE ERCOT DATA</span>
            ) : (
              <span className="ml-2 text-yellow-600">● LIMITED DATA</span>
            )}
          </p>
        </div>

        {/* Situation Overview */}
        <Grid numItemsMd={4} className="gap-4 mb-6">
          <Card decoration="top" decorationColor={ercotData?.system_load_mw > 70000 ? 'red' : 'green'}>
            <div className="flex items-start justify-between">
              <div>
                <Text>System Load</Text>
                <Metric>{ercotData?.system_load_mw ? `${(ercotData.system_load_mw / 1000).toFixed(1)} GW` : 'N/A'}</Metric>
              </div>
              <Activity className="h-8 w-8 text-gray-400" />
            </div>
            <ProgressBar value={(ercotData?.system_load_mw || 0) / 850} className="mt-2" />
          </Card>

          <Card decoration="top" decorationColor="blue">
            <div className="flex items-start justify-between">
              <div>
                <Text>Price</Text>
                <Metric>{ercotData?.price_per_mwh ? `$${ercotData.price_per_mwh.toFixed(2)}/MWh` : 'N/A'}</Metric>
              </div>
              <Zap className="h-8 w-8 text-gray-400" />
            </div>
            <Text className="mt-2">Reserves: {ercotData?.reserves_mw ? `${(ercotData.reserves_mw / 1000).toFixed(1)} GW` : 'N/A'}</Text>
          </Card>

          <Card decoration="top" decorationColor="yellow">
            <div className="flex items-start justify-between">
              <div>
                <Text>Temperature</Text>
                <Metric>{weather?.temperature_f?.toFixed(0) || '--'}°F</Metric>
              </div>
              <CloudSun className="h-8 w-8 text-gray-400" />
            </div>
            <Text className="mt-2">{weather?.conditions || '--'}</Text>
          </Card>

          <Card decoration="top" decorationColor="purple">
            <div className="flex items-start justify-between">
              <div>
                <Text>Peak Forecast</Text>
                <Metric>{forecast?.peak_load_mw ? `${(forecast.peak_load_mw / 1000).toFixed(1)} GW` : 'N/A'}</Metric>
              </div>
              <AlertCircle className="h-8 w-8 text-gray-400" />
            </div>
            <Text className="mt-2">{forecast?.peak_hour ? `Hour ${forecast.peak_hour}` : 'No forecast'}</Text>
          </Card>
        </Grid>

        {/* Load Forecast Chart */}
        <Card className="mb-6">
          <Title>24-Hour Load Forecast</Title>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hour" />
              <YAxis orientation="left" />
              <Tooltip />
              <Area type="monotone" dataKey="load" stroke="#3b82f6" fill="#93c5fd" />
            </AreaChart>
          </ResponsiveContainer>
        </Card>

        {/* Cohorts Table */}
        <Card className="mb-6">
          <Title>Customer Cohorts</Title>
          <div className="mt-4 overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Select</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Cohort</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Accounts</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Flex MW</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Acceptance</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Segment</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {cohorts.map(cohort => (
                  <tr key={cohort.id} className="hover:bg-gray-50">
                    <td className="px-4 py-2">
                      <input
                        type="checkbox"
                        checked={selectedCohorts.includes(cohort.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedCohorts([...selectedCohorts, cohort.id]);
                          } else {
                            setSelectedCohorts(selectedCohorts.filter(id => id !== cohort.id));
                          }
                        }}
                        className="h-4 w-4 text-blue-600"
                      />
                    </td>
                    <td className="px-4 py-2 text-sm font-medium text-gray-900">{cohort.name}</td>
                    <td className="px-4 py-2 text-sm text-gray-500">{cohort.num_accounts.toLocaleString()}</td>
                    <td className="px-4 py-2 text-sm text-gray-500">
                      {((cohort.num_accounts * cohort.flex_kw_per_account) / 1000).toFixed(1)}
                    </td>
                    <td className="px-4 py-2">
                      <Badge color={cohort.baseline_acceptance_rate > 0.6 ? 'green' : 'yellow'}>
                        {(cohort.baseline_acceptance_rate * 100).toFixed(0)}%
                      </Badge>
                    </td>
                    <td className="px-4 py-2 text-sm text-gray-500">{cohort.segment}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        {/* DR Plan Composer */}
        <Card className="mb-6">
          <Title>DR Plan Composer</Title>
          <div className="mt-4 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Strategy</label>
              <select
                value={strategy}
                onChange={(e) => setStrategy(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                <option value="balanced">Balanced</option>
                <option value="cost_minimize">Cost Minimize</option>
                <option value="reliability">Reliability</option>
                <option value="emergency">Emergency</option>
              </select>
            </div>

            <div className="flex flex-wrap gap-3">
              <Button
                onClick={proposePlan}
                disabled={loading}
                className="bg-blue-600 text-white px-4 py-2 rounded"
              >
                {loading ? 'Generating...' : 'Generate Plan'}
              </Button>
            </div>
          </div>
        </Card>

        {/* Proposed Plan */}
        {proposedPlan && (
          <Card className="mb-6 border-2 border-blue-500">
            <div className="flex justify-between items-start mb-4">
              <div>
                <Title>Proposed DR Plan</Title>
                <Badge color={getStressColor(proposedPlan.situation_summary?.stress_level)}>
                  {proposedPlan.situation_summary?.stress_level} stress
                </Badge>
              </div>
              <div className="flex gap-2">
                <Button
                  onClick={approvePlan}
                  className="bg-green-600 text-white px-4 py-2 rounded flex items-center gap-2"
                >
                  <Send className="h-4 w-4" />
                  Approve & Send
                </Button>
                <Button
                  onClick={() => setProposedPlan(null)}
                  className="bg-red-600 text-white px-4 py-2 rounded"
                >
                  Reject
                </Button>
              </div>
            </div>

            <Grid numItemsMd={3} className="gap-4 mb-4">
              <Card>
                <Text>Target MW</Text>
                <Metric>{proposedPlan.target_mw_total.toFixed(1)} MW</Metric>
              </Card>
              <Card>
                <Text>Predicted MW</Text>
                <Metric>{proposedPlan.predicted_mw_total.toFixed(1)} MW</Metric>
              </Card>
              <Card>
                <Text>Confidence</Text>
                <Metric>{(proposedPlan.confidence_score * 100).toFixed(0)}%</Metric>
              </Card>
            </Grid>

            <div className="mt-4">
              <Text className="font-medium mb-2">Explanation:</Text>
              <pre className="text-sm text-gray-600 whitespace-pre-wrap">{proposedPlan.explanation}</pre>
            </div>

            <div className="mt-4">
              <Text className="font-medium mb-2">Cohort Allocations:</Text>
              <div className="space-y-2">
                {proposedPlan.cohort_allocations.map((allocation: any) => (
                  <div key={allocation.cohort_id} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                    <Text>{allocation.cohort_name}</Text>
                    <div className="flex flex-wrap gap-3">
                      <Badge>{allocation.target_mw.toFixed(1)} MW target</Badge>
                      <Badge color="green">{(allocation.acceptance_probability * 100).toFixed(0)}% likely</Badge>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}
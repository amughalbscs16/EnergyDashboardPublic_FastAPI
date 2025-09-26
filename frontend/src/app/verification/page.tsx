'use client';

import React, { useState, useEffect } from 'react';
import { Card, Title, Text, Badge, Grid, Button, ProgressBar } from '@tremor/react';
import { CheckCircle, XCircle, AlertCircle, RefreshCw, Globe, Database, Zap } from 'lucide-react';
import axios from 'axios';
import Link from 'next/link';

const API_BASE = 'http://localhost:8002/api';

interface ApiCheck {
  name: string;
  endpoint: string;
  status: 'checking' | 'success' | 'error' | 'pending';
  responseTime?: number;
  dataSource?: string;
  message?: string;
  data?: any;
}

export default function VerificationDashboard() {
  const [apiChecks, setApiChecks] = useState<ApiCheck[]>([
    { name: 'ERCOT Current Load', endpoint: '/ercot/current', status: 'pending' },
    { name: 'ERCOT Forecast', endpoint: '/ercot/forecast', status: 'pending' },
    { name: 'ERCOT Real-Time Prices', endpoint: '/ercot/real-time-prices', status: 'pending' },
    { name: 'Weather Data (Austin)', endpoint: '/weather/78701', status: 'pending' },
    { name: 'Weather Alerts (Texas)', endpoint: '/weather/alerts/TX', status: 'pending' },
    { name: 'Customer Cohorts', endpoint: '/cohorts/', status: 'pending' },
    { name: 'Plan Generation', endpoint: '/plans/propose', status: 'pending' },
  ]);

  const [isChecking, setIsChecking] = useState(false);
  const [summary, setSummary] = useState<any>(null);

  const runVerification = async () => {
    setIsChecking(true);
    const results = [...apiChecks];

    for (let i = 0; i < results.length; i++) {
      results[i].status = 'checking';
      setApiChecks([...results]);

      const startTime = Date.now();

      try {
        let response;
        const check = results[i];

        // Different request types for different endpoints
        if (check.endpoint.includes('propose')) {
          response = await axios.post(`${API_BASE}${check.endpoint}`, {
            window_start: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
            window_end: new Date(Date.now() + 26 * 60 * 60 * 1000).toISOString(),
            strategy: 'balanced',
            operator_id: 'test_operator'
          });
        } else {
          response = await axios.get(`${API_BASE}${check.endpoint}`);
        }

        results[i] = {
          ...results[i],
          status: 'success',
          responseTime: Date.now() - startTime,
          dataSource: response.data.data_source || 'api',
          data: response.data
        };
      } catch (error: any) {
        results[i] = {
          ...results[i],
          status: 'error',
          responseTime: Date.now() - startTime,
          message: error.message
        };
      }

      setApiChecks([...results]);
    }

    // Calculate summary
    const successCount = results.filter(r => r.status === 'success').length;
    const errorCount = results.filter(r => r.status === 'error').length;
    const avgResponseTime = results.reduce((acc, r) => acc + (r.responseTime || 0), 0) / results.length;

    // Check data sources
    const ercotData = results.find(r => r.name.includes('ERCOT'))?.data;
    const weatherData = results.find(r => r.name.includes('Weather'))?.data;

    setSummary({
      totalChecks: results.length,
      successful: successCount,
      failed: errorCount,
      avgResponseTime: avgResponseTime.toFixed(0),
      ercotSource: ercotData?.data_source || 'unknown',
      weatherSource: weatherData?.data_source || 'unknown',
      timestamp: new Date().toLocaleString()
    });

    setIsChecking(false);
  };

  useEffect(() => {
    runVerification();
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'error':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'checking':
        return <RefreshCw className="h-5 w-5 text-blue-500 animate-spin" />;
      default:
        return <AlertCircle className="h-5 w-5 text-gray-400" />;
    }
  };

  const getDataSourceBadge = (source: string) => {
    if (!source) return null;

    const colors: any = {
      'synthetic': 'yellow',
      'nws': 'blue',
      'openweather': 'green',
      'ercot': 'purple',
      'api': 'gray'
    };

    return <Badge color={colors[source] || 'gray'}>{source.toUpperCase()}</Badge>;
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Navigation */}
        <div className="mb-8 bg-white p-4 rounded-lg shadow">
          <div className="flex gap-4">
            <Link href="/">
              <Button variant="secondary">DR Planning</Button>
            </Link>
            <Link href="/verification">
              <Button variant="primary">API Verification</Button>
            </Link>
          </div>
        </div>

        <div className="mb-8 flex justify-between items-center">
          <div>
            <Title>System Verification Dashboard</Title>
            <Text>Real-time API health and data source verification</Text>
          </div>
          <Button onClick={runVerification} disabled={isChecking} icon={RefreshCw}>
            {isChecking ? 'Verifying...' : 'Run Verification'}
          </Button>
        </div>

        {/* Summary Cards */}
        {summary && (
          <Grid numItemsMd={3} className="gap-4 mb-8">
            <Card>
              <div className="flex items-center gap-2">
                <Zap className="h-5 w-5 text-blue-500" />
                <Text>System Health</Text>
              </div>
              <div className="mt-2">
                <div className="flex items-baseline gap-2">
                  <Text className="text-3xl font-bold text-green-600">
                    {summary.successful}
                  </Text>
                  <Text className="text-gray-500">/ {summary.totalChecks}</Text>
                </div>
                <ProgressBar
                  value={(summary.successful / summary.totalChecks) * 100}
                  color={summary.successful === summary.totalChecks ? 'green' : 'yellow'}
                  className="mt-2"
                />
              </div>
            </Card>

            <Card>
              <div className="flex items-center gap-2">
                <Globe className="h-5 w-5 text-purple-500" />
                <Text>Data Sources</Text>
              </div>
              <div className="mt-4 space-y-2">
                <div className="flex justify-between">
                  <Text>ERCOT:</Text>
                  {getDataSourceBadge(summary.ercotSource)}
                </div>
                <div className="flex justify-between">
                  <Text>Weather:</Text>
                  {getDataSourceBadge(summary.weatherSource)}
                </div>
              </div>
            </Card>

            <Card>
              <div className="flex items-center gap-2">
                <Database className="h-5 w-5 text-green-500" />
                <Text>Performance</Text>
              </div>
              <div className="mt-4">
                <Text className="text-3xl font-bold">{summary.avgResponseTime}ms</Text>
                <Text className="text-gray-500">Avg Response Time</Text>
                <Text className="text-xs text-gray-400 mt-2">
                  Last check: {summary.timestamp}
                </Text>
              </div>
            </Card>
          </Grid>
        )}

        {/* API Checks Table */}
        <Card>
          <Title>API Endpoints Status</Title>
          <div className="mt-4 space-y-2">
            {apiChecks.map((check, index) => (
              <div key={index} className="p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {getStatusIcon(check.status)}
                    <div>
                      <Text className="font-semibold">{check.name}</Text>
                      <Text className="text-sm text-gray-500">{API_BASE}{check.endpoint}</Text>
                    </div>
                  </div>

                  <div className="flex items-center gap-4">
                    {check.dataSource && getDataSourceBadge(check.dataSource)}
                    {check.responseTime && (
                      <Badge color={check.responseTime < 200 ? 'green' : check.responseTime < 500 ? 'yellow' : 'red'}>
                        {check.responseTime}ms
                      </Badge>
                    )}
                    <Badge color={check.status === 'success' ? 'green' : check.status === 'error' ? 'red' : 'gray'}>
                      {check.status}
                    </Badge>
                  </div>
                </div>

                {check.message && (
                  <div className="mt-2 p-2 bg-red-50 rounded">
                    <Text className="text-red-600 text-sm">{check.message}</Text>
                  </div>
                )}

                {check.status === 'success' && check.data && (
                  <div className="mt-2 p-2 bg-green-50 rounded">
                    <details>
                      <summary className="cursor-pointer text-sm text-green-700">
                        View Response Data
                      </summary>
                      <pre className="mt-2 text-xs overflow-x-auto">
                        {JSON.stringify(check.data, null, 2).substring(0, 500)}...
                      </pre>
                    </details>
                  </div>
                )}
              </div>
            ))}
          </div>
        </Card>

        {/* Data Source Information */}
        <Card className="mt-6">
          <Title>Data Source Information</Title>
          <div className="mt-4 space-y-4">
            <div>
              <Text className="font-semibold mb-2">ERCOT Data:</Text>
              <div className="space-y-1">
                <Text className="text-sm">• <Badge color="purple">ERCOT API</Badge> - Live data (requires API key in .env)</Text>
                <Text className="text-sm">• Configure ERCOT_PUBLIC_API_KEY and ERCOT_ESR_API_KEY</Text>
              </div>
            </div>

            <div>
              <Text className="font-semibold mb-2">Weather Data:</Text>
              <div className="space-y-1">
                <Text className="text-sm">• <Badge color="blue">NWS API</Badge> - National Weather Service (FREE, no key required)</Text>
                <Text className="text-sm">• Real-time weather data for Texas cities</Text>
                <Text className="text-sm">• Live weather alerts for Texas</Text>
              </div>
            </div>

            <div className="mt-4 p-3 bg-blue-50 rounded">
              <Text className="text-sm">
                <strong>Note:</strong> This system uses ONLY real data sources. NWS weather data is live and free.
                ERCOT data requires valid API keys configured in the .env file.
              </Text>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
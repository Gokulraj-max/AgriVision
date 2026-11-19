import React from 'react';
import { Tabs } from 'expo-router';
import { Text } from 'react-native';

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        headerStyle: {
          backgroundColor: '#15803d',
        },
        headerTintColor: '#ffffff',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
        tabBarActiveTintColor: '#15803d',
        tabBarInactiveTintColor: '#6b7280',
        tabBarStyle: {
          backgroundColor: '#ffffff',
          borderTopColor: '#e5e7eb',
          height: 60,
          paddingBottom: 8,
          paddingTop: 6,
        },
        tabBarLabelStyle: {
          fontSize: 11,
          fontWeight: '600',
        },
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: 'Home',
          headerTitle: '🌾 AgriVision AI 2.0',
          tabBarIcon: ({ color }) => (
            <Text style={{ fontSize: 20, color }}>🏠</Text>
          ),
        }}
      />
      <Tabs.Screen
        name="scanner"
        options={{
          title: 'Live Scan',
          headerTitle: '📷 Live AI Crop Scanner',
          tabBarIcon: ({ color }) => (
            <Text style={{ fontSize: 22, color }}>🔍</Text>
          ),
        }}
      />
      <Tabs.Screen
        name="weather"
        options={{
          title: 'Weather & Risk',
          headerTitle: '🌦️ Microclimate Risk',
          tabBarIcon: ({ color }) => (
            <Text style={{ fontSize: 20, color }}>🌤️</Text>
          ),
        }}
      />
      <Tabs.Screen
        name="farms"
        options={{
          title: 'My Farms',
          headerTitle: '🚜 Farm Management',
          tabBarIcon: ({ color }) => (
            <Text style={{ fontSize: 20, color }}>🌾</Text>
          ),
        }}
      />
      <Tabs.Screen
        name="assistant"
        options={{
          title: 'Assistant',
          headerTitle: '🤖 Agri Assistant (தமிழ் / EN)',
          tabBarIcon: ({ color }) => (
            <Text style={{ fontSize: 20, color }}>💬</Text>
          ),
        }}
      />
    </Tabs>
  );
}

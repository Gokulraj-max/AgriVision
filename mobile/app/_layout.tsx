import React, { useEffect } from 'react';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { initOfflineDatabase } from '../src/database/sqlite';

export default function RootLayout() {
  useEffect(() => {
    initOfflineDatabase();
  }, []);

  return (
    <SafeAreaProvider>
      <StatusBar style="light" backgroundColor="#15803d" />
      <Stack
        screenOptions={{
          headerStyle: {
            backgroundColor: '#15803d',
          },
          headerTintColor: '#ffffff',
          headerTitleStyle: {
            fontWeight: 'bold',
          },
        }}
      >
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        <Stack.Screen name="(auth)/login" options={{ title: 'Farmer Sign In' }} />
        <Stack.Screen name="(auth)/register" options={{ title: 'Register Account' }} />
        <Stack.Screen 
          name="inspection/[id]" 
          options={{ 
            title: 'Diagnostic Report',
            headerBackTitle: 'Back'
          }} 
        />
      </Stack>
    </SafeAreaProvider>
  );
}

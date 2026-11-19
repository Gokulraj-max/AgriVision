import React, { useState } from 'react';
import { 
  View, 
  Text, 
  TextInput, 
  TouchableOpacity, 
  StyleSheet, 
  ActivityIndicator, 
  Alert,
  KeyboardAvoidingView,
  Platform,
  ScrollView
} from 'react-native';
import { useRouter } from 'expo-router';
import { api } from '../../src/services/api';

export default function LoginScreen() {
  const router = useRouter();
  const [phoneOrEmail, setPhoneOrEmail] = useState('farmer@agrivision.ai');
  const [password, setPassword] = useState('farmer123');
  const [language, setLanguage] = useState<'en' | 'ta'>('en');
  const [loading, setLoading] = useState(false);

  const isTamil = language === 'ta';

  const handleLogin = async () => {
    if (!phoneOrEmail || !password) {
      Alert.alert(
        isTamil ? 'பிழை' : 'Validation Error',
        isTamil ? 'மின்னஞ்சல் அல்லது கடவுச்சொல்லை உள்ளிடவும்' : 'Please provide credentials'
      );
      return;
    }

    setLoading(true);
    try {
      await api.login(phoneOrEmail, password);
      router.replace('/(tabs)');
    } catch (err: any) {
      Alert.alert(
        isTamil ? 'உள்நுழைவு தோல்வி' : 'Login Failed',
        err.message || 'Check connection or demo credentials'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView 
      style={styles.container} 
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <ScrollView contentContainerStyle={styles.scroll}>
        <View style={styles.header}>
          <Text style={styles.brandTitle}>🌱 AgriVision AI 2.0</Text>
          <Text style={styles.brandSubtitle}>
            {isTamil ? 'ஸ்மார்ட் விவசாயம் மற்றும் பயிர் நோய் கண்டறிதல்' : 'Smart Agriculture & Live Disease Detection'}
          </Text>
        </View>

        {/* Language Toggle */}
        <View style={styles.langContainer}>
          <TouchableOpacity 
            style={[styles.langBtn, language === 'en' && styles.langBtnActive]}
            onPress={() => setLanguage('en')}
          >
            <Text style={[styles.langText, language === 'en' && styles.langTextActive]}>English</Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={[styles.langBtn, language === 'ta' && styles.langBtnActive]}
            onPress={() => setLanguage('ta')}
          >
            <Text style={[styles.langText, language === 'ta' && styles.langTextActive]}>தமிழ் (Tamil)</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.card}>
          <Text style={styles.label}>
            {isTamil ? 'மின்னஞ்சல் அல்லது தொலைபேசி' : 'Email or Mobile Number'}
          </Text>
          <TextInput
            style={styles.input}
            value={phoneOrEmail}
            onChangeText={setPhoneOrEmail}
            placeholder="e.g. farmer@agrivision.ai"
            autoCapitalize="none"
          />

          <Text style={styles.label}>
            {isTamil ? 'கடவுச்சொல்' : 'Password'}
          </Text>
          <TextInput
            style={styles.input}
            value={password}
            onChangeText={setPassword}
            placeholder="••••••••"
            secureTextEntry
          />

          <TouchableOpacity 
            style={styles.submitBtn} 
            onPress={handleLogin}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.submitBtnText}>
                {isTamil ? 'உள்நுழைக' : 'Sign In'}
              </Text>
            )}
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.demoBtn} 
            onPress={() => router.replace('/(tabs)')}
          >
            <Text style={styles.demoBtnText}>
              {isTamil ? 'டெமோ பயன்முறையில் தொடரவும் ➔' : 'Continue as Demo Farmer ➔'}
            </Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f0fdf4',
  },
  scroll: {
    padding: 24,
    justifyContent: 'center',
    flexGrow: 1,
  },
  header: {
    alignItems: 'center',
    marginBottom: 24,
  },
  brandTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#166534',
  },
  brandSubtitle: {
    fontSize: 14,
    color: '#4b5563',
    marginTop: 6,
    textAlign: 'center',
  },
  langContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginBottom: 20,
  },
  langBtn: {
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 20,
    backgroundColor: '#e5e7eb',
    marginHorizontal: 6,
  },
  langBtnActive: {
    backgroundColor: '#16a34a',
  },
  langText: {
    fontSize: 13,
    color: '#374151',
    fontWeight: '600',
  },
  langTextActive: {
    color: '#ffffff',
  },
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 16,
    padding: 20,
    elevation: 3,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowOffset: { width: 0, height: 2 },
    shadowRadius: 6,
  },
  label: {
    fontSize: 13,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 6,
    marginTop: 10,
  },
  input: {
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 8,
    padding: 12,
    fontSize: 15,
    backgroundColor: '#f9fafb',
  },
  submitBtn: {
    backgroundColor: '#16a34a',
    borderRadius: 8,
    paddingVertical: 14,
    alignItems: 'center',
    marginTop: 20,
  },
  submitBtnText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  demoBtn: {
    alignItems: 'center',
    marginTop: 16,
    paddingVertical: 8,
  },
  demoBtnText: {
    color: '#15803d',
    fontSize: 14,
    fontWeight: '600',
  },
});

import React, { useState, useRef, useEffect } from 'react';
import { 
  View, 
  Text, 
  ScrollView, 
  TextInput, 
  TouchableOpacity, 
  StyleSheet, 
  ActivityIndicator, 
  KeyboardAvoidingView, 
  Platform,
  Alert 
} from 'react-native';
import { api } from '../../src/services/api';
import { AssistantMessage } from '../../src/types';

export default function AssistantScreen() {
  const [messages, setMessages] = useState<AssistantMessage[]>([
    {
      id: 'welcome',
      sender: 'assistant',
      text: 'வணக்கம்! நான் அக்ரிவிஷன் AI வேளாண்மை உதவியாளர். தக்காளி, உருளைக்கிழங்கு, நெல், பருத்தி, மக்காச்சோளம் பயிர்களின் நோய்கள் மற்றும் மேலாண்மை குறித்து என்னிடம் கேட்கலாம்.\n\nHello! I am AgriVision AI Assistant. Ask me anything about crop diseases, organic remedies, or weather risks.',
      language: 'ta',
      timestamp: new Date().toLocaleTimeString(),
      suggestions: [
        'தக்காளியில் ஆரம்பகால கருகல் நோய் கட்டுப்பாடு?',
        'நெல் பயிரில் குலை நோய் (Blast) அறிகுறிகள்?',
        'Organic treatment for potato late blight?',
        'Cotton leaf curl virus prevention?'
      ]
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [language, setLanguage] = useState<'ta' | 'en'>('ta');
  const [loading, setLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const scrollViewRef = useRef<ScrollView>(null);

  useEffect(() => {
    scrollViewRef.current?.scrollToEnd({ animated: true });
  }, [messages]);

  const handleSend = async (textToSend?: string) => {
    const query = textToSend || inputText;
    if (!query.trim()) return;

    const userMsg: AssistantMessage = {
      id: `usr_${Date.now()}`,
      sender: 'user',
      text: query,
      language: language,
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!textToSend) setInputText('');
    setLoading(true);

    try {
      const response = await api.askAssistant(query, language);
      const assistantMsg: AssistantMessage = {
        id: `ast_${Date.now()}`,
        sender: 'assistant',
        text: response.reply,
        language: (response.language as 'ta' | 'en') || language,
        audio_url: response.audio_url,
        timestamp: new Date().toLocaleTimeString(),
        suggestions: response.suggested_actions
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      const errorMsg: AssistantMessage = {
        id: `err_${Date.now()}`,
        sender: 'assistant',
        text: language === 'ta' 
          ? 'மன்னிக்கவும், தகவல் தொடர்பில் பிழை ஏற்பட்டது. மீண்டும் முயற்சிக்கவும்.'
          : 'Service temporarily unavailable. Please check your network.',
        language: language,
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleMicPress = () => {
    if (isRecording) {
      setIsRecording(false);
      // Simulated voice transcribed query
      const voiceQuery = language === 'ta' 
        ? 'தக்காளியில் இலைக்கருகல் நோயை எவ்வாறு தடுப்பது?'
        : 'How to prevent Early Blight in tomato crop?';
      handleSend(voiceQuery);
    } else {
      setIsRecording(true);
      Alert.alert(
        language === 'ta' ? 'குரல் உள்ளீடு' : 'Voice Input Active',
        language === 'ta' ? 'பேசுங்கள்... பதிவு செய்யப்படுகிறது.' : 'Listening... Speak your crop question.'
      );
      setTimeout(() => {
        setIsRecording(false);
        const voiceQuery = language === 'ta' 
          ? 'தக்காளியில் இலைக்கருகல் நோயை எவ்வாறு தடுப்பது?'
          : 'How to prevent Early Blight in tomato crop?';
        handleSend(voiceQuery);
      }, 2000);
    }
  };

  const handlePlayAudio = (msg: AssistantMessage) => {
    Alert.alert(
      msg.language === 'ta' ? 'குரல் வழிகாட்டுதல்' : 'Audio Readout',
      msg.language === 'ta' ? 'வேளாண் ஆலோசனை தமிழில் ஒலிக்கப்படுகிறது...' : 'Playing agronomic advisory...'
    );
  };

  return (
    <KeyboardAvoidingView 
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={80}
    >
      {/* Top Language Toggle Bar */}
      <View style={styles.topLangBar}>
        <Text style={styles.langBarTitle}>Language / மொழி:</Text>
        <View style={styles.langPills}>
          <TouchableOpacity 
            style={[styles.langPill, language === 'ta' && styles.langPillActive]}
            onPress={() => setLanguage('ta')}
          >
            <Text style={[styles.langPillText, language === 'ta' && styles.langPillTextActive]}>
              தமிழ் (Tamil)
            </Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={[styles.langPill, language === 'en' && styles.langPillActive]}
            onPress={() => setLanguage('en')}
          >
            <Text style={[styles.langPillText, language === 'en' && styles.langPillTextActive]}>
              English
            </Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Messages Scroll Area */}
      <ScrollView 
        ref={scrollViewRef}
        style={styles.messageScroll}
        contentContainerStyle={styles.scrollContent}
      >
        {messages.map((m) => (
          <View 
            key={m.id} 
            style={[
              styles.msgWrapper,
              m.sender === 'user' ? styles.msgWrapperUser : styles.msgWrapperAssistant
            ]}
          >
            <View 
              style={[
                styles.bubble,
                m.sender === 'user' ? styles.bubbleUser : styles.bubbleAssistant
              ]}
            >
              <View style={styles.bubbleHeader}>
                <Text style={styles.senderLabel}>
                  {m.sender === 'user' ? '👨‍🌾 You' : '🌱 AgriVision AI'}
                </Text>
                <Text style={styles.timeLabel}>{m.timestamp}</Text>
              </View>

              <Text style={[
                styles.msgText,
                m.sender === 'user' ? styles.msgTextUser : styles.msgTextAssistant
              ]}>
                {m.text}
              </Text>

              {m.sender === 'assistant' && (
                <TouchableOpacity 
                  style={styles.audioPlayBtn}
                  onPress={() => handlePlayAudio(m)}
                >
                  <Text style={styles.audioPlayText}>🔊 Listen Audio ({m.language === 'ta' ? 'தமிழ்' : 'EN'})</Text>
                </TouchableOpacity>
              )}
            </View>

            {/* Quick Suggestion Pills */}
            {m.suggestions && m.suggestions.length > 0 && (
              <View style={styles.suggestionRow}>
                {m.suggestions.map((s, idx) => (
                  <TouchableOpacity 
                    key={idx}
                    style={styles.suggestPill}
                    onPress={() => handleSend(s)}
                  >
                    <Text style={styles.suggestPillText}>💡 {s}</Text>
                  </TouchableOpacity>
                ))}
              </View>
            )}
          </View>
        ))}

        {loading && (
          <View style={styles.loadingBubble}>
            <ActivityIndicator size="small" color="#15803d" />
            <Text style={styles.loadingText}>
              {language === 'ta' ? 'விடை தேடுகிறது...' : 'Searching agronomic database...'}
            </Text>
          </View>
        )}
      </ScrollView>

      {/* Bottom Input Area */}
      <View style={styles.inputContainer}>
        <TouchableOpacity 
          style={[styles.micBtn, isRecording && styles.micBtnActive]}
          onPress={handleMicPress}
        >
          <Text style={{ fontSize: 20 }}>{isRecording ? '🔴' : '🎙️'}</Text>
        </TouchableOpacity>

        <TextInput
          style={styles.textInput}
          value={inputText}
          onChangeText={setInputText}
          placeholder={language === 'ta' ? 'பயிர் நோய்கள் பற்றி கேளுங்கள்...' : 'Ask about crop health, treatments...'}
          multiline
        />

        <TouchableOpacity 
          style={styles.sendBtn}
          onPress={() => handleSend()}
          disabled={loading || !inputText.trim()}
        >
          <Text style={styles.sendBtnText}>➔</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  topLangBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 10,
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#e2e8f0',
  },
  langBarTitle: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#475569',
  },
  langPills: {
    flexDirection: 'row',
  },
  langPill: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 14,
    backgroundColor: '#f1f5f9',
    marginLeft: 6,
  },
  langPillActive: {
    backgroundColor: '#15803d',
  },
  langPillText: {
    fontSize: 12,
    color: '#64748b',
    fontWeight: '600',
  },
  langPillTextActive: {
    color: '#ffffff',
  },
  messageScroll: {
    flex: 1,
  },
  scrollContent: {
    padding: 16,
    paddingBottom: 24,
  },
  msgWrapper: {
    marginBottom: 16,
    maxWidth: '85%',
  },
  msgWrapperUser: {
    alignSelf: 'flex-end',
  },
  msgWrapperAssistant: {
    alignSelf: 'flex-start',
  },
  bubble: {
    borderRadius: 16,
    padding: 14,
    elevation: 1,
  },
  bubbleUser: {
    backgroundColor: '#15803d',
    borderBottomRightRadius: 4,
  },
  bubbleAssistant: {
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: '#e2e8f0',
    borderBottomLeftRadius: 4,
  },
  bubbleHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 6,
  },
  senderLabel: {
    fontSize: 11,
    fontWeight: 'bold',
    color: '#94a3b8',
  },
  timeLabel: {
    fontSize: 10,
    color: '#94a3b8',
  },
  msgText: {
    fontSize: 14,
    lineHeight: 20,
  },
  msgTextUser: {
    color: '#ffffff',
  },
  msgTextAssistant: {
    color: '#1e293b',
  },
  audioPlayBtn: {
    marginTop: 10,
    backgroundColor: '#f0fdf4',
    borderWidth: 1,
    borderColor: '#bbf7d0',
    borderRadius: 8,
    paddingVertical: 5,
    paddingHorizontal: 10,
    alignSelf: 'flex-start',
  },
  audioPlayText: {
    color: '#15803d',
    fontSize: 11,
    fontWeight: 'bold',
  },
  suggestionRow: {
    marginTop: 8,
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  suggestPill: {
    backgroundColor: '#e2e8f0',
    borderRadius: 12,
    paddingHorizontal: 10,
    paddingVertical: 5,
    marginRight: 6,
    marginBottom: 6,
  },
  suggestPillText: {
    fontSize: 11,
    color: '#334155',
    fontWeight: '500',
  },
  loadingBubble: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    backgroundColor: '#ffffff',
    borderRadius: 12,
    alignSelf: 'flex-start',
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  loadingText: {
    marginLeft: 8,
    fontSize: 12,
    color: '#64748b',
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 10,
    backgroundColor: '#ffffff',
    borderTopWidth: 1,
    borderTopColor: '#e2e8f0',
  },
  micBtn: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#f1f5f9',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 8,
  },
  micBtnActive: {
    backgroundColor: '#fee2e2',
  },
  textInput: {
    flex: 1,
    backgroundColor: '#f8fafc',
    borderWidth: 1,
    borderColor: '#cbd5e1',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 8,
    fontSize: 14,
    maxHeight: 90,
  },
  sendBtn: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#15803d',
    alignItems: 'center',
    justifyContent: 'center',
    marginLeft: 8,
  },
  sendBtnText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: 'bold',
  },
});

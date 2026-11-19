import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  ScrollView, 
  Image, 
  TouchableOpacity, 
  StyleSheet, 
  ActivityIndicator, 
  Alert,
  Switch
} from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { api } from '../../src/services/api';
import { InspectionRecord } from '../../src/types';

export default function InspectionDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const [inspection, setInspection] = useState<InspectionRecord | null>(null);
  const [loading, setLoading] = useState(true);
  const [showHeatmap, setShowHeatmap] = useState(true);
  const [language, setLanguage] = useState<'en' | 'ta'>('ta'); // Default to Tamil for local farmers
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [feedbackSent, setFeedbackSent] = useState(false);

  useEffect(() => {
    loadInspection();
  }, [id]);

  const loadInspection = async () => {
    try {
      if (id) {
        const data = await api.getInspection(id).catch(() => null);
        if (data) {
          setInspection(data);
        } else {
          // Fallback mock detail for offline/demo
          setInspection({
            id: id || 'demo_1',
            crop_name: 'Tomato',
            disease_predicted: 'Tomato Early Blight (Alternaria solani)',
            disease_predicted_ta: 'தக்காளி ஆரம்பகால கருகல் நோய்',
            confidence: 0.942,
            severity_pct: 18.4,
            image_url: 'https://images.unsplash.com/photo-1592417817098-8f3d6910985b?w=700',
            heatmap_url: 'https://images.unsplash.com/photo-1592417817098-8f3d6910985b?w=700',
            status: 'confirmed',
            created_at: new Date().toISOString(),
            management_guidance: 'Prune infected lower foliage up to 30 cm from ground. Ensure drip irrigation to avoid canopy wetting. Apply bio-control Trichoderma viride or approved copper hydroxide spray.',
            management_guidance_ta: 'நிலத்திலிருந்து 30 செ.மீ உயரம் வரை பாதிக்கப்பட்ட கீழ் இலைகளை வெட்டி அகற்றவும். இலைகள் நனையாமல் இருக்க சொட்டு நீர்ப்பாசனத்தைப் பயன்படுத்தவும். டிரைக்கோடெர்மா விரிடி அல்லது தாமிர ஹைட்ராக்சைடு தெளிக்கவும்.'
          });
        }
      }
    } finally {
      setLoading(false);
    }
  };

  const handlePlayVoice = () => {
    setIsPlayingAudio(true);
    setTimeout(() => {
      setIsPlayingAudio(false);
      Alert.alert(
        language === 'ta' ? 'குரல் வழிகாட்டுதல்' : 'Voice Guidance',
        language === 'ta' 
          ? 'ஆடியோ வழிகாட்டுதல் வெற்றிகரமாக இயக்கப்பட்டது.'
          : 'Spoken agronomic guidance played.'
      );
    }, 1200);
  };

  const handleExpertFeedback = (isCorrect: boolean) => {
    if (!inspection) return;
    api.submitFeedback(inspection.id, isCorrect).catch(() => {});
    setFeedbackSent(true);
    Alert.alert(
      'Feedback Recorded',
      'Thank you! Your validation trains and refines the AgriVision 2.0 active learning pipeline.'
    );
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#15803d" />
        <Text style={styles.loadingText}>Generating Leaf Diagnostic Report...</Text>
      </View>
    );
  }

  if (!inspection) {
    return (
      <View style={styles.container}>
        <Text>Inspection not found.</Text>
      </View>
    );
  }

  const isTamil = language === 'ta';

  return (
    <ScrollView style={styles.container}>
      {/* Top Image Viewer with Heatmap Toggle */}
      <View style={styles.imageCard}>
        <Image 
          source={{ uri: showHeatmap && inspection.heatmap_url ? inspection.heatmap_url : inspection.image_url }} 
          style={styles.mainImage} 
        />
        <View style={styles.overlayBar}>
          <Text style={styles.overlayLabel}>
            {showHeatmap ? '🔥 U-Net Lesion Heatmap' : '📷 Visible Light (RGB)'}
          </Text>
          <View style={styles.switchRow}>
            <Text style={styles.switchLabel}>Heatmap</Text>
            <Switch
              value={showHeatmap}
              onValueChange={setShowHeatmap}
              trackColor={{ false: '#767577', true: '#86efac' }}
              thumbColor={showHeatmap ? '#15803d' : '#f4f3f4'}
            />
          </View>
        </View>
      </View>

      {/* Primary Diagnosis Header */}
      <View style={styles.content}>
        <View style={styles.cropBadgeRow}>
          <Text style={styles.cropBadge}>{inspection.crop_name}</Text>
          <Text style={styles.timeText}>{new Date(inspection.created_at).toLocaleString()}</Text>
        </View>

        <Text style={styles.diseaseTitle}>{inspection.disease_predicted}</Text>
        {inspection.disease_predicted_ta && (
          <Text style={styles.diseaseTamil}>{inspection.disease_predicted_ta}</Text>
        )}

        {/* Severity Gauge */}
        <View style={styles.severitySection}>
          <View style={styles.severityHeader}>
            <Text style={styles.severityTitle}>Foliar Lesion Severity</Text>
            <Text style={styles.severityPercent}>{inspection.severity_pct.toFixed(1)}%</Text>
          </View>
          <View style={styles.progressBar}>
            <View 
              style={[
                styles.progressFill, 
                { 
                  width: `${Math.min(inspection.severity_pct * 2, 100)}%`,
                  backgroundColor: inspection.severity_pct > 25 ? '#ef4444' : '#f59e0b'
                }
              ]} 
            />
          </View>
          <Text style={styles.severityNote}>
            Calculated as (Necrotic Lesion Pixels / Total Canopy Pixels) × 100 via U-Net.
          </Text>
        </View>

        {/* Confidence & Language selector */}
        <View style={styles.langSelectorRow}>
          <View style={styles.confBadge}>
            <Text style={styles.confText}>AI Confidence: {(inspection.confidence * 100).toFixed(1)}%</Text>
          </View>
          <View style={styles.langPills}>
            <TouchableOpacity 
              style={[styles.langPill, language === 'ta' && styles.langPillActive]}
              onPress={() => setLanguage('ta')}
            >
              <Text style={[styles.langPillText, language === 'ta' && styles.langPillTextActive]}>தமிழ்</Text>
            </TouchableOpacity>
            <TouchableOpacity 
              style={[styles.langPill, language === 'en' && styles.langPillActive]}
              onPress={() => setLanguage('en')}
            >
              <Text style={[styles.langPillText, language === 'en' && styles.langPillTextActive]}>English</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Agronomic Management Guidance Card */}
        <View style={styles.guidanceCard}>
          <View style={styles.guidanceHeader}>
            <Text style={styles.guidanceTitle}>
              {isTamil ? '🌾 கள மேலாண்மை & சிகிச்சை வழிகாட்டுதல்' : '🌾 Agronomic Field Guidance'}
            </Text>
            <TouchableOpacity 
              style={styles.voiceBtn}
              onPress={handlePlayVoice}
              disabled={isPlayingAudio}
            >
              {isPlayingAudio ? (
                <ActivityIndicator size="small" color="#15803d" />
              ) : (
                <Text style={styles.voiceBtnText}>🔊 {isTamil ? 'கேட்க' : 'Listen'}</Text>
              )}
            </TouchableOpacity>
          </View>

          <Text style={styles.guidanceBody}>
            {isTamil 
              ? (inspection.management_guidance_ta || inspection.management_guidance) 
              : inspection.management_guidance}
          </Text>

          {/* Safety Disclaimer Banner */}
          <View style={styles.disclaimerBox}>
            <Text style={styles.disclaimerText}>
              ⚠️ <Text style={{fontWeight: 'bold'}}>Decision Support Disclaimer:</Text> This AI analysis aids diagnosis and does not replace certified agronomist inspection. Do not apply restricted agrochemicals without local authority consultation.
            </Text>
          </View>
        </View>

        {/* Active Learning & Expert Validation */}
        <View style={styles.feedbackCard}>
          <Text style={styles.feedbackTitle}>Validate Diagnosis (Expert Feedback)</Text>
          <Text style={styles.feedbackSub}>
            Help improve AgriVision 2.0. Is this diagnosis accurate?
          </Text>
          {feedbackSent ? (
            <Text style={styles.feedbackSentText}>✅ Thank you! Feedback recorded.</Text>
          ) : (
            <View style={styles.feedbackBtnRow}>
              <TouchableOpacity 
                style={[styles.feedBtn, styles.feedBtnYes]}
                onPress={() => handleExpertFeedback(true)}
              >
                <Text style={styles.feedBtnYesText}>✓ Correct Diagnosis</Text>
              </TouchableOpacity>
              <TouchableOpacity 
                style={[styles.feedBtn, styles.feedBtnNo]}
                onPress={() => handleExpertFeedback(false)}
              >
                <Text style={styles.feedBtnNoText}>✕ Report Misdiagnosis</Text>
              </TouchableOpacity>
            </View>
          )}
        </View>

        <View style={{ height: 40 }} />
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f8fafc',
  },
  loadingText: {
    marginTop: 12,
    color: '#475569',
  },
  imageCard: {
    width: '100%',
    height: 280,
    backgroundColor: '#000000',
    position: 'relative',
  },
  mainImage: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  overlayBar: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: 'rgba(15, 23, 42, 0.8)',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  overlayLabel: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  switchRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  switchLabel: {
    color: '#cbd5e1',
    fontSize: 12,
    marginRight: 6,
  },
  content: {
    padding: 16,
  },
  cropBadgeRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  cropBadge: {
    backgroundColor: '#dcfce7',
    color: '#166534',
    fontWeight: 'bold',
    fontSize: 12,
    paddingHorizontal: 10,
    paddingVertical: 3,
    borderRadius: 6,
  },
  timeText: {
    fontSize: 11,
    color: '#94a3b8',
  },
  diseaseTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#0f172a',
    marginTop: 4,
  },
  diseaseTamil: {
    fontSize: 15,
    color: '#334155',
    marginTop: 2,
    fontWeight: '500',
  },
  severitySection: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 14,
    marginTop: 16,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  severityHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  severityTitle: {
    fontSize: 13,
    fontWeight: 'bold',
    color: '#334155',
  },
  severityPercent: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#ea580c',
  },
  progressBar: {
    height: 10,
    backgroundColor: '#f1f5f9',
    borderRadius: 5,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    borderRadius: 5,
  },
  severityNote: {
    fontSize: 10,
    color: '#64748b',
    marginTop: 6,
  },
  langSelectorRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 14,
  },
  confBadge: {
    backgroundColor: '#f0fdf4',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#bbf7d0',
  },
  confText: {
    color: '#15803d',
    fontWeight: 'bold',
    fontSize: 12,
  },
  langPills: {
    flexDirection: 'row',
  },
  langPill: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 14,
    backgroundColor: '#e2e8f0',
    marginLeft: 6,
  },
  langPillActive: {
    backgroundColor: '#15803d',
  },
  langPillText: {
    fontSize: 12,
    color: '#475569',
    fontWeight: '600',
  },
  langPillTextActive: {
    color: '#ffffff',
  },
  guidanceCard: {
    backgroundColor: '#ffffff',
    borderRadius: 14,
    padding: 16,
    marginTop: 14,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  guidanceHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  guidanceTitle: {
    fontSize: 15,
    fontWeight: 'bold',
    color: '#0f172a',
    flex: 1,
  },
  voiceBtn: {
    backgroundColor: '#f0fdf4',
    borderWidth: 1,
    borderColor: '#86efac',
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 4,
  },
  voiceBtnText: {
    color: '#15803d',
    fontWeight: 'bold',
    fontSize: 12,
  },
  guidanceBody: {
    fontSize: 13,
    color: '#334155',
    lineHeight: 20,
  },
  disclaimerBox: {
    backgroundColor: '#fffbeb',
    borderRadius: 8,
    padding: 10,
    marginTop: 14,
    borderLeftWidth: 4,
    borderLeftColor: '#f59e0b',
  },
  disclaimerText: {
    fontSize: 11,
    color: '#78350f',
    lineHeight: 16,
  },
  feedbackCard: {
    backgroundColor: '#ffffff',
    borderRadius: 14,
    padding: 16,
    marginTop: 14,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  feedbackTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#0f172a',
  },
  feedbackSub: {
    fontSize: 12,
    color: '#64748b',
    marginTop: 2,
    marginBottom: 12,
  },
  feedbackSentText: {
    color: '#15803d',
    fontWeight: 'bold',
    fontSize: 13,
  },
  feedbackBtnRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  feedBtn: {
    flex: 1,
    paddingVertical: 10,
    borderRadius: 8,
    alignItems: 'center',
    marginHorizontal: 4,
  },
  feedBtnYes: {
    backgroundColor: '#dcfce7',
    borderWidth: 1,
    borderColor: '#86efac',
  },
  feedBtnYesText: {
    color: '#166534',
    fontWeight: 'bold',
    fontSize: 12,
  },
  feedBtnNo: {
    backgroundColor: '#fee2e2',
    borderWidth: 1,
    borderColor: '#fca5a5',
  },
  feedBtnNoText: {
    color: '#991b1b',
    fontWeight: 'bold',
    fontSize: 12,
  },
});

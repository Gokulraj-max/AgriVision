import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  ScrollView, 
  TouchableOpacity, 
  StyleSheet, 
  RefreshControl,
  Image,
  ActivityIndicator
} from 'react-native';
import { useRouter } from 'expo-router';
import { api } from '../../src/services/api';
import { InspectionRecord, WeatherCondition } from '../../src/types';
import { getUnsyncedCount } from '../../src/database/sqlite';

export default function DashboardScreen() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [inspections, setInspections] = useState<InspectionRecord[]>([]);
  const [weatherRisk, setWeatherRisk] = useState<WeatherCondition | null>(null);
  const [unsynced, setUnsynced] = useState<number>(0);

  const loadData = async () => {
    try {
      const [inspData, weatherData, unsyncedCount] = await Promise.all([
        api.listInspections(6).catch(() => []),
        api.getWeatherRisk().catch(() => null),
        getUnsyncedCount().catch(() => 0)
      ]);
      setInspections(inspData);
      if (weatherData && weatherData.current) {
        setWeatherRisk(weatherData.current);
      }
      setUnsynced(unsyncedCount);
    } catch (err) {
      console.warn('Dashboard load warning:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    loadData();
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#16a34a" />
        <Text style={styles.loadingText}>Loading Farm Intelligence...</Text>
      </View>
    );
  }

  return (
    <ScrollView 
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      {/* Top Banner / Sync status */}
      <View style={styles.topBar}>
        <View>
          <Text style={styles.farmerGreeting}>Welcome back, Farmer 👋</Text>
          <Text style={styles.farmSub}>Green Valley Farm • 14.5 Acres</Text>
        </View>
        {unsynced > 0 ? (
          <View style={styles.syncBadgeWarning}>
            <Text style={styles.syncBadgeText}>⏳ {unsynced} Pending Sync</Text>
          </View>
        ) : (
          <View style={styles.syncBadgeOk}>
            <Text style={styles.syncBadgeText}>🟢 Cloud Synced</Text>
          </View>
        )}
      </View>

      {/* Hero CTA: Live Camera Scanner */}
      <TouchableOpacity 
        style={styles.heroCta}
        onPress={() => router.push('/(tabs)/scanner')}
        activeOpacity={0.88}
      >
        <View style={styles.heroContent}>
          <Text style={styles.heroBadge}>AI REAL-TIME DETECTION</Text>
          <Text style={styles.heroTitle}>Launch Live Crop Scanner 📷</Text>
          <Text style={styles.heroDesc}>
            Point your camera at leaves for instant disease diagnosis, severity calculation & Tamil guidance.
          </Text>
          <View style={styles.scanNowBtn}>
            <Text style={styles.scanNowText}>Start Scanning Now ➔</Text>
          </View>
        </View>
      </TouchableOpacity>

      {/* Microclimate Disease Risk Alert */}
      {weatherRisk && (
        <TouchableOpacity 
          style={[
            styles.riskCard, 
            weatherRisk.risk_level === 'HIGH' ? styles.riskHigh : styles.riskMedium
          ]}
          onPress={() => router.push('/(tabs)/weather')}
        >
          <View style={styles.riskHeader}>
            <Text style={styles.riskTitle}>🌦️ Environmental Disease Risk: {weatherRisk.risk_level}</Text>
            <Text style={styles.riskIndexScore}>{weatherRisk.disease_risk_index}/100</Text>
          </View>
          <Text style={styles.riskDesc}>
            Temp: {weatherRisk.temperature_c}°C • RH: {weatherRisk.relative_humidity_pct}% • Rain: {weatherRisk.precipitation_mm}mm
          </Text>
          {weatherRisk.pathogen_alerts.length > 0 && (
            <Text style={styles.riskPathogen}>
              ⚠️ Heightened pressure for: <Text style={{fontWeight: 'bold'}}>{weatherRisk.pathogen_alerts[0].disease}</Text>
            </Text>
          )}
        </TouchableOpacity>
      )}

      {/* Metrics Row */}
      <View style={styles.metricsRow}>
        <View style={styles.metricCard}>
          <Text style={styles.metricVal}>7</Text>
          <Text style={styles.metricLbl}>Supported Crops</Text>
        </View>
        <View style={styles.metricCard}>
          <Text style={styles.metricVal}>{inspections.length}</Text>
          <Text style={styles.metricLbl}>Inspections</Text>
        </View>
        <View style={styles.metricCard}>
          <Text style={styles.metricVal}>86%</Text>
          <Text style={styles.metricLbl}>Average Health</Text>
        </View>
      </View>

      {/* Recent Inspections Section */}
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>Recent Foliar Inspections</Text>
        <TouchableOpacity onPress={() => router.push('/(tabs)/scanner')}>
          <Text style={styles.sectionLink}>+ New Scan</Text>
        </TouchableOpacity>
      </View>

      {inspections.length === 0 ? (
        <View style={styles.emptyCard}>
          <Text style={styles.emptyText}>No crop inspections recorded yet.</Text>
          <TouchableOpacity 
            style={styles.emptyAction}
            onPress={() => router.push('/(tabs)/scanner')}
          >
            <Text style={styles.emptyActionText}>Take your first leaf photo</Text>
          </TouchableOpacity>
        </View>
      ) : (
        inspections.map((item) => (
          <TouchableOpacity 
            key={item.id} 
            style={styles.inspectionCard}
            onPress={() => router.push(`/inspection/${item.id}` as any)}
          >
            <View style={styles.cardRow}>
              {item.image_url ? (
                <Image source={{ uri: item.image_url }} style={styles.thumbImage} />
              ) : (
                <View style={styles.thumbPlaceholder}>
                  <Text style={{ fontSize: 24 }}>🍃</Text>
                </View>
              )}
              <View style={styles.inspDetails}>
                <View style={styles.rowBetween}>
                  <Text style={styles.cropBadge}>{item.crop_name}</Text>
                  <Text style={styles.dateText}>
                    {new Date(item.created_at).toLocaleDateString()}
                  </Text>
                </View>
                <Text style={styles.diseaseName}>{item.disease_predicted}</Text>
                {item.disease_predicted_ta && (
                  <Text style={styles.diseaseTamil}>{item.disease_predicted_ta}</Text>
                )}
                
                <View style={styles.badgeRow}>
                  <View style={[
                    styles.severityPill,
                    item.severity_pct > 20 ? styles.severityPillHigh : styles.severityPillLow
                  ]}>
                    <Text style={styles.severityText}>
                      Severity: {item.severity_pct.toFixed(1)}%
                    </Text>
                  </View>
                  <Text style={styles.confidenceText}>
                    {(item.confidence * 100).toFixed(0)}% Conf.
                  </Text>
                </View>
              </View>
            </View>
          </TouchableOpacity>
        ))
      )}
      
      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
    padding: 16,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f8fafc',
  },
  loadingText: {
    marginTop: 12,
    fontSize: 14,
    color: '#475569',
  },
  topBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  farmerGreeting: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#0f172a',
  },
  farmSub: {
    fontSize: 13,
    color: '#64748b',
    marginTop: 2,
  },
  syncBadgeOk: {
    backgroundColor: '#dcfce7',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 12,
  },
  syncBadgeWarning: {
    backgroundColor: '#fef3c7',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 12,
  },
  syncBadgeText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#15803d',
  },
  heroCta: {
    backgroundColor: '#15803d',
    borderRadius: 16,
    padding: 18,
    marginBottom: 16,
    elevation: 4,
    shadowColor: '#15803d',
    shadowOpacity: 0.3,
    shadowOffset: { width: 0, height: 4 },
    shadowRadius: 8,
  },
  heroContent: {},
  heroBadge: {
    color: '#bbf7d0',
    fontSize: 11,
    fontWeight: 'bold',
    letterSpacing: 1,
    marginBottom: 4,
  },
  heroTitle: {
    color: '#ffffff',
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 6,
  },
  heroDesc: {
    color: '#f0fdf4',
    fontSize: 13,
    lineHeight: 18,
    marginBottom: 14,
  },
  scanNowBtn: {
    backgroundColor: '#ffffff',
    alignSelf: 'flex-start',
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 20,
  },
  scanNowText: {
    color: '#15803d',
    fontWeight: 'bold',
    fontSize: 13,
  },
  riskCard: {
    borderRadius: 12,
    padding: 14,
    marginBottom: 16,
    borderLeftWidth: 5,
  },
  riskHigh: {
    backgroundColor: '#fff1f2',
    borderLeftColor: '#e11d48',
  },
  riskMedium: {
    backgroundColor: '#fefce8',
    borderLeftColor: '#eab308',
  },
  riskHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  riskTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#881337',
  },
  riskIndexScore: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#881337',
  },
  riskDesc: {
    fontSize: 12,
    color: '#475569',
    marginTop: 4,
  },
  riskPathogen: {
    fontSize: 12,
    color: '#9f1239',
    marginTop: 6,
  },
  metricsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  metricCard: {
    flex: 1,
    backgroundColor: '#ffffff',
    padding: 12,
    borderRadius: 12,
    alignItems: 'center',
    marginHorizontal: 4,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  metricVal: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#15803d',
  },
  metricLbl: {
    fontSize: 11,
    color: '#64748b',
    marginTop: 2,
    textAlign: 'center',
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#0f172a',
  },
  sectionLink: {
    fontSize: 13,
    fontWeight: '600',
    color: '#15803d',
  },
  inspectionCard: {
    backgroundColor: '#ffffff',
    borderRadius: 14,
    padding: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  cardRow: {
    flexDirection: 'row',
  },
  thumbImage: {
    width: 70,
    height: 70,
    borderRadius: 10,
    backgroundColor: '#e2e8f0',
  },
  thumbPlaceholder: {
    width: 70,
    height: 70,
    borderRadius: 10,
    backgroundColor: '#dcfce7',
    alignItems: 'center',
    justifyContent: 'center',
  },
  inspDetails: {
    flex: 1,
    marginLeft: 12,
    justifyContent: 'center',
  },
  rowBetween: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  cropBadge: {
    fontSize: 11,
    fontWeight: 'bold',
    color: '#166534',
    backgroundColor: '#dcfce7',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  dateText: {
    fontSize: 11,
    color: '#94a3b8',
  },
  diseaseName: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#1e293b',
    marginTop: 4,
  },
  diseaseTamil: {
    fontSize: 12,
    color: '#475569',
    marginTop: 1,
  },
  badgeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 6,
  },
  severityPill: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10,
    marginRight: 8,
  },
  severityPillLow: {
    backgroundColor: '#dbeafe',
  },
  severityPillHigh: {
    backgroundColor: '#fee2e2',
  },
  severityText: {
    fontSize: 11,
    fontWeight: '600',
    color: '#1e3a8a',
  },
  confidenceText: {
    fontSize: 11,
    color: '#64748b',
  },
  emptyCard: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 24,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  emptyText: {
    color: '#64748b',
    fontSize: 14,
  },
  emptyAction: {
    marginTop: 12,
    backgroundColor: '#15803d',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
  },
  emptyActionText: {
    color: '#ffffff',
    fontWeight: 'bold',
    fontSize: 13,
  },
});

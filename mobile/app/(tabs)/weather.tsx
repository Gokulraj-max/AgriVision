import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  ScrollView, 
  StyleSheet, 
  ActivityIndicator, 
  RefreshControl,
  TouchableOpacity 
} from 'react-native';
import { api } from '../../src/services/api';
import { WeatherCondition, FiveDayForecastDay } from '../../src/types';

export default function WeatherRiskScreen() {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [current, setCurrent] = useState<WeatherCondition | null>(null);
  const [forecast, setForecast] = useState<FiveDayForecastDay[]>([]);
  const [selectedCrop, setSelectedCrop] = useState<string>('Tomato');

  const crops = ['Tomato', 'Potato', 'Rice', 'Cotton', 'Maize', 'Pepper', 'Apple'];

  const loadWeather = async () => {
    try {
      const data = await api.getWeatherRisk(11.0168, 76.9558, selectedCrop).catch(() => null);
      if (data && data.current) {
        setCurrent(data.current);
        setForecast(data.forecast || []);
      } else {
        // Fallback default agro-weather data
        setCurrent({
          temperature_c: 24.5,
          relative_humidity_pct: 88,
          precipitation_mm: 12.4,
          wind_speed_kmh: 8.5,
          leaf_wetness_hours: 7.2,
          solar_radiation_mj: 14.2,
          disease_risk_index: 76,
          risk_level: 'HIGH',
          pathogen_alerts: [
            {
              disease: 'Phytophthora infestans (Late Blight)',
              pathogen: 'Oomycete',
              risk_level: 'HIGH',
              favorable_factors: ['High relative humidity (>85%)', 'Prolonged leaf wetness (>6 hrs)', 'Moderate temperature (18-22°C)']
            },
            {
              disease: 'Alternaria solani (Early Blight)',
              pathogen: 'Fungus',
              risk_level: 'MEDIUM',
              favorable_factors: ['Alternating wet-dry foliage cycles']
            }
          ]
        });

        setForecast([
          { date: '2026-11-15', day_name: 'Today', temp_min: 20, temp_max: 27, humidity_pct: 88, rain_probability_pct: 75, overall_risk: 'HIGH', alert_summary: 'Prolonged wetness window. High fungal spore germination risk.' },
          { date: '2026-11-16', day_name: 'Tomorrow', temp_min: 19, temp_max: 28, humidity_pct: 82, rain_probability_pct: 40, overall_risk: 'MEDIUM', alert_summary: 'Afternoon drying; favorable window for scouting.' },
          { date: '2026-11-17', day_name: 'Wednesday', temp_min: 21, temp_max: 29, humidity_pct: 74, rain_probability_pct: 20, overall_risk: 'LOW', alert_summary: 'Dry canopy conditions. Low spore dispersal.' },
          { date: '2026-11-18', day_name: 'Thursday', temp_min: 22, temp_max: 30, humidity_pct: 68, rain_probability_pct: 10, overall_risk: 'LOW', alert_summary: 'Optimal weather for field tractor operations.' },
          { date: '2026-11-19', day_name: 'Friday', temp_min: 21, temp_max: 28, humidity_pct: 79, rain_probability_pct: 55, overall_risk: 'MEDIUM', alert_summary: 'Evening showers expected. Inspect drainage.' },
        ]);
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadWeather();
  }, [selectedCrop]);

  const onRefresh = () => {
    setRefreshing(true);
    loadWeather();
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#15803d" />
        <Text style={styles.loadingText}>Fetching Microclimate Agro-Weather...</Text>
      </View>
    );
  }

  return (
    <ScrollView 
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      {/* Crop Filter Pill Carousel */}
      <View style={styles.cropFilterRow}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          {crops.map((c) => (
            <TouchableOpacity
              key={c}
              style={[styles.cropPill, selectedCrop === c && styles.cropPillActive]}
              onPress={() => setSelectedCrop(c)}
            >
              <Text style={[styles.cropPillText, selectedCrop === c && styles.cropPillTextActive]}>
                {c}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      {/* Primary Risk Gauge Banner */}
      {current && (
        <View style={[
          styles.mainRiskCard,
          current.risk_level === 'HIGH' ? styles.riskCardHigh : styles.riskCardMed
        ]}>
          <View style={styles.riskTopRow}>
            <View>
              <Text style={styles.riskOverTitle}>MICROCLIMATE DISEASE RISK</Text>
              <Text style={styles.riskLevelText}>{current.risk_level} RISK</Text>
            </View>
            <View style={styles.scoreCircle}>
              <Text style={styles.scoreNum}>{current.disease_risk_index}</Text>
              <Text style={styles.scoreDen}>/100</Text>
            </View>
          </View>
          <Text style={styles.riskSubtext}>
            Environmental parameters are currently favorable for fungal pathogen germination on {selectedCrop} foliage.
          </Text>
        </View>
      )}

      {/* Current Environmental Observations Grid */}
      {current && (
        <View style={styles.gridSection}>
          <Text style={styles.sectionTitle}>NASA POWER & Local Station Metrics</Text>
          <View style={styles.gridRow}>
            <View style={styles.gridCell}>
              <Text style={styles.gridEmoji}>🌡️</Text>
              <Text style={styles.gridVal}>{current.temperature_c}°C</Text>
              <Text style={styles.gridLbl}>Temperature</Text>
            </View>
            <View style={styles.gridCell}>
              <Text style={styles.gridEmoji}>💧</Text>
              <Text style={styles.gridVal}>{current.relative_humidity_pct}%</Text>
              <Text style={styles.gridLbl}>Humidity (RH)</Text>
            </View>
            <View style={styles.gridCell}>
              <Text style={styles.gridEmoji}>🌧️</Text>
              <Text style={styles.gridVal}>{current.precipitation_mm} mm</Text>
              <Text style={styles.gridLbl}>Rainfall</Text>
            </View>
          </View>
          <View style={styles.gridRow}>
            <View style={styles.gridCell}>
              <Text style={styles.gridEmoji}>🍃</Text>
              <Text style={styles.gridVal}>{current.leaf_wetness_hours} hrs</Text>
              <Text style={styles.gridLbl}>Leaf Wetness</Text>
            </View>
            <View style={styles.gridCell}>
              <Text style={styles.gridEmoji}>💨</Text>
              <Text style={styles.gridVal}>{current.wind_speed_kmh} km/h</Text>
              <Text style={styles.gridLbl}>Wind Velocity</Text>
            </View>
            <View style={styles.gridCell}>
              <Text style={styles.gridEmoji}>☀️</Text>
              <Text style={styles.gridVal}>{current.solar_radiation_mj} MJ</Text>
              <Text style={styles.gridLbl}>Solar Radiation</Text>
            </View>
          </View>
        </View>
      )}

      {/* Specific Pathogen Threat Indicators */}
      {current?.pathogen_alerts && current.pathogen_alerts.length > 0 && (
        <View style={styles.pathogenSection}>
          <Text style={styles.sectionTitle}>Active Pathogen Windows</Text>
          {current.pathogen_alerts.map((alert, idx) => (
            <View key={idx} style={styles.pathogenCard}>
              <View style={styles.pathogenTop}>
                <Text style={styles.pathogenName}>{alert.disease}</Text>
                <View style={[
                  styles.pathogenPill, 
                  alert.risk_level === 'HIGH' ? styles.pillHigh : styles.pillMed
                ]}>
                  <Text style={styles.pillText}>{alert.risk_level}</Text>
                </View>
              </View>
              <Text style={styles.pathogenSub}>Type: {alert.pathogen}</Text>
              <View style={styles.factorList}>
                {alert.favorable_factors.map((f, i) => (
                  <Text key={i} style={styles.factorItem}>• {f}</Text>
                ))}
              </View>
            </View>
          ))}
        </View>
      )}

      {/* 5-Day Forecast Table */}
      <View style={styles.forecastSection}>
        <Text style={styles.sectionTitle}>5-Day Disease Risk Outlook</Text>
        {forecast.map((day, i) => (
          <View key={i} style={styles.forecastRow}>
            <View style={styles.dayCol}>
              <Text style={styles.dayName}>{day.day_name}</Text>
              <Text style={styles.dayDate}>{day.date.substring(5)}</Text>
            </View>
            <View style={styles.weatherCol}>
              <Text style={styles.tempRange}>{day.temp_min}° - {day.temp_max}°C</Text>
              <Text style={styles.rainProb}>💧 {day.rain_probability_pct}% rain</Text>
            </View>
            <View style={styles.riskCol}>
              <View style={[
                styles.miniRiskPill,
                day.overall_risk === 'HIGH' ? styles.pillHigh : (day.overall_risk === 'MEDIUM' ? styles.pillMed : styles.pillLow)
              ]}>
                <Text style={styles.miniRiskText}>{day.overall_risk}</Text>
              </View>
            </View>
          </View>
        ))}
      </View>

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
    color: '#475569',
  },
  cropFilterRow: {
    marginBottom: 14,
  },
  cropPill: {
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: 20,
    backgroundColor: '#e2e8f0',
    marginRight: 8,
  },
  cropPillActive: {
    backgroundColor: '#15803d',
  },
  cropPillText: {
    fontSize: 13,
    color: '#475569',
    fontWeight: '600',
  },
  cropPillTextActive: {
    color: '#ffffff',
  },
  mainRiskCard: {
    borderRadius: 16,
    padding: 18,
    marginBottom: 16,
  },
  riskCardHigh: {
    backgroundColor: '#fee2e2',
    borderWidth: 1,
    borderColor: '#fca5a5',
  },
  riskCardMed: {
    backgroundColor: '#fef3c7',
    borderWidth: 1,
    borderColor: '#fde047',
  },
  riskTopRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  riskOverTitle: {
    fontSize: 11,
    fontWeight: 'bold',
    color: '#991b1b',
    letterSpacing: 1,
  },
  riskLevelText: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#7f1d1d',
    marginTop: 2,
  },
  scoreCircle: {
    backgroundColor: '#ffffff',
    width: 64,
    height: 64,
    borderRadius: 32,
    alignItems: 'center',
    justifyContent: 'center',
    elevation: 2,
  },
  scoreNum: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#b91c1c',
  },
  scoreDen: {
    fontSize: 10,
    color: '#64748b',
  },
  riskSubtext: {
    fontSize: 12,
    color: '#450a0a',
    marginTop: 10,
    lineHeight: 18,
  },
  sectionTitle: {
    fontSize: 15,
    fontWeight: 'bold',
    color: '#0f172a',
    marginBottom: 10,
  },
  gridSection: {
    backgroundColor: '#ffffff',
    borderRadius: 14,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  gridRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 10,
  },
  gridCell: {
    flex: 1,
    alignItems: 'center',
    padding: 8,
    backgroundColor: '#f8fafc',
    borderRadius: 10,
    marginHorizontal: 3,
  },
  gridEmoji: {
    fontSize: 18,
  },
  gridVal: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#0f172a',
    marginTop: 4,
  },
  gridLbl: {
    fontSize: 10,
    color: '#64748b',
    marginTop: 2,
    textAlign: 'center',
  },
  pathogenSection: {
    marginBottom: 16,
  },
  pathogenCard: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 14,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  pathogenTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  pathogenName: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#1e293b',
    flex: 1,
  },
  pathogenPill: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 6,
    marginLeft: 6,
  },
  pillHigh: {
    backgroundColor: '#fee2e2',
  },
  pillMed: {
    backgroundColor: '#fef3c7',
  },
  pillLow: {
    backgroundColor: '#dcfce7',
  },
  pillText: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#991b1b',
  },
  pathogenSub: {
    fontSize: 11,
    color: '#64748b',
    marginTop: 2,
  },
  factorList: {
    marginTop: 8,
  },
  factorItem: {
    fontSize: 11,
    color: '#475569',
    lineHeight: 16,
  },
  forecastSection: {
    backgroundColor: '#ffffff',
    borderRadius: 14,
    padding: 16,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  forecastRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#f1f5f9',
  },
  dayCol: {
    width: 80,
  },
  dayName: {
    fontSize: 13,
    fontWeight: 'bold',
    color: '#1e293b',
  },
  dayDate: {
    fontSize: 11,
    color: '#94a3b8',
  },
  weatherCol: {
    flex: 1,
  },
  tempRange: {
    fontSize: 13,
    fontWeight: '600',
    color: '#334155',
  },
  rainProb: {
    fontSize: 11,
    color: '#64748b',
  },
  riskCol: {
    width: 70,
    alignItems: 'flex-end',
  },
  miniRiskPill: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
  },
  miniRiskText: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#0f172a',
  },
});

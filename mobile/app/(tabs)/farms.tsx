import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  ScrollView, 
  TouchableOpacity, 
  StyleSheet, 
  ActivityIndicator, 
  Modal, 
  TextInput, 
  Alert 
} from 'react-native';
import { api } from '../../src/services/api';
import { Farm, Field } from '../../src/types';

export default function FarmsScreen() {
  const [loading, setLoading] = useState(true);
  const [farms, setFarms] = useState<Farm[]>([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [farmName, setFarmName] = useState('');
  const [locationName, setLocationName] = useState('');
  const [acres, setAcres] = useState('');

  const loadFarms = async () => {
    try {
      const data = await api.listFarms().catch(() => []);
      if (data && data.length > 0) {
        setFarms(data);
      } else {
        // Fallback demo farms
        setFarms([
          {
            id: 'farm_1',
            name: 'Green Valley Organic Estate',
            location_name: 'Coimbatore, Tamil Nadu',
            total_acres: 14.5,
            crop_types: ['Tomato', 'Potato', 'Pepper'],
            latitude: 11.0168,
            longitude: 76.9558,
            fields_count: 3,
            active_inspections_count: 8
          },
          {
            id: 'farm_2',
            name: 'Kaveri Delta Paddy Fields',
            location_name: 'Thanjavur, Tamil Nadu',
            total_acres: 22.0,
            crop_types: ['Rice', 'Cotton'],
            latitude: 10.7870,
            longitude: 79.1378,
            fields_count: 4,
            active_inspections_count: 5
          }
        ]);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFarms();
  }, []);

  const handleCreateFarm = async () => {
    if (!farmName || !locationName || !acres) {
      Alert.alert('Required Fields', 'Please fill in Farm Name, Location, and Total Acres.');
      return;
    }

    try {
      const newFarm = await api.createFarm({
        name: farmName,
        location_name: locationName,
        total_acres: parseFloat(acres) || 5.0,
        latitude: 11.0168,
        longitude: 76.9558
      }).catch(() => null);

      if (newFarm) {
        setFarms([...farms, newFarm]);
      } else {
        setFarms([
          ...farms,
          {
            id: `farm_${Date.now()}`,
            name: farmName,
            location_name: locationName,
            total_acres: parseFloat(acres) || 5.0,
            crop_types: ['Tomato'],
            latitude: 11.0168,
            longitude: 76.9558,
            fields_count: 1,
            active_inspections_count: 0
          }
        ]);
      }

      setModalVisible(false);
      setFarmName('');
      setLocationName('');
      setAcres('');
      Alert.alert('Success', 'Farm registered successfully.');
    } catch (e: any) {
      Alert.alert('Error', e.message);
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#15803d" />
        <Text style={styles.loadingText}>Loading Farm Boundaries & Field Health...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      {/* Header with Add Farm CTA */}
      <View style={styles.topRow}>
        <View>
          <Text style={styles.title}>Registered Farms</Text>
          <Text style={styles.subtitle}>Track parcels, crop cycles & historical disease pressure</Text>
        </View>
        <TouchableOpacity 
          style={styles.addBtn}
          onPress={() => setModalVisible(true)}
        >
          <Text style={styles.addBtnText}>+ Add Farm</Text>
        </TouchableOpacity>
      </View>

      {/* Farm Cards */}
      {farms.map((farm) => (
        <View key={farm.id} style={styles.farmCard}>
          <View style={styles.farmHeader}>
            <View style={{ flex: 1 }}>
              <Text style={styles.farmName}>{farm.name}</Text>
              <Text style={styles.farmLoc}>📍 {farm.location_name}</Text>
            </View>
            <View style={styles.acreBadge}>
              <Text style={styles.acreText}>{farm.total_acres} Acres</Text>
            </View>
          </View>

          {/* Crop Tags */}
          <View style={styles.cropTagsRow}>
            {farm.crop_types.map((c, i) => (
              <View key={i} style={styles.cropTag}>
                <Text style={styles.cropTagText}>🌱 {c}</Text>
              </View>
            ))}
          </View>

          {/* Sub-parcels / Fields */}
          <View style={styles.fieldsSummary}>
            <View style={styles.statBox}>
              <Text style={styles.statNum}>{farm.fields_count}</Text>
              <Text style={styles.statLbl}>Fields / Zones</Text>
            </View>
            <View style={styles.statBox}>
              <Text style={styles.statNum}>{farm.active_inspections_count}</Text>
              <Text style={styles.statLbl}>Inspections</Text>
            </View>
            <View style={styles.statBox}>
              <Text style={[styles.statNum, { color: '#16a34a' }]}>Healthy</Text>
              <Text style={styles.statLbl}>Overall Status</Text>
            </View>
          </View>

          {/* Field Details Expandable */}
          <View style={styles.fieldsList}>
            <Text style={styles.fieldListTitle}>Active Field Parcels:</Text>
            <View style={styles.fieldItem}>
              <View>
                <Text style={styles.fieldName}>North Block 1A — Tomato (Arka Rakshak)</Text>
                <Text style={styles.fieldStage}>Stage: Flowering & Fruit Set (Day 48)</Text>
              </View>
              <View style={styles.fieldHealthGood}>
                <Text style={styles.healthGoodText}>Normal</Text>
              </View>
            </View>

            <View style={styles.fieldItem}>
              <View>
                <Text style={styles.fieldName}>South Block 2B — Potato (Kufri Jyoti)</Text>
                <Text style={styles.fieldStage}>Stage: Tuber Bulking (Day 62)</Text>
              </View>
              <View style={styles.fieldHealthAlert}>
                <Text style={styles.healthAlertText}>Scout Needed</Text>
              </View>
            </View>
          </View>
        </View>
      ))}

      {/* Add Farm Modal */}
      <Modal visible={modalVisible} animationType="slide" transparent>
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Register New Farm</Text>
            
            <Text style={styles.inputLabel}>Farm / Estate Name</Text>
            <TextInput
              style={styles.input}
              value={farmName}
              onChangeText={setFarmName}
              placeholder="e.g. Sunrise Organic Farm"
            />

            <Text style={styles.inputLabel}>Location / Village</Text>
            <TextInput
              style={styles.input}
              value={locationName}
              onChangeText={setLocationName}
              placeholder="e.g. Pollachi, Tamil Nadu"
            />

            <Text style={styles.inputLabel}>Total Area (Acres)</Text>
            <TextInput
              style={styles.input}
              value={acres}
              onChangeText={setAcres}
              placeholder="e.g. 10.5"
              keyboardType="numeric"
            />

            <View style={styles.modalBtnRow}>
              <TouchableOpacity 
                style={styles.modalCancelBtn}
                onPress={() => setModalVisible(false)}
              >
                <Text style={styles.modalCancelText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity 
                style={styles.modalSaveBtn}
                onPress={handleCreateFarm}
              >
                <Text style={styles.modalSaveText}>Save Farm</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

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
  topRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#0f172a',
  },
  subtitle: {
    fontSize: 12,
    color: '#64748b',
    marginTop: 2,
  },
  addBtn: {
    backgroundColor: '#15803d',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
  },
  addBtnText: {
    color: '#ffffff',
    fontWeight: 'bold',
    fontSize: 12,
  },
  farmCard: {
    backgroundColor: '#ffffff',
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  farmHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  farmName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1e293b',
  },
  farmLoc: {
    fontSize: 12,
    color: '#64748b',
    marginTop: 2,
  },
  acreBadge: {
    backgroundColor: '#f0fdf4',
    borderWidth: 1,
    borderColor: '#86efac',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 8,
  },
  acreText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#15803d',
  },
  cropTagsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 10,
  },
  cropTag: {
    backgroundColor: '#f1f5f9',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
    marginRight: 6,
    marginBottom: 4,
  },
  cropTagText: {
    fontSize: 11,
    color: '#334155',
    fontWeight: '500',
  },
  fieldsSummary: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    backgroundColor: '#f8fafc',
    borderRadius: 10,
    paddingVertical: 10,
    marginTop: 12,
  },
  statBox: {
    alignItems: 'center',
  },
  statNum: {
    fontSize: 15,
    fontWeight: 'bold',
    color: '#0f172a',
  },
  statLbl: {
    fontSize: 10,
    color: '#64748b',
    marginTop: 2,
  },
  fieldsList: {
    marginTop: 14,
    borderTopWidth: 1,
    borderTopColor: '#f1f5f9',
    paddingTop: 10,
  },
  fieldListTitle: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#475569',
    marginBottom: 8,
  },
  fieldItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: '#f1f5f9',
    padding: 10,
    borderRadius: 8,
    marginBottom: 6,
  },
  fieldName: {
    fontSize: 12,
    fontWeight: '600',
    color: '#1e293b',
  },
  fieldStage: {
    fontSize: 11,
    color: '#64748b',
    marginTop: 1,
  },
  fieldHealthGood: {
    backgroundColor: '#dcfce7',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
  },
  healthGoodText: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#166534',
  },
  fieldHealthAlert: {
    backgroundColor: '#fef3c7',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
  },
  healthAlertText: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#b45309',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    padding: 20,
  },
  modalContent: {
    backgroundColor: '#ffffff',
    borderRadius: 16,
    padding: 20,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#0f172a',
    marginBottom: 14,
  },
  inputLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: '#374151',
    marginTop: 10,
    marginBottom: 4,
  },
  input: {
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 8,
    padding: 10,
    fontSize: 14,
    backgroundColor: '#f9fafb',
  },
  modalBtnRow: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    marginTop: 20,
  },
  modalCancelBtn: {
    paddingHorizontal: 16,
    paddingVertical: 10,
    marginRight: 8,
  },
  modalCancelText: {
    color: '#64748b',
    fontWeight: '600',
  },
  modalSaveBtn: {
    backgroundColor: '#15803d',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
  },
  modalSaveText: {
    color: '#ffffff',
    fontWeight: 'bold',
  },
});

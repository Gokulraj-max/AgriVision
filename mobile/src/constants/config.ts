import { Platform } from "react-native";

// In Android emulator, 10.0.2.2 connects to host machine's localhost:8000
const DEV_EMULATOR_URL = "http://10.0.2.2:8000";
const DEV_LOCAL_URL = "http://localhost:8000";

export const API_BASE_URL = Platform.select({
  android: DEV_EMULATOR_URL,
  ios: DEV_LOCAL_URL,
  default: DEV_LOCAL_URL
});

export const APP_CONFIG = {
  appName: "AgriVision AI",
  version: "2.0.0",
  defaultCrop: "Tomato",
  confidenceThreshold: 0.60,
  scanIntervalMs: 2000,
  offlineSyncIntervalMs: 30000
};

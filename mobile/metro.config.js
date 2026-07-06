// Default Expo Metro config. Kept explicit so native module resolution
// (react-native-mmkv, etc.) is easy to extend when we prebuild.
const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

module.exports = config;

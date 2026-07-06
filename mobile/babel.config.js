module.exports = function (api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    plugins: [
      [
        'module-resolver',
        {
          root: ['./'],
          alias: { '@': './src' },
        },
      ],
      // NB: SDK 50+ folds expo-router's babel plugin into babel-preset-expo,
      // so it is intentionally NOT listed here.
    ],
  };
};

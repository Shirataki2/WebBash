module.exports = {
  transpileDependencies: ["vuetify"],
  devServer: {
    proxy: "http://proxy",
  },
  pwa: {
    name: 'Web Bash',
    themeColor: '#1D6AF2',
    msTileColor: '#000000',
    appleMobileWebAppCapable: 'yes',
    appleMobileWebAppStatusBarStyle: 'black',
    workboxPluginMode: 'GenerateSW',
    workboxOptions: {
      // ...other Workbox options...
    },
  }
};

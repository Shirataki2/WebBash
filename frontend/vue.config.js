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
    workboxPluginMode: 'InjectManifest',
    workboxOptions: {
      swSrc: 'dev/sw.js',
      // ...other Workbox options...
    }
  }
};

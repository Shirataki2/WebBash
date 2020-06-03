module.exports = {
  publicPath: "/static/",
  transpileDependencies: ["vuetify"],
  devServer: {
    proxy: "http://proxy",
  },
};

module.exports = {
  lintOnSave: false,
  devServer: {
    disableHostCheck: true,
    port: 8084,
    proxy: {
      '/api': {
        target: 'http://localhost:8085',
        changeOrigin: true
      }
    }
  }
}

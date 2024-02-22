module.exports = {
  publicPath: process.env.NODE_ENV === 'production' ? '/static' : '/',
  lintOnSave: process.env.NODE_ENV !== 'production'
}

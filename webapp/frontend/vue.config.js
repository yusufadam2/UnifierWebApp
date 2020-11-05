module.exports = {
  outputDir: "../static",
  assetsDir: "",
  parallel: false,

  lintOnSave: process.env.NODE_ENV !== "production",
  devServer: {
    overlay: {
      warnings: true,
      errors: true
    }
  },

  runtimeCompiler: false,
  productionSourceMap: true,

  css: {
    extract: true,
    sourceMap: true
  },

  crossorigin: undefined,
  integrity: true
};

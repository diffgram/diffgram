'use strict' // strict mode helps to write more secure and reliable code

// path module is a core Node.js module for handling file and directory paths
const path = require('path')

// utils is a custom module that contains utility functions
const utils = require('./utils')

// config is a custom module that contains configuration settings
const config = require('../config')

// vueLoaderConfig is a custom module that contains configuration settings for vue-loader
const vueLoaderConfig = require('./vue-loader.conf')

// VueLoaderPlugin is a webpack plugin for vue-loader
const VueLoaderPlugin = require('vue-loader/lib/plugin')

// resolve is a helper function that resolves a given directory path
function resolve (dir) {
  return path.join(__dirname, '..', dir) // __dirname is a Node.js global variable that refers to the directory where the currently executing script is located
}

// createLintingRule is a function that creates a webpack rule for linting
const createLintingRule = () => ({
  test: /\.(js|vue)$/, // test property specifies which file types the rule applies to
  loader: 'eslint-loader', // loader property specifies the loader to be used
  enforce: 'pre', // enforce property specifies when the loader should be applied
  include: [resolve('src'), resolve('test')], // include property specifies which directories the rule applies to
  options: {
    formatter: require('eslint-friendly-formatter'), // options property specifies the options to be passed to the loader
    emitWarning: !config.dev.showEslintErrorsInOverlay // emitWarning property specifies whether to emit warnings or errors
  }
})

// module.exports is an object that exports the webpack configuration
module.exports = {
  context: path.resolve(__dirname, '../'), // context property specifies the directory where webpack should start looking for modules
  plugins: [
    new VueLoaderPlugin() // plugins property specifies the webpack plugins to be used
  ],
  entry: { // entry property specifies the entry points for the application
    app: './src/main.ts'
  },
  output: { // output property specifies the output settings for the application
    path: config.build.assetsRoot, // path property specifies the output directory
    filename: '[name].js', // filename property specifies the name of the output file
    publicPath: process.env.NODE_ENV === 'production'
      ? config.build.assetsPublicPath
      : config.dev.assetsPublicPath // publicPath property specifies the public URL for the output files
  },
  resolve: { // resolve property specifies the resolution settings for the application
    extensions: ['.js', '.vue', '.json', '.ts'], // extensions property specifies the file extensions that should be resolved
    alias: { // alias property specifies the module aliases
      'vue$': 'vue/dist/vue.esm.js',
      '@': resolve('src'),
    }
  },
  module: { // module property specifies the module settings for the application
    rules: [
      ...(config.dev.useEslint ? [createLintingRule()] : []), // rules property specifies the loaders and rules for the application

      {
        test: /\.ts$/,
        exclude: /node_modules/,
        loader: 'ts-loader',
        options: {
          appendTsSuffixTo: [/\.vue$/],
          transpileOnly: true
        }
      },
      {
        test: /\.vue$/,
        loader: 'vue-loader',
        options: vueLoaderConfig
      },
      {
        test: /\.js$/,
        loader: 'babel-loader',
        options: {
          presets: ['@babel/preset-env']
        },
        include: [
          resolve('src'),
          resolve('test'),
          resolve('node_modules/webpack-dev-server/client')]
      },
      {
        test: /\.(png|jpe?g|gif|svg)(\?.*)?$/,
        loader: 'url-loader',
        options: {
          limit: 10000,
          name: utils.assetsPath('img/[name].[hash:7].[ext]')
        }
      },
      {
        test: /\.(mp4|webm|ogg|mp3|wav|flac|aac)(\?.*)?$/,
        loader: 'url-loader',
        options: {
          limit: 10000,
          name: utils.assetsPath('media/[name].[hash:7].[ext]')
        }
      },
      {
        test: /\.(woff2?|eot|ttf|otf)(\?.*)?$/,
        loader: 'url-loader',
        options: {
          id: 'font-loader',
          name: '[name].[hash:7].[ext]',
          outputPath: utils.assetsPath('fonts'),
          limit: 10000
        }
      },
      //
      // for vueitfy version 2 migration
      // https://vuetifyjs.com/en/getting-started/quick-start#webpack-install
      {
        test: /\.s(c|a)ss$/,
        exclude: /node_modules/,
        use: [
          'vue-style-loader',
          'css-loader',
          {
            loader: 'sass-loader',
            options: {
              implementation: require('sass'),
              sassOptions: {
                indentedSyntax: true // optional
              },
            },
          },
        ],
      }

    ]
  },
  node: {
    // prevent webpack from injecting useless setImmediate polyfill because Vue
    // source contains it (although only uses it if it's native).
    setImmediate: false,
    // prevent webpack from injecting mocks to Node native modules
    // that does not make sense for the client
    dgram: 'empty',
    fs: 'empty',
    net: 'empty',
    tls: 'empty',
    child_process: 'empty'
  }
}


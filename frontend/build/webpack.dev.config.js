const path = require('path');
const { merge } = require('webpack-merge');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const baseConfig = require('./webpack.base.config.js');

const HOST = 'paas-dev.bktencent.com';
const ORIGIN = `https://${HOST}`;
const SITE_URL = '/o/bk_nocode/';

module.exports = merge(baseConfig, {
  mode: 'development',
  output: {
    path: path.resolve(__dirname, '../dist'),
    filename: '[name][contenthash].js',
  },
  module: {
    rules: [
      {
        test: /\.(css|postcss)$/,
        use: [
          'style-loader',
          'css-loader',
          'postcss-loader',
        ],
      },
    ],
  },
  plugins: [
    new HtmlWebpackPlugin({
      filename: 'index.html',
      template: 'index-dev.html',
      inject: true,
    }),
  ],
  devtool: 'inline-source-map',
  stats: {
    children: false,
    entrypoints: false,
    modules: false,
  },
  devServer: {
    host: 'dev.paas-dev.bktencent.com',
    port: 8001,
    https: ORIGIN.indexOf('https') > -1,
    static: {
      directory: path.posix.join(__dirname, '../static'),
    },
    historyApiFallback: true,
    proxy: {
      [`${SITE_URL}api/*`]: {
        target: `${ORIGIN}`,
        changeOrigin: true,
        secure: false,
        headers: {
          referer: ORIGIN,
        },
      },
      [`${SITE_URL}openapi/*`]: {
        target: `${ORIGIN}`,
        changeOrigin: true,
        secure: false,
        headers: {
          referer: ORIGIN,
        },
      },
    },
  },
});

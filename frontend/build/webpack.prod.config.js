const path = require('path');
const { merge } = require('webpack-merge');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');

const baseConfig = require('./webpack.base.config.js');

module.exports = merge(baseConfig, {
  mode: 'production',
  output: {
    filename: 'assets/js/[name].[contenthash:7].js',
    publicPath: '{{BK_STATIC_URL}}',
  },
  module: {
    rules: [
      {
        test: /.css$/,
        use: [
          {
            loader: MiniCssExtractPlugin.loader,
            options: {
              publicPath: '../../',
            },
          },
          'css-loader',
          'postcss-loader'],
      },
    ],
  },
  plugins: [
    new HtmlWebpackPlugin({
      filename: 'assets/index.html',
      template: 'index.html',
      inject: true,
    }),
    new MiniCssExtractPlugin({
      filename: 'assets/css/[name].[contenthash:10].css',
    }),
  ],
  optimization: {
    minimize: true,
    minimizer: [new CssMinimizerPlugin()],
  },
});

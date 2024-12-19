// webpack.config.js
const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = (env, argv) => {
  const isDevelopment = argv.mode === 'development';

  return {
    entry: {
      main: [
        './scss/styles.scss',
        './js/main.js'
      ]
    },
    output: {
      path: path.resolve(__dirname, 'dist'),
      filename: 'js/[name].bundle.js',
      clean: true
    },
    devtool: isDevelopment ? 'source-map' : false,
    module: {
      rules: [
        {
          test: /\.scss$/,
          use: [
            MiniCssExtractPlugin.loader,
            {
              loader: 'css-loader',
              options: {
                sourceMap: isDevelopment
              }
            },
            {
              loader: 'sass-loader',
              options: {
                sourceMap: isDevelopment,
                sassOptions: {
                  includePaths: ['node_modules'],
                  outputStyle: isDevelopment ? 'expanded' : 'compressed'
                }
              }
            }
          ]
        }
      ]
    },
    plugins: [
      new MiniCssExtractPlugin({
        filename: 'css/[name].css'
      })
    ],
    optimization: {
      minimize: !isDevelopment,
      splitChunks: {
        cacheGroups: {
          styles: {
            name: 'styles',
            test: /\.css$/,
            chunks: 'all',
            enforce: true
          }
        }
      }
    },
    stats: {
      children: false,
      modules: false,
      version: false,
      hash: false,
      builtAt: false,
      entrypoints: false,
      assets: true
    }
  };
};
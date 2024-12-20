const path = require('path');

module.exports = (env, argv) => {
  const isDevelopment = argv.mode === 'development';

  return {
    mode: isDevelopment ? 'development' : 'production',
    entry: './src/js/index.js',
    output: {
      path: path.resolve(__dirname, 'dist/js'),
      filename: '[name].bundle.js',
      clean: true,
    },
    devtool: isDevelopment ? 'source-map' : false,
    module: {
      rules: [
      ],
    },
    resolve: {
      extensions: ['.js'],
    },
    stats: 'normal',
  };
};

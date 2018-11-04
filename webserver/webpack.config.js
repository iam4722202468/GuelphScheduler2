const path = require('path');
const webpack = require('webpack');

module.exports = {
  context: path.resolve(__dirname, 'public'),
  entry: {
    app: ['./javascript/scheduler/main.js', './stylesheets/footer.scss', './stylesheets/index.scss'],
    dist: ['./bootstrap/js/bootstrap.js', './bootstrap/css/bootstrap.css']
  },
  module: {
    rules: [{
      test: /\.(scss|css)$/,
      use: [
        "style-loader", // creates style nodes from JS strings
        "css-loader", // translates CSS into CommonJS
        "sass-loader" // compiles Sass to CSS, using Node Sass by default
      ]
    },
    {
      test: /\.(woff(2)?|ttf|eot|svg)(\?v=\d+\.\d+\.\d+)?$/,
      use: [{
        loader: 'file-loader',
        options: {
          name: '[name].[ext]',
          outputPath: 'fonts/'
        }
      }]
    }]
  },
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: '[name].bundle.js',
  },
};

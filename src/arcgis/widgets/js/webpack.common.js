const path = require("path");

module.exports = {
    devtool: "source-map",
    resolve: {
        extensions: [".ts", ".tsx", ".js", ".jsx"],
    },
    module: {
        rules: [
            { test: /\.css$/,
            //  exclude: [],
              use: ['to-string-loader', 'css-loader'],
            },
            { test: /\.tsx?$/,
              loader: "ts-loader" }
        ]
    },
    externals: ["@jupyter-widgets/base", "@phosphor/widgets"],
}

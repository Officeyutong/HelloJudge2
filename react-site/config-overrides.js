const {
    override,
    addWebpackPlugin
} = require("customize-cra");
const HtmlWebpackTopBannerPlugin = require("./my-html-transformer");
module.exports = override(
    addWebpackPlugin(new HtmlWebpackTopBannerPlugin(`\nMade by MikuNotFoundException\n`))
);
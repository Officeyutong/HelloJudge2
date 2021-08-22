const HtmlWebpackPlugin = require('html-webpack-plugin')
const HtmlWebpackTopBannerPlugin = require('html-webpack-top-banner-plugin');
module.exports = {
    plugins: [
        new HtmlWebpackPlugin(),
        new HtmlWebpackTopBannerPlugin(`<!--
        HelloJudge2, by MikuNotFoundException
        
        辛苦了
        可以哭了
        可以笑着说结束了
        丢下所有规则 忘记所有挫折
        敬自己一杯 因为值得
        ———— B站2021年拜年纪 《时光盲盒》        
        -->`)
    ]
}
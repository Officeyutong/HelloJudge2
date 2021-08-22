const HtmlWebpackPlugin = require('html-webpack-plugin');
class HtmlWebpackTopBannerPlugin {
    banner = ''

    constructor(options) {
        const banner = this.getBannerFromOptions(options)
        this.banner = `<!--${banner.join('\n')}-->\n`
    }

    getBannerFromOptions(options) {
        const isArray = Array.isArray(options)
        if (isArray) {
            return options
        } else if (typeof options === 'string') {
            return [options]
        } else if (typeof options === 'object') {
            return this.getBannerFromOptions(options.banner)
        }
        return []
    }

    apply(compiler) {
        compiler.hooks.compilation.tap(
            'HtmlWebpackTopBannerPlugin',
            (compilation) => {
                HtmlWebpackPlugin.getHooks(compilation).beforeEmit.tapAsync(
                    'HtmlWebpackTopBannerPlugin',
                    (data, callback) => {
                        data.html = this.banner + data.html;
                        callback(null, data)
                    }
                )
            }
        )
    }
}

module.exports = HtmlWebpackTopBannerPlugin

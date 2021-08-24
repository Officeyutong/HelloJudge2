import katex from "katex";
import "katex/contrib/mhchem/mhchem";


const renderKatex = (tex, displaymode) => {
    return katex.renderToString(tex, {
        throwOnError: false,
        displayMode: displaymode,
        output: "html"
    });
};

export { renderKatex };
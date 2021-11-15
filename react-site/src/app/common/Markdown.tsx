import React from "react";
import showdown from "showdown";
import { renderKatex } from "./katex-wrapper";
import { StateType } from "../states/Manager";
import { connect } from "react-redux";
import _ from "lodash";


const TREMA = String.fromCharCode(168);
const DOLLARD_CHR = TREMA + "D";
// const htmlDecode = (input: string) => {
//     let doc = new DOMParser().parseFromString(input, "text/html");
//     return doc.documentElement.textContent!;
// };
const showdownClassMap = {
    h1: 'ui large header',
    h2: 'ui medium header',
    ul: 'ui list',
    li: 'ui item',
    table: "ui table"
};

const showdownBindings = Object.keys(showdownClassMap)
    .map(key => ({
        type: 'output',
        regex: new RegExp(`<${key}(.*)>`, 'g'),
        replace: `<${key} class="${showdownClassMap[key as keyof typeof showdownClassMap]}" $1>`
    }));
const converter = new showdown.Converter({
    extensions: [
        {
            type: 'lang', regex: `${DOLLARD_CHR}${DOLLARD_CHR}([\\S\\s]+?)${DOLLARD_CHR}${DOLLARD_CHR}`, replace: (x: string, y: string) => {
                return renderKatex(y, true);
            }
        },
        {
            type: 'lang', regex: `${DOLLARD_CHR}([\\S\\s]+?)${DOLLARD_CHR}`, replace: (x: string, y: string) => {
                return renderKatex(y, false);
            }
        },
        {
            type: "output",
            regex: /!!!problem-card: ?([0-9]+)!!!/g,
            replace: (str: string, problemID: string) => {
                return `<iframe src="/card/problem/${problemID}" frameborder="0" style="height:75px"> </iframe>`;
            }
        },
        ...showdownBindings
    ],
    tables: true,
    literalMidWordUnderscores: true,
    strikethrough: true
});



const Markdown = connect((state: StateType) => ({ state: state }))
    (((props) => {
        const { markdown } = props;
        return <div dangerouslySetInnerHTML={{ __html: converter.makeHtml(markdown) }} {...(_.omit(props, ["markdown", "state", "dispatch"]))} >

        </div>
    }) as React.FC<{ markdown: string, state: StateType } & React.DetailedHTMLProps<React.HTMLAttributes<HTMLDivElement>, HTMLDivElement>>);

export { converter, Markdown };
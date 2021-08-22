import { useSelector } from "react-redux";
import { StateType } from "./Manager";
import * as ace from 'ace-builds/src-noconflict/ace';
ace.config.set('basePath', '/assets/ui/');
ace.config.set('modePath', '');
ace.config.set('themePath', '');
const themesContext = require.context("ace-builds/src-noconflict", false, /theme-.+\.js$/);
themesContext.keys().forEach(v => {
    themesContext(v);
});
const modesContext = require.context("ace-builds/src-noconflict", false, /mode-.+\.js$/);
modesContext.keys().forEach(v => {
    modesContext(v);
});
export function useAceTheme() {
    const theme = useSelector((s: StateType) => s.userConfig.aceTheme);
    return theme;
}
export function useAceThemeURL() {
    const theme = useAceTheme();
    return `ace-builds/src-noconflict/theme-${theme}`;
}
export function useAceThemeTuple(): [string, string] {
    const theme = useAceTheme();
    return [theme, `ace-builds/src-noconflict/theme-${theme}`];
}
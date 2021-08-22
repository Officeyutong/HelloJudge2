import React from "react";
import { useAceTheme } from "../../states/StateUtils";
import AceEditor from "react-ace";
interface SimpleAceWrapperProps {
    value: string;
    onChange: (d: string) => void;
    mode: string;
};

const SimpleAceWrapper: React.FC<SimpleAceWrapperProps> = (props) => {
    const theme = useAceTheme();

    return <AceEditor
        value={props.value}
        onChange={props.onChange}
        theme={theme}
        mode={props.mode}
        width="100%"
        height="200px"
        wrapEnabled
        style={{
            borderWidth:"1px",
            borderStyle:"solid",
            borderColor:"rgba(34, 36, 38, 0.15)"
        }}
    ></AceEditor>
};

export default SimpleAceWrapper;
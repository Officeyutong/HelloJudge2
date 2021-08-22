import React from "react";
import { Label, SemanticCOLORS } from "semantic-ui-react";
import { ProblemTagEntry } from "../../common/types";

interface ProblemTagLabelProps {
    data: Pick<ProblemTagEntry, "color" | "display">;
    onClick?: () => void;
};

const ProblemTagLabel: React.FC<ProblemTagLabelProps> = (props) => {
    const clickable = props.onClick !== undefined;
    return <Label onClick={props.onClick} style={clickable ? { cursor: "pointer" } : undefined} size="tiny" color={props.data.color as SemanticCOLORS}>
        {props.data.display}
    </Label>
};

export default ProblemTagLabel;
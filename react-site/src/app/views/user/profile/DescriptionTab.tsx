import React from "react";
import { Markdown } from "../../../common/Markdown";

const DescriptionTab: React.FC<{ data: string }> = ({ data }) => {
    return data.trim() === "" ? <div style={{ height: "100%" }}>这个人好懒...什么都没有写...</div> : <div style={{ maxHeight: "1000px" }}>
        <Markdown
            markdown={data}
        ></Markdown>
    </div>
};

export default DescriptionTab;

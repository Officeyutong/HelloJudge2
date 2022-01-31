import React from "react";
import { useParams } from "react-router-dom";

const WikiVersionList: React.FC<{}> = () => {
    const { page } = useParams<{ page: string }>();
    const numberPage = parseInt(page);
    
    return <></>;
}
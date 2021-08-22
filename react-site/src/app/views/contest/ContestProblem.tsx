import QueryString from "qs";
import React from "react";
import { useLocation, useParams } from "react-router";

const ContestProblem: React.FC<{}> = () => {
    const { contestID, problemID } = useParams<{ contestID: string; problemID: string }>();
    const location = useLocation();
    const virtualID = parseInt(QueryString.parse(location.search).virtualID as string || "-1");
    const numberContestID = parseInt(contestID);
    
    return <div>
        {`contest: ${contestID} problem: ${problemID} virtual: ${virtualID}`}
    </div>;
};

export default ContestProblem;
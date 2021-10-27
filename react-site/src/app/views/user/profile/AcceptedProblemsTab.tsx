import React from "react";
import { Grid } from "semantic-ui-react";
import { UserProfileResponse } from "../client/types";

const AcceptedProblemsTab: React.FC<{ data: UserProfileResponse["ac_problems"] }> = ({ data }) => {

    return <div>
        {data.length === 0 ? <div>这个人很懒，还没做过题</div> : <>
            <div style={{ color: "grey", marginBottom: "10px" }}>此处仅统计非比赛提交和已经关闭了的比赛中的提交，且不一定会即时更新。</div>
            <Grid style={{ marginRight: "5px" }} columns="10">
                {data.map((x, i) => <Grid.Column key={i}>
                    <span>[<a href={`/show_problem/${x}`}>{x}</a>]</span>
                </Grid.Column>)}
            </Grid>
        </>}
    </div>;
};
export default AcceptedProblemsTab;
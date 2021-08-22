import React from "react";
import { Grid, Icon, SemanticICONS, Statistic } from "semantic-ui-react";
import { GeneralInfo } from "../client/types";


const GeneralView: React.FC<{ data: GeneralInfo }> = ({ data }) => {

    return <div>
        <Grid columns="3">
            {[
                { icon: "tasks" as SemanticICONS, title: "题目数量", value: data.problemCount },
                { icon: "tasks" as SemanticICONS, title: "公开题目数量", value: data.publicProblemCount },
                { icon: "address card" as SemanticICONS, title: "用户数量", value: data.userCount },
                { icon: "hdd" as SemanticICONS, title: "提交数量", value: data.submissionCount },
                { icon: "hdd" as SemanticICONS, title: "通过提交数量", value: data.acceptedSubmissionCount },
                { icon: "keyboard" as SemanticICONS, title: "讨论数量", value: data.discussionCount },
                { icon: "hdd" as SemanticICONS, title: "今日提交数量", value: data.todaySubmissionCount },
                { icon: "hdd" as SemanticICONS, title: "今日编译错误提交数量", value: data.todayCESubmissionCount },
            ].map((x, i) => <Grid.Column key={i}>
                <Statistic>
                    <Statistic.Value>
                        <Icon name={x.icon}></Icon>
                        {x.value}
                    </Statistic.Value>
                    <Statistic.Label>{x.title}</Statistic.Label>
                </Statistic>
            </Grid.Column>)}
        </Grid>
    </div>;
};

export default GeneralView;
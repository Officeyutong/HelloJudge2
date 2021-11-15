import { useEffect, useState } from "react";
import { useParams } from "react-router";
import { Dimmer, Grid, Loader, Segment } from "semantic-ui-react";
import { useBaseViewDisplay } from "../../states/StateUtils";
import JudgeStatusLabel from "../utils/JudgeStatusLabel";
import ScoreLabel from "../utils/ScoreLabel";
import cardClient from "./client/CardClient";
import { ProblemCardResponse } from "./client/types";

const ProblemCard: React.FC<{}> = () => {
    const { id } = useParams<{ id: string }>();
    const numberId = parseInt(id);
    const [loaded, setLoaded] = useState(false);
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState<null | ProblemCardResponse>(null);
    const [, setDisplayBaseView] = useBaseViewDisplay();
    useEffect(() => {
        setDisplayBaseView(false);
        const rawVal = document.body.style.overflowX;
        const color = document.body.style.backgroundColor;
        document.body.style.backgroundColor = "white"
        document.body.style.overflowX = "hidden";
        return () => {
            setDisplayBaseView(true);
            document.body.style.overflowX = rawVal;
            document.body.style.backgroundColor = color;
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);
    useEffect(() => {
        if (!loaded) {
            let cancelled = false;
            (async () => {
                try {
                    setLoading(true);
                    const resp = await cardClient.getProblemCard(numberId);
                    if (!cancelled) {
                        setData(resp);
                        setLoading(false);
                        setLoaded(true);
                    }
                } catch { } finally { }
            })();
            return () => cancelled = true;
        }
        return () => { };
    }, [loaded, numberId])
    return <>
        {!loaded && loading && <>
            <div style={{ height: "50px", width: "100px" }}>
                <Dimmer active>
                    <Loader></Loader>
                </Dimmer>
            </div>
        </>}
        {loaded && data !== null && <>
            <Segment style={{ width: "fit-content" }}>
                <Grid columns="1">
                    <Grid.Column>
                        <a href={`/show_problem/${data.id}`} target="_blank" rel="noreferrer">#{data.id}. {data.title}</a>
                        提交: {data.submitCount} | 通过: {data.acceptedCount}
                    </Grid.Column>
                </Grid>
                {data.myStatus !== null && <div>
                    <a href={`/show_submission/${data.myStatus.submissionID}`} target="_blank" rel="noreferrer">
                        <ScoreLabel {...data.myStatus}></ScoreLabel>
                        <JudgeStatusLabel {...data.myStatus}></JudgeStatusLabel>
                    </a>
                </div>}

            </Segment>
        </>}
    </>;
};

export default ProblemCard;
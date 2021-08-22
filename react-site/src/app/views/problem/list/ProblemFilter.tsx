import React, { useMemo, useState } from "react";
import { Button, Container, Divider, Grid, Header, Input } from "semantic-ui-react";
import { KeyDownEvent, ProblemTagEntry } from "../../../common/types";
import { useInputValue } from "../../../common/Utils";
import ProblemTagLabel from "../../utils/ProblemTagLabel";
import { ProblemSearchFilter } from "../client/types";

interface ProblemFilterProps {
    filter: ProblemSearchFilter;
    update: (d: ProblemSearchFilter) => void;
    allTags: ProblemTagEntry[];
}

const ProblemFilter: React.FC<ProblemFilterProps> = ({
    filter, update, allTags
}) => {
    const keyword = useInputValue(filter.searchKeyword || "");
    const [usedTags, setUsedTags] = useState(filter.tag || []);
    const tagsMapping = useMemo(() => new Map(allTags.map(x => ([x.id, x]))), [allTags]);
    const [showTags, setShowTags] = useState(false);
    const apply = () => {
        update({ searchKeyword: keyword.value === "" ? undefined : keyword.value, tag: usedTags.length === 0 ? undefined : usedTags });
    }
    return <>
        <Container style={{ marginTop: "30px" }}>
            <Grid columns="2">
                <Grid.Column>
                    <Input placeholder="按回车键发起搜索" icon="search" {...keyword} onKeyDown={(evt: KeyDownEvent) => {
                        if (evt.key === "Enter") apply();
                    }}></Input>
                </Grid.Column>
                <Grid.Column>
                    <Container textAlign="right">
                        <Button size="tiny" onClick={() => setShowTags(c => !c)} color="green">
                            {showTags ? "隐藏" : "题目标签筛选"}
                        </Button>
                    </Container>
                </Grid.Column>
            </Grid>
        </Container>
        {showTags && <Container>
            <Header as="h3">
                所有标签
            </Header>
            <div>
                {allTags.map((x, i) => <ProblemTagLabel
                    key={i}
                    data={x}
                    onClick={() => setUsedTags(c => [...c.filter(y => y !== x.id), x.id])}
                ></ProblemTagLabel>)}
            </div>
            <Divider></Divider>
            <Header as="h3">
                已选中标签
            </Header>
            <div>
                {usedTags.map((x, u) => <ProblemTagLabel
                    data={tagsMapping.get(x)!}
                    onClick={() => setUsedTags(c => c.filter(y => y !== x))}
                ></ProblemTagLabel>)}
            </div>
            <Button color="red" size="tiny" onClick={apply}>
                执行搜索
            </Button>
        </Container>}
    </>;
};

export default ProblemFilter;
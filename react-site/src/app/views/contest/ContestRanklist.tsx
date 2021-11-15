import QueryString from "qs";
import React, { useEffect, useState } from "react";
import { useLocation, useParams } from "react-router-dom";
import { Button, Dimmer, Header, Label, Loader, Message, Segment, Table } from "semantic-ui-react";
import { useDocumentTitle } from "../../common/Utils";
import contestClient from "./client/ContestClient";
import { ContestRanklist as ContestRanklistType } from "./client/types";
// import XLSX from "xlsx";
import XLSX from "xlsx-js-style";
import { DateTime } from "luxon";
import { ButtonClickEvent } from "../../common/types";
(window as (typeof window) & { qwq: any }).qwq = DateTime;
const ContestRanklist: React.FC<{}> = () => {
    const { contestID } = useParams<{ contestID: string }>();
    const { search } = useLocation();
    const queryArgs = QueryString.parse(search.substr(1));
    const virtualID = parseInt(queryArgs.virtual_contest as (string | undefined) || "-1");
    const [loaded, setLoaded] = useState(false);
    const [data, setData] = useState<ContestRanklistType | null>(null);
    useEffect(() => {
        if (!loaded) {
            (async () => {
                try {
                    const resp = await contestClient.getContestRanklist(parseInt(contestID), virtualID);
                    setData(resp);
                    setLoaded(true);
                } catch { } finally {

                }
            })();
        }
    }, [contestID, loaded, virtualID]);
    useDocumentTitle(`${data?.name} - ${contestID} - 排行榜`);
    const refreshRanklist = async (evt: ButtonClickEvent) => {
        const target = evt.currentTarget;
        try {
            target.classList.add("loading");
            await contestClient.refreshRanklist(parseInt(contestID), virtualID);
            setLoaded(false);
        } catch { } finally {
            target.classList.remove("loading");
        }
    };
    const exportToExcel = (evt: React.MouseEvent<HTMLButtonElement, MouseEvent>) => {
        if (data === null) return;
        const target = evt.currentTarget;
        try {
            target.classList.add("loading");
            const workbook = XLSX.utils.book_new();
            const sheetData: string[][] = [];
            sheetData.push([
                "排名", "用户名", "总分(分数/总时间 或 通过数/罚时)", ...data.problems.map((x, i) => `#${i}. ${x.name}`)
            ]);
            sheetData.push([
                "合计", "通过提交数", "---", ...data.problems.map((x, i) => `${x.accepted_submit}`)
            ]);
            sheetData.push([
                "合计", "总提交数", "---", ...data.problems.map((x, i) => `${x.total_submit}`)
            ]);
            const greenCells: string[] = [];
            const redCells: string[] = [];
            let currRow = 3;
            for (const line of data.ranklist) {
                const row = currRow;
                sheetData.push([
                    `${line.rank}`,
                    `${line.username}${line.virtual ? "[虚拟提交]" : ""}`,
                    data.using_penalty ? `${line.total.ac_count}/${line.total.penalty}` : `${line.total.score}/${line.total.submit_time_sum}`,
                    ...line.scores.map((x, i) => {
                        if (x.status === "accepted") greenCells.push(XLSX.utils.encode_cell({ r: row, c: i + 3 }));
                        if (x.status === "unaccepted") redCells.push(XLSX.utils.encode_cell({ r: row, c: i + 3 }));

                        if (x.submit_id === -1) return "未提交";
                        if (!data.using_penalty) return `${x.score}/${x.submit_time}`;
                        return x.status === "accepted" ? `-${x.submit_count}(${x.penalty})` : `-${x.submit_count}`;
                    })
                ]);
                currRow++;
            }

            const sheet = XLSX.utils.aoa_to_sheet(sheetData);
            // XLSX.SSF.format()
            greenCells.forEach(x => {
                const cell: XLSX.CellObject = sheet[x];
                cell.s = {
                    fill: {
                        fgColor: {
                            rgb: "FF00FF00"
                        },
                        // patternType: "solid"
                    }
                }
            });
            redCells.forEach(x => {
                const cell: XLSX.CellObject = sheet[x];
                cell.s = {
                    fill: {
                        fgColor: {
                            rgb: "FFFF0000"
                        },
                        // patternType: "solid"
                    }
                }
            });
            sheet["!cols"] = [{ width: 10 }, { width: 20 }];
            XLSX.utils.book_append_sheet(workbook, sheet, "ranklist");
            XLSX.writeFile(workbook, `${data?.name} - 排行榜 - ${DateTime.now().toJSDate().toLocaleString()}.xlsx`)
        } catch (e) {
            console.error(e);
        } finally {
            target.classList.remove("loading");
        }
    };
    return <>
        {!loaded && <Segment>
            <div style={{ height: "400px" }}>
                <Dimmer active>
                    <Loader>加载中..</Loader>
                </Dimmer>
            </div></Segment>}
        {loaded && data !== null && <div>
            <Header as="h1">
                {data.name} - 排行榜
            </Header>

            <Segment stacked style={{ overflowX: "scroll" }}>
                <Message info>
                    <Message.Header>
                        提示
                    </Message.Header>
                    <Message.Content>
                        <p>{!data.running && "当前比赛已结束，"}排行榜每 {data.refresh_interval} 秒刷新一次。</p>
                        {virtualID !== -1 && <p>
                            当前显示的为虚拟比赛的排行榜。
                        </p>}
                    </Message.Content>
                </Message>
                <Table className="ranklist-table" basic="very">
                    <Table.Header>
                        <Table.Row>
                            <Table.HeaderCell></Table.HeaderCell>
                            <Table.HeaderCell>用户名</Table.HeaderCell>
                            <Table.HeaderCell textAlign="center">总分</Table.HeaderCell>
                            {data.problems.map((x, i) => <Table.HeaderCell textAlign="center" style={{ minWidth: "100px" }} key={i}>
                                <a href={`/contest/${contestID}/problem/${x.id}`}>#{x.id + 1}. {x.name}</a>
                                <div>
                                    <span style={{ color: "green" }}>{x.accepted_submit}</span>/{x.total_submit}
                                </div>
                            </Table.HeaderCell>)}
                        </Table.Row>
                    </Table.Header>
                    <Table.Body>
                        {data.ranklist.map((x, i) => <Table.Row key={i}>
                            <Table.Cell textAlign="center">
                                {(() => {
                                    switch (x.rank) {
                                        case 1:
                                            return <Label ribbon color="yellow">1</Label>
                                        case 2:
                                            return <Label ribbon >2</Label>
                                        case 3:
                                            return <Label color="brown" ribbon>3</Label>
                                        default:
                                            return <div>{x.rank}</div>
                                    }
                                })()}
                            </Table.Cell>
                            <Table.Cell>
                                <a href={`/profile/${x.uid}`}>{x.username}</a>
                                {x.virtual && <Label color="red">虚拟提交</Label>}
                            </Table.Cell>
                            <Table.Cell textAlign="center">
                                {data.using_penalty ? <span>
                                    <div style={{ color: "green" }}>{x.total.ac_count}</div>
                                    <div style={{ color: "red" }}>{x.total.penalty}</div>
                                </span> : <span>
                                    <div style={{ color: "green" }}>{x.total.score}</div>
                                    <div style={{ color: "red" }}>{x.total.submit_time_sum}</div>
                                </span>}
                            </Table.Cell>
                            {x.scores.map((y, j) => <Table.Cell textAlign="center" positive={y.status === "accepted"} negative={y.status === "unaccepted"} key={j}>
                                {y.submit_id !== -1 && <div>
                                    <a href={`/show_submission/${y.submit_id}`}>
                                        {data.using_penalty === false ? <span>
                                            <div>{y.score}</div>
                                            <div style={{ color: "red" }}>{y.submit_time}</div>
                                        </span> : <span>
                                            {y.status === "accepted" ? <div>
                                                <div>-{y.submit_count}</div>
                                                <div style={{ color: "red" }}>{y.penalty}</div>
                                            </div> : <div>-{y.submit_count}</div>}
                                        </span>}
                                    </a>
                                </div>}
                            </Table.Cell>)}
                        </Table.Row>)}
                    </Table.Body>
                </Table>
            </Segment>
            <div>
                <Segment style={{ width: "max-content" }} >
                    <Button size="tiny" color="green" onClick={exportToExcel}>导出为Excel文档</Button>
                    {data.managable && <Button size="tiny" color="green" onClick={refreshRanklist}>刷新排行榜</Button>}
                </Segment>
            </div>
        </div>}
    </>;

};

export default ContestRanklist;

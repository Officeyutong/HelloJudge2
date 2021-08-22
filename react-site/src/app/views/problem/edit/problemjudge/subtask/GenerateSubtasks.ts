import _ from "lodash";
import { ProblemDataProps } from "../ProblemJudgeTab";
type SubtaskType = ProblemDataProps["subtasks"];
const generateSubtasks = (files: ProblemDataProps["files"]): SubtaskType => {
    const fileNames = files.map(x => x.name);
    const rawNames = new Set(fileNames);
    const majorNames = new Set(
        _(fileNames)
            .filter(
                x => x.endsWith(".ans") || x.endsWith(".out") || x.endsWith(".in")
            )
            .map(x => x.substr(0, x.lastIndexOf(".")))
            .value());
    const casePairs: [string, string][] = [];
    majorNames.forEach(v => {
        const inName = `${v}.in`;
        if (rawNames.has(inName)) {
            const ansName = `${v}.ans`;
            const outName = `${v}.out`;
            if (rawNames.has(outName)) {
                casePairs.push([inName, outName]);
            } else if (rawNames.has(ansName)) {
                casePairs.push([inName, ansName]);
            }
        }
    });
    casePairs.sort(([a, b], [c, d]) => {
        if (a === c) return 0;
        else if (a < c) return -1;
        else return 1;
    });
    const remScore = 100 % casePairs.length;
    const subtasks: SubtaskType = [
        {
            name: "默认子任务",
            comment: `共 ${casePairs.length} 个测试点`,
            memory_limit: 512,
            time_limit: 1000,
            method: "sum",
            score: 100,
            testcases: casePairs.map(([x, y]) => ({
                input: x,
                output: y,
                full_score: Math.floor(100 / casePairs.length)
            }))
        }
    ];
    _.last(subtasks[0].testcases)!.full_score += remScore;
    return subtasks;
};

export default generateSubtasks;
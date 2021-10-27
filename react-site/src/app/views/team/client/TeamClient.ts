import QueryString from "qs";
import GeneralClient from "../../../common/GeneralClient";
import { TeamDetail, TeamFileEntry, TeamListEntry, TeamRawData, TeamThingsAddedResponse, TeamUpdateInfo } from "./types";

class TeamClient extends GeneralClient {

    async addTeamThings(teamID: number, problems: number[], contests: number[], problemsets: number[]): Promise<TeamThingsAddedResponse> {
        return (await this.client!.post("/api/team/add_problem_or_contest_or_problemset", { teamID, problems, contests, problemsets })).data;
    }
    async getTeamList(): Promise<TeamListEntry[]> {
        return (await this.client!.post("/api/team/list")).data;
    }
    async createTeam(): Promise<{ team_id: number }> {
        return (await this.unwrapExtraClient!.post("/api/team/create")).data;
    }
    async joinTeam(uid: number, team_id: number, invite_code: string) {
        await this.client!.post("/api/team/join", QueryString.stringify({ uid, team_id, invite_code }));
    }
    async quitTeam(uid: number, team_id: number) {
        await this.client!.post("/api/team/quit", QueryString.stringify({ uid, team_id }));
    }
    async teamSetAdmin(team_id: number, uid: number, value: boolean) {
        await this.client!.post("/api/team/set_admin", QueryString.stringify({ uid, team_id, value }));
    }
    async getTeamDetail(team_id: number): Promise<TeamDetail> {
        return (await this.client!.post("/api/team/show", QueryString.stringify({ team_id }))).data;
    }
    async getTeamRawData(team_id: number): Promise<TeamRawData> {
        return (await this.client!.post("/api/team/raw_data", QueryString.stringify({ team_id }))).data;
    }
    async updateTeamInfo(team_id: number, data: TeamUpdateInfo) {
        await this.client!.post("/api/team/update", QueryString.stringify({ team_id: team_id, data: JSON.stringify(data) }));
    }
    async batchAddMembers(team: number, uid: number[], setAdmin: boolean): Promise<void> {
        await this.client!.post("/api/team/invite", { team, uid, setAdmin });
    }
    async getTeamFiles(teamID: number): Promise<TeamFileEntry[]> {
        return (await this.client!.post("/api/team/get_files", { teamID })).data;
    }
    async removeTeamFile(teamID: number, fileID: string) {
        await this.client!.post("/api/team/remove_file", { teamID, fileID });
    }
    async uploadTeamFile(teamID: number, files: FormData, prorgressHandler: (evt: ProgressEvent) => void) {
        await this.unwrapClient!.post(`/api/team/upload_file`, files, {
            headers: { 'Content-Type': 'multipart/form-data' },
            onUploadProgress: prorgressHandler,
            params: { teamID }
        });
    }
};

const teamClient = new TeamClient();

export default teamClient;

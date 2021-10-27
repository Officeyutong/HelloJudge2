import { GeneralUserEntry } from "../../../common/types";

interface TeamListEntry {
    name: string;
    id: number;
    owner_id: number;
    owner_username: string;
    member_count: number;
    private: boolean;
    accessible: boolean;
};
interface TeamDetail {
    // 是否有team.manage权限
    canManage: boolean;
    id: number;
    name: string;
    description: string;
    owner_id: number;
    owner_username: string;
    admins: number[];
    members: { username: string; uid: number; email: string; group_name: string; }[];
    create_time: string;
    // 是否有查看团队详细信息、自由加入退出的权限
    hasPermission: boolean;
    private: boolean;
    team_problems: { id: number; title: string }[];
    team_contests: { id: number; name: string; start_time: number }[];
    team_problemsets: { id: number; name: string }[];
};
interface TeamThingsAddedResponse {
    team_problems: { id: number; title: string }[];
    team_contests: { id: number; name: string }[];
    team_problemsets: { id: number; name: string }[];
};
interface TeamRawData {
    id: number;
    name: string;
    description: string;
    private: boolean;
    invite_code: string;
    tasks: { name: string; problems: number[] }[];
    team_problems: number[];
    team_contests: number[];
    team_problemsets: number[];
};
interface TeamUpdateInfo {
    name: string;
    description: string;
    tasks: { name: string; problems: number[] }[];
    private: boolean;
    invite_code: string;
    team_problems: number[];
    team_contests: number[];
    team_problemsets: number[];
};

interface TeamFileEntry {
    file_id: string;
    filename: string;
    filesize: number;
    upload_time: number;
    uploader: GeneralUserEntry;
};

export type {
    TeamListEntry,
    TeamDetail,
    TeamRawData,
    TeamUpdateInfo,
    TeamThingsAddedResponse,
    TeamFileEntry
};
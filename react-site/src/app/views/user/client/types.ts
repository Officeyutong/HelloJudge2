import { GeneralUserEntry } from "../../../common/types";

interface UserProfileResponse {
    id: number;
    banned: number;
    username: string;
    description: string;
    email: string;
    register_time: string;
    rating: number;
    rating_history: { result: number; contest_id: number; contest_name: string }[];
    permission_group: string;
    permissions: string[];
    phone_verified: boolean;
    following: boolean;
    phone_number?: string;
    ac_problems: number[];
    joined_teams: { id: number; name: string }[];
    group_name: string;
    group_permissions: string[];
    managable: boolean; //是否有user.manage权限
    canSetAdmin: boolean; //是否有permission.manage权限

};

interface UserProfileUpdateRequest {
    banned: number;
    username: string;
    email: string;
    description: string;
    changePassword: boolean;
    newPassword: string;
    permission_group: string;
    permissions: string[];
};
interface FollowerItem extends GeneralUserEntry {
    time: string;
    followedByMe: boolean;

};
interface FolloweeItem extends GeneralUserEntry {
    time: string;
    followedByMe: boolean;
}

interface GlobalRanklistItem {
    username: string;
    uid: number;
    rating: number;
    description: string;
};

export type {
    UserProfileResponse,
    UserProfileUpdateRequest,
    FolloweeItem,
    FollowerItem,
    GlobalRanklistItem
};
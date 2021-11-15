import qs from "qs";
import GeneralClient from "../../../common/GeneralClient";
import { FolloweeItem, FollowerItem, GlobalRanklistItem, UserProfileResponse, UserProfileUpdateRequest } from "./types";

class UserClient extends GeneralClient {
    async doLogin(identifier: string, password: string) {
        await this.client!.post("/api/login", qs.stringify({ identifier: identifier, password: (password) }));
    }
    async doRequireResetPassword(identifier: string) {
        await this.client!.post("/api/require_reset_password", qs.stringify({ identifier: identifier }));
    }
    async doEmailRegister(username: string, password: string, email: string) {
        await this.client!.post("/api/register", qs.stringify({ username: username, password: password, email: email }));
    }
    async doPhoneRegister(username: string, password: string, email: string, phone: string, authcode: string) {
        await this.client!.post("/api/phoneuser/register", { username: username, password: password, email: email, phone: phone, authcode: authcode });
    }
    async doEmailResetPassword(identifier: string, passwordHash: string, reset_token: string) {
        await this.client!.post("/api/reset_password", qs.stringify({ identifier: identifier, password: passwordHash, reset_token: reset_token }));
    }
    async doEmailAuth(username: string, token: string) {
        await this.client!.post("/api/auth_email", qs.stringify({ username: username, token: token }));
    }
    async doPhoneResetPassword(phone: string, passwordHash: string, authcode: string) {
        await this.client!.post("/api/phoneuser/reset_password", { phone: phone, password: passwordHash, authcode: authcode });
    }
    async checkPhoneUsing(phone: string): Promise<{ using: boolean }> {
        return (await this.client!.post("/api/phoneuser/check_phone", { phone: phone })).data;
    }
    async getUserProfile(uid: number): Promise<UserProfileResponse> {
        return (await this.client!.post("/api/get_user_profile", qs.stringify({ uid: uid }))).data;
    }
    async toggleAdminMode() {
        await this.client!.post("/api/user/toggle_admin_mode");
    }
    async toggleFollowState(target: number): Promise<{ followed: boolean }> {
        return (await this.client!.post("/api/user/toggle_follow_state", { target: target })).data;
    }
    async getFolloweeList(source: number, page: number): Promise<{ data: FolloweeItem[]; pageCount: number }> {
        return (await this.unwrapClient!.post("/api/user/get_followee_list", { source: source, page: page })).data;
    }
    async getFollowerList(target: number, page: number): Promise<{ data: FollowerItem[]; pageCount: number }> {
        return (await this.unwrapClient!.post("/api/user/get_follower_list", { target: target, page: page })).data;
    }
    async updateProfile(uid: number, data: UserProfileUpdateRequest) {
        await this.client!.post("/api/update_profile", qs.stringify({
            uid: uid,
            data: JSON.stringify(data)
        }));
    }
    async getAllPermissions(uid: number): Promise<string[]> {
        return (await this.client!.post("/api/permission/get_all_permissions", { uid: uid })).data;
    }
    async forgetUsername(phone: string, code: string): Promise<{ username: string }> {
        return (await this.client!.post("/api/phoneuser/forget_username", {
            phone: phone,
            code: code
        })).data;
    }
    async getGlobalRanklist(page: number, search: string = ""): Promise<{ pageCount: number; ranklist: GlobalRanklistItem[] }> {
        return (await this.client!.post("/api/ranklist", {
            page, search
        })).data;
    }
    async doPhoneAuth(code: string, phone: string) {
        await this.client!.post("/api/phoneauth/auth", { code, phone });
    }
};

const userClient = new UserClient();

export default userClient;

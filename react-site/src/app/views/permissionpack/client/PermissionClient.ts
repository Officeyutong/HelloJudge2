import GeneralClient from "../../../common/GeneralClient";
import { PermissionPackDetail, PermissionPackListItem, PermissionPackUserItem, UserPermissionPackDetail } from "./types";

class PermissionPackClient extends GeneralClient {
    async createPermissionPack(): Promise<{ id: number; name: string }> {
        return (await this.unwrapClient!.post("/api/permissionpack/create")).data;
    }
    async removePermissionPack(id: number) {
        await this.client!.post("/api/permissionpack/remove", { id: id });
    }
    async listPermissionPacks(): Promise<PermissionPackListItem[]> {
        return (await this.client!.post("/api/permissionpack/all")).data;
    }
    async getPermissionPackDetail(packID: number): Promise<PermissionPackDetail> {
        return (await this.client!.post("/api/permissionpack/detail", { packID: packID })).data;
    }
    async getPermissionPackUsers(packID: number, page: number): Promise<{ pageCount: number; data: PermissionPackUserItem[] }> {
        return (await this.unwrapClient!.post("/api/permissionpack/users", { packID: packID, page: page })).data;
    }
    async removePermissionPackUsers(packID: number, toRemove: string[] = [], removeAll: boolean = false) {
        await this.client!.post("/api/permissionpack/users/remove", { packID: packID, toRemove: toRemove, removeAll: removeAll });
    }
    async updatePermissionPackDetails(packID: number, name: string, description: string, permissions: string[]) {
        await this.client!.post("/api/permissionpack/update", { packID: packID, name: name, description: description, permissions: permissions });
    }
    async getPermissionPacksForCurrentUser(): Promise<UserPermissionPackDetail[]> {
        return (await this.client!.post("/api/permissionpack/user_packs")).data;
    }
    async claimPermissionPack(packID: number) {
        return (await this.client!.post("/api/permissionpack/claim", { packID: packID }));
    }
    async uploadUserList(pack_id: number, column: number, files: FormData, progressHandler: any) {
        files.set("pack_id", pack_id.toString());
        files.set("column", column.toString());
        await this.client!.post("/api/permissionpack/users/upload", files, { headers: { 'Content-Type': 'multipart/form-data' }, onUploadProgress: progressHandler });

    }
};
const permissionPackClient = new PermissionPackClient();

export default permissionPackClient;

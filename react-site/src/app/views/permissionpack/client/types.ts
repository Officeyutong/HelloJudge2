
interface PermissionPackListItem {
    id: number;
    name: string;
    permissionCount: number;
    userCount: number;
};
interface PermissionPackDetail {
    name: string;
    id: number;
    permissions: string[];
    description: string;
};
interface PermissionPackUserItem {
    phone: string;
    username: "[用户未注册]" | string;
    claimed: boolean;
};
interface UserPermissionPackDetail {
    id: number;
    name: string;
    description: string | null;
    permissions: string[];
    claimed: boolean;
};
export type {
    PermissionPackListItem,
    PermissionPackDetail,
    PermissionPackUserItem,
    UserPermissionPackDetail
}
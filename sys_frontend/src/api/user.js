/** @format */

import request from "@/utils/request";

// 获取用户列表
export function getUserList(params) {
	return request({
		url: "/admin-api/user/users/",
		method: "get",
		params,
	});
}

// 获取用户详情
export function getUserDetail(id) {
	return request({
		url: `/admin-api/user/users/${id}/`,
		method: "get",
	});
}

// 更新用户状态
export function updateUserStatus(id, data) {
	return request({
		url: `/admin-api/user/users/${id}/toggle_active/`,
		method: "post",
		data,
	});
}

// 删除用户
export function deleteUser(id) {
	return request({
		url: `/admin-api/user/users/${id}/`,
		method: "delete",
	});
}

// 获取用户统计
export function getUserStats() {
	return request({
		url: "/admin-api/user/users/statistics/",
		method: "get",
	});
}

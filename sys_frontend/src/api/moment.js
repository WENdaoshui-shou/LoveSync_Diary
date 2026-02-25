/** @format */

import request from "@/utils/request";

// 动态管理API
export function getMomentList(params) {
	return request({
		url: "/admin-api/moment/moments/",
		method: "get",
		params,
	});
}

export function getMomentDetail(id) {
	return request({
		url: `/admin-api/moment/moments/${id}/`,
		method: "get",
	});
}

export function toggleMomentShare(id) {
	return request({
		url: `/admin-api/moment/moments/${id}/toggle_share/`,
		method: "post",
	});
}

export function deleteMoment(id) {
	return request({
		url: `/admin-api/moment/moments/${id}/`,
		method: "delete",
	});
}

export function getMomentStatistics() {
	return request({
		url: "/admin-api/moment/moments/statistics/",
		method: "get",
	});
}

export function getHotMoments(params) {
	return request({
		url: "/admin-api/moment/moments/hot_moments/",
		method: "get",
		params,
	});
}

// 评论管理API
export function getCommentList(params) {
	return request({
		url: "/admin-api/moment/comments/",
		method: "get",
		params,
	});
}

export function deleteComment(id) {
	return request({
		url: `/admin-api/moment/comments/${id}/`,
		method: "delete",
	});
}

export function getCommentStatistics() {
	return request({
		url: "/admin-api/moment/comments/statistics/",
		method: "get",
	});
}

// 标签管理API
export function getTagList(params) {
	return request({
		url: "/admin-api/moment/tags/",
		method: "get",
		params,
	});
}

export function deleteTag(id) {
	return request({
		url: `/admin-api/moment/tags/${id}/delete_tag/`,
		method: "delete",
	});
}

export function getTagStatistics() {
	return request({
		url: "/admin-api/moment/tags/statistics/",
		method: "get",
	});
}

/** @format */

import request from "@/utils/request";

// 专栏管理API
export function getColumnList(params) {
	return request({
		url: "/admin-api/community/articles/",
		method: "get",
		params,
	});
}

export function getColumnDetail(id) {
	return request({
		url: `/admin-api/community/articles/${id}/`,
		method: "get",
	});
}

export function createColumn(data) {
	return request({
		url: "/admin-api/community/articles/",
		method: "post",
		data,
	});
}

export function updateColumn(id, data) {
	return request({
		url: `/admin-api/community/articles/${id}/`,
		method: "put",
		data,
	});
}

export function deleteColumn(id) {
	return request({
		url: `/admin-api/community/articles/${id}/`,
		method: "delete",
	});
}

export function getColumnStatistics() {
	return request({
		url: "/admin-api/community/articles/statistics/",
		method: "get",
	});
}

// 活动管理API
export function getEventList(params) {
	return request({
		url: "/admin-api/community/events/",
		method: "get",
		params,
	});
}

export function getEventDetail(id) {
	return request({
		url: `/admin-api/community/events/${id}/`,
		method: "get",
	});
}

export function createEvent(data) {
	return request({
		url: "/admin-api/community/events/",
		method: "post",
		data,
	});
}

export function updateEvent(id, data) {
	return request({
		url: `/admin-api/community/events/${id}/`,
		method: "put",
		data,
	});
}

export function deleteEvent(id) {
	return request({
		url: `/admin-api/community/events/${id}/`,
		method: "delete",
	});
}

export function toggleEventPin(id) {
	return request({
		url: `/admin-api/community/events/${id}/toggle-pin/`,
		method: "post",
	});
}

export function getEventStatistics() {
	return request({
		url: `/admin-api/community/events/statistics/`,
		method: "get",
	});
}

// 举报管理API
export function getReportList(params) {
	return request({
		url: "/admin-api/community/reports/",
		method: "get",
		params,
	});
}

export function getReportDetail(id) {
	return request({
		url: `/admin-api/community/reports/${id}/`,
		method: "get",
	});
}

export function updateReportStatus(id, status, notes) {
	return request({
		url: `/admin-api/community/reports/${id}/update-status/`,
		method: "post",
		data: { status, notes },
	});
}

export function createPublicReport(data) {
	return request({
		url: "/admin-api/community/reports/create_public/",
		method: "post",
		data,
	});
}

export function getReportStatistics() {
	return request({
		url: "/admin-api/community/reports/statistics/",
		method: "get",
	});
}

export function startReviewReport(id) {
	return request({
		url: `/admin-api/community/reports/${id}/start_review/`,
		method: "post",
	});
}

export function resolveReport(id, data) {
	return request({
		url: `/admin-api/community/reports/${id}/resolve/`,
		method: "post",
		data,
	});
}

export function dismissReport(id, data) {
	return request({
		url: `/admin-api/community/reports/${id}/dismiss/`,
		method: "post",
		data,
	});
}

// 话题管理API
export function getTopicList(params) {
	return request({
		url: "/admin-api/community/topics/",
		method: "get",
		params,
	});
}

export function getTopicDetail(id) {
	return request({
		url: `/admin-api/community/topics/${id}/`,
		method: "get",
	});
}

export function createTopic(data) {
	return request({
		url: "/admin-api/community/topics/",
		method: "post",
		data,
	});
}

export function updateTopic(id, data) {
	return request({
		url: `/admin-api/community/topics/${id}/`,
		method: "put",
		data,
	});
}

export function deleteTopic(id) {
	return request({
		url: `/admin-api/community/topics/${id}/`,
		method: "delete",
	});
}

export function getTopicStatistics() {
	return request({
		url: "/admin-api/community/topics/statistics/",
		method: "get",
	});
}

export function toggleTopicStatus(id) {
	return request({
		url: `/admin-api/community/topics/${id}/toggle_status/`,
		method: "post",
	});
}

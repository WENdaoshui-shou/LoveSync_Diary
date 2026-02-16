/** @format */

import axios from "axios";
import { Message } from "element-ui";
import router from "@/router";

// 创建axios实例
const service = axios.create({
	baseURL: process.env.VUE_APP_BASE_API || "http://localhost:8001",
	timeout: 10000, // 请求超时时间
});

// 请求拦截器
service.interceptors.request.use(
	(config) => {
		// 在发送请求之前做些什么
		const token = localStorage.getItem("admin_token");
		if (token) {
			config.headers["Authorization"] = `Bearer ${token}`;
		}
		return config;
	},
	(error) => {
		// 对请求错误做些什么
		console.error("Request error:", error);
		return Promise.reject(error);
	},
);

// 响应拦截器
service.interceptors.response.use(
	(response) => {
		// 对响应数据做点什么
		const res = response.data;

		// 检查是否是分页数据格式（包含results字段）
		if (res.results !== undefined) {
			// 分页数据，直接返回
			return response;
		}

		// 检查是否是标准响应格式（包含code字段）
		if (res.code !== undefined) {
			// 如果自定义状态码不是成功状态，则判断为错误
			if (res.code !== 200) {
				Message({
					message: res.message || "Error",
					type: "error",
					duration: 5 * 1000,
				});

				// 401: 未登录或token过期
				if (res.code === 401) {
					localStorage.removeItem("admin_token");
					// 避免重复跳转登录页
					if (window.location.pathname !== "/login") {
						router.push("/login");
					}
				}

				return Promise.reject(new Error(res.message || "Error"));
			} else {
				return response;
			}
		}

		// 其他格式，直接返回
		return response;
	},
	(error) => {
		// 对响应错误做点什么
		console.error("Response error:", error);

		let message = "网络错误";
		if (error.response) {
			switch (error.response.status) {
				case 400:
					message = "请求错误";
					break;
				case 401:
					message = "未授权，请登录";
					localStorage.removeItem("admin_token");
					// 避免重复跳转登录页
					if (window.location.pathname !== "/login") {
						router.push("/login");
					}
					break;
				case 403:
					message = "拒绝访问";
					break;
				case 404:
					message = "请求地址不存在";
					break;
				case 500:
					message = "服务器内部错误";
					break;
				default:
					message = "未知错误";
			}
		} else if (error.request) {
			message = "网络错误，请检查网络连接";
		} else {
			message = error.message;
		}

		Message({
			message: message,
			type: "error",
			duration: 5 * 1000,
		});

		return Promise.reject(error);
	},
);

export default service;

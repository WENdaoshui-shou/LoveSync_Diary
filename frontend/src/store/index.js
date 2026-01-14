/** @format */

import Vue from "vue";
import Vuex from "vuex";
import axios from "axios";

Vue.use(Vuex);

// 创建Axios实例
const apiClient = axios.create({
	baseURL: "http://127.0.0.1:8000/api/",
	withCredentials: true,
});

// 请求拦截器，添加Authorization头
apiClient.interceptors.request.use((config) => {
	const token =
		typeof localStorage !== "undefined" ? localStorage.getItem("token") : null;
	if (token) {
		config.headers.Authorization = `Bearer ${token}`;
	}
	return config;
});

export default new Vuex.Store({
	state: {
		user: null,
		token:
			typeof localStorage !== "undefined"
				? localStorage.getItem("token") || null
				: null,
		isAuthenticated:
			typeof localStorage !== "undefined"
				? !!localStorage.getItem("token")
				: false,
	},
	mutations: {
		SET_USER(state, user) {
			state.user = user;
		},
		SET_TOKEN(state, token) {
			state.token = token;
			state.isAuthenticated = !!token;
			if (typeof localStorage !== "undefined") {
				if (token) {
					localStorage.setItem("token", token);
				} else {
					localStorage.removeItem("token");
				}
			}
		},
		LOGOUT(state) {
			state.user = null;
			state.token = null;
			state.isAuthenticated = false;
			if (typeof localStorage !== "undefined") {
				localStorage.removeItem("token");
			}
		},
	},
	actions: {
		// 用户登录
		async login({ commit }, credentials) {
			try {
				const response = await apiClient.post("core/token/", credentials);
				commit("SET_TOKEN", response.data.access);
				commit("SET_USER", response.data.user);
				return response.data;
			} catch (error) {
				throw error.response.data;
			}
		},

		// 用户注册
		async register({ commit }, userData) {
			try {
				const response = await apiClient.post(
					"core/register/register/",
					userData
				);
				return response.data;
			} catch (error) {
				throw error.response.data;
			}
		},

		// 获取当前用户信息
		async fetchUser({ commit }) {
			try {
				const response = await apiClient.get("core/profile/me/");
				commit("SET_USER", response.data.user);
				return response.data;
			} catch (error) {
				commit("LOGOUT");
				throw error.response.data;
			}
		},

		// 用户登出
		logout({ commit }) {
			commit("LOGOUT");
		},
	},
	getters: {
		isAuthenticated: (state) => state.isAuthenticated,
		currentUser: (state) => state.user,
	},
});

/** @format */

// 模拟localStorage，必须在导入store之前定义
global.localStorage = {
	_data: {},
	getItem: function (key) {
		return this._data[key] || null;
	},
	setItem: function (key, value) {
		this._data[key] = value;
	},
	removeItem: function (key) {
		delete this._data[key];
	},
	clear: function () {
		this._data = {};
	},
};

import Vue from "vue";
import Vuex from "vuex";
import store from "@/store";

Vue.use(Vuex);

describe("store", () => {
	beforeEach(() => {
		// 清除localStorage数据，确保每次测试都是干净的
		localStorage.clear();
		// 重置store状态
		store.commit("LOGOUT");
	});

	// 测试初始状态
	it("should have correct initial state", () => {
		expect(store.state.user).toBeNull();
		expect(store.state.token).toBeNull();
		expect(store.state.isAuthenticated).toBe(false);
	});

	// 测试SET_TOKEN mutation
	it("should update token and isAuthenticated when SET_TOKEN is called with a token", () => {
		const token = "test-token";
		store.commit("SET_TOKEN", token);

		expect(store.state.token).toBe(token);
		expect(store.state.isAuthenticated).toBe(true);
		expect(localStorage.getItem("token")).toBe(token);
	});

	it("should clear token and set isAuthenticated to false when SET_TOKEN is called with null", () => {
		// 先设置一个token
		store.commit("SET_TOKEN", "test-token");

		// 然后清除token
		store.commit("SET_TOKEN", null);

		expect(store.state.token).toBeNull();
		expect(store.state.isAuthenticated).toBe(false);
		expect(localStorage.getItem("token")).toBeNull();
	});

	// 测试SET_USER mutation
	it("should update user when SET_USER is called", () => {
		const user = {
			id: 1,
			username: "testuser",
			name: "Test User",
		};

		store.commit("SET_USER", user);
		expect(store.state.user).toEqual(user);
	});

	// 测试LOGOUT mutation
	it("should clear all user data when LOGOUT is called", () => {
		// 先设置一些数据
		store.commit("SET_USER", { id: 1, username: "testuser" });
		store.commit("SET_TOKEN", "test-token");

		// 然后调用LOGOUT
		store.commit("LOGOUT");

		expect(store.state.user).toBeNull();
		expect(store.state.token).toBeNull();
		expect(store.state.isAuthenticated).toBe(false);
		expect(localStorage.getItem("token")).toBeNull();
	});

	// 测试getters
	it("should return correct values for getters", () => {
		// 测试isAuthenticated getter
		store.commit("SET_TOKEN", "test-token");
		expect(store.getters.isAuthenticated).toBe(true);

		// 测试currentUser getter
		const user = { id: 1, username: "testuser" };
		store.commit("SET_USER", user);
		expect(store.getters.currentUser).toEqual(user);
	});
});

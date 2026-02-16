/** @format */

import Vue from "vue";
import App from "./App.vue";
import router from "./router";
import ElementUI from "element-ui";
import "element-ui/lib/theme-chalk/index.css";
import axios from "axios";
import VueRouter from "vue-router";

Vue.config.productionTip = false;

// 使用Element UI
Vue.use(ElementUI);

// 配置axios
Vue.prototype.$axios = axios;

// 设置axios默认配置
axios.defaults.baseURL = "http://localhost:8001";

// 请求拦截器
axios.interceptors.request.use(
	(config) => {
		const token = localStorage.getItem("admin_token");
		if (token) {
			config.headers.Authorization = `Bearer ${token}`;
		}
		return config;
	},
	(error) => {
		return Promise.reject(error);
	},
);

// 响应拦截器
axios.interceptors.response.use(
	(response) => {
		return response;
	},
	(error) => {
		if (error.response && error.response.status === 401) {
			localStorage.removeItem("admin_token");
			router.replace("/login");
		}
		return Promise.reject(error);
	},
);

// 处理导航重复错误
const originalPush = VueRouter.prototype.push;
VueRouter.prototype.push = function push(location, onResolve, onReject) {
	if (onResolve || onReject) {
		return originalPush.call(this, location, onResolve, onReject);
	}
	return originalPush.call(this, location).catch((err) => {
		if (err.name !== "NavigationDuplicated") {
			throw err;
		}
	});
};

// 处理导航替换错误
const originalReplace = VueRouter.prototype.replace;
VueRouter.prototype.replace = function replace(location, onResolve, onReject) {
	if (onResolve || onReject) {
		return originalReplace.call(this, location, onResolve, onReject);
	}
	return originalReplace.call(this, location).catch((err) => {
		if (err.name !== "NavigationDuplicated") {
			throw err;
		}
	});
};

new Vue({
	router,
	render: (h) => h(App),
}).$mount("#app");

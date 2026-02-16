/** @format */

import Vue from "vue";
import VueRouter from "vue-router";
import Layout from "@/views/Layout.vue";

Vue.use(VueRouter);

const routes = [
	{
		path: "/login",
		name: "Login",
		component: () => import("@/views/Login.vue"),
	},
	{
		path: "/",
		component: Layout,
		children: [
			{
				path: "",
				name: "Dashboard",
				component: () => import("@/views/Dashboard.vue"),
			},
			{
				path: "/users",
				name: "UserList",
				component: () => import("@/views/user/UserList.vue"),
			},
			{
				path: "/moments",
				name: "MomentList",
				component: () => import("@/views/moment/MomentList.vue"),
			},
			// 社区管理相关页面
			{
				path: "/community/events",
				name: "CommunityEvents",
				component: () => import("@/views/community/CommunityEvents.vue"),
			},
			{
				path: "/community/achievements",
				name: "CommunityAchievements",
				component: () => import("@/views/community/CommunityAchievements.vue"),
			},
			{
				path: "/community/topics",
				name: "CommunityTopics",
				component: () => import("@/views/community/CommunityTopics.vue"),
			},
			{
				path: "/community/reports",
				name: "ReportManagement",
				component: () => import("@/views/community/ReportManagement.vue"),
			},
			{
				path: "/community/articles",
				name: "CommunityArticles",
				component: () => import("@/views/community/CommunityArticles.vue"),
			},
			// 情侣管理相关页面
			{
				path: "/couple/recommended",
				name: "RecommendedCouples",
				component: () => import("@/views/couple/RecommendedCouples.vue"),
			},
			{
				path: "/couple/places",
				name: "PlaceManagement",
				component: () => import("@/views/couple/PlaceManagement.vue"),
			},
			{
				path: "/couple/tests",
				name: "TestManagement",
				component: () => import("@/views/couple/TestManagement.vue"),
			},
			{
				path: "/couple/games",
				name: "GameManagement",
				component: () => import("@/views/couple/GameManagement.vue"),
			},
			// 商城管理相关页面
			// 商品管理
			{
				path: "/mall/products",
				name: "ProductList",
				component: () => import("@/views/mall/products/ProductList.vue"),
			},
			// 分类管理
			{
				path: "/mall/categories",
				name: "CategoryList",
				component: () => import("@/views/mall/categories/CategoryList.vue"),
			},
			// 订单管理
			{
				path: "/mall/orders",
				name: "OrderList",
				component: () => import("@/views/mall/orders/OrderList.vue"),
			},
			// 营销管理
			{
				path: "/mall/marketing/flash-sale",
				name: "FlashSaleList",
				component: () => import("@/views/mall/marketing/FlashSaleList.vue"),
			},
			{
				path: "/mall/marketing/coupon",
				name: "CouponList",
				component: () => import("@/views/mall/marketing/CouponList.vue"),
			},
			// 内容管理
			{
				path: "/mall/content",
				name: "BannerList",
				component: () => import("@/views/mall/content/BannerList.vue"),
			},
			// 用户地址管理
			{
				path: "/mall/users",
				name: "AddressList",
				component: () => import("@/views/mall/users/AddressList.vue"),
			},
		],
	},
];

const router = new VueRouter({
	mode: "history",
	base: process.env.BASE_URL,
	routes,
});

// 路由守卫
router.beforeEach((to, from, next) => {
	const token = localStorage.getItem("admin_token");

	// 如果用户已登录且尝试访问登录页，跳转到首页
	if (to.path === "/login" && token) {
		next("/");
		return;
	}

	// 如果用户未登录且尝试访问非登录页，跳转到登录页
	if (to.path !== "/login" && !token) {
		next("/login");
	} else {
		next();
	}
});

// 处理导航错误
router.onError((error) => {
	if (error.name !== "NavigationDuplicated") {
		console.error("路由导航错误:", error);
	}
});

// 全局错误处理
window.addEventListener("unhandledrejection", (event) => {
	if (event.reason && event.reason.name === "NavigationDuplicated") {
		event.preventDefault();
	}
});

export default router;
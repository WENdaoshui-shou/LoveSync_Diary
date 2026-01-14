/** @format */

import Vue from "vue";
import Router from "vue-router";

Vue.use(Router);

// 创建路由实例
const router = new Router({
	routes: [
		{
			path: "/",
			redirect: "/login",
		},
		{
			path: "/login",
			name: "Login",
			component: () => import("@/views/Login.vue"),
		},
		{
			path: "/register",
			name: "Register",
			component: () => import("@/views/Register.vue"),
		},
		{
			path: "/index",
			name: "Index",
			component: () => import("@/views/Index.vue"),
			meta: {
				requiresAuth: true,
			},
		},
		{
			path: "/personal_center",
			name: "PersonalCenter",
			component: () => import("@/views/PersonalCenter.vue"),
			meta: {
				requiresAuth: true,
			},
		},
		{
			path: "/moments",
			name: "Moments",
			component: () => import("@/views/Moments.vue"),
			meta: {
				requiresAuth: true,
			},
		},
		{
			path: "/lovesync",
			name: "LoveSync",
			component: () => import("@/views/LoveSync.vue"),
			meta: {
				requiresAuth: true,
			},
		},
		// 情侣关系管理
		{
			path: "/couple",
			name: "Couple",
			component: () => import("@/views/Couple.vue"),
			meta: {
				requiresAuth: true,
			},
		},
		// 尚未实现的组件，暂时注释
		// {
		//   path: '/note',
		//   name: 'Note',
		//   component: () => import('@/views/Note.vue'),
		//   meta: {
		//     requiresAuth: true
		//   }
		// },
		// {
		//   path: '/photo_album',
		//   name: 'PhotoAlbum',
		//   component: () => import('@/views/PhotoAlbum.vue'),
		//   meta: {
		//     requiresAuth: true
		//   }
		// },
		// {
		//   path: '/mall',
		//   name: 'Mall',
		//   component: () => import('@/views/Mall.vue'),
		//   meta: {
		//     requiresAuth: true
		//   }
		// }
	],
});

// 路由守卫
router.beforeEach((to, from, next) => {
	if (to.matched.some((record) => record.meta.requiresAuth)) {
		const isAuthenticated = !!localStorage.getItem("token");
		if (!isAuthenticated) {
			next({
				path: "/login",
				query: { redirect: to.fullPath },
			});
		} else {
			next();
		}
	} else {
		next();
	}
});

export default router;

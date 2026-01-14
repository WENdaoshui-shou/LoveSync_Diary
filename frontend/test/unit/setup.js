/** @format */

import Vue from "vue";

Vue.config.productionTip = false;

// 模拟localStorage
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

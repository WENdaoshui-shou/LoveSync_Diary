/** @format */
import request from '@/utils/request'

// 商品管理 API

// 获取商品列表
export function getProducts(params) {
  return request({
    url: '/admin-api/mall/products/',
    method: 'get',
    params
  })
}

// 获取单个商品详情
export function getProduct(id) {
  return request({
    url: `/admin-api/mall/products/${id}/`,
    method: 'get'
  })
}

// 创建商品
export function createProduct(data) {
  return request({
    url: '/admin-api/mall/products/',
    method: 'post',
    data
  })
}

// 更新商品
export function updateProduct(id, data) {
  return request({
    url: `/admin-api/mall/products/${id}/`,
    method: 'put',
    data
  })
}

// 删除商品
export function deleteProduct(id) {
  return request({
    url: `/admin-api/mall/products/${id}/`,
    method: 'delete'
  })
}

// 商品分类管理 API

// 获取商品分类列表
export function getCategories(params) {
  return request({
    url: '/admin-api/mall/categories/',
    method: 'get',
    params
  })
}

// 获取单个商品分类详情
export function getCategory(id) {
  return request({
    url: `/admin-api/mall/categories/${id}/`,
    method: 'get'
  })
}

// 创建商品分类
export function createCategory(data) {
  return request({
    url: '/admin-api/mall/categories/',
    method: 'post',
    data
  })
}

// 更新商品分类
export function updateCategory(id, data) {
  return request({
    url: `/admin-api/mall/categories/${id}/`,
    method: 'put',
    data
  })
}

// 删除商品分类
export function deleteCategory(id) {
  return request({
    url: `/admin-api/mall/categories/${id}/`,
    method: 'delete'
  })
}

// 订单管理 API

// 获取订单列表
export function getOrders(params) {
  return request({
    url: '/admin-api/mall/orders/',
    method: 'get',
    params
  })
}

// 获取单个订单详情
export function getOrder(id) {
  return request({
    url: `/admin-api/mall/orders/${id}/`,
    method: 'get'
  })
}

// 更新订单状态
export function updateOrderStatus(id, data) {
  return request({
    url: `/admin-api/mall/orders/${id}/`,
    method: 'put',
    data
  })
}

// 支付管理 API

// 获取支付记录列表
export function getPayments(params) {
  return request({
    url: '/admin-api/mall/payments/',
    method: 'get',
    params
  })
}

// 秒杀活动管理 API

// 获取秒杀活动列表
export function getFlashSales(params) {
  return request({
    url: '/admin-api/mall/flash-sales/',
    method: 'get',
    params
  })
}

// 创建秒杀活动
export function createFlashSale(data) {
  return request({
    url: '/admin-api/mall/flash-sales/',
    method: 'post',
    data
  })
}

// 更新秒杀活动
export function updateFlashSale(id, data) {
  return request({
    url: `/admin-api/mall/flash-sales/${id}/`,
    method: 'put',
    data
  })
}

// 删除秒杀活动
export function deleteFlashSale(id) {
  return request({
    url: `/admin-api/mall/flash-sales/${id}/`,
    method: 'delete'
  })
}

// 优惠券管理 API

// 获取优惠券列表
export function getCoupons(params) {
  return request({
    url: '/admin-api/mall/coupons/',
    method: 'get',
    params
  })
}

// 创建优惠券
export function createCoupon(data) {
  return request({
    url: '/admin-api/mall/coupons/',
    method: 'post',
    data
  })
}

// 更新优惠券
export function updateCoupon(id, data) {
  return request({
    url: `/admin-api/mall/coupons/${id}/`,
    method: 'put',
    data
  })
}

// 删除优惠券
export function deleteCoupon(id) {
  return request({
    url: `/admin-api/mall/coupons/${id}/`,
    method: 'delete'
  })
}

// 首页轮播图管理 API

// 获取首页轮播图列表
export function getBanners(params) {
  return request({
    url: '/admin-api/mall/banners/',
    method: 'get',
    params
  })
}

// 创建首页轮播图
export function createBanner(data) {
  return request({
    url: '/admin-api/mall/banners/',
    method: 'post',
    data
  })
}

// 更新首页轮播图
export function updateBanner(id, data) {
  return request({
    url: `/admin-api/mall/banners/${id}/`,
    method: 'put',
    data
  })
}

// 删除首页轮播图
export function deleteBanner(id) {
  return request({
    url: `/admin-api/mall/banners/${id}/`,
    method: 'delete'
  })
}

// 收货地址管理 API

// 获取收货地址列表
export function getAddresses(params) {
  return request({
    url: '/admin-api/mall/addresses/',
    method: 'get',
    params
  })
}

// 获取单个收货地址详情
export function getAddressDetail(id) {
  return request({
    url: `/admin-api/mall/addresses/${id}/`,
    method: 'get'
  })
}

// 删除收货地址
export function deleteAddress(id) {
  return request({
    url: `/admin-api/mall/addresses/${id}/`,
    method: 'delete'
  })
}

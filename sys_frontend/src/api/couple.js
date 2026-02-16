/** @format */
import request from '@/utils/request'

// 推荐情侣管理 API

// 获取推荐情侣列表
export function getRecommendedCouples(params) {
  return request({
    url: '/admin-api/couple/recommended-couples/',
    method: 'get',
    params
  })
}

// 获取单个推荐情侣详情
export function getRecommendedCouple(id) {
  return request({
    url: `/admin-api/couple/recommended-couples/${id}/`,
    method: 'get'
  })
}

// 创建推荐情侣
export function createRecommendedCouple(data) {
  return request({
    url: '/admin-api/couple/recommended-couples/',
    method: 'post',
    data
  })
}

// 更新推荐情侣
export function updateRecommendedCouple(id, data) {
  return request({
    url: `/admin-api/couple/recommended-couples/${id}/`,
    method: 'put',
    data
  })
}

// 删除推荐情侣
export function deleteRecommendedCouple(id) {
  return request({
    url: `/admin-api/couple/recommended-couples/${id}/`,
    method: 'delete'
  })
}

// 地点管理 API

// 获取地点列表
export function getPlaces(params) {
  return request({
    url: '/admin-api/couple/places/',
    method: 'get',
    params
  })
}

// 获取单个地点详情
export function getPlace(id) {
  return request({
    url: `/admin-api/couple/places/${id}/`,
    method: 'get'
  })
}

// 创建地点
export function createPlace(data) {
  return request({
    url: '/admin-api/couple/places/',
    method: 'post',
    data
  })
}

// 更新地点
export function updatePlace(id, data) {
  return request({
    url: `/admin-api/couple/places/${id}/`,
    method: 'put',
    data
  })
}

// 删除地点
export function deletePlace(id) {
  return request({
    url: `/admin-api/couple/places/${id}/`,
    method: 'delete'
  })
}

// 爱情测试管理 API

// 获取爱情测试列表
export function getLoveTests(params) {
  return request({
    url: '/admin-api/couple/love-tests/',
    method: 'get',
    params
  })
}

// 获取单个爱情测试详情
export function getLoveTest(id) {
  return request({
    url: `/admin-api/couple/love-tests/${id}/`,
    method: 'get'
  })
}

// 创建爱情测试
export function createLoveTest(data) {
  return request({
    url: '/admin-api/couple/love-tests/',
    method: 'post',
    data
  })
}

// 更新爱情测试
export function updateLoveTest(id, data) {
  return request({
    url: `/admin-api/couple/love-tests/${id}/`,
    method: 'put',
    data
  })
}

// 删除爱情测试
export function deleteLoveTest(id) {
  return request({
    url: `/admin-api/couple/love-tests/${id}/`,
    method: 'delete'
  })
}

// 情侣游戏管理 API

// 获取情侣游戏列表
export function getCoupleGames(params) {
  return request({
    url: '/admin-api/couple/couple-games/',
    method: 'get',
    params
  })
}

// 获取单个情侣游戏详情
export function getCoupleGame(id) {
  return request({
    url: `/admin-api/couple/couple-games/${id}/`,
    method: 'get'
  })
}

// 创建情侣游戏
export function createCoupleGame(data) {
  return request({
    url: '/admin-api/couple/couple-games/',
    method: 'post',
    data
  })
}

// 更新情侣游戏
export function updateCoupleGame(id, data) {
  return request({
    url: `/admin-api/couple/couple-games/${id}/`,
    method: 'put',
    data
  })
}

// 删除情侣游戏
export function deleteCoupleGame(id) {
  return request({
    url: `/admin-api/couple/couple-games/${id}/`,
    method: 'delete'
  })
}

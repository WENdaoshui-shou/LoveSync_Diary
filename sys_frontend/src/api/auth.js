import request from '@/utils/request'

// 用户登录
export function login(data) {
  return request({
    url: '/admin-api/user/auth/login/',
    method: 'post',
    data
  })
}

// 获取用户信息
export function getUserInfo() {
  return request({
    url: '/admin-api/user/auth/user/',
    method: 'get'
  })
}
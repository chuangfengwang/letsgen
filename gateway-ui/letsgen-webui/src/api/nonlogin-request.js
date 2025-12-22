// 用于非登录状态下的接口请求

import request from '@/api/ui-request';

export function registerFirstAdmin(data) {
    return request({
      url: '/admin/create_first_admin_user',
      method: 'post',
      data
    });
  }

export function login(data) {
  res = request({
    url: '/normal/login',
    method: 'post',
    data
  })
  // 设置 cookie
  document.cookie = `jwt=${res.data.jwt}; path=/;`;
  return res;
}

export function register(data) {
  return request({
    url: '/normal/register',
    method: 'post',
    data
  });
}

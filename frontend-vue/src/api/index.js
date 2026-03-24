import request from './request'

/**
 * 用户登录
 * @param {string} username 用户名
 * @param {string} password 密码
 */
export const login = (username, password) => {
  return request({
    url: '/api/login',
    method: 'post',
    data: { username, password }
  })
}

/**
 * 查询订单
 * @param {number} userId 用户ID
 * @param {string} queryText 查询文本
 */
export const queryOrder = (userId, queryText) => {
  return request({
    url: '/api/query',
    method: 'post',
    data: { user_id: userId, query_text: queryText }
  })
}

/**
 * 获取查询历史
 * @param {number} userId 用户ID
 */
export const getQueryLogs = (userId) => {
  return request({
    url: '/api/logs',
    method: 'get',
    params: { user_id: userId }
  })
}

/**
 * 用户登出
 */
export const logout = () => {
  return request({
    url: '/api/logout',
    method: 'post'
  })
}

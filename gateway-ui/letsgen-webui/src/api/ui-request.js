// 用于 ui 的接口请求

import axios from 'axios';
import { ElMessage } from 'element-plus/es';

// 1. 创建实例
// 使用环境变量配置 API 地址
// 开发环境：通过 Vite 代理转发
// 生产环境：使用相对路径（通过 Nginx 代理）或完整 URL（如果后端配置了 CORS）
const service = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || '/api/ui',
    timeout: 2000 // 请求超时时间
});

// 2. 请求拦截器 (例如：在 header 中注入 token)
service.interceptors.request.use(
    config => {
        // 设置默认 Content-Type 为 application/json（POST/PUT/PATCH 请求）
        if (['post', 'put', 'patch'].includes(config.method?.toLowerCase())) {
            if (!config.headers['Content-Type']) {
                config.headers['Content-Type'] = 'application/json';
            }
        }

        // 注入认证 token
        const llmApiKey = localStorage.getItem('llmApiKey');
        if (llmApiKey) {
            config.headers['Authorization'] = `Bearer ${llmApiKey}`;
        }
        return config;
    },
    error => Promise.reject(error)
);

// 3. 响应拦截器 (例如：统一处理错误状态码)
service.interceptors.response.use(
    response => {
        const res = response.data;
        // 根据后端约定的状态码判断
        if (res.status !== 0) {
            // 使用 Element Plus 的 ElMessage 弹窗显示错误信息
            ElMessage({
                message: res.msg || '系统错误',
                type: 'error',
                duration: 5 * 1000
            });

            return Promise.reject(new Error(res.msg || 'Error'));
        }
        return res;
    },
    error => {
        // 处理 HTTP 错误状态码（如 422, 400, 500 等）
        if (error.response) {
            const { status, data } = error.response;
            const errorMessage = data?.msg || `请求失败 (${status})`;

            // 422 错误通常包含详细的验证错误信息
            if (status === 422 && data?.detail) {
                // 如果是数组格式的验证错误，格式化显示
                if (Array.isArray(data.detail)) {
                    const details = data.detail.map(err => `${err.loc?.join('.')}: ${err.msg}`).join('\n');
                    ElMessage({
                        message: details || '参数格式验证错误',
                        type: 'error',
                        duration: 5 * 1000
                    });
                    return Promise.reject(new Error(details || errorMessage));
                }
                // 如果是对象格式
                if (typeof data.detail === 'object') {
                    const details = Object.entries(data.detail)
                        .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : value}`)
                        .join('\n');
                    // console.error('验证错误详情:', details);

                    // 处理 HTTP 网络错误 (如 404, 500 等)
                    ElMessage({
                        message: error.details || '网络连接异常',
                        type: 'error',
                        duration: 5 * 1000
                    });
                    return Promise.reject(new Error(details || errorMessage));
                }
            }
            
            // 其他 HTTP 错误（如 400, 401, 403, 404, 500 等）
            // console.error(`API 错误 [${status}]:`, data);
            ElMessage({
                message: errorMessage,
                type: 'error',
                duration: 5 * 1000
            });
            return Promise.reject(new Error(errorMessage));
        }

        // 网络错误或其他错误（如后端服务未启动、超时等）
        console.error('请求错误:', error.message);
        ElMessage({
            message: error.message || '网络连接失败',
            type: 'error',
            duration: 5 * 1000
        });
        return Promise.reject(error);
    }
);

export default service;

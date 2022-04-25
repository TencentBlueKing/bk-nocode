import Vue from 'vue';
import axios from 'axios';
import bus from '@/utils/bus.js';

const instance = axios.create({
  validateStatus: status => status >= 200 && status <= 505,
  baseURL: `${window.SITE_URL}api`,
  // `headers` are custom headers to be sent
  headers: { 'X-Requested-With': 'XMLHttpRequest' },
  // csrftoken变量名
  xsrfCookieName: 'bknocode_csrftoken',
  // cookie中的csrftoken信息名称
  xsrfHeaderName: 'X-CSRFToken',
  withCredentials: true,
});

/**
 * request interceptor
 */
instance.interceptors.request.use(
  config => config,
  error => Promise.reject(error)
);

instance.interceptors.response.use(
  (response) => {
    if (response.status === 401) {
      // 登录控制
      const { data, config } = response;
      if (data.has_plain) {
        window.BLUEKING.corefunc.open_login_dialog(data.login_url, data.width, data.height, config.method);
      }
    } else if (response.status === 499) {
      const permissions = response.data.permission;
      let isViewApply = false;
      let viewType = 'other';
      if (permissions.actions.find(item => item.id === 'project_view')) {
        viewType = 'project';
        isViewApply = true;
      } else {
        isViewApply = permissions.actions.some(item => ['project_view', 'operational_data_view'].includes(item.id));
      }
      if (isViewApply) {
        bus.$emit('togglePermissionApplyPage', true, viewType, permissions);
      } else {
        bus.$emit('showPermissionModal', permissions);
      }
    } else if (response.status >= 500) {
      Vue.prototype.$bkMessage({
        message: `系统错误，请联系管理员，${response.statusText}`,
        theme: 'error',
        ellipsisLine: 0,
      });
    } else {
      if ('result' in response.data) {
        if (!response.data.result) {
          Vue.prototype.$bkMessage({
            message: response.data.message,
            theme: 'error',
            ellipsisLine: 0,
          });
          return Promise.reject(response);
        }
      }
    }
    return response;
  },
  error => Promise.reject(error)
);

Vue.prototype.$http = instance;

export default instance;

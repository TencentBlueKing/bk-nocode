<template>
  <section class="setting-page-container">
    <router-view></router-view>
  </section>
</template>
<script>
export default {
  name: 'SettingHome',
  created() {
    this.getConfigurInfo;
  },
  methods: {
    // 获取节点配置字段信息
    getConfigurInfo() {
      return this.$store.dispatch('setting/getConfigurInfo').then((res) => {
        const value = res.data;
        const globalInfo = {};
        for (const key in value) {
          const listInfo = [];
          // 区分返回的是数组还是对象
          if (Array.isArray(value[key])) {
            for (let i = 0; i < value[key].length; i++) {
              if (Array.isArray(value[key][i])) {
                listInfo.push({
                  id: i + 1,
                  name: value[key][i][1] ? value[key][i][1] : '无',
                  typeName: value[key][i][0],
                });
              } else {
                listInfo.push(value[key][i]);
              }
            }
            globalInfo[key] = listInfo;
          } else {
            globalInfo[key] = value[key];
          }
        }
        /* 触发器隐藏部分触发事件
        * 节点触发器隐藏  分派单据 认领单据
        * 流程触发器隐藏  终止 挂起 恢复单据
        * 处理人隐藏 cmdb业务公用角色 通用角色表  权限中心角色
        * */
        globalInfo.processor_type.splice(0, 2);
        globalInfo.processor_type.splice(-1, 1);
        globalInfo.trigger_signals.STATE = { DELIVER_STATE: '转单', ENTER_STATE: '进入节点', LEAVE_STATE: '离开节点' };
        globalInfo.trigger_signals.FLOW = { CLOSE_TICKET: '关闭单据', CREATE_TICKET: '创建单据', DELETE_TICKET: '撤销单据' };
        this.$store.commit('setting/changeConfigur', globalInfo);
        sessionStorage.setItem('globalInfo', JSON.stringify(globalInfo));
      })
        .catch((res) => {
          errorHandler(res, this);
        });
    },
  },
};
</script>
<style lang="postcss" scoped>
.setting-page-container{
  overflow: hidden;
}
</style>

<template>
  <!-- 功能卡片、表格页面二级页面 -->
  <div class="common-create-ticket">
    <create-ticket
      ref="createTicketComp"
      :app-id="appId"
      :app-name="appName"
      :component-id="componentId"
      :func-id="funcId"
      :action-id="actionId"
      :action-type="actionType"
      :page="crtPage"
      :version="version"
      :show-cancel="true"
      @onCancel="handleCancel">
    </create-ticket>
  </div>
</template>
<script>
import CreateTicket from './components/createTicket.vue';

export default {
  name: 'CommonCreateTicket',
  components: {
    CreateTicket,
  },
  props: {
    appId: String,
    appName: [String, Number],
    version: String,
    crtPage: {
      type: Object,
      default: () => ({}),
    },
    componentId: Number,
    funcId: Number,
    actionId: [Number, String],
    actionType: String,
  },
  methods: {
    handleCancel() {
      this.$router.push({
        name: 'appPageContent',
        params: { appId: this.appId, version: this.version, pageId: this.crtPage.id },
      });
    },
  },
  // beforeRouteLeave(to, from, next) {
  //   if (this.$refs.createTicketComp.needLeaveConfirm) {
  //     this.$bkInfo({
  //       title: '此操作会导致您的编辑没有保存，确认吗？',
  //       type: 'warning',
  //       width: 500,
  //       confirmFn: () => {
  //         next();
  //       },
  //     });
  //   } else {
  //     next();
  //   }
  // },
};
</script>
<style lang="postcss" scoped>
.common-create-ticket {
  margin: 24px 24px 0;
  height: calc(100% - 48px);
  background: #ffffff;
  box-shadow: 0 2px 4px 0 rgba(25, 25, 41, 0.05);
  border-radius: 2px;
  overflow: auto;
}
</style>

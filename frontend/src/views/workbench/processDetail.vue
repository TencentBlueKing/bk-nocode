<template>
  <section class="workbench-processDetail-content" v-bkloading="{ isLoading: loading.ticketLoading }">
    <page-wrapper :title="ticketInfo&&ticketInfo.service_name" :back-icon="true" @back="handleGoBack">
      <bk-button
        :theme="'default'"
        type="submit"
        :title="'基础按钮'"
        @click="handleRefresh"
        class="refresh-btn"
        icon="refresh">
        刷新
      </bk-button>
      <div class="detail-page-content">
        <div class="process-container">
          <div class="tool-panel-container" v-if="active==='processPreview'">
            <div class="tool-item" @click="handleFullScreen">
              <i class="custom-icon-font icon-fullscreen"></i>
            </div>
          </div>
          <bk-tab :active.sync="active" type="unborder-card">
            <bk-tab-panel label="节点详情" name="nodeDetail">
              <node-detail
                v-if="!loading.ticketLoading && !loading.nodeInfoLoading "
                ref="nodeDetail"
                :loading="loading.ticketLoading"
                :basic-infomation="ticketInfo"
                :node-list="nodeList"
                :ticket-trigger-list="ticketTriggerList"
                @refresh="handleRefresh">
              </node-detail>
            </bk-tab-panel>
            <bk-tab-panel label="流程预览" name="processPreview">
            </bk-tab-panel>
            <process-preview
              v-if="ticketInfo.flow_id && active==='processPreview' &&!showdialog"
              :node-list="nodeList"
              :flow-id="ticketInfo.flow_id">
            </process-preview>
          </bk-tab>
        </div>
        <div class="right-container">
          <bk-tab :active.sync="rightActive" type="unborder-card">
            <bk-tab-panel
              v-for="(panel, index) in rightPanels"
              v-bind="panel"
              :key="index">
            </bk-tab-panel>
          </bk-tab>
          <basic-info
            :basic-info="ticketInfo"
            v-if="JSON.stringify(ticketInfo)!=='{}'&&rightActive==='basicInfo'"></basic-info>
          <flow-log ref="flowLog" v-if="rightActive==='flowLog'"></flow-log>
          <trigger-record v-if="rightActive==='trigger'"></trigger-record>
        </div>
      </div>
      <bk-dialog
        v-model="visible"
        render-directive="if"
        header-position="left"
        :fullscreen="true"
        :close-icon="false"
        title="流程详情">
        <process-preview
          v-if="ticketInfo.flow_id && active==='processPreview' && showdialog"
          :node-list="nodeList"
          :flow-id="ticketInfo.flow_id">
        </process-preview>
        <div slot="footer">
          <bk-button :theme="'default'" type="submit" :title="'基础按钮'" @click="handleCancel" class="mr10">
            取消
          </bk-button>
        </div>
      </bk-dialog>
    </page-wrapper>
  </section>
</template>

<script>
import basicInfo from './components/basicInfo.vue';
import fieldMix from '@/commonMix/field.js';
import flowLog from './components/flowLog.vue';
import nodeDetail from './components/nodeDetail.vue';
import triggerRecord from './components/triggerRecord.vue';
import processPreview from './components/processPreview.vue';
import PageWrapper from '@/components/pageWrapper.vue';
import { deepClone } from '@/utils/util';
import MemberSelect from '@/components/memberSelect.vue';

export default {
  name: 'ProcessDetail',
  components: {
    basicInfo,
    flowLog,
    nodeDetail,
    processPreview,
    PageWrapper,
    triggerRecord,
    MemberSelect,
  },
  mixins: [fieldMix],
  provide() {
    return {
      getNodeList: this.initData,
    };
  },
  data() {
    return {
      panels: [
        { name: 'nodeDetail', label: '节点详情' },
        { name: 'processPreview', label: '流程预览' },
      ],
      rightPanels: [
        { name: 'basicInfo', label: '基本信息', count: 10 },
        { name: 'flowLog', label: '流转日志', count: 20 },
        { name: 'trigger', label: '触发器记录', count: 30 },
      ],
      formData: {
        name: [],
      },
      rules: {
        name: [
          {
            required: true,
            message: '转派人为必填项',
            trigger: 'blur',
          },
        ],
      },
      rightActive: 'basicInfo',
      ticketId: '',
      // 节点列表
      nodeList: [],
      // 单据详情信息
      ticketInfo: {},
      active: 'nodeDetail',
      loading: {
        ticketLoading: false,
        nodeInfoLoading: false,
      },
      ticketTriggerList: [],
      visible: false,
      showdialog: false,
    };
  },
  mounted() {
    this.initData();
  },
  methods: {
    async initData() {
      this.ticketId = this.$route.params.id;
      await this.getTicketDetailInfo();
      await this.getNodeList();
      await this.getTriggers();
    },
    handleRefresh() {
      this.initData();
      this.$refs.flowLog && this.$refs.flowLog.getOperationLogList();
    },
    // 获取单据信息详情
    async getTicketDetailInfo() {
      this.loading.ticketLoading = true;
      const params = {
        id: this.ticketId,
        token: this.token || undefined,
      };

      await this.$store.dispatch('workbench/getOrderDetails', params).then((res) => {
        this.ticketInfo = res.data;
      })
        .catch((res) => {
          // 显示 404 页面
          this.ticketErrorMessage = res.data.code === 'OBJECT_NOT_EXIST' ? '单据不存在或已被撤销' : '您没有权限访问';
        })
        .finally(() => {
          this.loading.ticketLoading = false;
        });
    },
    // 获取单据节点的详情
    async getNodeList() {
      this.loading.nodeInfoLoading = true;
      const params = {
        id: this.ticketId,
        token: this.token || undefined,
      };
      try {
        const res = await this.$store.dispatch('workbench/getNodeList', params);
        this.updateNodeList(res.data);
      } catch (e) {
        console.warn(e);
      } finally {
        this.loading.nodeInfoLoading = false;
      }
    },
    // 更新节点信息
    updateNodeList(newNodeList) {
      const copyList = deepClone(newNodeList);
      copyList.forEach((item) => {
        item.fields.forEach((fields) => {
          this.$set(fields, 'showFeild', !fields.show_conditions.connector);
          this.$set(fields, 'val', '');
        });
        if (item.status === 'AUTO_SUCCESS') {
          item.status = 'FINISHED';
        }
      });
      this.nodeList = copyList;
      this.$store.commit('setting/setNodeList', copyList);
    },
    handleGoBack() {
      if (window.history.length <= 1) {
        this.$router.push({ path: '/workbench/all' });
        return false;
      }
      this.$router.go(-1);
    },
    handleSuccess() {
      this.initData();
    },
    handleFullScreen() {
      this.visible = true;
      this.showdialog = true;
    },
    handleCancel() {
      this.visible = false;
      this.showdialog = false;
    },
    // 获取单据手动触发器
    async getTriggers() {
      try {
        const res = await this.$store.dispatch('workbench/getTicketHandleTriggers', { id: this.ticketId });
        this.ticketTriggerList = res.data.filter(trigger => trigger.signal_type === 'STATE');
      } catch (e) {
        console.error(e);
      }
    },
    handleTransTicket() {
      this.transDialog.visible = true;
    },
    onConfirm() {
      this.transDialog.loading = true;
      this.$refs.transPerson.validate().then((validator) => {
        this.transTicket();
      })
        .catch((e) => {
          this.transDialog.loading = false;
        });
    },
    onCancel() {
      this.formData.name = [];
      this.$refs.transPerson.clearError();
      this.transDialog.visible = false;
    },
    // 转派单据
    async transTicket() {
      // TODO
      try {

      } catch (e) {

      } finally {
        this.transDialog.loading = false;
      }
    },
    // async getTicketStatus() {
    //   try {
    //     const res = await  this.polling('workbench/getNodeList', { id: this.ticketId });
    //     this.updateNodeList(res.data);
    //   } catch (e) {
    //     console.warn(e);
    //   }
    // },
    // polling(url, data, delay = 10000) {
    //   return new Promise((resolve, reject) => {
    //     this.$store.dispatch(url, data).then((res) => {
    //       if (!['FINISHED', 'FAILED'].includes(res.data[0].status)) {  // 这个继续进行轮询的条件，需要根据自己的需要修改
    //         setTimeout(() => resolve(this.polling(url, data, delay), delay));
    //       } else {
    //         resolve(res);
    //       }
    //     });
    //   });
    // },
  },
};
</script>

<style lang="postcss" scoped>
@import "../../css/scroller.css";

/deep/ .bk-tab-section {
  padding: 0;
}

/deep/ .page-main-wrapper {
  overflow-y: hidden;
}

.workbench-processDetail-content {
  .refresh-btn {
    position: absolute;
    top: 10px;
    right: 24px;
    z-index: 100;

    /deep/ .bk-icon {
      line-height: 30px;
      font-size: 14px;
      top: 0;
    }
  }

  .trans-btn {
    position: absolute;
    top: 10px;
    right: 110px;
    z-index: 100;

    /deep/ .bk-icon {
      line-height: 30px;
      font-size: 14px;
      top: 0;
    }
  }

  .detail-page-content {
    position: relative;
    display: flex;
    margin: 24px;
    height: 100%;
  }

  .process-container {
    position: relative;
    min-width: 832px;
    height: calc(100% - 48px);
    flex: 1;
    margin-right: 24px;
    background: #ffffff;
    box-shadow: 0 2px 4px 0 rgba(25, 25, 41, 0.05);
    border-radius: 2px;
  }

  .right-container {
    height: calc(100% - 48px);
    width: 452px;
    background: #ffffff;
    box-shadow: 0 2px 4px 0 rgba(25, 25, 41, 0.05);
    border-radius: 2px;
  }
}

.tool-panel-container {
  position: absolute;
  right: 16px;
  top: 56px;
  display: flex;
  align-items: center;
  z-index: 100;

  .tool-item {
    padding: 0 10px;
    line-height: 32px;
    font-size: 20px;
    color: #c4c6cc;
    cursor: pointer;

    &:hover {
      color: #979ba5;
      background: #e1e3e6;
      cursor: pointer;
    }
  }
}

</style>

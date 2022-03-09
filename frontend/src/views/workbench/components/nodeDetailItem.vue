<template>
  <div :class="['bk-content-node', `state_id_${nodeInfo.state_id}`]">
    <!-- 线条 -->
    <div class="bk-content-line" v-if="!isLastNode"></div>
    <!-- 圆圈 -->
    <div class="bk-node-circle"></div>
    <!-- content -->
    <div :class="['bk-node-info']">
      <div class="bk-node-header">
        <p class="bk-node-title bk-node-cursor" @click="closeUnflod($event)">
          <!-- 折叠 icon -->
          <template>
            <i class="circle icon-default" v-if="nodeInfo.type === 'DATA-PROC'"></i>
            <i v-else-if="unfold" class="bk-icon icon-down-shape icon-default"></i>
            <!--            <i v-else-if="isHaveApprovePermission"-->
            <!--               class="bk-itsm-icon icon-icon-no-permissions"-->
            <!--               style="margin-left: 5px"-->
            <!--              v-bk-tooltips.top="'您暂无权限处理'">-->
            <!--            </i>-->
            <i v-else class="bk-icon icon-right-shape icon-default"></i>
          </template>
          <!-- 无权限提示 icon -->
          <!--          <i v-else-->
          <!--             class="bk-itsm-icon icon-icon-no-permissions"-->
          <!--             style="margin-left: 5px;"-->
          <!--             v-bk-tooltips.top="'您暂无权限处理'">-->
          <!--          </i>-->
          <span class="node-name">{{ nodeInfo.name }}</span>
          <!-- 当前节点处理人 -->
          <span class="node-deal-person">
            {{ nodeInfo.name === '提单' ? '发起人:' : '处理人：'
            }}{{ !!currSignProcessorInfo ? signProcessors : nodeInfo.processors }}
          </span>
          <span class="node-deal-time" v-show="nodeInfo.name === '提单'">
            {{ '创建时间：' }}{{ nodeInfo.create_at }}
          </span>
          <!--          &lt;!&ndash; 会签人员信息 &ndash;&gt;-->
          <!--          <bk-popover placement="top" theme="light" trigger="click">-->
          <!--                        <span-->
          <!--                          v-if="nodeInfo.type === 'SIGN'"-->
          <!--                          class="bk-processor-check">-->
          <!--                            {{ nodeInfo.is_sequential ? '点击查看' : '查看会签顺序' }}-->
          <!--                        </span>-->
          <!--        <div class="bk-processor-content" slot="content">-->
          <!--          <div v-for="(processor, pIndex) in nodeInfo.tasks" :key="pIndex" class="bk-processor-one">-->
          <!--            <div v-if="nodeInfo.is_sequential && pIndex" class="bk-arrow">-->
          <!--              <i class="bk-itsm-icon icon-arrow-long arrow-cus"></i>-->
          <!--            </div>-->
          <!--            <div class="bk-processor-span">-->
          <!--              <span class="mr5 ml5">{{ processor.processor }}</span>-->
          <!--            </div>-->
          <!--          </div>-->
          <!--        </div>-->
          <!--        </bk-popover>-->
          <!-- 状态 icon, API 节点和标准运维节点才显示 -->
          <span class="node-deal-status" v-if="nodeInfo.status === 'RUNNING'">
            <span class="status-icon">
              <bk-spin theme="primary" size="mini" placement="right"> 处理中 </bk-spin>
            </span>
          </span>

          <!--        <task-status :status="nodeInfo.status"></task-status>-->
          <!-- sla 时间 -->
        </p>
        <p class="sla-time-info" v-if="nodeInfo.sla_task_status === 2">
          <span class="bk-operation-timeout" :style="'color: ' + slaInfo.color">
            <i class="bk-itsm-icon icon-clock-new"></i>
            <span style="margin-left: 5px"> {{ '计划完成时间：' }}{{ nodeInfo.sla_deadline || '--' }} </span>
            <span style="margin-left: 15px">
              {{ slaInfo.isTimeOut ? '超时：' : '剩余：' }}{{ nodeInfo.sla_timeout }}
            </span>
          </span>
        </p>
      </div>
      <collapse-transition>
        <div class="bk-node-form" v-if="unfold && nodeInfo.type !== 'DATA-PROC'" :style="backGroundColor">
          <!-- 禁用遮罩 -->
          <!--          <div class="bk-node-disabled"></div>-->
          <div class="bk-form bk-form-vertical">
            <!-- 节点任务 -->
            <!--                        <node-task-list-->
            <!--                          v-if="(nodeInfo.can_create_task || nodeInfo.can_execute_task)"-->
            <!--                          :node-info="nodeInfo"-->
            <!--                          :ticket-info="ticketInfo"-->
            <!--                          @updateCurrentStep="successFn">-->
            <!--                        </node-task-list>-->
            <div v-if="nodeInfo.status !== 'RUNNING'" class="bk-area-show-back">
              <!-- 静态展示 -->
              <template v-for="(ite, fIndex) in nodeInfo.fields">
                <fields-done :key="fIndex" :item="ite" origin="log"> </fields-done>
              </template>
            </div>
            <!-- 字段列表 -->
            <div v-else-if="nodeInfo.fields.length > 0">
              <field-info
                ref="fieldInfo"
                :fields="nodeInfo.fields"
                :all-field-list="allFieldList">
              </field-info>
            </div>
          </div>
          <div class="bk-form-btn" v-if="nodeInfo.type !== 'TASK'">
            <!-- 响应后才能处理 -->
            <template v-if="isShowDealBtns">
              <template v-for="(btn, btnIndex) in nodeInfo.operations">
                <bk-button
                  style="margin-right: 8px"
                  v-if="ignoreOperations.indexOf(btn.key) === -1"
                  :key="btn.key"
                  :theme="btnIndex === 0 ? 'primary' : 'default'"
                  :title="btn.name"
                  :disabled="!btn.can_operate || !nodeInfo.is_schedule_ready"
                  :loading="isBtnLoading(nodeInfo) || submitting"
                  @click="clickBtn(btn)">
                  <template v-if="!nodeInfo.is_schedule_ready">
                    <span v-bk-tooltips.top="'请将任务列表中的任务全部处理完成之后再进行处理提交'">{{ btn.name }}</span>
                  </template>
                  <template v-else>
                    {{ btn.name }}
                  </template>
                </bk-button>
              </template>
              <bk-button
                style="margin-right: 8px"
                v-if="ignoreOperations.indexOf('TRANSITION') === -1"
                :theme="'default'"
                :disabled="!nodeInfo.is_schedule_ready"
                @click="clickBtn('RESET')">
                重置
              </bk-button>
            </template>
            <!-- 节点触发器 -->
            <bk-dropdown-menu
              v-if="triggers && triggers.length && nodeInfo.can_operate"
              ref="dropdown"
              class="bk-node-trigger"
              :align="'right'"
              :font-size="'medium'"
              @show="isDropdownShow = true"
              @hide="isDropdownShow = false">
              <bk-button class="node-trigger-btn" slot="dropdown-trigger" style="width: auto">
                <span>{{ '更多操作' }}</span>
                <i :class="['bk-icon icon-angle-down', { 'icon-flip': isDropdownShow }]"></i>
              </bk-button>
              <ul class="bk-dropdown-list" slot="dropdown-content">
                <li v-for="(trigger, tIndex) in triggers" :key="tIndex">
                  <a href="javascript:;" @click="openTriggerDialog(trigger)">{{ trigger.display_name }}</a>
                </li>
              </ul>
            </bk-dropdown-menu>
          </div>
        </div>
      </collapse-transition>
    </div>
    <ticket-trigger-dialog ref="triggerDialog" @init-info="successFn"></ticket-trigger-dialog>
    <node-deal-dialog
      :node-info="nodeInfo"
      :submitting="submitting"
      :open-form-info="openFormInfo"
      :all-groups="allGroups"
      :ticket-info="ticketInfo"
      @submitFormAjax="submitFormAjax"></node-deal-dialog>
  </div>
</template>

<script>
import collapseTransition from '@/utils/collapse-transition.js';
import fieldInfo from './fieldInfo.vue';
import fieldsDone from './fieldsDone.vue';
import commonMix from '@/commonMix/common.js';
import ticketTriggerDialog from './ticketTriggerDialog.vue';
import { errorHandler } from '@/utils/errorHandler.js';
import { convertTimeArrToMS, convertTimeArrToString, convertMStoString } from '@/utils/util.js';
import nodeDealDialog from './nodeDealDialog.vue';
import cloneDeep from 'lodash.clonedeep';

export default {
  name: 'NodeDetailItem',
  components: {
    fieldsDone,
    fieldInfo,
    collapseTransition,
    ticketTriggerDialog,
    nodeDealDialog,
  },
  inject: ['getNodeList'],
  mixins: [commonMix],
  props: {
    ticketInfo: {
      type: Object,
      default: () => ({}),
    },
    nodeInfo: {
      type: Object,
      default: () => ({}),
    },
    index: {
      type: Number,
    },
    nodeList: {
      type: Array,
      default() {
        return [];
      },
    },
    allFieldList: {
      type: Array,
      default() {
        return [];
      },
    },
    allGroups: {
      type: Array,
      default: () => [],
    },
    ticketTriggerList: {
      type: Array,
      default: () => [],
    },
    isLastNode: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      convertTimeArrToString,
      replyBtnLoading: false,
      unfold: false, // 是否展开
      isFullScreen: false,
      submitting: false,
      ignoreOperations: ['SUSPEND', 'TERMINATE'],
      nodeDetailLoading: false,
      validatePopInfo: {
        openShow: false,
        content: '',
        title: '缺少必填信息',
      },
      // 弹窗处理信息(填写表单)
      openFormInfo: {
        isShow: false,
        title: '',
        width: 700,
        headerPosition: 'left',
        autoClose: false,
        precision: 0,
        btnInfo: {},
      },
      openSubmitInfo: {
        openShow: false,
        content: '',
      },
      slaInfo: {
        color: '',
        isTimeOut: false,
      },
      // 当审批节点为部门时 储存该部门人员
      userList: [],
      isDropdownShow: false,
    };
  },
  computed: {
    // 背景颜色
    backGroundColor() {
      if (this.nodeInfo.status !== 'RUNNING') {
        return {
          background: '#F5F7FA',
        };
      }
      return '';
    },
    isHaveApprovePermission() {
      if (this.nodeInfo.type === 'APPROVAL') {
        if (this.nodeInfo.processors_type === 'ORGANIZATION') {
          return this.userList.map(item => item.username).includes(window.username);
        }
        return this.nodeInfo.origin_processors.split(',').includes(window.username);
      }
      return true;
    },

    // 会签人信息
    currSignProcessorInfo() {
      if (!this.nodeInfo.can_operate && this.nodeInfo.type === 'SIGN') {
        return this.nodeInfo.tasks.find(task => task.can_view);
      }
      return undefined;
    },
    // tips 显示的处理人列表
    tipsProcessorsInfo() {
      // 把 `(共2人, 已处理0人)` 字符串从处理人中提取出来
      let completedStr = '';
      const processors =        this.nodeInfo.processors_type === 'ORGANIZATION' ? this.nodeInfo.members : this.nodeInfo.processors;
      const replaceStr = processors.replace(/ \(共\d+人, 已处理\d+人\)/, (match) => {
        completedStr = match;
        return '';
      });
      const list = replaceStr.split(',').filter(name => !!name);
      if (list.length >= 30 && this.nodeInfo.processors_type === 'ORGANIZATION') {
        list.push('...');
      }
      return {
        list,
        extend: completedStr,
      };
    },
    // 会签完成信息
    signProcessors() {
      const { tasks } = this.nodeInfo;
      if (this.currSignProcessorInfo) {
        return `${`${this.currSignProcessorInfo.processor}(共${tasks.length}人，已处理${
          tasks.filter(task => task.status === 'FINISHED').length
        }`}人`;
      }
      return '';
    },
    // 当前节点触发器列表
    triggers() {
      return this.ticketTriggerList.filter(trigger => Number(trigger.sender) === Number(this.nodeInfo.state_id));
    },
    // // 节点操作权限
    // hasNodeOptAuth() {
    //   return this.nodeInfo.can_operate || !!this.currSignProcessorInfo || this.nodeInfo.can_execute_task;
    // },
    // 是否显示处理按钮
    isShowDealBtns() {
      // 失败任务（主要是标准运维失败时），有单独处理
      if (this.nodeInfo.status === 'FAILED') {
        return false;
      }
      // SLA 需要响应后才显示处理按钮
      if (this.nodeInfo.sla_task_status === 2 && this.nodeInfo.is_reply_need === true) {
        return false;
      }
      if (this.nodeInfo.status === 'FINISHED' || this.nodeInfo.type === 'DATA-PROC') {
        return false;
      }
      return true;
    },
  },
  async created() {
    this.initData();
    if (this.nodeInfo.type === 'APPROVAL' && this.nodeInfo.processors_type === 'ORGANIZATION') {
      this.nodeDetailLoading = true;
      this.userList = await this.getUserByDepartment(this.nodeInfo.origin_processors);
      this.nodeDetailLoading = false;
    }
  },
  methods: {
    async getUserByDepartment(params) {
      try {
        // params maybe ,8,
        const  id = params.replace(/,/g, '');
        const res = await this.$store.dispatch('setting/getUserByDepartment', { id });
        return res.data;
      } catch (e) {
        console.warn(e);
      } finally {
      }
    },
    initData() {
      // this.unfold = this.hasNodeOptAuth;
      const item = this.nodeInfo;
      if (item.sla_task_status === 2) {
        if (item.sla_status === 2) {
          this.slaInfo.color = '#FE9C00';
        }
        if (item.sla_status === 4) {
          this.slaInfo.color = '#EA3536';
          this.slaInfo.isTimeOut = true;
        }
        // this.runTime();
      }
    },

    // 按钮操作
    clickBtn(btn) {
      if (btn === 'RESET') {
        const fields = cloneDeep(this.nodeInfo.fields).map((item) => {
          const  resetVal = item.meta.code === 'APPROVE_RESULT' ? 'true' : '';
          return { ...item, val: '', value: resetVal  };
        });
        this.$set(this.nodeInfo, 'fields', fields);
        return;
      }
      // 字段校验
      if (btn.key === 'TRANSITION' && this.$refs.fieldInfo && !this.$refs.fieldInfo.checkValue()) {
        return;
      }
      this.openFormInfo.btnInfo = btn;
      this.openFormInfo.title = btn.name;
      // 二次确认弹窗的样式不同
      if (['TRANSITION', 'CLAIM', 'UNSUSPEND'].includes(this.openFormInfo.btnInfo.key)) {
        const contentMap = {
          TRANSITION: '提交后，流程将转入下一环节，当前提交的部分内容将无法修改',
          CLAIM: '执行认领操作后，单据将流入我的待办',
          UNSUSPEND: '执行恢复操作后，单据将可以继续处理',
        };
        this.openSubmitInfo.content = contentMap[this.openFormInfo.btnInfo.key];
        this.$bkInfo({
          type: 'warning',
          title: btn.key === 'TRANSITION' ? `是否${this.openFormInfo.title}` : this.openFormInfo.title,
          subTitle: this.openSubmitInfo.content,
          confirmFn: () => {
            this.submitFormAjax();
          },
        });
      } else {
        this.openFormInfo.isShow = true;
        this.openFormInfo.title = btn.name;
      }
    },
    submitFormAjax(submitFormData) {
      const id = this.nodeInfo.ticket_id;
      // 终止
      if (this.openFormInfo.btnInfo.key === 'TERMINATE') {
        const params = {
          state_id: this.nodeInfo.state_id,
          terminate_message: submitFormData.terminate_message,
        };
        this.submitAjax('terminableOrder', params, id);
      }
      // 审批、通过
      if (this.openFormInfo.btnInfo.key === 'TRANSITION') {
        // 将字段中的时间转换一遍
        this.fieldFormatting(this.nodeInfo.fields);
        const params = {
          state_id: this.nodeInfo.state_id,
          fields: this.nodeInfo.fields
            .filter(ite => !ite.is_readonly && ite.showFeild && ite.type)
            .map((item) => {
              if (item.type === 'FILE') {
                item.value = item.value.toString();
              }
              if (item.type === 'IMAGE') {
                return {
                  id: item.id,
                  key: item.key,
                  type: item.type,
                  choice: item.choice,
                  value: JSON.stringify(item.val) || '',
                };
              }
              return {
                id: item.id,
                key: item.key,
                type: item.type,
                choice: item.choice,
                // 兼容DESC字段
                value: (item.type === 'DESC' ? item.display_value : item.value) || '',
              };
            }),
        };
        this.submitAjax('proceedOrder', params, id);
      }
      // 转单，挂起，恢复，分派，认领
      if (
        this.openFormInfo.btnInfo.key === 'SUSPEND'
        || this.openFormInfo.btnInfo.key === 'UNSUSPEND'
        || this.openFormInfo.btnInfo.key === 'CLAIM'
      ) {
        const params = {
          state_id: this.nodeInfo.state_id,
          processors: '',
          processors_type: '',
          action_type: this.openFormInfo.btnInfo.key,
        };
        // 挂起
        if (this.openFormInfo.btnInfo.key === 'SUSPEND') {
          params.processors = window.username;
          params.processors_type = 'PERSON';
          params.action_message = submitFormData.suspend_message;
        }
        // 恢复，认领
        if (this.openFormInfo.btnInfo.key === 'UNSUSPEND' || this.openFormInfo.btnInfo.key === 'CLAIM') {
          params.processors = window.username;
          params.processors_type = 'PERSON';
        }
        this.submitAjax('distributeOrder', params, id);
      }
      if (this.openFormInfo.btnInfo.key === 'DELIVER' || this.openFormInfo.btnInfo.key === 'DISTRIBUTE') {
        const params = {
          state_id: this.nodeInfo.state_id,
          action_type: this.openFormInfo.btnInfo.key,
          processors: '',
          processors_type: '',
        };
        // 转单
        if (this.openFormInfo.btnInfo.key === 'DELIVER') {
          params.processors = submitFormData.person.value;
          params.processors_type = submitFormData.person.type;
          params.action_message = submitFormData.deliverReason;
        }
        // 分派
        if (this.openFormInfo.btnInfo.key === 'DISTRIBUTE') {
          params.processors = submitFormData.person.value;
          params.processors_type = submitFormData.person.type;
        }
        this.submitAjax('newAssignDeliver', params, id);
      }
    },
    submitAjax(type, params, id) {
      if (this.submitting) {
        return;
      }
      this.submitting = true;
      const valueParams = {
        params,
        id,
      };
      this.$store
        .dispatch(`workbench/${type}`, valueParams)
        .then((res) => {
          if (res.result) {
            this.$bkMessage({
              message: `${this.openFormInfo.title}成功`,
              theme: 'success',
            });
          }
          this.cancelForm();
          this.successFn();
          this.getNodeList();
          this.$emit('closeSlider');
        })
        .catch((res) => {
          errorHandler(res, this);
        })
        .finally(() => {
          this.submitting = false;
          const typeList = ['TRANSITION', 'SUSPEND', 'UNSUSPEND', 'CLAIM'];
          if (typeList.some(item => item === this.openFormInfo.btnInfo.key)) {
            this.cancelForm();
          }
        });
    },
    // 展开收起
    closeUnflod(e) {
      // // 禁止冒泡
      // if (e.target.className.indexOf('bk-processor-check') === -1) {
      //   if (!this.nodeInfo.can_operate && !this.currSignProcessorInfo) {
      //     return;
      //   }
      //   this.unfold = !this.unfold;
      // }
      if (this.isHaveApprovePermission) {
        this.unfold = !this.unfold;
      }
    },
    // 操作成功
    successFn() {
      this.$emit('successFn');
    },
    cancelForm() {
      this.openFormInfo.isShow = false;
    },
    openTriggerDialog(trigger) {
      this.$refs.triggerDialog.openDialog(trigger);
    },
    // 提交按钮 loading 状态
    isBtnLoading(item) {
      // 会签或审批节点提交后，当前处理人task 为 RUNNING|EXECUTED状态，则继续轮询 FINISHED
      const currUserDealTask =        (item.tasks
          && item.tasks.find((task) => {
            const splitName = task.processor.replace(/\((.+?)\)/, '');
            return splitName === window.username;
          }))
        || {};
      if (['SIGN', 'APPROVAL'].includes(item.type) && ['RUNNING', 'EXECUTED'].includes(currUserDealTask.status)) {
        return true;
      }
      return false;
    },
    runTime() {
      let { slaTime } = this.slaInfo;
      if (!slaTime) {
        slaTime = convertTimeArrToMS(this.nodeInfo.sla_timeout.map(num => Math.abs(num)));
        this.nodeInfo.sla_timeout = convertMStoString(slaTime * 1000);
      }
      this.myInterval(() => {
        this.slaInfo.isTimeOut ? slaTime++ : slaTime--;
        if (slaTime <= 0) {
          this.slaInfo.isTimeOut = true;
          this.slaInfo.color = '#EA3536';
        }
        this.nodeInfo.sla_timeout = convertMStoString(slaTime * 1000);
      }, 1000);
    },
    myInterval(fn, time) {
      if (this._isDestroyed === true) return false;
      const outTimeKey = setTimeout(() => {
        fn();
        clearTimeout(outTimeKey);
        this.myInterval(fn, time);
      }, time);
    },
    // 响应按钮
    replyAssignDeliver() {
      const ticketId = this.ticketInfo.id;
      const stateId = this.nodeInfo.state_id;
      const valueParams = {
        params: {
          state_id: stateId,
        },
        id: ticketId,
      };
      this.replyBtnLoading = true;
      this.$store
        .dispatch('deployOrder/replyAssignDeliver', valueParams)
        .then((res) => {
          this.$bkMessage({
            message: '响应成功',
            theme: 'success',
          });
          this.cancelForm();
          this.successFn();
          this.$emit('closeSlider');
        })
        .catch((res) => {
          this.$bkMessage({
            message: res.data.msg || '响应失败！',
            theme: 'error',
            ellipsisLine: 0,
          });
        })
        .finally(() => {
          this.replyBtnLoading = false;
        });
    },
  },
};
</script>
<style scoped lang="postcss">
.bk-content-node {
  padding-bottom: 28px;
  margin-bottom: 2px;
  position: relative;

  .bk-node-circle {
    position: absolute;
    top: 16px;
    left: -1px;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: #a3c5fd;
    z-index: 1;
  }

  .bk-node-info {
    position: relative;
    font-size: 14px;
    margin-left: 27px;

    .bk-node-title {
      margin-bottom: 4px;
      outline: none;
      background-color: #f0f1f5;
      color: #737987;
      padding: 0;
      width: 100%;
      display: flex;
      align-items: center;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;

      .node-title-processor {
        display: inline-block;
        max-width: 80%;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        outline: none;
        font-size: 12px;
      }

      .bk-processor-check {
        cursor: pointer;
        font-size: 12px;
        color: #3a84ff;
        margin-left: 10px;
        outline: none;
      }

      .node-name {
        margin: 0 15px 0 5px;
        color: #63656e;
        font-size: 12px;
        font-weight: bold;
      }

      .node-deal-person {
        font-size: 12px;
        color: #979ba5;
        margin-left: 9px;
      }

      .node-deal-time {
        font-size: 12px;
        color: #979ba5;
        margin-left: 9px;
      }

      .node-deal-status {
        font-size: 12px;
        color: #3a84ff;
        float: right;
        position: absolute;
        top: 4px;
        right: 0;
        line-height: 34px;
        margin-right: 24px;
      }
    }

    .bk-node-header {
      position: relative;
      padding: 8px 8px;
      height: 34px;
      width: 100%;
      color: #737987;
      background-color: #f5f7fa;
      border-radius: 2px;

      .icon-angle-down {
        font-size: 22px;
      }
    }

    .sla-time-info {
      padding-left: 20px;
      font-size: 12px;
    }

    .icon-default {
      font-size: 12px;
      color: #979ba5;
    }

    .circle {
      width: 8px;
      height: 8px;
      background: #979ba5;
      border-radius: 50%;
    }

    .right-float {
      position: absolute;
      right: 10px;
      top: 50%;
      transform: translateY(-50%);
      margin-left: auto;
    }

    .full-screen-wrap {
      .icon-order-open {
        font-size: 16px;
        color: #979ba5;
        z-index: 2;
        cursor: pointer;

        &:hover {
          color: #63656e;
        }
      }

      .exit-full-screen {
        padding: 0px 10px 0px 18px;
        display: inline-block;
        height: 40px;
        line-height: 40px;
        font-size: 16px;
        color: #979ba5;
        z-index: 2;
        cursor: pointer;

        .exit-text {
          font-size: 12px;
        }

        &:hover {
          background-color: #dcdee5;
        }
      }
    }

    .bk-node-cursor {
      cursor: pointer;
      background: #f5f7fa;
    }

    .bk-node-form {
      position: relative;
      padding: 15px 5px 15px 15px;
      transition: 0.3s height ease-in-out, 0.3s padding-top ease-in-out, 0.3s padding-bottom ease-in-out;
      font-size: 12px;
      color: #979ba5;

      .bk-node-trigger {
        display: inline-block;
        vertical-align: middle;

        .node-trigger-btn {
          width: auto;
        }
      }

      .bk-form-btn {
        display: flex;
        margin-top: 10px;
      }

      .bk-form {
        position: relative;
      }

      .bk-area-show-back {
        display: flex;
        flex-wrap: wrap;
      }
    }

    .bk-node-disabled {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      cursor: not-allowed;
      z-index: 5;
    }
  }

  .bk-content-line {
    position: absolute;
    top: 20px;
    left: 2px;
    height: 100%;
    border-left: 2px solid #f0f3f6;
  }

  .bk-operation-timeout {
    display: block;
    width: calc(100% - 26px);
    margin-left: 16px;
    margin-right: 10px;
    color: #979ba5;
    line-height: 34px;
    min-width: 265px;
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;
    font-size: 12px;

    .icon-clock-new {
      vertical-align: 1px;
    }
  }
}

.status-icon {
  display: inline-flex;

  /deep/ .bk-spin .bk-spin-title {
    color: #3a84ff;
    font-size: 12px;
  }
}

.image-item {
  position: relative;
  display: inline-block;
  margin-left: 8px;
  margin-bottom: 8px;
  padding: 5px;
  width: 100px;
  height: 100px;
  background: #fafbfd;
  border: 1px solid #c4c6cc;
  border-radius: 2px;

  img {
    width: 100%;
  }

  &:not(.disabled):hover {
    &:after {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.6);
    }

    .delete-icon {
      display: block;
    }
  }
}
</style>

<template>
  <div class="create-ticket-container">
    <div v-if="!showSuccess" class="form-fields-content">
      <template v-if="!fieldListLoading">
        <template v-if="fieldList.length > 0">
          <form-fields style="width: 760px" :fields="fieldList" :value="formValue" @change="debounceChange">
          </form-fields>
          <div class="btn-actions">
            <bk-button
              v-cursor="{ active: noOperatePerm }"
              theme="primary"
              :class="['submit-btn', { 'btn-permission-disabled': noOperatePerm }]"
              :disabled="actionId ? false : !(componentId in actionsPermMap)"
              :loading="submitPending"
              @click="submit">
              提交
            </bk-button>
            <bk-button v-if="showCancel" @click="$emit('onCancel')">取消</bk-button>
          </div>
        </template>
        <bk-exception v-else type="empty">暂无表单字段数据</bk-exception>
      </template>
    </div>
    <create-ticket-success v-else-if="!isBuiltIn && showSuccess" :id="ticketId" @back="handleSuccessBack">
    </create-ticket-success>
    <bk-dialog
      v-if="isBuiltIn"
      :value="visible"
      :render-directive="'if'"
      theme="primary"
      v-model="visible"
      :mask-close="false"
      header-position="left"
      :show-footer="false"
      @value-change="handleCloseDialog"
      title="提交详情">
      <div class="status-wrapper">
        <div class="icon-wrapper">
          <bk-spin size="large" placement="bottom" v-if="ticketStatus === 'RUNNING'"> 提交中</bk-spin>
        </div>
        <div class="icon-wrapper" v-if="ticketStatus === 'FINISHED'">
          <i class="bk-icon icon-check-circle"></i>
          <p>提交成功</p>
        </div>
        <div class="icon-wrapper" v-if="ticketStatus === 'FAILED'">
          <i class="bk-icon icon-close-circle error-icon"></i>
          <p>
            提交失败,
            <bk-button theme="primary" @click="goToDetail" text class="detail-btn">查看流程详情</bk-button>
          </p>
        </div>
      </div>
    </bk-dialog>
  </div>
</template>
<script>
import clonedeep from 'lodash.clonedeep';
import permission from '@/components/permission/mixins.js';
import { FIELDS_TYPES } from '@/constants/forms.js';
import FormFields from '@/components/form/formFields/index.vue';
import CreateTicketSuccess from './createTicketSuccess.vue';
import { debounce } from '@/utils/util';

export default {
  name: 'CreateTicket',
  components: {
    FormFields,
    CreateTicketSuccess,
  },
  mixins: [permission],
  props: {
    appId: String,
    appName: String,
    funcId: Number,
    // 标识入口字段，为空表示表单类型页面，不为空则表示来自于功能卡片或者表格操作项，值可能为功能卡片的component_id或者表格操作按钮的id
    actionId: [String, Number],
    actionType: String, // 标识表格页面的操作区域，例如顶部按钮操作，表格内操作
    componentId: Number, // 页面内的组件id，表格、表单、功能卡片
    version: String,
    page: {
      type: Object,
      default: () => ({}),
    },
    actionsPermMap: {
      type: Object,
      default: () => ({}),
    },
    showCancel: Boolean,
  },
  data() {
    return {
      fieldList: [],
      fieldListLoading: false,
      formValue: {},
      visible: false,
      ticketId: '',
      isBuiltIn: false,
      showSuccess: false,
      submitPending: false,
      ticketStatus: 'RUNNING',
    };
  },
  computed: {
    noOperatePerm() {
      return !this.actionId && this.actionsPermMap[this.componentId] === false;
    },
    // 离开提单页面时，是否需要二次确认
    needLeaveConfirm() {
      return !this.showSuccess && !this.visible;
    },
  },
  watch: {
    funcId(val) {
      if (typeof val === 'number') {
        this.fieldList = [];
        this.formValue = {};
        this.getFieldList();
      }
    },
  },
  created() {
    if (typeof this.funcId === 'number') {
      this.getFieldList();
      this.getBuiltInService();
    }
    this.debounceChange = debounce(this.handleChangeFormValue, 300);
  },
  methods: {
    async getFieldList() {
      try {
        this.fieldListLoading = true;
        const res = await this.$store.dispatch('application/getFormPageFields', {
          type: this.page.type,
          paths: {
            project_key: this.appId,
            page_id: this.page.id,
            version_number: this.version,
            page_component_id: this.componentId,
            service_id: this.funcId,
            source: this.actionType,
          },
        });
        this.fieldList = res.data.filter(item => item.type !== 'AUTO-NUMBER');
        this.formValue = this.getFormValue();
      } catch (e) {
        console.error(e);
      } finally {
        this.fieldListLoading = false;
      }
    },
    getFormValue() {
      const value = {};
      this.fieldList.forEach((item) => {
        if ('default' in item) {
          if (['MULTISELECT', 'CHECKBOX', 'MEMBER', 'MEMBERS', 'TABLE', 'IMAGE'].includes(item.type)) {
            value[item.key] = item.default ? item.default.split(',') : [];
          } else {
            value[item.key] = item.default;
          }
        } else {
          value[item.key] = clonedeep(FIELDS_TYPES.find(item => item.type === this.field.type).default);
        }
      });
      return value;
    },
    getApiFields() {
      return this.fieldList.map((item) => {
        const { choice, id, key, type } = item;
        let value = this.formValue[key];
        if (type === 'IMAGE') {
          value = this.formValue[key].map(item => item.path);
        } else if (['MULTISELECT', 'CHECKBOX', 'MEMBER', 'MEMBERS'].includes(type)) {
          value = Array.isArray(this.formValue[key]) ? this.formValue[key].join(',') : this.formValue[key];
        } else if (type === 'INT') {
          value = this.formValue[key] || 0;
        }
        return { choice, id, key, type, value };
      });
    },
    resetData() {
      this.fieldList = [];
      this.formValue = this.getFormValue();
    },
    handleSuccessBack() {
      this.showSuccess = false;
      this.ticketId = '';
    },
    async getBuiltInService() {
      try {
        const res = await this.$store.dispatch('setting/getBuiltInService', this.funcId);
        this.isBuiltIn = res.data.is_builtin;
      } catch (e) {
        console.error(e);
      }
    },
    async submit() {
      if (this.noOperatePerm) {
        const resource = {
          action: [{ id: this.componentId, name: '提交' }],
          page: [{ id: this.page.id, name: this.page.name }],
          project: [{ id: this.appId, name: this.appName }],
        };
        this.applyForPermission(['action_execute'], [], resource);
        return;
      }

      // 校验多值类型的表单配置值的数目范围后，用户填写的值数目是否范围内
      let formValNumRangeValid = true;
      this.fieldList.some((field) => {
        const fieldVal = this.formValue[field.key];
        if ('num_range' in field) {
          let msg = '';
          if (typeof field.num_range[0] === 'number' && fieldVal.length < field.num_range[0]) {
            msg = `${field.name}表单的值数目不能小于${field.num_range[0]}`;
          }
          if (typeof field.num_range[1] === 'number' && fieldVal.length > field.num_range[1]) {
            msg = `${field.name}表单的值数目不能大于${field.num_range[1]}`;
          }
          if (msg) {
            formValNumRangeValid = false;
            this.$bkMessage({
              theme: 'error',
              message: msg,
            });
            return true;
          }
        }
      });
      if (!formValNumRangeValid) {
        return;
      }

      try {
        this.submitPending = true;
        const fieldsRequest = this.getApiFields();
        const params = {
          service_id: this.funcId,
          fields: fieldsRequest,
          project_key: this.appId,
          page_id: this.page.id,
          action_id: this.actionId || this.componentId, // 优先取action_id，若没有则取表单页面component_id
        };
        const res = await this.$store.dispatch('application/createTicket', params);
        this.ticketId = res.data.id;
        if (this.isBuiltIn) {
          this.visible = true;
          this.polling('workbench/getOrderStatus', { id: this.ticketId });
        }
        this.formValue = this.getFormValue();
        this.showSuccess = !this.isBuiltIn;
      } catch (e) {
        console.error(e);
      } finally {
        this.submitPending = false;
      }
    },
    async polling(url, data, delay = 1000) {
      let timer;
      try {
        const res = await this.$store.dispatch(url, data);
        const resData = res.data.filter(i => i.type === 'DATA-PROC');
        const currentStatus = resData.length > 0 ? resData[0].status : '';
        if (!['FINISHED', 'FAILED'].includes(currentStatus) && this.visible) {
          timer = setTimeout(() => this.polling(url, data, delay), delay);
        } else {
          clearTimeout(timer);
          this.ticketStatus = currentStatus;
        }
      } catch (e) {
        console.warn(e);
      }
    },
    handleCloseDialog() {
      this.ticketStatus = 'RUNNING';
      if (!this.visible) {
        this.formValue = {};
        this.getFieldList();
      }
    },
    goToDetail() {
      this.$router.push({ name: 'processDetail', params: { id: this.ticketId } });
    },
    async handleChangeFormValue(key, $event) {
      this.formValue = $event;
      const item = this.fieldList;
      for (let i = 0 ;i < item.length;i++) {
        // 当前用户输入的值 跳出联动
        if (item[i].key === key) {
          continue;
        }
        if (item[i].meta.data_config) {
          const { type, conditions, value } = item[i].meta.data_config;
          // 判断变化的字段是不是被联动的字段
          const isRelationFields = conditions.map(condition => `${item[i].meta.worksheet.key}_${condition.id}`).includes(key);
          // 当前表单
          let isConditonFlag;
          if (type === 1 && isRelationFields) {
            isConditonFlag = conditions.every((condition) => {
              const tempkey = `${item[i].meta.worksheet.key}_${condition.id}`;
              if (condition.type === 'variable') {
                return $event[tempkey] === $event[`${item[i].meta.worksheet.key}_${condition.relationCurrentValue}`];
              }
              return $event[tempkey] === condition.relationCurrentValue;
            });
            isConditonFlag ? this.formValue[item[i].key] = value : this.formValue[item[i].key] = '';
          } else if (type === 2 || type === 3) {
            let res;
            let validateFlag;
            for (let j = 0; j < conditions.length;j++) {
              const field = conditions[j].id;
              // 当前表单字段
              let curKey;
              // 是否含有联动字段
              const isHaveRelationFields = item
                .some(it => it.meta.worksheet.field_key === conditions[j].relationCurrentValue);
              if (isHaveRelationFields) {
                curKey = item.find(it => it.meta.worksheet.field_key === conditions[j].relationCurrentValue).key;
              }
              // const curKey = `${conditions[j].relationCurrentValue}`;
              const params = this.getConditionParams({
                key: field,
                value: conditions[j].type === 'variable' ? $event[curKey] : conditions[j].relationCurrentValue,
                token: item[i].token, fields: [item[i].meta.data_config.value],
              });
              try {
                res = await this.$store.dispatch('setting/getWorksheetData', params);
                if (res.data && res.data.length > 0) {
                  validateFlag = true;
                } else {
                  validateFlag = false;
                  break;
                }
              } catch (e) {
                console.error(e);
              }
            }
            validateFlag && this.$set(this.formValue, item[i].key, res.data[0][item[i].meta.data_config.value]);
          }
        }
      }
    },
    getConditionParams(info) {
      const   { key, value, token, fields } = info;
      const params = {
        token,
        fields,
        conditions: {
          connector: 'and',
          expressions: [
            {
              key,
              value,
              type: 'const',
              condition: '==',
            },
          ],
        },
      };
      return params;
    },
  },
};
</script>
<style lang="postcss" scoped>
@import '../../../css/scroller.css';

.create-ticket-container {
  padding: 40px;
  height: 100%;
  background: #ffffff;
  overflow: auto;
  @mixin scroller;
}

.btn-actions {
  margin-top: 40px;

  .submit-btn {
    margin-right: 4px;
  }
}

/deep/ .bk-exception-text {
  font-size: 18px;
}

.icon-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;

  .detail-btn {
    font-size: 16px;
  }

  & > i {
    font-size: 56px;
    color: #2dcb56;
  }

  & > p {
    margin: 20px 0 8px;
    color: #000000;
    font-size: 16px;
    line-height: 1;
  }

  .error-icon {
    color: #ea3636;
  }

  .desc {
    color: #63656e;
    font-size: 12px;
  }
}

.status-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>

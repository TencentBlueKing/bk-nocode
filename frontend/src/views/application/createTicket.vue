<template>
  <div>
    <div class="common-page-wrapper">
      <div class="page-header-container">
        <div class="title-area">
          <div class="page-title">表单外链填写</div>
        </div>
      </div>
    </div>
    <div class="create-ticket-container" v-if="!showSuccess">
      <div class="form-fields-content">
        <template v-if="!fieldListLoading">
          <template v-if="fieldList.length > 0">
            <form-fields
              style="width: 760px"
              :fields="fieldList"
              :value="formValue"
              @change="(key,$event) => formValue = $event">
            </form-fields>
            <div class="btn-actions">
              <bk-button
                theme="primary"
                class="submit-btn"
                :loading="submitPending"
                @click="submit">
                提交
              </bk-button>
            </div>
          </template>
          <bk-exception v-else type="empty">暂无表单字段数据</bk-exception>
        </template>
      </div>
    </div>
    <div class="create-ticket-success" v-else-if="showSuccess">
      <div class="success-tip-content">
        <div class="icon-wrapper">
          <i class="bk-icon icon-check-circle"></i>
          <p>提单成功</p>
        </div>
        <div class="btn-action">
          <bk-button @click="handleSuccessBack">继续提单</bk-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import clonedeep from 'lodash.clonedeep';
import { FIELDS_TYPES } from '@/constants/forms.js';
import FormFields from '@/components/form/formFields/index.vue';

export default {
  name: 'CreateTicket',
  components: {
    FormFields,
  },
  props: {
    token: String,
  },
  data() {
    return {
      fieldList: [],
      fieldListLoading: false,
      showSuccess: false,
      formValue: {},
      submitPending: false,
    };
  },
  created() {
    this.getFieldList();
  },
  methods: {
    async getFieldList() {
      try {
        this.fieldListLoading = true;
        const res = await this.$store.dispatch('application/getOpenFormPageFields', {
          token: this.token,
        });
        console.log(res.data);
        this.fieldList = res.data.filter(item => item.type !== 'AUTO-NUMBER');
      } catch (e) {
        console.error(e);
      } finally {
        this.fieldListLoading = false;
      }
    },
    getApiFields() {
      return this.fieldList.map((item) => {
        const { choice, id, key, type } = item;
        let value = this.formValue[key];
        if (type === 'IMAGE') {
          value = this.formValue[key].map(item => item.path);
        } else if (['MULTISELECT', 'CHECKBOX', 'MEMBER', 'MEMBERS'].includes(type)) {
          value = Array.isArray(this.formValue[key]) ? this.formValue[key].join(',') : this.formValue[key];
        }
        return { choice, id, key, type, value };
      });
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
    async submit() {
      // 校验多值类型的表单配置值的数目范围后，用户填写的值数目是否范围内
      let formValNumRangeValid = true;
      this.fieldList.some(field => {
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
          fields: fieldsRequest,
          token: this.token,
        };
        const res = await this.$store.dispatch('application/createOpenApiTicket', params);
        if (res.result) {
          this.formValue = this.getFormValue();
          this.showSuccess = true;
        }
        // this.ticketId = res.data.id;
        // if (this.isBuiltIn) {
        //   this.visible = true;
        //   this.polling('workbench/getOrderStatus', { id: this.ticketId });
        // }
      } catch (e) {
        console.error(e);
      } finally {
        this.submitPending = false;
      }
    },
    handleSuccessBack() {
      this.showSuccess = false;
    },
  },
};
</script>

<style scoped lang="postcss">
@import '../../css/scroller.css';

.create-ticket-container {
  padding: 16px 40px 40px 40px;
  margin: 24px;
  height: calc(100vh - 100px);
  background: #ffffff;
  overflow: auto;
  @mixin scroller;
}

.page-header-container {
  position: relative;
  display: flex;
  align-items: center;
  height: 52px;
  background: #ffffff;
  box-shadow: 0 3px 4px 0 rgba(64, 112, 203, 0.06);
  z-index: 1;

  .title-area {
    display: flex;
    align-items: center;
    height: 100%;


    .page-title {
      padding-left: 24px;
      color: #313238;
      font-size: 16px;
    }
  }
}

.btn-actions {
  margin-top: 40px;

  .submit-btn {
    margin-right: 4px;
  }
}

.create-ticket-success {
  height: calc(100vh - 52px);
  display: flex;
  align-items: center;
  justify-content: center;

  .success-tip-content {
    text-align: center;
  }

  .icon-wrapper {
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

    .desc {
      color: #63656e;
      font-size: 12px;
    }
  }

  .btn-action {
    margin-top: 40px;
  }
}
</style>

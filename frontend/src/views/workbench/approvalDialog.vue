<template>
  <bk-dialog
    render-directive="if"
    :width="640"
    :value="isShow"
    :mask-close="false"
    :auto-close="false"
    header-position="left"
    title="审批"
    :loading="approvalConfirmBtnLoading"
    @confirm="onApprovalConfirm"
    @cancel="onApprovalCancel">
    <bk-form ref="approvalForm" :model="formData" :rules="formRules">
      <bk-form-item label="审批结果" :label-width="140">
        <bk-radio-group
          v-if="approvalInfo.showAllOption"
          v-model="approvalInfo.result">
          <bk-radio :value="true" class="mr50">通过</bk-radio>
          <bk-radio :value="false">拒绝</bk-radio>
        </bk-radio-group>
        <span v-else
              :class="['result-tag', approvalInfo.result ? '' : 'reject']">
                    {{ approvalInfo.result ? '通过' : '拒绝' }}
                </span>
      </bk-form-item>

      <bk-form-item label="备注" :label-width="140" :required="!approvalInfo.result" property="approvalNotice">
        <bk-input type="textarea" :row="4" :maxlength="200" v-model="formData.approvalNotice"></bk-input>
      </bk-form-item>
    </bk-form>
  </bk-dialog>
</template>

<script>
export default {
  name: 'ApprovalDialog',
  props: {
    isShow: {
      type: Boolean,
      default: false,
    },
    approvalInfo: {
      type: Object,
      default: () => ({
        result: true,
        showAllOption: false,
        approvalList: [],
      }),
    },
  },
  data() {
    return {
      approvalConfirmBtnLoading: false,
      formData: { approvalNotice: '' },
      formRules: {
        approvalNotice: [{
          validator: this.checkApprovalNotice,
          message: '备注' + '为必填项，请补充完善',
          trigger: 'blur',
        }],
      },
    };
  },
  methods: {
    onApprovalConfirm() {
      this.approvalConfirmBtnLoading = true;
      this.$refs.approvalForm.validate().then(async (val) => {
        if (val) {
          const data = {
            result: this.approvalInfo.result.toString(),
            opinion: this.formData.approvalNotice,
            approval_list: this.approvalInfo.approvalList,
          };
          try {
            await this.$store.dispatch('workbench/batchApproval', data);
            this.$emit('cancel', true);
          } catch (e) {
            console.log(e);
          } finally {
            this.formData.approvalNotice = '';
          }
        }
      })
        .finally(() => {
          this.approvalConfirmBtnLoading = false;
        });
    },
    onApprovalCancel() {
      this.formData.approvalNotice = '';
      this.approvalConfirmBtnLoading = false;
      this.$emit('cancel');
    },
    checkApprovalNotice(val) {
      if (!this.approvalInfo.result) {
        return val !== '';
      }
      return true;
    },
  },
};
</script>
<style lang='postcss' scoped>
.result-tag {
  display: inline-block;
  padding: 5px 10px;
  line-height: 1;
  color: #2dcb56;
  border: 1px solid #2dcb56;
  background: #dcffe2;
  font-size: 14px;
  font-weight: bold;
  border-radius: 2px;

  &.reject {
    color: #ff5656;
    border-color: #ff5656;
    background: #fedddc;
  }
}
</style>

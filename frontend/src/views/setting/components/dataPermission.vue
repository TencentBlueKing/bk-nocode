<template>
  <div>
  <bk-table
    :data="listData"
    :col-border="true"
    :outer-border="false">
    <bk-table-column label="页面" :width="190">
        宿舍管理
    </bk-table-column>
    <bk-table-column label="功能" :width="190">
      <template>
        <div class="system-function">
          <bk-checkbox-group class="checkbox-container">
            <bk-checkbox :value="'1'">全部范围</bk-checkbox>
            <bk-checkbox :value="'2'">仅自己提交</bk-checkbox>
            <bk-checkbox :value="'3'">制定范围  <bk-icon type="cog-shape" @click.stop="handleClick"></bk-icon>
            </bk-checkbox>
          </bk-checkbox-group>
        </div>
      </template>
    </bk-table-column>
  </bk-table>
  <bk-dialog
    title="指定范围"
    header-position="left"
    :mask-close="false"
    :auto-close="false"
    :width="640"
    :loading="dialogLoading"
    v-model="dialogShow"
    @confirm="handleConfirm"
    @cancel="handleCancel">
    <div class="form-basic-info">
    </div>
  </bk-dialog>
  </div>
</template>

<script>
export default {
  name: 'DataPermission',
  data() {
    return {
      listData: [{}],
      dialogLoading: false,
      dialogShow: false,
    };
  },
  methods: {
    handleClick() {
      this.dialogShow = true;
    },
    handleCancel() {

    },
    handleConfirm() {

    },

  },
};
</script>

<style scoped lang="postcss">

/deep/ .bk-table{
  .bk-table-border{
    border-top: none;
  }
}
.system-function{
  padding: 0 16px 16px;
}
/deep/ .bk-form-checkbox{
  margin-top: 16px;
}
.checkbox-container{
  display: flex;
  flex-direction: column;
}
</style>

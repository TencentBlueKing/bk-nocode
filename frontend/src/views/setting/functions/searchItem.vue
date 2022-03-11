<template>
  <div class="search-info">
    <div class="bk-filter">
      <bk-form
        form-type="vertical"
        ext-cls="dynamic-form"
        v-model="formData"
        ref="dynamicForm">
          <bk-form-item label="功能类型" ext-cls="form-item">
            <bk-select
              searchable
              placeholder="请选择功能类型"
              v-model="formData.is_builtin"
              clearable
              style="background: #fff">
              <bk-option
                v-for="option in functionTypeList"
                :key="option.key"
                :id="option.key"
                :name="option.name">
              </bk-option>
            </bk-select>
          </bk-form-item>
        <bk-form-item label="功能属性" ext-cls="form-item">
          <bk-select
            searchable
            placeholder="请选择功能属性"
            v-model="formData.type"
            clearable
            style="background: #fff">
            <bk-option
              v-for="option in functionAttarList"
              :key="option.key"
              :id="option.key"
              :name="option.name">
            </bk-option>
          </bk-select>
        </bk-form-item>
          <bk-form-item label="功能名称" ext-cls="form-item">
            <bk-input placeholder="请输入功能名称" clearable v-model="formData.name">
            </bk-input>
          </bk-form-item>
          <bk-form-item label="关联表单" ext-cls="form-item">
            <bk-input placeholder="`请输入关联表单" clearable v-model="formData.relate_worksheet">
            </bk-input>
          </bk-form-item>
      </bk-form>
      <div class="bk-filter-line">
        <bk-button :theme="'primary'" type="submit" :title="'查询'" @click="handleSearch">
          查询
        </bk-button>
        <bk-button :theme="'default'" :title="'取消'" @click="handleCancel" style="margin-left: 8px">
          取消
        </bk-button>
      </div>
    </div>
  </div>
</template>

<script>
import Bus from '@/utils/bus.js';
export default {
  name: 'SearchItem',
  data() {
    return {
      formData: {
        is_builtin: '',
        type: '',
        relate_worksheet: '',
        name: '',
      },
      functionTypeList: [{
        key: 0,
        name: '自定义功能',
      },
      {
        key: 1,
        name: '系统功能',
      }],
      functionAttarList: [
        { key: 'ADD', name: '添加' },
        { key: 'EDIT', name: '编辑' },
        { key: 'DELETE', name: '删除' },
        { key: 'IMPORT', name: '导入' },
        { key: 'DETAIL', name: '详情' },
        { key: 'EXPORT', name: '导出' }],
    };
  },
  mounted() {
    Bus.$on('clearSearchItem', (item) => {
      Object.assign(this.formData, item);
    });
  },
  methods: {
    handleCancel() {
      this.formData = {};
      this.$emit('cancel');
    },
    handleSearch() {
      const funcType = this.formData.is_builtin && this.functionTypeList
        .find(item => item.key === this.formData.is_builtin).name ;
      const attr = this.formData.type && this.functionAttarList.find(item => item.key === this.formData.type).name ;
      console.log(funcType, attr);
      this.$emit('search', {  ...this.formData, funcType, attr });
    },
  },
};
</script>

<style scoped lang="postcss">
.search-info {
  box-sizing: content-box;
  margin-top: 8px;
  width: 100%;
  background: #F5F7FA;
  border-radius: 2px;

  .bk-filter {
    padding-bottom: 24px;

    .dynamic-form {
      display: flex;
      flex-wrap: nowrap;
      align-items: flex-end;
    }

    .bk-filter-line {
      margin: 16px 0 0 16px;
      border: 1px solid transparent;
    }

  }
}
.form-item {
  margin-left: 16px;
  width: calc((100% - 80px )/ 4);
}
</style>

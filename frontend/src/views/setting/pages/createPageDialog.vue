<template>
  <bk-dialog
    title="新增页面"
    header-position="left"
    :mask-close="false"
    :auto-close="false"
    :width="640"
    :loading="savePending"
    :value="show"
    @confirm="createPageConfirm"
    @cancel="createPageCancel">
    <bk-form ref="pageForm" :label-width="400" form-type="vertical" :model="formData" :rules="rules">
      <bk-form-item label="页面名称" :required="true" :property="'name'" :error-display-type="'normal'">
        <bk-input v-model="formData.name"></bk-input>
      </bk-form-item>
      <bk-form-item label="分组">
        <bk-select v-model="formData.group" @clear="formData.group = undefined">
          <bk-option v-for="option in groupList" :key="option.id" :id="option.id" :name="option.name"> </bk-option>
        </bk-select>
      </bk-form-item>
      <bk-form-item label="页面类型" :required="true" :property="'type'" ext-cls="custom-from" :error-display-type="'normal'">
        <div class="page-type-container">
          <div
            v-for="item in typeList"
            :class="['type-card-item', { selected: item.type === formData.type }]"
            :key="item.type"
            :style="{ backgroundColor: item.bgColor, borderColor: item.iconColor }"
            @click="formData.type = item.type">
            <div class="icon-wrapper" :style="{ backgroundColor: item.iconColor }">
              <i class="custom-icon-font icon-project icon-card" v-if="item.type==='FUNCTION'"></i>
              <i class="custom-icon-font icon-project icon-file" v-else-if="item.type==='SHEET'"></i>
              <i class="custom-icon-font icon-project icon-sheet" v-else></i>
            </div>
            <h4>{{ item.name }}</h4>
            <p>{{ item.desc }}</p>
          </div>
        </div>
      </bk-form-item>
    </bk-form>
  </bk-dialog>
</template>

<script>
import cloneDeep from 'lodash.clonedeep';

export default {
  name: 'CreatePageDialog',
  props: {
    show: {
      type: Boolean,
      default: false,
    },
    group: Number,
    appId: String,
    pageList: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      savePending: false,
      formData: {
        name: '',
        type: '',
        group: this.group,
      },
      rules: {
        name: [
          {
            required: true,
            message: '必填项',
            trigger: 'blur',
          },
        ],
      },
      typeList: [
        {
          type: 'FUNCTION',
          name: '功能卡片',
          desc: '搭建应用功能的快捷入口',
          bgColor: '#e1ecff',
          iconColor: '#3a84ff',
        },
        {
          type: 'SHEET',
          name: '表单',
          desc: '搭建收集数据的表单页',
          bgColor: '#ffe8c3',
          iconColor: '#ff9c01',
        },
        {
          type: 'LIST',
          name: '表格',
          desc: '搭建一个数据管理页',
          bgColor: '#ffdddd',
          iconColor: '#ff5656',
        },
      ],
    };
  },
  computed: {
    groupList() {
      return this.pageList.filter(item => item.type === 'GROUP');
    },
  },
  watch: {
    group(val) {
      this.formData.group = val;
    },
  },
  methods: {
    createPageConfirm() {
      if (this.formData.type === '') {
        this.$bkMessage({
          theme: 'error',
          message: '请选择页面类型',
        });
        return;
      }
      this.savePending = true;
      this.$refs.pageForm
        .validate()
        .then(async () => {
          try {
            const params = {
              project_key: this.appId,
              name: this.formData.name,
              type: this.formData.type,
              parent: this.formData.group,
            };
            const res = await this.$store.dispatch('setting/createPage', params);
            const list = cloneDeep(this.pageList);
            if (this.formData.group === undefined) {
              list.push(res.data);
            } else {
              const group = list.find(item => item.id === this.formData.group);
              group.children.push(res.data);
            }
            this.resetForm();
            this.$emit('confirm', res.data, list);
          } catch (e) {
            console.error(e);
          } finally {
            this.savePending = false;
          }
        })
        .catch(() => {
          this.savePending = false;
        });
    },
    createPageCancel() {
      this.resetForm();
      this.$refs.pageForm.clearError();
      this.$emit('cancel');
    },
    resetForm() {
      this.formData = {
        name: '',
        type: '',
        group: undefined,
      };
    },
  },
};
</script>

<style lang="postcss" scoped>
.page-type-container {
  display: flex;
  justify-content: space-between;
  .type-card-item {
    padding: 19px 10px;
    width: 186px;
    height: 120px;
    text-align: center;
    border: 1px solid transparent;
    border-radius: 4px;
    cursor: pointer;
    &:not(.selected) {
      border-color: transparent !important;
    }
    & > h4 {
      margin: 0;
      line-height: 22px;
      font-size: 14px;
      font-weight: normal;
      color: #313238;
    }
    & > p {
      margin: 0;
      font-size: 12px;
      color: #63656e;
    }
  }
  .icon-wrapper {
    margin: 0 auto 8px;
    width: 32px;
    height: 32px;
    color: #ffffff;
    border-radius: 4px;
    i{
      font-size: 26px;
    }
  }
}
</style>

<template>
  <div class="attribute-config">
    <div class="section-title">{{ title }}</div>
    <div class="form-container">
      <bk-form v-if="'funcId' in value" ref="configForm" form-type="vertical" :model="formData" :rules="rules">
        <bk-form-item label="功能绑定" :required="true">
          <bk-select v-model="formData.funcId" :clearable="false" :loading="functionListLoading" @change="change">
            <bk-option v-for="func in functionList" :key="func.id" :id="func.id" :name="func.name"></bk-option>
          </bk-select>
        </bk-form-item>
        <bk-form-item
          label="表单外链"
          ext-cls="link-container"
          v-if="page.type === 'SHEET'"
          desc-type="icon"
          desc="开启外链后，可复制链接给外部用户填写表单">
          <div class="link-switch">
            <bk-switcher
              v-model="linkIsOpen"
              theme="primary"
              size="small"
              @change="handleChangeSwitch"
              :pre-check="requestHandler">
            </bk-switcher>
          </div>
          <div class="link-container" v-show="linkIsOpen" v-bkloading="{ bkLoading: linkIsLoading }">
            <span class="link-address" v-bk-overflow-tips>{{ formData.linkAddress }}</span>
            <span class="custom-icon-font icon-copy-line" v-bk-copy="formData.linkAddress"></span>
          </div>
        </bk-form-item>
        <template v-if="page.type === 'FUNCTION'">
          <bk-form-item label="卡片名称" :required="true">
            <bk-input v-model="formData.name" @change="change"></bk-input>
          </bk-form-item>
          <bk-form-item label="卡片描述">
            <bk-input v-model="formData.desc" type="textarea" @change="change"></bk-input>
          </bk-form-item>
        </template>
      </bk-form>
    </div>
  </div>
</template>
<script>
import cloneDeep from 'lodash.clonedeep';

export default {
  name: 'AttributeConfig',
  props: {
    appId: String,
    page: {
      type: Object,
      default: () => ({}),
    },
    value: {
      type: Object,
      default: () => ({}),
    },
  },
  data() {
    return {
      formData: cloneDeep(this.value),
      functionList: [],
      functionListLoading: false,
      linkIsOpen: !!cloneDeep(this.value).linkAddress,
      linkIsLoading: false,
      rules: {
        funcId: {
          required: true,
          message: '必填项',
          trigger: 'blur',
        },
      },
    };
  },
  computed: {
    title() {
      return this.page.type === 'SHEET' ? '表单属性' : '卡片属性';
    },
  },
  watch: {
    value(val) {
      this.formData = cloneDeep(val);
      this.linkIsOpen = !!cloneDeep(val).linkAddress;
    },
  },
  created() {
    this.getFunctionList();
  },
  methods: {
    async getFunctionList() {
      try {
        this.functionListLoading = true;
        const params = {
          project_key: this.appId,
        };
        const res = await this.$store.dispatch('setting/getFunctionBindList', params);
        this.functionList = res.data.filter(item => !item.is_builtin && ['ADD'].includes(item.type));
      } catch (e) {
        console.error(e);
      } finally {
        this.functionListLoading = false;
      }
    },
    async getLinkAddress() {
      try {
        const params = {
          page_id: this.page.id,
          service_id: this.value.funcId,
          project_key: this.appId,
          end_time: '2099-12-31 23:59:59',
        };
        this.linkIsLoading = true;
        const res = await this.$store.dispatch('setting/getSheetLink', params);
        this.formData.linkAddress = res.data.url;
      } catch (e) {
      } finally {
        this.linkIsLoading = false;
      }
    },
    async removeLinkAddress() {
      try {
        const params = {
          page_id: this.page.id,
          project_key: this.appId,
        };
        await this.$store.dispatch('setting/removeSheetLink', params);
        this.formData.linkAddress = '';
      } catch (e) {
      } finally {
        this.linkIsLoading = false;
      }
    },
    change() {
      if (this.linkIsOpen) {
        this.$bkInfo({
          title: '此操作删除访问外链，确认吗？',
          type: 'warning',
          width: 500,
          confirmFn: async () => {
            this.linkIsOpen = false;
            await this.removeLinkAddress();
            this.$emit('change', this.formData);
          },
        });
      }
      this.$emit('change', this.formData);
    },
    async handleChangeSwitch(val) {
      if (val) {
        await this.getLinkAddress();
        this.$emit('change', this.formData);
      }
    },
    requestHandler(lastValue) {
      return new Promise((resolve, reject) => {
        if (!lastValue) {
          this.$bkInfo({
            title: '此操作删除访问外链，确认吗？',
            type: 'warning',
            width: 500,
            confirmFn: async () => {
              await this.removeLinkAddress();
              this.$emit('change', this.formData);
              resolve();
            },
          });
        } else {
          resolve();
        }
      });
    },
  },
};
</script>
<style lang="postcss" scoped>
.section-title {
  padding: 0 24px;
  height: 40px;
  line-height: 40px;
  font-size: 14px;
  color: #313238;
  background: #ffffff;
  box-shadow: 0 1px 0 0 #dcdee5;
}

.form-container {
  padding: 16px 24px;
}

.link-container {
  position: relative;

  .link-switch {
    position: absolute;
    right: 8px;
    top: -32px;
  }

  .link-container {
    display: flex;
    justify-content: space-between;

    span {
      display: block;
    }

    &:hover {
      color: #3a84ff;
      cursor: pointer;
    }
  }
}

.link-address {
  width: 240px;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}
</style>

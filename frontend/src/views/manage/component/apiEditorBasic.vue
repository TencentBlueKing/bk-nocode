<template>
  <div class="bk-api-editor-basic">
    <bk-form :label-width="120" :model="basicInfo">
      <bk-form-item class="bk-editor-form" :required="true" :label="'接口名称：'">
        <bk-input :disabled="basicInfo.is_builtin" :placeholder="'请输入接口名称'" v-model="basicInfo.name"> </bk-input>
      </bk-form-item>
      <template v-if="basicInfo.hasOwnProperty('method')">
        <bk-form-item class="bk-editor-form" :required="true" :label="'接口路径：'">
          <bk-input v-model="basicInfo.path" placeholder="/path" :disabled="basicInfo.is_builtin">
            <template slot="prepend">
              <bk-dropdown-menu
                class="group-text"
                @show="dropdownShow"
                @hide="dropdownHide"
                ref="requestwayDrop"
                slot="append"
                :font-size="'normal'"
                :disabled="basicInfo.is_builtin">
                <bk-button type="primary" slot="dropdown-trigger">
                  <span> {{ basicInfo.method }} </span>
                  <i :class="['bk-icon icon-angle-down', { 'icon-flip': isDropdownShow }]"></i>
                </bk-button>
                <ul class="bk-dropdown-list" slot="dropdown-content">
                  <li v-for="(requestway, requestwayIndex) in typeList" :key="requestwayIndex">
                    <a href="javascript:;" @click="requestHandler(requestway, requestwayIndex)">
                      {{ requestway.name }}
                    </a>
                  </li>
                </ul>
              </bk-dropdown-menu>
            </template>
          </bk-input>
        </bk-form-item>
      </template>
      <bk-form-item class="bk-editor-form" :label="'负责人：'">
        <member-select v-model="basicInfo.ownersInputValue"></member-select>
      </bk-form-item>
      <bk-form-item class="bk-editor-form" :label="'备注：'">
        <bk-input
          :disabled="basicInfo.is_builtin"
          :placeholder="'请输入描述'"
          :type="'textarea'"
          :rows="3"
          v-model="basicInfo.desc">
        </bk-input>
      </bk-form-item>
    </bk-form>
  </div>
</template>

<script>
import memberSelect from '@/components/memberSelect.vue';

export default {
  name: 'ApiEditorBasic',
  components: { memberSelect },
  props: {
    detailInfoOri: {
      type: Object,
      default() {
        return {};
      },
    },
    // 分类列表
    treeList: {
      type: Array,
      default() {
        return [];
      },
    },
    // 接口列表
    pathList: {
      type: Array,
      default() {
        return [];
      },
    },
    // 内建系统列表
    isBuiltinIdList: {
      type: Array,
      default() {
        return [];
      },
    },
  },
  data() {
    return {
      // 请求方式
      typeList: [
        { name: 'GET' },
        { name: 'POST' },
        // { name: 'DELETE' },
        // { name: 'PUT' },
        // { name: 'PATCH' }
      ],
      // 状态
      stateList: [
        { id: 0, name: '未完成' },
        { id: 1, name: '已完成' },
      ],
      isDropdownShow: false,
    };
  },
  computed: {
    // 基本设置
    basicInfo: {
      // getter
      get() {
        return this.detailInfoOri;
      },
      // setter
      set(newVal) {
        this.$parent.DetailInfo = newVal;
      },
    },
  },
  watch: {},
  mounted() {},
  methods: {
    switchChange(isActivated) {
      this.basicInfo.is_activated = isActivated;
    },
    dropdownShow() {
      this.isDropdownShow = true;
    },
    dropdownHide() {
      this.isDropdownShow = false;
    },
    requestHandler(requestway) {
      this.$refs.requestwayDrop.hide();
      this.$emit('changeRequest', requestway.name);
    },
    changeMethod(val) {
      this.basicInfo.method = val;
    },
  },
};
</script>

<style lang="postcss" scoped>
.bk-editor-form {
  width: 500px;
}
</style>

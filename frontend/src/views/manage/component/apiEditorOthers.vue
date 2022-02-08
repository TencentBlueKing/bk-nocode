<template>
  <div class="bk-api-editor-others">
    <bk-form
      :label-width="120"
      :model="basicInfo">
      <bk-form-item
        :label="'开放接口：'">
        <bk-switcher v-model="basicInfo.is_activated" size="small" :disabled="basicInfo.is_builtin">
        </bk-switcher>
      </bk-form-item>
    </bk-form>
  </div>
</template>

<script>
export default {
  name: 'ApiEditorOthers',
  props: {
    detailInfoOri: {
      type: Object,
      default() {
        return {};
      },
    },
  },
  data() {
    return {};
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
  methods: {},
};
</script>

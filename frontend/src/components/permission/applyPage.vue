<template>
  <div class="apply-perm-page">
    <permission-content :permission-data="permissionData"> </permission-content>
    <div class="operation-btns">
      <bk-button ext-cls="apply-btn" theme="primary" :loading="loading" @click="applyBtnClick">
        {{ hasClicked ? '已申请' : '去申请' }}
      </bk-button>
    </div>
  </div>
</template>
<script>
import PermissionContent from './permissionContent.vue';
import permission from './mixins.js';

export default {
  name: 'ApplyPage',
  components: {
    PermissionContent,
  },
  mixins: [permission],
  props: {
    permissionData: {
      type: Object,
      default: () => ({}),
    },
  },
  data() {
    return {
      url: '',
      loading: false,
      hasClicked: false,
    };
  },
  watch: {
    permissionData() {
      this.hasClicked = false;
      this.loadPermissionUrl();
    },
  },
  created() {
    this.loadPermissionUrl();
  },
  methods: {
    applyBtnClick() {
      this.goToAuthCenter();
    },
    goToAuthCenter() {
      if (this.loading || !this.url) {
        return;
      }
      if (this.hasClicked) {
        window.location.reload();
      } else {
        this.hasClicked = true;
        window.open(this.url, '__blank');
      }
    },
    async loadPermissionUrl() {
      try {
        this.loading = true;
        const res = await this.$store.dispatch('permission/getPermUrl', this.permissionData);
        this.url = res.data.url;
      } catch (err) {
        console.error(err);
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>
<style lang="postcss" scoped>
.apply-perm-page {
  width: 100%;
  height: 100%;
}
.permission-content {
  margin: 80px auto 0;
  width: 620px;
}
.operation-btns {
  margin-top: 40px;
  text-align: center;
}
</style>

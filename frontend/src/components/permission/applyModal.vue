<template>
  <bk-dialog
    width="768"
    ext-cls="permission-dialog"
    :z-index="2010"
    :mask-close="false"
    :header-position="'left'"
    :title="''"
    :value="isModalShow"
    @cancel="onCloseDialog">
    <permission-content :permission-data="permissionData"> </permission-content>
    <div class="permission-footer" slot="footer">
      <div class="button-group">
        <bk-button theme="primary" :loading="loading" @click="goToApply">{{
          hasClicked ? '已申请' : '去申请'
        }}</bk-button>
        <bk-button theme="default" @click="onCloseDialog">取消</bk-button>
      </div>
    </div>
  </bk-dialog>
</template>
<script>
import PermissionContent from './permissionContent.vue';
export default {
  name: 'ApplyModal',
  components: {
    PermissionContent,
  },
  data() {
    return {
      isModalShow: false,
      hasClicked: false,
      permissionData: {},
      loading: false,
    };
  },
  watch: {
    isModalShow(val) {
      if (val) {
        this.loadPermissionUrl();
      }
    },
  },
  methods: {
    async loadPermissionUrl() {
      try {
        this.loading = true;
        const res = await this.$store.dispatch('permission/getPermUrl', this.permissionData);
        this.url = res.data.url;
      } catch (err) {
        console.error(err, this);
      } finally {
        this.loading = false;
      }
    },
    show(data) {
      this.isModalShow = true;
      this.permissionData = data;
    },
    goToApply() {
      if (this.loading) {
        return;
      }
      if (this.hasClicked) {
        window.location.reload();
      } else {
        this.hasClicked = true;
        window.open(this.url, '__blank');
      }
    },
    onCloseDialog() {
      this.isModalShow = false;
    },
  },
};
</script>
<style lang="postcss" scoped>
.button-group {
  .bk-button {
    margin-left: 7px;
  }
}
</style>

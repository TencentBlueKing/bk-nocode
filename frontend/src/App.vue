<template>
  <div id="nocode-app-container">
    <!-- 外链提单页面隐藏导航栏   -->
    <div class="nocode-app-content" v-if="!$route.name||$route.name==='openCreatTicket'">
      <router-view></router-view>
    </div>
    <navigator v-else>
      <div class="nocode-app-content">
        <router-view></router-view>
      </div>
    </navigator>
    <permission-modal ref="permissionModal"></permission-modal>
  </div>
</template>
<script>
import bus from '@/utils/bus.js';
import Navigator from '@/components/navigator/index.vue';
import PermissionModal from '@/components/permission/applyModal.vue';

export default {
  name: 'App',
  components: {
    Navigator,
    PermissionModal,
  },
  created() {
    this.$store.dispatch('permission/getPermMeta');
  },
  mounted() {
    bus.$on('showPermissionModal', (data) => {
      this.$refs.permissionModal && this.$refs.permissionModal.show(data);
    });
  },
};
</script>



export default {
  data() {
    return {
    };
  },
  methods: {
    onReleaseClick() {
      this.$bkInfo({
        title: '确认发布本应用？',
        confirmLoading: true,
        confirmFn: async () => {
          try {
            await this.$store.dispatch('setting/releaseApp', { project_key: this.appId });
            this.$bkMessage({
              theme: 'success',
              message: '发布成功',
            });
          } catch (e) {
            console.error(e);
          }
        },
      });
    },
  },
};

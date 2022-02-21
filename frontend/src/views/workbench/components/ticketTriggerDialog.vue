<template>
  <div class="trigger-dialog-box"></div>
</template>
<script>
export default {
  name: 'TicketTriggerDialog',
  data() {
    return {
      triggerId: '',
    };
  },
  methods: {
    openDialog(trigger) {
      this.triggerId = trigger.id;
      this.$bkInfo({
        title: '确定执行该操作？',
        subTitle: trigger.display_name,
        confirmFn: () => {
          this.executeTrigger(trigger);
        },
      });
    },
    async executeTrigger(trigger) {
      try {
        const res = await  this.$store.dispatch('workbench/executeHandleTriggers', trigger.id);
        if (res.result) {
          this.$bkMessage({
            message: '执行成功',
            theme: 'success',
          });
          if (trigger.need_refresh || !trigger.can_repeat) {
            this.$emit('init-info');
          }
        }
      } catch (e) {
        console.error(e);
      }
    },
  },
};
</script>


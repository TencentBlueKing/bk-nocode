<template>
    <span class="header-title-icon" @click="$emit('click')">
        <svg viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="4756" class="icon" style="width: 1em; height: 1em;fill: currentcolor; overflow: hidden;vertical-align: middle;"><path d="M416 480h320v64H416l96 96-48 48-176-176 176-176 48 48-96 96z" p-id="4757"></path></svg>
    </span>
</template>

<script>
export default {
  name: 'ArrowsLeftIcon',
};
</script>
<style lang="postcss">
.header-title-icon {
  line-height: 0;
  font-size: 28px;
  color: #3a84ff;
  cursor: pointer;
}
</style>

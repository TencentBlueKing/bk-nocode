<template>
  <bk-form :label-width="150" ext-cls="custom-form">
    <bk-form-item v-for="item in localVal" :label="`${item.name}:`" :key="item.id">
      <span v-if="['SELECT', 'RADIO', 'CHECKBOX','INPUTSELECT', 'MULTISELECT'].includes(item.type)">
        {{ transformFields(item) }}
      </span>
      <span v-else-if="item.type === 'RICHTEXT'" v-html="item.val||'--'"></span>
      <span v-else-if="item.type === 'IMAGE'">
        <image-file :view-mode="true" :value="item.val" v-if="item.val && item.val.length!==0"></image-file>
        <span v-else>--</span>
      </span>
      <span v-else-if="item.type === 'IMAGE'">
        <image-file :view-mode="true" :value="item.val"></image-file>
      </span>
      <span v-else-if="item.type === 'TABLE'">
         <bk-table :data="item.val" v-if="item.val&&item.val.length!==0">
            <template v-for="col in item.choice">
              <bk-table-column :label="col.name" :key="col.key">
                <template slot-scope="{ row }">
                  <span>{{ row[col.key] }}</span>
                </template>
              </bk-table-column>
            </template>
          </bk-table>
          <span v-else>--</span>
      </span>
      <span v-else-if="item.type === 'FILE'">
         <bk-button
           v-if="item.val"
           theme="primary"
           style="margin-right: 8px"
           @click="handleDownload(item.val)"
           text>
                点击下载
          </bk-button>
          <span v-else>--</span>
      </span>
      <span v-else>{{item.val}}</span>
    </bk-form-item>
  </bk-form>
</template>

<script>
import imageFile from '@/components/form/formFields/fields/imageFile.vue';
import cloneDeep from 'lodash.clonedeep';
export default {
  name: 'ItemFrom',
  components: {
    imageFile,
  },
  props: {
    fieldList: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      localVal: cloneDeep(this.fieldList),
    };
  },
  watch: {
    fieldList(val) {
      this.localVal = val;
    },
  },
  methods: {
    transformFields(field) {
      let showValue = '';
      if (['SELECT', 'RADIO', 'CHECKBOX', 'INPUTSELECT',  'MULTISELECT'].includes(field.type)) {
        if (['MULTISELECT', 'CHECKBOX'].includes(field.type)) {
          const tempArr = [];
          field.choice.forEach((item) => {
            if (field.val &&  Array.isArray(field.val.split(','))) {
              field.val.split(',').forEach((val) => {
                if (item.key === val) {
                  tempArr.push(item.name);
                }
              });
            }
          });
          showValue = tempArr.toString();
        } else {
          field.choice.forEach((item) => {
            if (item.key === field.val) {
              showValue = item.name;
            }
          });
        }
      }
      return  showValue || '--';
    },
    handleDownload(val) {
      console.log(val);
      const fileArr = (new Function(`return( ${val} );`))();
      fileArr.forEach((item) => {
        window.open(`${window.location.origin}${window.SITE_URL}api/misc/download_file/?file_name=${item.file_name}&origin_name=${item.origin_name}&download_flag=1`);
      });
    },
  },
};
</script>

<style scoped lang="postcss">
.custom-form {
  margin-top: 24px;

  /deep/ .bk-label-text {
    font-size: 14px;
    color: #979ba5;
  }

  /deep/ .bk-form-content {
    font-size: 14px;
    color: #63656e;
  }
}
</style>

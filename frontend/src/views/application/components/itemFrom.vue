<template>
  <bk-form :label-width="150" ext-cls="custom-detail-form">
    <template v-for="item in localVal">
      <bk-form-item v-if="isShow(item)" :label="`${item.name}:`" :key="item.id">
      <span v-if="dataSourceField.includes(item.type)">
        {{ transformFields(item) }}
      </span>
        <span v-else-if="item.type === 'RICHTEXT'" v-html="item.val||'--'"></span>
        <span v-else-if="item.type === 'IMAGE'">
        <image-file :view-mode="true" :value="item.val" v-if="item.val && item.val.length!==0"></image-file>
        <span v-else>--</span>
      </span>
        <!--        <span v-else-if="item.type === 'IMAGE'">-->
        <!--        <image-file :view-mode="true" :value="item.val"></image-file>-->
        <!--      </span>-->
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
        <span v-else-if="item.type === 'TEXT'" v-html="textTrans(item.val)">
      </span>
        <span v-else>{{ item.val }}</span>
      </bk-form-item>
    </template>
  </bk-form>
</template>

<script>
import imageFile from '@/components/form/formFields/fields/imageFile.vue';
import { DATA_SOURCE_FIELD } from '@/constants/forms.js';
import judgeFieldsConditionMixins from '@/components/form/formFields/judgeFieldsConditionMixins';
import cloneDeep from 'lodash.clonedeep';

export default {
  name: 'ItemFrom',
  components: {
    imageFile,
  },
  mixins: [judgeFieldsConditionMixins],
  props: {
    fieldList: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      localVal: cloneDeep(this.fieldList),
      dataSourceField: DATA_SOURCE_FIELD,
    };
  },
  watch: {
    fieldList: {
      handler(val) {
        this.localVal = cloneDeep(this.fieldList);
        this.initChoice();
      },
      immediate: true,
    },
  },
  methods: {
    async initChoice() {
      const arr = this.localVal;
      const len = arr.length;
      if (len > 0) {
        for (let i = 0; i < len; i++) {
          if (DATA_SOURCE_FIELD.includes(arr[i].type) && arr[i].source_type !== 'CUSTOM') {
            await this.setSourceData(arr[i]);
          }
        }
      }
    },
    transformFields(field) {
      let showValue = '';
      if (DATA_SOURCE_FIELD.includes(field.type)) {
        if (['MULTISELECT', 'CHECKBOX'].includes(field.type)) {
          const tempArr = [];
          field.choice.forEach((item) => {
            if (field.val && Array.isArray(field.val.split(','))) {
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
      return showValue || '--';
    },
    handleDownload(val) {
      const fileArr = val;
      fileArr.forEach((item) => {
        window.open(`${window.location.origin}${window.SITE_URL}api/misc/download_file/?file_name=${item.file_name}&origin_name=${item.origin_name}&download_flag=1`);
      });
    },
    setSourceData(field) {
      if (field.source_type === 'CUSTOM') {
        this.sourceData = field.choice;
      } else if (field.source_type === 'API') {
        this.setApiData(field);
        return;
      } else if (field.source_type === 'WORKSHEET') {
        this.setWorksheetData(field);
      }
    },
    async setApiData(field) {
      try {
        const { id, api_info, api_instance_id, kv_relation } = field;
        const params = {
          id,
          api_instance_id,
          kv_relation,
          api_info: {
            api_instance_info: api_info,
            remote_api_info: api_info.remote_api_info,
          },
        };
        const resp = await this.$store.dispatch('setting/getSourceData', params);
        field.choice = resp.data.map((item) => {
          const { key, name } = item;
          return { key, name };
        });
      } catch (e) {
        console.error(e);
      }
    },
    textTrans(val) {
      return val.replaceAll('\n', '</br>') || '--';
    },
    async setWorksheetData(item) {
      try {
        const { field, conditions } = item.meta.data_config;
        let params;
        if (!conditions.connector && !conditions.expressions.every(i => i)) {
          params = {
            token: item.token,
            fields: [field],
            conditions: {},
          };
        } else {
          params = {
            token: item.token,
            fields: [field],
            conditions,
          };
        }
        const resp = await this.$store.dispatch('setting/getWorksheetData', params);
        item.choice = resp.data.map((item) => {
          const val = item[field];
          return { key: val, name: val };
        });
      } catch (e) {
        console.error(e);
      }
    },
    isShow(item) {
      if (this.isObjectHaveAttr(item.show_conditions)) {
        console.log(!this.judgeFieldsCondition(item.show_conditions));
        return !this.judgeFieldsCondition(item.show_conditions);
      }
      return  true;
    },
  },
};
</script>

<style scoped lang="postcss">
.custom-detail-form {
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

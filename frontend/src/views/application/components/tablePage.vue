<template>
  <div class="list-page">
    <div v-if="!fieldListLoading && !showSuccess" class="table-config">
      <div class="header-config">
        <div class="function-btn" v-if="config.buttonGroup">
          <bk-button
            v-for="(item, index) in config.buttonGroup.slice(0, 3)"
            v-cursor="{ active: actionsPermMap[item.id] === false }"
            :key="index"
            :theme="index === 0 ? 'primary' : 'default'"
            :class="{ 'btn-permission-disabled': actionsPermMap[item.id] === false }"
            :disabled="!(item.id in actionsPermMap)"
            size="normal"
            class="btn-content"
            @click="handleClick(item, {}, 'buttonGroup')">
            {{ item.name }}
          </bk-button>
          <bk-dropdown-menu
            @show="dropdownShow"
            @hide="dropdownHide"
            ref="dropdown"
            style="margin-left: 8px"
            v-if="config.buttonGroup.length > 3">
            <div class="dropdown-trigger-btn" style="padding-left: 19px" slot="dropdown-trigger">
              更多
              <i :class="['bk-icon icon-angle-down', { 'icon-flip': isDropdownShow }]"></i>
            </div>
            <!--      <ul class="bk-dropdown-list" slot="dropdown-content" v-for="item in buttonGroup">-->
            <ul class="bk-dropdown-list" slot="dropdown-content">
              <li v-for="(item, index) in config.buttonGroup.slice(3)" :key="index">
                <a
                  v-cursor="{ active: actionsPermMap[item.id] === false }"
                  href="javascript:;"
                  :class="{
                    'text-permission-disabled': actionsPermMap[item.id] === false,
                    disabled: !(item.id in actionsPermMap),
                  }"
                  @click="handleClick(item, {}, 'buttonGroup')">
                  {{ item.name }}
                </a>
              </li>
              <!--              <li><a href="javascript:;" @click="handleExport"> 导出</a></li>-->
            </ul>
          </bk-dropdown-menu>
        </div>
        <div class="search-icon top-start" @click="isShowSearchInfo = !isShowSearchInfo" v-bk-tooltips="topStart">
          <i class="custom-icon-font icon-filter-funnel"></i>
        </div>
      </div>
      <show-search-info
        v-show="config.searchInfo && config.searchInfo.length !== 0 && isShowSearchInfo"
        :search-info="config.searchInfo"
        :filed-list="fieldList"
        @search="handleSearch"
        @cancel="handleCancel">
      </show-search-info>
      <div class="search-item-container">
        <template v-if="!isShowSearchInfo && searchInfo.length!==0">
          <search-tag
            v-for="item in searchInfo"
            :search-item="item"
            :key="item.key"
            @delete="handleRemoveSearch">
          </search-tag>
        </template>
      </div>
      <div class="custom-table">
        <bk-table
          v-bkloading="{ isLoading: tableDataLoading,zIndex: 9999 }"
          v-if="fields.length !== 0"
          ext-cls="table-border"
          :data="tableData"
          :outer-border="false"
          :pagination="pagination"
          @page-change="handlePageChange"
          @page-limit-change="handlePageLimitChange"
          @select="handleSelect"
          @select-all="handleSelectAll"
          :header-border="false"
          :header-cell-style="{ background: '#FAFBFD ' }">
          <bk-table-column type="selection" width="60"></bk-table-column>
          <bk-table-column
            v-for="field in fields"
            :key="field.id"
            :label="field.name"
            :prop="field.key"
            :show-overflow-tooltip="true">
            <template slot-scope="{ row,column }">
              <span
                v-if="['RICHTEXT', 'IMAGE','TABLE'].includes(field.type)
                &&(!row[column.property]||row[column.property].length===0)">
                暂无内容
              </span>
              <span
                v-else-if="['FILE'].includes(field.type)
                &&row[column.property].length===0">
                暂无内容
              </span>
              <bk-button
                v-else-if="['RICHTEXT','TABLE'].includes(field.type)"
                theme="primary"
                style="margin-right: 8px"
                @click="handleView(row,column,field)"
                text>
                查看
              </bk-button>
              <div v-else-if="'IMAGE'.includes(field.type)" class="photo-view">
                <viewer :images="getImageListFullPath(row[column.property])">
                  <template v-for=" (item,index) in row[column.property]">
                    <img :src="getFullPath(item)" :key="index" v-show="index===0" />
                  </template>
                  <span v-if="row[column.property].length>1">
                   ...
                  </span>
                </viewer>
              </div>
              <bk-button
                v-else-if="['FILE'].includes(field.type)"
                theme="primary"
                @click="handleDownload(row,column)"
                text>
                点击下载
              </bk-button>
              <bk-button
                v-else-if="['LINK'].includes(field.type)&&row[column.property]"
                theme="primary"
                @click="goToLink(row,column)"
                text>
                点击跳转
              </bk-button>
              <span v-else-if=" ['create_at','update_at'].includes(field.id)">{{ row[field.key] | formatTimer }}</span>
              <span
                v-else-if="['SELECT', 'RADIO','CHECKBOX', 'INPUTSELECT', 'MULTISELECT','FORMULA'].includes(field.type)">
                {{ transformFields(field, row) }}</span
              >
              <span v-else>{{ row[field.key] | formatData }}</span>
            </template>
          </bk-table-column>
          <bk-table-column label="操作" width="200" fixed="right" v-if="config.optionList.length>0">
            <template slot-scope="{ row }">
              <bk-button
                v-for="(btn, index) in config.optionList.slice(0, 3)"
                :key="index"
                theme="primary"
                style="margin-right: 12px"
                v-cursor="{ active: actionsPermMap[btn.id] === false }"
                :class="{ 'text-permission-disabled': actionsPermMap[btn.id] === false }"
                :disabled="!(btn.id in actionsPermMap)"
                @click="handleClick(btn, row, 'optionList')"
                text>
                {{ btn.name }}
              </bk-button>
              <bk-popover
                placement="bottom-start"
                theme="light"
                ext-cls="more-option-popover"
                :tippy-options="{ arrow: false, hideOnClick: false }">
                <i v-if="config.optionList.length > 3" class="bk-icon icon-more table-more-icon"></i>
                <div class="table-more-actions" slot="content">
                  <div
                    v-for="(btn, index) in config.optionList.slice(3)"
                    v-cursor="{ active: actionsPermMap[btn.id] === false }"
                    :class="{
                      'action-item': true,
                      'text-permission-disabled': actionsPermMap[btn.id] === false,
                      disabled: !(btn.id in actionsPermMap),
                    }"
                    :key="index"
                    @click="handleClick(btn, row, 'optionList')">
                    {{ btn.name }}
                  </div>
                </div>
              </bk-popover>
            </template>
          </bk-table-column>
          <bk-table-column type="setting">
            <bk-table-setting-content
              :fields="selectionFields"
              :selected="fields"
              :label-key="'name'"
              :value-key="'id'"
              @setting-change="handleSettingChange">
            </bk-table-setting-content>
          </bk-table-column>
        </bk-table>
      </div>
    </div>
    <bk-sideslider
      :is-show.sync="sidesliderIsShow"
      :width="640"
      ext-cls="custom-sidelider">
      <div slot="header">{{ slideTitle }}</div>
      <div slot="content" v-bkloading="{ isLoading: editorLoading }">
        <item-from :field-list="showFiled" v-if="!isEditor &&showFiled.length!==0" />
        <editor-form
          :fields="editorList"
          @change="handleChange"
          v-if="isEditor && editorList.length !== 0"
          :value="editorValue"></editor-form>
      </div>
      <div slot="footer" v-if="isEditor" class="king-slider-footer">
        <bk-button theme="primary" @click="submit" :loading="submitPending"> 确定</bk-button>
        <bk-button theme="default" @click="handleClose" style="margin-left: 8px">取消</bk-button>
      </div>
    </bk-sideslider>
    <create-ticket-success v-if="!isBuiltIn && showSuccess" @back="handleSuccessBack" :id="ticketId">
    </create-ticket-success>
    <bk-dialog
      :value="visible"
      v-if="isBuiltIn"
      :render-directive="'if'"
      v-model="visible"
      theme="primary"
      :mask-close="false"
      header-position="left"
      @value-change="handleCloseDialog"
      :show-footer="false"
      title="提单详情">
      <div class="status-wrapper">
        <div class="icon-wrapper">
          <bk-spin size="large" placement="bottom" v-if="ticketStatus === 'RUNNING'"> 提交中</bk-spin>
        </div>
        <div class="icon-wrapper" v-if="ticketStatus === 'FINISHED'">
          <i class="bk-icon icon-check-circle"></i>
          <p>提交成功</p>
        </div>
        <div class="icon-wrapper" v-if="ticketStatus === 'FAILED'">
          <i class="bk-icon icon-close-circle error-icon"></i>
          <p>提交失败,
            <bk-button theme="primary" @click="goToDetail" text class="detail-btn">查看流程详情</bk-button>
          </p>
        </div>
      </div>
    </bk-dialog>
    <bk-dialog
      :value="imageConfig.imageVisible"
      :render-directive="'if'"
      v-model="imageConfig.imageVisible"
      theme="primary"
      :mask-close="false"
      header-position="left"
      :show-footer="false"
      width="640"
      title="查看详情">
      <div class="img-wrapper">
        <bk-form :label-width="150" ext-cls="custom-form">
          <bk-form-item :label="`${imageConfig.label}:`">
            <span v-if="imageConfig.type === 'RICHTEXT'" v-html="imageConfig.imgList" style="overflow: hidden"></span>
            <custom-table
              v-else-if="imageConfig.type === 'TABLE'"
              :view-mode="true"
              :value="imageConfig.imgList.val"
              :field="imageConfig.imgList.fields">
            </custom-table>
          </bk-form-item>
        </bk-form>
      </div>
    </bk-dialog>
    <bk-dialog
      :render-directive="'if'"
      v-model="importConfig.visible"
      theme="primary"
      :close-icon="false"
      :mask-close="false"
      header-position="left"
      width="640"
      title="导入文件">
      <div class="upload-content" v-if="uploadStatus==='UPLOAD'">
        <bk-upload
          :tip="'仅支持xsl，xlsx格式文件'"
          :url="url"
          :with-credentials="true"
          :custom-request="customRequest"
          :accept="'.xsl,.xlsx'"
        ></bk-upload>
        <span @click="handleDownloadTemplate">下载模版</span>
      </div>
      <div class="status-wrapper">
        <div class="icon-wrapper" v-if="uploadStatus === 'SUCCESS'">
          <i class="bk-icon icon-check-circle"></i>
          <p>导入成功</p>
        </div>
        <div class="icon-wrapper" v-if="uploadStatus === 'FAILED'">
          <i class="bk-icon icon-close-circle error-icon"></i>
          <p>导入失败</p>
          <p class="fail-reason">失败原因:{{ importFailMessge }}</p>
        </div>
      </div>
    </bk-dialog>
  </div>
</template>

<script>
import cloneDeep from 'lodash.clonedeep';
import itemFrom from './itemFrom.vue';
import Bus from '@/utils/bus.js';
import editorForm from './editorForm.vue';
import showSearchInfo from './showSearchInfo.vue';
import permission from '@/components/permission/mixins.js';
import { SYS_FIELD } from '@/constants/sysField.js';
import { formatTimer, getQuery } from '../../../utils/util';
import CreateTicketSuccess from './createTicketSuccess.vue';
import customTable from '@/components/form/formFields/fields/table.vue';
import SearchTag from './searchTag.vue';
import { SHOW_SELECT_TYPE_LIST } from '@/constants/fromTypeMap.js';

export default {
  name: 'TablePage',
  components: {
    SearchTag,
    editorForm,
    itemFrom,
    showSearchInfo,
    CreateTicketSuccess,
    customTable,
  },
  filters: {
    formatTimer(value) {
      if (!value) return '--';
      const date = new Date(value);
      const y = date.getFullYear();
      let MM = date.getMonth() + 1;
      MM = MM < 10 ? `0${MM}` : MM;
      let d = date.getDate();
      d = d < 10 ? `0${d}` : d;
      let h = date.getHours();
      h = h < 10 ? `0${h}` : h;
      let m = date.getMinutes();
      m = m < 10 ? `0${m}` : m;
      return `${y}-${MM}-${d} ${h}:${m}`;
    },
    formatData(value) {
      // value=0
      if (typeof value === 'number') {
        return value;
      }
      if (!value) {
        return '--';
      }
      return value;
    },
  },
  mixins: [permission],
  props: {
    appId: String,
    appName: String,
    version: String,
    page: {
      type: Object,
      default: () => ({}),
    },
    formId: [String, Number],
    componentId: Number,
    config: {
      type: Object,
      default: () => {
      },
    },
    actionsPermMap: {
      type: Object,
      default: () => ({}),
    },
  },
  data() {
    return {
      submitPending: false,
      tableDataLoading: false,
      isShowSearchInfo: false,
      pagination: {
        current: 1,
        count: 10,
        limit: 10,
      },
      topStart: {
        content: '更多筛选条件',
        placement: 'top-start',
      },
      imageConfig: {
        imgList: '',
        imageVisible: false,
        label: '',
        type: '',
      },
      importConfig: {
        visible: false,
      },
      uploadStatus: 'UPLOAD',
      url: `${window.SITE_URL}api/engine/data/import_data/`,
      sidesliderIsShow: false,
      importFailMessge: '',
      slideTitle: '',
      isEditor: '',
      tableData: [],
      editorList: [],
      editorValue: {},
      selectionFields: [],
      fields: [],
      fieldList: [],
      DAY_TIME_STAMP: 60 * 60 * 24 * 1000,
      // 编辑和详情需要的全部字段
      editFiledsList: [],
      fieldListLoading: false,
      isDropdownShow: false,
      btnValue: '',
      editorLoading: false,
      selection: [],
      ticketId: '',
      showSuccess: false,
      isBuiltIn: false,
      ticketStatus: 'RUNNING',
      visible: false,
      btnId: '',
      showFiled: [],
      searchFormData: {},
    };
  },
  computed: {
    searchInfo() {
      const searchArr = [];
      if (JSON.stringify(this.searchFormData) !== '{}') {
        for (const key in this.searchFormData) {
          this.fieldList.forEach((el) => {
            if (el.key === key) {
              // 排除其他数据源
              const IsSourceType = !['API', 'WORKSHEET'].includes(el.source_type);
              if (Array.isArray(this.searchFormData[key]) && !['CHECKBOX', 'MULTISELECT'].includes(el.type)) {
                if (this.searchFormData[key].every(it => it)) {
                  searchArr.push({
                    name: el.name,
                    value: `${formatTimer(this.searchFormData[key][0])}--${formatTimer(this.searchFormData[key][1])}`,
                    key,
                  });
                }
              } else if (Array.isArray(this.searchFormData[key]) && IsSourceType) {
                if (!this.searchFormData[key].length > 0) {
                  return;
                }
                ;
                const tempName = this.searchFormData[key].map(it => el.choice.find(ele => it === ele.key).name);
                searchArr.push({
                  name: el.name,
                  value: tempName.toString(),
                  key,
                });
              } else if (['SELECT', 'RADIO', 'INPUTSELECT'].includes(el.type) && IsSourceType) {
                const tempName = el.choice.find(ele => this.searchFormData[key] === ele.key).name;
                searchArr.push({
                  name: el.name,
                  value: tempName,
                  key,
                });
              } else {
                if (!this.searchFormData[key]) {
                  return;
                }
                searchArr.push({ name: el.name, value: this.searchFormData[key], key });
              }
            }
          });
        }
      }
      return searchArr;
    },
  },
  watch: {
    'page.id'() {
      this.getFieldList();
      this.getTableList();
    },
    fieldListLoading(oval, nval) {
      if (oval && !nval && !this.tableDataLoading) this.$emit('isFinishLoading');
    },
    tableDataLoading(oval, nval) {
      if (oval && !nval && !this.tableDataLoading) this.$emit('isFinishLoading');
    },
  },
  async mounted() {
    await this.getFieldList();
    await this.getTableList();
  },

  methods: {
    handleSearch(item) {
      this.searchFormData = item;
      this.isShowSearchInfo = false;
      // 不允许在第二页搜索
      this.pagination.current = 1;
      // 查询的时候清空选中的内容
      this.selection = [];
      if (JSON.stringify(item) === '{}') {
        this.getTableList();
      } else {
        const condition = this.formatSearchCondition(item);
        const conditions = {
          connector: 'and',
          expressions: condition,
        };
        if (condition.length > 0) {
          this.getTableList(conditions);
        } else {
          this.getTableList();
        }
        // this.isShowSearchInfo = false;
      }
    },
    // 格式化搜索条件
    formatSearchCondition(item) {
      const tempIntType = this.fieldList.filter(item => item.type === 'INT').map(item => item.key);
      const tempMutiSelecet = this.fieldList.filter(item => ['CHECKBOX', 'MULTISELECT'].includes(item.type)).map(item => item.key);
      const tempText = this.fieldList.filter(item => ['STRING', 'TEXT'].includes(item.type)).map(item => item.key);
      // 下拉框数据源为api和表单 来源
      const tempSourceType = this.fieldList.filter(item => SHOW_SELECT_TYPE_LIST.includes(item.type)
        && ['API', 'WORKSHEET'].includes(item.source_type)).map(item => item.key);
      const tempArr = [];
      for (const key in item) {
        // 时间类型
        if (Array.isArray(item[key]) && !tempMutiSelecet.includes(key)) {
          item[key].forEach((el, index) => {
            if (el) {
              tempArr.push({ key, value: formatTimer(el), type: 'const', condition: index === 0 ? '>=' : '<=' });
            }
          });
          //  多选下拉框以及checkbox
        } else if (Array.isArray(item[key]) && item[key].length > 0) {
          tempArr.push({ key, value: item[key].toString(), type: 'const', condition: '==' });
          //  数字类型
        } else if (tempIntType.includes(key) && item[key].length > 0) {
          tempArr.push({ key, value: Number(item[key]), type: 'const', condition: '==' });
        } else if (tempText.includes(key) || tempSourceType.includes(key)) {
          if (item[key].length > 0) {
            tempArr.push({ key, value: item[key], type: 'const', condition: 'icontains' });
          }
        } else {
          tempArr.push({ key, value: item[key], type: 'const', condition: '==' });
        }
      }
      return tempArr;
    },
    handleRemoveSearch(item) {
      const tempObj = cloneDeep(this.searchFormData);
      delete tempObj[item.key];
      this.searchFormData = tempObj;
      const params = {};
      for (const key in tempObj) {
        params[key] = tempObj[key];
      }
      this.handleSearch(params);
      Bus.$emit('clearSearch', item);
    },
    async handleCloseDialog() {
      this.ticketStatus = 'RUNNING';
      if (!this.visible) {
        this.showSuccess = false;
        await this.getFieldList();
        await this.getTableList();
      }
    },

    async getTableList(conditions) {
      const params = {
        page: this.pagination.current,
        page_size: this.pagination.limit,
        page_id: this.page.id,
        version_number: this.version,
      };
      if (conditions) {
        params.conditions = conditions;
      }
      try {
        this.tableDataLoading = true;
        const res = await this.$store.dispatch('application/getListData', params);
        this.tableData = res.data.items;
        this.pagination.current = res.data.page;
        this.pagination.count = res.data.count;
      } catch (e) {
        console.log(e);
      } finally {
        this.tableDataLoading = false;
      }
    },
    async getFieldList() {
      const params = {
        project_key: this.appId,
        version_number: this.version,
        worksheet_id: this.formId,
      };
      const { fields } = this.config;
      const tempSysfiledList = SYS_FIELD.filter(filed => this.config.fields && this.config.fields.includes(filed.key));
      try {
        this.fieldListLoading = true;
        const result = await this.$store.dispatch('application/getWorksheetFiledConfig', params);
        this.fieldList = result.data.filter(item => fields.indexOf(item.id) !== -1);
        this.fieldList.push(...tempSysfiledList);
        this.editFiledsList = [...result.data, ...tempSysfiledList];
        this.fields = this.transFiledByOrder(result.data);
        this.selectionFields = cloneDeep(this.fieldList);
      } catch (e) {
        console.log(e);
      } finally {
        this.fieldListLoading = false;
      }
    },
    transFiledByOrder() {
      const tempFields = [];
      this.config.fields.forEach((item) => {
        this.fieldList.forEach(((fields) => {
          if (fields.id === item) {
            tempFields.push(fields);
          }
        }));
      });
      return tempFields;
    },
    handlePageChange(page) {
      this.pagination.current = page;
      this.getTableList();
    },
    handlePageLimitChange(limit) {
      this.pagination.limit = limit;
      this.pagination.current = 1;
      this.getTableList();
    },
    handleSettingChange({ fields }) {
      this.fields = fields;
    },
    dropdownShow() {
      this.isDropdownShow = true;
    },
    dropdownHide() {
      this.isDropdownShow = false;
    },
    triggerHandler(item) {
      this.$emit('headerBtnClick', item);
      this.$refs.dropdown.hide();
    },
    // 导出
    async handleExport() {
      const params = {
        page_id: Number(this.page.id),
        version_number: this.$route.params.version,
      };
      if (JSON.stringify(this.searchFormData) !== '{}') {
        const condition = this.formatSearchCondition(this.searchFormData);
        const conditions = {
          connector: 'and',
          expressions: condition,
        };
        params.conditions = conditions;
      }
      if (this.selection.length > 0) {
        const ids = this.selection.map(item => item.id);
        params.ids = ids;
      }
      const res = await this.$store.dispatch('application/exportData', params);
      const href = window.URL.createObjectURL(new Blob(
        [res],
        { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }
      ));
      const downloadElement = document.createElement('a');
      downloadElement.href = href;
      downloadElement.download = `${this.page.name}.csv`; // 下载后文件名
      document.body.appendChild(downloadElement);
      downloadElement.click(); // 点击下载
      document.body.removeChild(downloadElement); // 下载完成移除元素
      window.URL.revokeObjectURL(href); // 释放掉blob对象
    },
    // 详情
    async handleviewDetail(btn, row) {
      this.slideTitle = '详情';
      this.sidesliderIsShow = true;
      this.isEditor = false;
      const params = {
        pk: row.id,
        service_id: btn.value,
        worksheet_id: this.formId,
      };
      try {
        this.editorLoading = true;
        const res = await this.$store.dispatch('application/getDetail', params);
        const resData = res.data[0];
        const showFiled = [];
        this.editFiledsList.forEach((item) => {
          if (typeof (resData[item.key]) !== 'undefined') {
            if (['IMAGE'].includes(item.type)) {
              const arr = resData[item.key];
              item.val = arr ? arr.map(el => ({
                path: el,
              })) : [];
            } else {
              item.val = resData[item.key];
            }
            showFiled.push(item);
          }
        });
        this.showFiled = showFiled;
      } catch (e) {
        console.log(e);
      } finally {
        this.editorLoading = false;
      }
    },
    // 获取当前某行数据的全部值
    async getTotalValue(value, row) {
      const params = {
        pk: row.id,
        service_id: value,
        worksheet_id: this.formId,
      };
      try {
        const res = await this.$store.dispatch('application/getDetail', params);
        return res.data[0];
      } catch (e) {
        console.warn(e);
      }
    },

    handleClick(btn, row = {}, actionType) {
      // 按钮权限映射表如果没有按钮id字段，则点击无效果
      if (!(btn.id in this.actionsPermMap)) {
        return;
      }
      if (this.actionsPermMap[btn.id] === false) {
        const resource = {
          action: [{ id: btn.id, name: btn.name }],
          page: [{ id: this.page.id, name: this.page.name }],
          project: [{ id: this.appId, name: this.appName }],
        };
        this.applyForPermission(['action_execute'], [], resource);
        return;
      }
      const { type, value, id } = btn;
      this.btnId = id || '';
      switch (type) {
        case 'DELETE':
          this.deleteItem(value, row);
          this.getBuiltInService(value);
          break;
        case 'EDIT':
          this.updateItem(value, row);
          this.getBuiltInService(value);
          break;
        case 'ADD':
          this.$router.push({
            name: 'commonCreateTicket',
            params: {
              appId: this.appId,
              version: this.version,
              pageId: this.page.id,
              funcId: value,
              actionId: this.btnId,
            },
            query: {
              actionType,
              componentId: this.componentId,
            },
          });
          break;
        case 'EXPORT':
          this.handleExport();
          break;
        case 'DETAIL':
          this.handleviewDetail(btn, row);
          break;
        case 'IMPORT':
          this.handleImportFields(btn, row);
          break;
        default:
      }
    },
    deleteItem(id, row) {
      let title = '是否删除这条信息';
      if (JSON.stringify(row) === '{}') {
        title = `是否删除${this.selection.length}条信息`;
      }
      this.$bkInfoBox({
        confirmLoading: true,
        title,
        confirmFn: async () => {
          try {
            const res = await this.getSheetPage(id);
            console.log(res);
            const fields = res.map((item) => {
              const { choice, id, key, type } = item;
              if (key === 'id') {
                return { choice, id, key, type, value: row.id || 0 };
              }
              if (key === 'ids') {
                return {
                  choice,
                  id,
                  key,
                  type,
                  value: JSON.stringify(row) === '{}' ? this.selection.map(i => i.id) : [],
                };
              }
              return { choice, id, key, type, value: '系统内置标题' };
            });
            const params = {
              fields,
              page_id: this.page.id,
              project_key: this.appId,
              action_id: this.btnId,
              service_id: Number(id),
            };
            const ticketRes = await this.$store.dispatch('application/createTicket', params);
            if (ticketRes.result) {
              this.ticketId = ticketRes.data.id;
              this.showSuccess = true;
              // this.getTableList();
              if (this.isBuiltIn) {
                this.visible = true;
                this.polling('workbench/getOrderStatus', { id: this.ticketId });
              }
              await this.getTableList();
            } else if (!ticketRes.result) {
              this.$bkMessage({
                message: ticketRes.message,
                theme: 'error',
              });
            }
            return true;
          } catch (e) {
            console.warn(e);
            return false;
          }
        },
      });
    },
    async updateItem(id, row) {
      this.isEditor = true;
      this.slideTitle = '编辑';
      this.sidesliderIsShow = true;
      this.editorLoading = true;
      const value = {};
      const editorValue = await this.getTotalValue(id, row);
      const editorData = await this.getEditFieldList(id);
      const tempEditData = [];
      const tempKeyList = this.editFiledsList.map(item => item.key);
      editorData.forEach((item) => {
        if (item.meta.worksheet) {
          for (const i in editorValue) {
            if (item.meta.worksheet.field_key === i) {
              item.value = editorValue[i];
              if (['MULTISELECT', 'CHECKBOX', 'MEMBER', 'MEMBERS'].includes(item.type)) {
                // 以上接受一个数组 给的是字符串
                value[item.key] = (editorValue[i] && editorValue[i].split(',')) || [];
              } else if ('INT' === item.type) {
                value[item.key] = editorValue[i] || 0;
              } else {
                // console.log(typeof  editorValue[i], editorValue[i]);
                value[item.key] = editorValue[i] || '';
              }
            }
          }
          if (tempKeyList.some(el => item.meta.worksheet.field_key === el)) {
            tempEditData.push(item);
          }
        } else if (item.key === 'id') {
          value.id = row.id;
          tempEditData.push(item);
        }
      });
      this.editorValue = value;
      this.editorList = tempEditData;
      this.btnValue = id;
    },
    handleImportFields() {
      this.uploadStatus = 'UPLOAD';
      this.importConfig.visible = true;
    },
    customRequest(fileData) {
      const data = new FormData();
      data.append('file', fileData.fileObj.origin);
      data.append('worksheet_id', this.formId);
      this.importFailMessge = '';
      return this.$store.dispatch('application/validateData', data).then((res) => {
        this.$store.dispatch('application/uploadFile', data).then((result) => {
          this.uploadStatus = 'SUCCESS';
        });
      })
        .catch((e) => {
          this.uploadStatus = 'FAILED';
          const { message } = e.data;
          this.importFailMessge = message;
          console.warn(e);
        });
    },
    handleDownloadTemplate() {
      const params = { page_id: this.page.id, version_number: this.version };
      const paramsStr = getQuery(params);
      const BASE_URL = `${window.SITE_URL}api/engine/data/generate_export_template/${paramsStr}`;
      window.open(BASE_URL);
    },
    async getSheetPage(id) {
      const params = {
        service_id: id,
      };
      try {
        const result = await this.$store.dispatch('setting/getSheetPage', params);
        return result.data;
      } catch (e) {
        console.log(e);
      } finally {
        this.editorLoading = false;
      }
    },
    async getEditFieldList(id) {
      try {
        const res = await this.$store.dispatch('application/getFormPageFields', {
          type: this.page.type,
          paths: {
            project_key: this.appId,
            page_id: this.page.id,
            version_number: this.version,
            page_component_id: this.componentId,
            service_id: id,
            source: 'optionList',
          },
        });
        return  res.data.filter(item => item.type !== 'AUTO-NUMBER');
      } catch (e) {
        console.error(e);
      } finally {
        this.editorLoading = false;
      }
    },
    handleClose() {
      (this.editorValue = {}), (this.sidesliderIsShow = false);
    },
    getApiFields() {
      return this.editorList.map((item) => {
        const { choice, id, key, type } = item;
        let value = this.editorValue[key];
        if (type === 'IMAGE') {
          value = this.editorValue[key].map(item => (item.path ? item.path : item));
        } else if (['MULTISELECT', 'CHECKBOX', 'MEMBER', 'MEMBERS'].includes(type)) {
          value = Array.isArray(this.editorValue[key]) ? this.editorValue[key].join(',') : this.editorValue[key];
        }
        return { choice, id, key, type, value };
      });
    },
    async submit() {
      this.submitPending = true;
      try {
        // 后端value只接受字符串需要改造下面这个方法
        const fieldsRequest = this.getApiFields();
        const params = {
          service_id: Number(this.btnValue),
          fields: fieldsRequest,
          page_id: this.page.id,
          project_key: this.appId,
          action_id: this.btnId,
        };
        const res = await this.$store.dispatch('application/createTicket', params);
        if (res.result) {
          this.ticketId = res.data.id;
          this.showSuccess = true;
          if (this.isBuiltIn) {
            this.visible = true;
            this.polling('workbench/getOrderStatus', { id: this.ticketId });
          }
        }
      } catch (e) {
        console.error(e);
      } finally {
        this.submitPending = false;
        this.sidesliderIsShow = false;
        this.editorValue = {};
      }
    },
    handleChange($event) {
      this.editorValue = Object.assign(this.editorValue, $event);
    },
    transformFields(field, row) {
      let showValue = '';
      if (['SELECT', 'RADIO', 'CHECKBOX', 'INPUTSELECT', 'MULTISELECT'].includes(field.type)) {
        if (['API', 'WORKSHEET'].includes(field.source_type)) {
          showValue = row[field.key];
        } else if (['CHECKBOX', 'MULTISELECT'].includes(field.type)) {
          const tempArr = [];
          field.choice.forEach((item) => {
            if (row[field.key] && Array.isArray(row[field.key].split(','))) {
              row[field.key].split(',').forEach((val) => {
                if (item.key === val) {
                  tempArr.push(item.name);
                }
              });
            }
            showValue = tempArr.toString();
          });
        } else {
          field.choice.forEach((item) => {
            if (item.key === row[field.key]) {
              showValue = item.name;
            }
          });
        }
      }
      if (field.type === 'FORMULA' && field.meta.config && field.meta.config.calculate_type === 'date') {
        const { accuracy, can_format, can_affix, default_time } = field.meta.config;
        const timeStampArr = row[field.key].split(' - ').map(item => new Date(item).getTime());
        if (!timeStampArr[0] || !timeStampArr[1]) {
          return showValue = '计算数值有误';
        }
        const timeStamp = timeStampArr[0] - timeStampArr[1];
        //	时间精确度
        if (accuracy) {
          if (timeStamp < 0) {
            showValue = '当前时间为负数，请检查是否设置前缀自适应';
          } else if (accuracy === 'hour') {
            showValue = this.$dayjs(timeStamp).format('DD天 HH');
          } else if (accuracy === 'minute') {
            showValue = this.$dayjs(timeStamp).format('DD天 HH:mm');
          } else if (accuracy === 'day') {
            showValue = this.$dayjs(timeStamp).format('DD天');
          }
        } else {
          showValue = default_time;
        }
        // 是否前缀自适应
        if (can_affix && accuracy) {
          if (timeStamp < 0) {
            const abSoluteValue = Math.abs(timeStamp);
            showValue = this.formatDay(abSoluteValue);
          } else {
            showValue = this.formatDay(timeStamp);
          }
        }
        //	是否格式自适应
        if (can_format && accuracy) {
          if (Math.abs(timeStamp) < this.DAY_TIME_STAMP) {
            showValue = timeStamp > 0 ? '还有0天' : '已经0天';
          } else {
            showValue = timeStamp > 0 ? `还有${this.formatDay(timeStamp)}` : `已经${this.formatDay(Math.abs(timeStamp))}`;
          }
        }
        // console.log(timeStamp, field);
      }
      if (field.type === 'FORMULA' && field.meta.config && field.meta.config.calculate_type === 'number') {
        showValue = row[field.key];
      }
      return showValue || '--';
    },
    getImageListFullPath(list) {
      return list.map(item => `${window.location.origin}${window.SITE_URL}${item}`);
    },
    getFullPath(item) {
      return `${window.location.origin}${window.SITE_URL}${item}`;
    },
    formatDay(abSoluteValue) {
      let totalYear;
      let totalDay;
      let totalMonth;
      const day = Math.floor(abSoluteValue / this.DAY_TIME_STAMP);
      totalYear = Math.floor(day / 365);
      totalMonth = Math.floor((day % 365) / 30);
      totalDay = day - (365 * totalYear) - (30 * totalMonth);
      return `${totalYear > 0 ? `${totalYear}年` : ''}${totalMonth > 0 ? `${totalMonth}月` : ''}${totalDay > 0 ? `${totalDay}天` : ''}`;
    },
    handleSelect(selection) {
      this.selection = selection;
    },
    handleSelectAll(selection) {
      this.selection = selection;
    },
    handleSuccessBack() {
      this.showSuccess = false;
      this.ticketId = '';
    },
    // 获取是否内置服务
    async getBuiltInService(id) {
      try {
        const res = await this.$store.dispatch('setting/getBuiltInService', id);
        this.isBuiltIn = res.data.is_builtin;
      } catch (e) {
        console.error(e);
      }
    },
    async polling(url, data, delay = 1000) {
      let timer;
      try {
        const res = await this.$store.dispatch(url, data);
        const resData = res.data.filter(i => i.type === 'DATA-PROC');
        const currentStatus = resData.length > 0 ? resData[0].status : '';
        if (!['FINISHED', 'FAILED'].includes(currentStatus) && this.visible) {
          timer = setTimeout(() => this.polling(url, data, delay), delay);
        } else {
          clearTimeout(timer);
          this.ticketStatus = currentStatus;
        }
      } catch (e) {
        console.warn(e);
      }
    },
    handleView(row, column, fields) {
      const { type } = fields;
      this.imageConfig.type = type;
      if (type === 'TABLE') {
        this.imageConfig.imgList = {};
        this.imageConfig.imgList.fields = fields;
        this.imageConfig.imgList.val = row[column.property];
      } else {
        this.imageConfig.imgList = type === 'IMAGE'
          ? row[column.property].map(item => ({ path: `${window.location.origin}${window.SITE_URL}${item}` })) : row[column.property];
      }
      this.imageConfig.label = column.label;
      this.imageConfig.imageVisible = true;
    },
    handleDownload(row, column) {
      if (row[column.property].length > 0) {
        row[column.property].forEach((item) => {
          window.open(`${window.location.origin}${window.SITE_URL}api/misc/download_file/?file_name=${item.file_name}&origin_name=${item.origin_name}&download_flag=1`);
        });
      }
    },
    handleCancel() {
      this.isShowSearchInfo = false;
      this.handleSearch();
    },
    goToDetail() {
      this.$router.push({ name: 'processDetail', params: { id: this.ticketId } });
    },
    goToLink(row, column) {
      let url = row[column.property];
      if (url.indexOf('http') !== 0) {
        url = `http://${url}`;
      }
      window.open(url, '_blank');
    },
  },
};
</script>

<style lang="postcss" scoped>
@import '../../../css/scroller.css';

.list-page {
  position: relative;
  height: 100%;

  .circle {
    position: absolute;
    top: -5px;
    right: 20px;
    width: 14px;
    height: 14px;
    background: #979ba5;
    border-radius: 50%;
    display: block;
    z-index: 5;

    i {
      color: #fcfcfc;
      font-size: 14px;
      height: 14px;
      display: block;
      line-height: 14px;
    }
  }

  .table-config {
    margin: 24px;
    padding: 20px 16px;
    border-radius: 2px;
    background: #ffffff;
    height: calc(100% - 56px);
    overflow: auto;
    position: relative;
    @mixin scroller;
  }

  .is-active {
    border: 1px dashed #3a84ff;
  }

  .header-config {
    height: 32px;
    width: 100%;
    display: flex;
    justify-content: space-between;
  }

  .function-btn {
    display: flex;

    .bk-dropdown-list {
      a.disabled {
        color: #cccccc;
        cursor: not-allowed;
      }
    }
  }

  .isActive {
    border: 1px dashed #3a84ff;
  }

  .table-border {
    margin-top: 16px;

    /deep/ .bk-table th {
      background: yellow !important;
    }
  }

  .search-icon {
    width: 32px;
    height: 32px;
    border: 1px solid #C4C6CC;
    cursor: pointer;
    display: flex;
    justify-content: center;
    align-items: center;
    border-radius: 2px;
    background: #FFFFFF;

    &:hover {
      border: 1px solid #979BA5;
    }

    i {
      color: #979BA5
    }
  }

  /deep/ .bk-table {
    &::before {
      height: 0;
    }

    .bk-table-column-setting {
      border-left: none;
    }
  }

  .dropdown-trigger-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid #c4c6cc;
    height: 26px;
    border-radius: 2px;
    padding: 0 15px;
    color: #63656e;
  }

  .dropdown-trigger-btn.bk-icon {
    font-size: 18px;
  }

  .dropdown-trigger-btn .bk-icon {
    font-size: 22px;
  }

  .dropdown-trigger-btn:hover {
    cursor: pointer;
    border-color: #979ba5;
  }

  .btn-content {
    margin-left: 8px;
  }
}

.table-more-icon {
  font-size: 16px;

  &:hover {
    color: #3a84ff;
  }
}

.table-more-actions {
  background: #fff;

  .action-item {
    padding: 0 12px;
    height: 32px;
    line-height: 32px;
    color: #63656e;
    cursor: pointer;

    &:hover {
      background: #f4f6fa;
      color: #3a84ff;
    }

    &.disabled {
      color: #cccccc;
      cursor: not-allowed;
    }

    i {
      width: 12px;
      margin-right: 4px;
    }
  }
}

.king-slider-footer {
  display: flex;
  align-items: center;
  width: 640px;
  height: 64px;
  padding-left: 20px;
  background-color: #fff;
  border-top: 1px solid #dcdee5;
}

/deep/ .custom-sidelider {
  .bk-sideslider-wrapper {
    overflow-y: hidden;

    .bk-sideslider-content {
      @mixin scroller;
      height: calc(100% - 60px) !important;

      .content {
        overflow-x: hidden;
      }
    }
  }
}

.icon-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;

  .detail-btn {
    font-size: 16px;
  }

  & > i {
    font-size: 56px;
    color: #2dcb56;
  }

  & > p {
    margin: 20px 0 8px;
    color: #000000;
    font-size: 16px;
    line-height: 1;
  }

  .fail-reason {
    @mixin scroller;
    color: red;
    overflow: auto;
    max-height: 100px;
  }

  .error-icon {
    color: #ea3636;
  }

  .desc {
    color: #63656e;
    font-size: 12px;
  }
}

.status-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
}

.custom-form {
  @mixin scroller;
  height: 500px;
  overflow: auto;

  /deep/ .bk-form-content {
    @mixin scroller;
    font-size: 14px;
    color: #63656e;
    overflow: auto;
  }
}

.search-item-container {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.image-item {
  position: relative;
  display: inline-block;
  margin-left: 8px;
  margin-bottom: 8px;
  padding: 5px;
  width: 100px;
  height: 100px;
  background: #fafbfd;
  border: 1px solid #c4c6cc;
  border-radius: 2px;

  img {
    width: 100%;
  }

  &:not(.disabled):hover {
    &:after {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.6);
    }

    .delete-icon {
      display: block;
    }
  }
}

.upload-content {
  position: relative;

  span {
    display: block;
    position: absolute;
    top: 82px;
    right: 0;
    cursor: pointer;
    font-size: 12px;
    color: #1768EF;
  }
}

.photo-view {
  img {
    height: 27px;
    width: 27px;
  }
}

</style>
<style lang="postcss">
.more-option-popover {
  .tippy-tooltip {
    padding: 2px 0;
  }
}

.tippy-content {
  padding: 0px;
}

.bk-tooltip-content {
  .content-scroller {
    .content-line-height {
      display: none;
    }
  }
}

</style>

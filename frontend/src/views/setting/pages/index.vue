<template>
  <section>
    <page-wrapper title="页面管理">
      <div class="page-container" v-bkloading="{ isLoading: pageListLoading }">
        <div class="left-setting">
          <page-tree
            :app-id="appId"
            :page-list="pageList"
            :root-page-id="rootPageId"
            :crt-page="crtPage.id"
            @update="handleUpdateList"
            @createPage="handleCreatePage"
            @select="handleSelectPage">
          </page-tree>
        </div>
        <template v-if="pageList.length > 0">
          <page-empty
            v-if="isGroupEmpty"
            :is-group="true"
            :id="pageList.find(item => item.type === 'GROUP').id"
            @createPage="handleCreatePage">
          </page-empty>
          <div v-else v-bkloading="{ isLoading: pageComponentLoading, opacity: 1 }" class="page-content-container">
            <div class="custom-page" v-if="crtPage.type==='CUSTOM'">
              <show-custom-page :page-list="pageComponent"> </show-custom-page>
            </div>
            <div class="center-page" v-if="['FUNCTION','SHEET','LIST'].includes(crtPage.type)">
              <function-page
                v-if="crtPage.type === 'FUNCTION'"
                :cards="pageComponent"
                :page-id="crtPage.id"
                :crt-index="attrData.index"
                @update="handleCardsUpdate">
              </function-page>
              <sheet-page v-if="crtPage.type === 'SHEET'" :func-id="attrData.funcId"></sheet-page>
              <list-page
                v-if="crtPage.type === 'LIST' && pageComponent.length > 0"
                ref="listPage"
                :list="pageComponent[0]">
              </list-page>
            </div>
            <div class="right-setting" v-if="['FUNCTION','SHEET','LIST'].includes(crtPage.type)">
              <attribute-config
                v-if="['FUNCTION','SHEET'].includes(crtPage.type)"
                :app-id="appId"
                :page="crtPage"
                :value="attrData"
                @change="handleAttrChange">
              </attribute-config>
              <right-setting
                v-else-if="crtPage.type==='LIST'"
                :is-show-work-sheet="isShowWorkSheet"
                :type="crtPage.type"
                :work-sheet-id="workSheetId"
                :show-mode="showMode"
                :conditions="conditions"
                :time-range="timeRange"
                :list-id="attrData.listId"
                @select="getTableFileds">
              </right-setting>
            </div>
            <div class="bottom-container">
              <template v-if="['FUNCTION','SHEET','LIST'].includes(crtPage.type)">
                <bk-button
                  class="btn-save"
                  theme="primary"
                  title="保存"
                  :disabled="pageComponentLoading"
                  :loading="pageComponentSaving"
                  @click="handleSave">
                  保存
                </bk-button>
                <bk-button
                  :theme="'default'"
                  type="submit"
                  :title="'基础按钮'"
                  :disabled="pageComponentSaving"
                  @click="handleRest"
                  class="btn-rest">
                  重置
                </bk-button>
              </template>
              <template v-else>
                <bk-button
                  class="btn-save"
                  theme="primary"
                  title="编辑页面"
                  :disabled="pageComponentLoading"
                  @click="handleEditPage">
                  编辑页面
                </bk-button>
              </template>
            </div>
          </div>
        </template>
        <page-empty v-else @createPage="handleCreatePage"></page-empty>
      </div>
    </page-wrapper>
    <create-page-dialog
      :show="createPageDialogShow"
      :page-list="pageList"
      :group="selectedGroup"
      :app-id="appId"
      @confirm="createPageConfirm"
      @cancel="createPageDialogShow = false">
    </create-page-dialog>
  </section>
</template>
<script>
import pageWrapper from '@/components/pageWrapper.vue';
import PageTree from './pageTree.vue';
import rightSetting from '../components/rightSetting.vue';
import functionPage from './functionPage.vue';
import sheetPage from './sheetPage.vue';
import PageEmpty from './pageEmpty.vue';
import listPage from '../components/listPage.vue';
import CreatePageDialog from './createPageDialog.vue';
import AttributeConfig from './attributeConfig.vue';
import showCustomPage from './showCustomPage.vue';
import cloneDeep from 'lodash.clonedeep';

export default {
  name: 'PageDesign',
  components: {
    PageTree,
    pageWrapper,
    rightSetting,
    sheetPage,
    listPage,
    PageEmpty,
    CreatePageDialog,
    AttributeConfig,
    showCustomPage,
    functionPage,
  },
  props: {
    appId: String,
  },
  data() {
    return {
      pageList: [],
      rootPageId: null,
      crtPage: {}, // 当前选中页面
      pageListLoading: false,
      selectedGroup: undefined,
      createPageDialogShow: false,
      pageComponentLoading: false,
      pageComponent: [], // 页面包含的组件
      attrData: {}, // 属性配置面板数据
      pageComponentSaving: false,
      // 待删除
      rightSideShow: false,
      rightForm: {},
      filedList: [],
      listLoading: false,
      listId: '',
      isShowWorkSheet: true,
      workSheetId: '',
      showMode: '',
      conditions: {},
      timeRange: '',
    };
  },
  computed: {
    isGroupEmpty() {
      if (this.pageList.length > 0) {
        const hasSinglePage = this.pageList.some((item) => {
          if (item.type === 'GROUP') {
            return item.children.some(page => page.type !== 'GROUP');
          }
          return true;
        });
        return !hasSinglePage;
      }
      return false;
    },
    tempPageComponent() {
      return this.$store.state.setting.tempPageComponent;
    },
  },
  created() {
    this.getPageList();
  },
  methods: {
    async getPageList() {
      try {
        this.pageListLoading = true;
        const res = await this.$store.dispatch('setting/getTreePage', { project_key: this.appId });
        this.pageList = res.data[0].children;
        this.rootPageId = res.data[0].id;
        this.setDefaultCrtPage();
        if ('id' in this.crtPage) {
          this.getPageComponent();
        }
      } catch (e) {
        console.error(e);
      } finally {
        this.pageListLoading = false;
      }
    },
    async getPageComponent() {
      try {
        this.pageComponentLoading = true;
        const res = await this.$store.dispatch('setting/getPageComponent', {
          page_id: this.crtPage.id,
          page_size: 1000,
        });
        this.$store.commit('setting/setComponent', cloneDeep(res.data.items));
        this.pageComponent = res.data.items;
        if (this.pageComponent.length > 0) {
          if (this.crtPage.type === 'SHEET') {
            this.attrData = {
              funcId: Number(this.pageComponent[0].value),
              linkAddress: this.pageComponent[0].config.linkAddress || '',
            };
          } else if (this.crtPage.type === 'FUNCTION') {
            // 功能卡片有添加卡片，取第一个为选中态
            const card = this.pageComponent[0];
            const { value, config } = card;
            const { name, desc } = config;
            this.attrData = { funcId: Number(value), name, desc, index: 0 };
          } else {
            const list = this.pageComponent[0];
            const { config } = this.pageComponent[0];
            if (!config.searchInfo) {
              this.$set(this.pageComponent[0].config, 'searchInfo', []);
            }
            if (!config.show_mode) {
              this.$set(this.pageComponent[0].config, 'show_mode', {
                mode: 0,
              });
            }
            if (!config.conditions) {
              this.$set(this.pageComponent[0].config, 'conditions', {
                connector: '',
                expressions: [{ condition: '', key: '', value: '', type: 'const' }],
              });
            }
            if (!config.time_range) {
              this.$set(this.pageComponent[0].config, 'time_range', 'all');
            }
            const { value } = list;
            this.listId = value;
            this.workSheetId = value || '';
            this.showMode = config.show_mode.mode || 0;
            this.conditions = config.conditions;
            this.timeRange = config.time_range || 'all';
          }
        } else {
          if (this.crtPage.type === 'SHEET') {
            this.attrData = { funcId: '', linkAddress: '' };
          } else if (this.crtPage.type === 'FUNCTION') {
            this.attrData = {};
          } else if (this.crtPage.type === 'LIST') {
            this.pageComponent.push({
              page_id: this.crtPage.id,
              value: '',
              type: 'LIST',
              config: {
                buttonGroup: [],
                optionList: [],
                fields: [],
                searchInfo: [],
                sys_fields: [],
                show_mode: { mode: 0 },
                time_range: 'all',
                conditions: { connector: '', expressions: [{ condition: '', key: '', value: '', type: 'const' }] },
              },
            });
          }
        }
      } catch (e) {
        console.error(e);
      } finally {
        this.pageComponentLoading = false;
      }
    },
    // 更新页面列表
    handleUpdateList(val) {
      this.pageList = val;
      if (this.pageList.length === 0) {
        this.crtPage = {};
      } else {
        if (!this.isCrtPageInList()) {
          this.setDefaultCrtPage();
          if ('id' in this.crtPage) {
            this.getPageComponent();
          }
        }
      }
    },
    // 当前选中页面是否存在页面列表里
    isCrtPageInList() {
      return this.pageList.some((item) => {
        if (this.crtPage.id === item.id) {
          return true;
        }
        if (item.children) {
          return item.children.some(page => page.id === this.crtPage.id);
        }
        return false;
      });
    },
    // 设置当前选中页面
    setDefaultCrtPage() {
      if (this.pageList.length > 0) {
        const hasSinglePage = this.pageList.some((item) => {
          if (item.type === 'GROUP') {
            if (item.children.length > 0) {
              this.crtPage = item.children[0];
              return true;
            }
          } else {
            this.crtPage = item;
            return true;
          }
        });
        if (!hasSinglePage) {
          this.crtPage = {};
        }
      } else {
        this.crtPage = {};
      }
    },
    handleCreatePage(group) {
      this.selectedGroup = group;
      this.createPageDialogShow = true;
    },
    createPageConfirm(data, list) {
      this.handleUpdateList(list);
      this.createPageDialogShow = false;
      this.handleSelectPage(data);
    },
    handleSelectPage(val) {
      this.crtPage = val;
      this.pageComponent = [];
      this.attrData = {};
      this.workSheetId = '';
      this.getPageComponent();
    },
    handleAttrChange(val) {
      if (this.crtPage.type === 'SHEET') {
        this.attrData = { ...val };
        console.log(val);
      } else if (this.crtPage.type === 'FUNCTION') {
        const { funcId, name, desc, bgColor, index } = val;
        const card = this.pageComponent[index];
        this.pageComponent.splice(index, 1, {
          ...card,
          value: funcId,
          config: { name, desc, bgColor },
        });
        this.attrData = { ...val };
      }
    },
    handleCardsUpdate(list, index) {
      this.pageComponent = list;
      const cardData = list[index];
      const { name, desc, bgColor } = cardData.config;
      this.attrData = { funcId: cardData.value, name, desc, bgColor, index };
    },
    // 待删除
    handleSettingChange(fields) {
      this.filedList = fields;
    },
    handleRest() {
      if (this.tempPageComponent.length !== 0) {
        this.pageComponent = cloneDeep(this.tempPageComponent);
        if (this.pageComponent[0].type === 'SHEET') {
          this.attrData = {
            funcId: Number(this.tempPageComponent[0].value),
          };
        }
      }
    },
    async handleSave() {
      const { id, type } = this.crtPage;
      let params = {
        page_id: id,
        type,
      };
      let action = 'createComponent';
      if (type === 'SHEET') {
        if (!this.attrData.funcId) {
          this.$bkMessage({
            theme: 'error',
            message: '请绑定功能',
          });
          return;
        }
        action = 'batchSaveComponent';
        if (this.pageComponent.length > 0) {
          params = {
            page_id: this.crtPage.id,
            components: [Object.assign(
              {}, this.pageComponent[0],
              { value: this.attrData.funcId }
            )],
          };
          params.components[0].config.linkAddress = this.attrData.linkAddress;
        } else {
          params = {
            page_id: this.crtPage.id,
            components: [
              {
                page_id: id,
                type,
                config: { linkAddress: this.attrData.linkAddress },
                value: this.attrData.funcId,
              },
            ],
          };
        }
      } else if (type === 'FUNCTION') {
        const flag = this.pageComponent.every(item => item.config.name);
        if (!flag) {
          this.$bkMessage({
            theme: 'error',
            message: '卡片名称未填写，请检查卡片名称！',
          });
          return;
        }
        action = 'batchSaveComponent';
        params = {
          page_id: this.crtPage.id,
          components: this.pageComponent,
        };
      } else {
        const tempParams = this.$refs.listPage.getData();
        if (!tempParams.value) {
          this.$bkMessage({
            theme: 'error',
            message: '请绑定表单',
          });
          return;
        }
        action = 'batchSaveComponent';
        if (this.pageComponent.length > 0) {
          params = {
            page_id: this.crtPage.id,
            components: [Object.assign({}, this.pageComponent[0], tempParams)],
          };
        } else {
          params = {
            page_id: this.crtPage.id,
            components: {
              page_id: id,
              type,
              ...tempParams,
            },
          };
        }
      }
      try {
        this.pageComponentSaving = true;
        await this.$store.dispatch(`setting/${action}`, params);
        this.$bkMessage({
          message: '保存成功',
          theme: 'success',
        });
      } catch (e) {
        console.log(e);
      } finally {
        this.pageComponentSaving = false;
        this.getPageComponent();
      }
    },
    handleEditPage() {
      this.$router.push({ name: 'customPage', params: { appId: this.appId, pageId: this.crtPage.id } });
    },
    async getTableFileds(val) {
      if (val) {
        this.listLoading = true;
        this.listId = val;
        try {
          const res = await this.$store.dispatch('setting/getFormFields', val);
          this.filedList = res.data;
        } catch (e) {
          console.log(e);
        } finally {
          this.listLoading = false;
        }
      }
    },
  },
};
</script>

<style lang="postcss" scoped>
.page-container {
  display: flex;
  height: 100%;
  justify-content: space-between;
  position: relative;

  .left-setting {
    height: 100%;
  }

  .page-content-container {
    position: relative;
    display: flex;
    justify-content: space-between;
    flex: 1 1 auto;
    width: calc(100% - 210px);
    height: 100%;
  }

  .center-page {
    width: calc(100% - 320px);
    height: calc(100% - 56px);
  }

  .custom-page {
    width: 100%;
    height: calc(100% - 104px);
    margin: 24px;
    background: #ffffff;
    border-radius: 2px;
  }

  .right-setting {
    width: 320px;
    height: calc(100% - 56px);
    background: #ffffff;
  }

  .bottom-container {
    position: absolute;
    bottom: 0;
    right: 0;
    width: 100%;
    height: 56px;
    line-height: 56px;
    border-top: 1px solid #dcdee5;
    background: #fafbfd;
  }

  .btn-save {
    margin-left: 24px;
    width: 88px;
    height: 32px;
  }

  .btn-rest {
    margin-left: 4px;
    width: 88px;
    height: 32px;
  }
}
</style>

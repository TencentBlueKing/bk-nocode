<template>
  <section class="app-list-page">
    <div class="operate-area">
      <div>
        <bk-button
          v-cursor="{ active: !hasCreateAppPerm }"
          theme="primary"
          icon="plus"
          :class="{ 'btn-permission-disabled': !hasCreateAppPerm }"
          :disabled="permLoading"
          @click="onCreateApp">
          添加应用
        </bk-button>
        <bk-button
          v-cursor="{ active: !hasCreateAppPerm }"
          theme="default"
          :class="['export',{ 'btn-permission-disabled': !hasCreateAppPerm }]"
          :disabled="permLoading"
          @click="onCreateApp('import')">
          导入
        </bk-button>
      </div>
      <div class="search-content">
        <bk-select class="app-status-filter" :clearable="false" v-model="status" @change="getAppList">
          <bk-option v-for="item in statusList" class="action-item" :key="item.id" :id="item.id" :name="item.name">
          </bk-option>
        </bk-select>
        <bk-input
          v-model.trim="searchStr"
          class="search-input"
          right-icon="bk-icon icon-search"
          placeholder="请输入应用名称"
          :clearable="true"
          @change="handleChange"
          @clear="handleSearchClear"
          @enter="handleSearchEnter">
        </bk-input>
      </div>
    </div>
    <div class="list-wrapper" v-bkloading="{ isLoading: listLoading }">
      <template v-if="listData.length > 0">
        <app-card
          v-for="app in listData"
          class="app-card-item"
          type="edit"
          :key="app.key"
          :releasing="appReleasingTimer[app.key] > 0"
          :app="app"
          @handleClick="handleCardClick">
        </app-card>
      </template>
      <bk-exception v-else class="no-data" type="empty" scene="part"></bk-exception>
    </div>
    <bk-dialog
      v-model="appEditDialogShow"
      :title="isImport?'应用导入':'应用设置'"
      header-position="left"
      :mask-close="false"
      :auto-close="false"
      :width="640"
      :loading="appEditPending"
      @confirm="onEditAppConfirm"
      @cancel="onEditAppCancel">
      <div v-if="editingApp" class="app-edit-content">
        <bk-form ref="appForm" form-type="vertical" :model="editingApp" :rules="appFormRules">
          <bk-form-item label="应用名称" property="name" :required="true" :error-display-type="'normal'">
            <bk-input placeholer="请输入应用名称" v-model.trim="editingApp.name" @change="debounceChange"></bk-input>
          </bk-form-item>
          <bk-form-item label="应用颜色">
            <ul class="color-wrap">
              <li
                v-for="(item, index) in appColors"
                :key="index"
                :style="getBgColor(item)"
                :class="[
                  'color-item',
                  { selected: editingApp.color[0] === item[0] && editingApp.color[1] === item[1] },
                ]"
                @click="onSelectBgColor(item)"></li>
            </ul>
          </bk-form-item>
          <bk-form-item label="应用标识" property="key" :required="true" :error-display-type="'normal'">
            <bk-input v-model.trim="editingApp.key" :disabled="!editingApp.isCreate"></bk-input>
            <p class="prefix-tips">应用唯一key值，只支持英文和下划线</p>
          </bk-form-item>
          <bk-form-item label="流程标识" property="prefix">
            <bk-input v-model.trim="editingApp.prefix"></bk-input>
            <p class="prefix-tips">流程标识将在工作台中用于标识该应用的流程，仅支持英文字母</p>
          </bk-form-item>
          <bk-form-item label="应用摘要" property="desc">
            <bk-input type="textarea" placeholder="请输入应用摘要" v-model.trim="editingApp.desc"></bk-input>
          </bk-form-item>
          <bk-form-item label="文件" property="file" :required="true" v-if="isImport" :error-display-type="'normal'">
            <bk-upload
              :theme="'button'"
              :tip="'仅支持.json格式文件'"
              :accept="'.json'"
              :url="url"
              :with-credentials="true"
              :multiple="false"
              :custom-request="customRequest"
            >
            </bk-upload>
          </bk-form-item>
        </bk-form>
      </div>
    </bk-dialog>
  </section>
</template>
<script>
import cloneDeep from 'lodash.clonedeep';
import pinyin from 'pinyin';
import permission from '@/components/permission/mixins.js';
import AppCard from './components/appCard.vue';
import { appColors } from '@/constants/colors.js';
import { debounce, getQuery } from '@/utils/util';

export default {
  name: 'AppList',
  components: {
    AppCard,
  },
  mixins: [permission],
  data() {
    return {
      appColors,
      permLoading: false,
      hasCreateAppPerm: false,
      listLoading: false,
      listData: [],
      searchStr: '',
      editingApp: null,
      appEditDialogShow: false,
      appDeleteDialogShow: false,
      appReleaseDialogShow: false,
      appEditPending: false,
      appDeletePending: false,
      status: 'ALL',
      appReleasingTimer: {},
      appFormRules: {
        name: [
          {
            required: true,
            message: '应用名称为必填项',
            trigger: 'blur',
          },
        ],
        key: [
          {
            required: true,
            message: '应用标识为必填项',
            trigger: 'blur',
          },
        ],
        file: [
          {
            required: true,
            message: '附件为必填项',
            trigger: 'blur',
          },
        ],
      },
      statusList: [
        { id: 'ALL', name: '全部' },
        { id: 'UNRELEASED', name: '未发布' },
        { id: 'RELEASED', name: '已发布' },
        { id: 'CHANGED', name: '已变更待发布' },
      ],
      isImport: false,
      url: `${window.SITE_URL}api/project/manager/import_project/`,
    };
  },
  created() {
    this.getCreateAppPerm();
    this.getAppList();
    this.debounceChange = debounce(this.handleAppNameChange, 500);
  },
  beforeDestroy() {
    Object.keys(this.appReleasingTimer).forEach((key) => {
      if (this.appReleasingTimer[key] > 0) {
        clearTimeout(this.appReleasingTimer[key]);
      }
    });
  },
  methods: {
    async getCreateAppPerm() {
      try {
        this.permLoading = true;
        const res = await this.$store.dispatch('permission/getPlatform');
        this.hasCreateAppPerm = res.data.project_create;
        this.permLoading = false;
      } catch (e) {
        console.error(e);
      }
    },
    async getAppList() {
      try {
        this.listLoading = true;
        const params = {
          show_type: 'manager_center',
        };
        if (this.searchStr !== '') {
          params.name__icontains = this.searchStr;
        }
        if (this.status !== 'ALL') {
          params.publish_status = this.status;
        }
        const res = await this.$store.dispatch('setting/getAllApp', params);
        this.listData = res.data;
        res.data.forEach((item) => {
          if (item.publish_status === 'RELEASING') {
            this.getAppStatus(item.key);
          }
        });
      } catch (e) {
        console.error(e);
      } finally {
        this.listLoading = false;
      }
    },
    handleChange(val) {
      if (!val) {
        this.getAppList();
      }
    },
    getAppStatus(key) {
      if (this.appReleasingTimer[key]) {
        clearTimeout(this.appReleasingTimer[key]);
      }
      const id = setTimeout(async () => {
        const res = await this.$store.dispatch('setting/getAppDetail', key);
        if (res.data.publish_status === 'RELEASING') {
          this.getAppStatus(key);
        } else {
          const index = this.listData.findIndex(item => item.key === key);
          this.listData.splice(index, 1, res.data);
          this.$set(this.appReleasingTimer, key, 0);
          this.$bkMessage({
            theme: 'success',
            message: '发布成功',
          });
        }
      }, 2000);
      this.$set(this.appReleasingTimer, key, id);
    },
    onCreateApp(type) {
      if (!this.hasCreateAppPerm) {
        this.applyForPermission(['project_create'], []);
        return;
      }
      this.isImport = type === 'import';
      this.editingApp = {
        key: '',
        prefix: '',
        name: '',
        desc: '',
        color: ['#3a84ff', '#6cbaff'],
        project_config: {},
        isCreate: true,
        file: '',
      };
      this.appEditDialogShow = true;
    },
    handleSearchEnter() {
      if (this.searchStr === '') {
        return;
      }
      this.getAppList();
    },
    handleSearchClear() {
      this.searchStr = '';
      this.getAppList();
    },
    handleCardClick(app, type) {
      const appData = cloneDeep(app);
      appData.prefix = appData.project_config.workflow_prefix;
      const { key, version_number, publish_status: publishStatus } = appData;
      this.editingApp = appData;
      switch (type) {
        case 'edit':
          this.appEditDialogShow = true;
          break;
        case 'detail':
          this.$router.push({ name: 'formList', params: { appId: this.editingApp.key, version: version_number } });
          break;
        case 'release':
          this.$bkInfo({
            title: `确认发布${this.editingApp.name}？`,
            confirmLoading: true,
            confirmFn: async () => {
              try {
                await this.$store.dispatch('setting/releaseApp', { project_key: this.editingApp.key });
                this.editingApp = null;
                this.getAppStatus(key);
              } catch (e) {
                console.error(e);
                this.$bkMessage({
                  theme: 'error',
                  message: '发布成功',
                });
              }
            },
          });
          break;
        case 'delete':
          this.$bkInfo({
            type: 'warning',
            subTitle: `确认删除应用：${this.editingApp.name}？`,
            confirmLoading: true,
            confirmFn: async () => {
              try {
                await this.$store.dispatch('setting/deleteApp', this.editingApp);
                this.editingApp = null;
                this.getAppList();
                this.$bkMessage({
                  theme: 'success',
                  message: '删除成功',
                });
              } catch (e) {
                console.error(e);
                this.$bkMessage({
                  theme: 'error',
                  message: '删除失败',
                });
              } finally {
                this.appDeletePending = false;
              }
            },
          });
          break;
        case 'down':
          this.editingApp.publish_status = 'UNRELEASED';
          this.$bkInfo({
            type: 'warning',
            subTitle: `确认下架应用：${this.editingApp.name}？`,
            confirmLoading: true,
            confirmFn: async () => {
              try {
                await this.$store.dispatch('setting/shelvesApp', this.editingApp);
                this.editingApp = null;
                this.getAppList();
                this.$bkMessage({
                  theme: 'success',
                  message: '下架成功',
                });
              } catch (e) {
                console.error(e);
                this.$bkMessage({
                  theme: 'error',
                  message: '下架失败',
                });
              } finally {
                this.appDeletePending = false;
              }
            },
          });
          break;
        case 'view':
          if (publishStatus === 'UNRELEASED') {
            return;
          }
          this.$router.push({ name: 'appPageContent', params: { appId: key, version: version_number } });
          break;
        case 'export':
          this.exportApp(app);
          break;
      }
    },
    getBgColor(color) {
      return {
        background: `linear-gradient(90deg, ${color[0]}, ${color[1]})`,
      };
    },
    onSelectBgColor(color) {
      this.editingApp.color = [...color];
    },
    // 编辑应用
    onEditAppConfirm() {
      this.appEditPending = true;
      this.$refs.appForm
        .validate()
        .then(async () => {
          try {
            this.editingApp.project_config.workflow_prefix = this.editingApp.prefix;
            const logo = pinyin(this.editingApp.name, {
              style: pinyin.STYLE_NORMAL,
              heteronym: false,
            })
              .join('')[0]
              .toUpperCase();
            this.editingApp.logo = logo;
            if (this.isImport) {
              await  this.importApp();
              return;
            }
            if (this.editingApp.isCreate) {
              const res = await this.$store.dispatch('setting/createApp', this.editingApp);
              this.$router.push({ name: 'formList', params: { appId: res.data.key } });
            }  else {
              await this.$store.dispatch('setting/editApp', this.editingApp);
              this.appEditDialogShow = false;
              this.editingApp = null;
              this.getAppList();
            }
          } catch (e) {
            console.error(e);
          } finally {
            this.appEditPending = false;
          }
        })
        .catch(() => {
          this.appEditPending = false;
        });
    },
    onEditAppCancel() {
      this.appEditDialogShow = false;
      this.editingApp = null;
    },
    // 自动填充key
    handleAppNameChange(val) {
      this.editingApp.key = pinyin(val, {
        style: pinyin.STYLE_NORMAL,
        heteronym: false,
      }).join('')
        .toUpperCase();
    },
    exportApp(app) {
      const params = {
        project_key: app.key,
      };
      window.open(`${window.location.origin}${window.SITE_URL}api/project/manager/export/${getQuery(params)}`);
    },
    customRequest(fileData) {
      this.editingApp.file = fileData.fileObj.origin;
    },
    async importApp() {
      this.appEditPending = true;
      const data = new FormData();
      const logo = pinyin(this.editingApp.name, {
        style: pinyin.STYLE_NORMAL,
        heteronym: false,
      })
        .join('')[0]
        .toUpperCase();
      this.editingApp.logo = logo;
      for (const key in this.editingApp) {
        if (['project_config', 'color'].includes(key)) {
          data.append(key, JSON.stringify(this.editingApp[key]));
          continue;
        }
        data.append(key, this.editingApp[key]);
      }
      try {
        const res = await this.$store.dispatch('setting/importApp', data);
        this.$bkMessage({
          theme: 'success',
          message: '导入成功',
        });
        this.$router.push({ name: 'formList', params: { appId: res.data.key } });
      } catch (e) {
        console.warn(e);
      } finally {
        this.appEditPending = false;
      }
    },
  },
};
</script>
<style lang="postcss" scoped>
@import "../../css/scroller.css";
.app-list-page {
  margin: 0 auto;
  padding: 44px 0;
  width: 1216px;
  overflow: auto;
}

.operate-area {
  display: flex;
  justify-content: space-between;
  margin: 0 8px;

  .search-content {
    display: flex;
    align-items: center;
    cursor: pointer;
  }

  .search-input {
    width: 215px;

    /deep/ .bk-form-input {
      border-top-left-radius: 0;
      border-bottom-left-radius: 0;
    }
  }
}

.list-wrapper {
  margin-top: 32px;
  overflow: hidden;

  .app-card-item {
    float: left;
    margin: 0 8px 16px;
  }
}

.no-data {
  padding: 200px 0;
  background: #f5f6fa;
}

/deep/ .bk-dialog-body{
  max-height: 400px;
  overflow: auto;
  @mixin scroller;
}
.app-edit-content {
  .bk-form.bk-form-vertical {
    .bk-form-item:not(:first-of-type) {
      margin-top: 15px;
    }
  }
  .color-wrap {
    display: flex;
  }
  .color-item {
    display: inline-block;
    width: 32px;
    height: 32px;
    margin-right: 12px;
    cursor: pointer;

    &.selected {
      position: relative;

      &:before {
        position: absolute;
        left: 9px;
        top: 10px;
        content: '';
        width: 14px;
        height: 6px;
        border-left: 1px solid #ffffff;
        border-bottom: 1px solid #ffffff;
        transform: rotate(-45deg);
      }
    }
  }
  .prefix-tips {
    font-size: 12px;
    color: #979ba5;
    line-height: 20px;
  }
}
.app-status-filter {
  width: 120px;
  border: 1px solid #c4c6cc;
  border-right: none;
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
  background: #ffffff;
  box-shadow: none;
}

.status-list-content {
  width: 120px;

  .action-item {
    padding: 0 12px;
    height: 32px;
    line-height: 32px;
    color: #63656e;
    cursor: pointer;

    &:hover,
    &.actived {
      background: #f4f6fa;
      color: #3a84ff;
    }

    i {
      width: 12px;
      margin-right: 4px;
    }
  }
}

.export {
  margin-left: 8px;
}
</style>
<style lang="postcss">
.status-popover {
  .bk-tooltip-content {
    background: #ffffff;
  }

  .tippy-tooltip {
    padding: 0;
  }
}
</style>

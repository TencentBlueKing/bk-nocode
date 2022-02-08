import './public-path';
import Vue from 'vue';
import router from './routers/index.js';
import store from './store/index.js';
import './directives/cursor.js';
import '@/utils/login.js';
import App from './App.vue';
import bkMagic from 'bk-magic-vue';
import { bkMessage, bkInfoBox } from 'bk-magic-vue';
import 'bk-magic-vue/dist/bk-magic-vue.min.css';
import '@/css/app.postcss';
import Viewer from 'v-viewer';
import 'viewerjs/dist/viewer.css';
Viewer.setDefaults({
  Options: { zIndexInline: 9999, inline: true, button: true, navbar: true, toolbar: true, tooltip: true, movable: true, zoomable: true, rotatable: true, scalable: true, transition: true, fullscreen: true,  url: 'data-source' },
});
Vue.use(Viewer);
Vue.use(bkMagic);
Vue.prototype.$bkMessage = bkMessage;
Vue.prototype.$bkInfoBox = bkInfoBox;
const ace = require('brace');
Vue.prototype.$ace = ace;
require('brace/mode/javascript');
require('brace/mode/python');
require('brace/mode/json');
require('brace/mode/yaml');
require('brace/theme/monokai');
require('brace/theme/textmate');
require('brace/theme/solarized_dark');
new Vue({
  el: '#app',
  router,
  store,
  render: h => h(App),
});

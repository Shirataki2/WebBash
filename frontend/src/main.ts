import Vue from 'vue'
import './plugins/axios'
import App from './App.vue'
import vuetify from './plugins/vuetify';
import './plugins/codemirror';
import './plugins/visibility';
import './plugins/vueClipboard2';
import router from './router'
import store from './store'
//import './registerServiceWorker'

Vue.config.productionTip = false

new Vue({
  vuetify,
  router,
  store,
  render: h => h(App)
}).$mount('#app')

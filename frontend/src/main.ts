/* eslint-disable */
// @ts-nocheck

// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App.vue'


// import StarRating from 'vue-star-rating'
// Vue.component('vue-star-rating', StarRating)

// import Spinner from 'vue-simple-spinner'

import vue2Dropzone from 'vue2-dropzone'
import './css/vue_dropzone.css'



// Look into https://vuejs.org/v2/guide/mixins.html#Global-Mixin
// for say that api error handling thing

/**
 *
 *  NOTE we only need to import things here
 *  we want to use in multiple components
 *
 *  Router automatically adds paths for other components
 *  and under belief that only loading components that
 *  "need" sub components results in more optimal config.
 *
 */

import file_preview from './components/source_control/file_preview'
Vue.component('file_preview', file_preview)

import file_preview_with_hover_expansion from './components/regular/file_preview_with_hover_expansion'
Vue.component('file_preview_with_hover_expansion', file_preview_with_hover_expansion)

import v_directory_list from './components/source_control/directory_list'
Vue.component('v_directory_list', v_directory_list)

import VueMarkDown from 'vue-markdown'

import upload_large from './components/upload_large'


import router from './router/router'
import user_account_verify_email from './components/user/account/verify_email'
import resend_verify_email from './components/user/account/resend_verify_email'

import task_list from './components/task/task/task_list'

/*
 * ABSTRACT regular methods
 *
 *
 */

import date_picker from './components/regular/date_picker'
Vue.component('date_picker', date_picker)

import job_select from './components/task/job/job_select'
Vue.component('job_select', job_select)

import info_multiple from './components/regular/info_multiple'
Vue.component('v_info_multiple', info_multiple)

import error_multiple from './components/regular/error_multiple'

import tooltip_button from './components/regular/tooltip_button'
Vue.component('tooltip_button', tooltip_button)

import ui_schema from './components/regular/ui_schema_wrapper'
Vue.component('ui_schema', ui_schema)

import button_with_confirm from './components/regular/button_with_confirm'
Vue.component('button_with_confirm', button_with_confirm)

import button_with_menu from './components/regular/button_with_menu'
Vue.component('button_with_menu', button_with_menu)

import text_with_menu from './components/regular/text_with_menu'
Vue.component('text_with_menu', text_with_menu)

import tooltip_icon from './components/regular/tooltip_icon'
Vue.component('tooltip_icon', tooltip_icon)

import diffgram_select from './components/regular/diffgram_select'
Vue.component('diffgram_select', diffgram_select)

import regular_table from './components/regular/regular_table'
Vue.component('regular_table', regular_table)

import regular_chip from './components/regular/regular_chip'
Vue.component('regular_chip', regular_chip)

import bread_crumbs from './components/regular/bread_crumbs'
Vue.component('bread_crumbs', bread_crumbs)

import icon_from_regular_list from './components/regular/icon_from_regular_list.vue'
Vue.component('icon_from_regular_list', icon_from_regular_list)

import connection_select from './components/connection/connection_select'
Vue.component('connection_select', connection_select)

import ahref_seo_optimal from './components/regular/ahref_seo_optimal'
Vue.component('ahref_seo_optimal', ahref_seo_optimal)

/*
 * CONCRETE regular methods
 *
 */


import job_status_select from './components/regular_concrete/job_status_select'
Vue.component('job_status_select', job_status_select)


import member_select from './components/user/member_select'
Vue.component('member_select', member_select)

import member_inline_view from './components/user/member_inline_view.vue';
Vue.component('member_inline_view', member_inline_view)


import user_icon from './components/user/user_icon'

import user_profile_image_edit from './components/user/user_profile_image_edit'
Vue.component('user_profile_image_edit', user_profile_image_edit)

import thumbnail from './components/annotation/thumbnail'
Vue.component('thumbnail', thumbnail)



import store from './store'

import './vue-canvas.js'
//import canvas_zoom_picture_in_picture from './components/vue_canvas/zoom_picture_in_picture'

import is_complete from './components/annotation/actions/is_complete'


import export_view from './components/export/export_home'

//import VueSocketio from 'vue-socket.io';
import project_manager from './components/project/project_manager'
import profile_in_menu from './components/user/profile_in_menu'
import main_menu from './components/main_menu/menu'

import labels_view from './components/annotation/labels_view'
import labels_new from './components/annotation/labels_new'
import labels_edit from './components/annotation/labels_edit'

import { Chrome } from 'vue-color'

import job_cancel from './components/task/job/job_cancel'

import annotation_trainer_menu from './components/annotation/trainer/trainer_menu'
import annotation_trainer_job_info from './components/annotation/trainer/trainer_job_info'

import annotation_core from './components/annotation/annotation_core'

import vue_scroll_to from 'vue-scrollto'
import media_core from './components/annotation/media_core'

import input_view from './components/input/input_view'

import collaborate_new from './components/share/share_new_member'
import collaborate_list_existing from './components/share/share_member_list'

import sequence_list from './components/video/sequence_list'


import user_new_otp from './components/user/one_time_pass/new_otp'

import project_star from './components/project/star'
import user_follow from './components/user/follow'
import user_follow_list from './components/user/follow_list'
import search_query from './components/search/query'
import project_tags from './components/project/tags'


import bar_chart from './components/report/charts/bar_chart'
import line_chart from './components/report/charts/line_chart'

Vue.component('line_chart', line_chart)
Vue.component('bar_chart', bar_chart)

import stats_task from './components/report/stats_task'

import job_info_builder from './components/task/job/job_info_builder'


import guide_new_or_edit from './components/task/guide/guide_new_or_edit'
import guide_list from './components/task/guide/guide_list'

import task_file_select from './components/task/file/file_select'
import task_file_attach from './components/task/file/file_attach'
import credential_type_attach_to_job from './components/task/credential/credential_type_attach_to_job'
import credential_list from './components/task/credential/credential_list'
import credential_type_new_or_edit from './components/task/credential/credential_type_new_or_edit'

import video from './components/video/video'

import VueQriously from 'vue-qriously'
Vue.use(VueQriously)

Vue.config.productionTip = false

// This is the "Full" install as we bring in vuetify
// and the full css file
// and pass the options straight in.

import Vuetify from 'vuetify'
import '@mdi/font/css/materialdesignicons.css'
import './css/vuetify-v2.4.7.min.css'
import './css/custom_changes.css'
import './css/mxgraph.css'

// Note this options are passed to our vue instance
// as part of the new Vuetify object, (instead of at the first
// Vue.use()
// TODO clarify why we need both Vue.use() and to pass as an option
// this is from migration guide
// https://vuetifyjs.com/en/getting-started/releases-and-migrations
// new install has a different suggestion but that seems to be for
// something different?

// https://vuetifyjs.com/en/features/theme/#customizing

const vuetify_options = {
  icons : {
    iconfont: 'mdi'
  },
  theme: {
    themes: {
      light: {
        primary: '#1e1e1e',
        secondary: '#1565c0'  // blue https://material.io/resources/color/#!/?view.left=0&view.right=0&primary.color=0D47A1
      }
    }
  }
}

Vue.use(Vuetify)


Vue.use(vue_scroll_to)

import VueMoment from 'vue-moment'
import moment from 'moment-timezone'
Vue.use(VueMoment, {
    moment,
})

Vue.component('v_task_list', task_list)
Vue.component('v_job_cancel', job_cancel)

Vue.component('v_job_info_builder', job_info_builder)

Vue.component('v_stats_task', stats_task)

Vue.component('v_error_multiple', error_multiple)

Vue.component('VueMarkDown', VueMarkDown)

Vue.component('slider-picker', Chrome) //https://github.com/xiaokaike/vue-color

Vue.component('vue-dropzone', vue2Dropzone)

Vue.component('v_upload_large', upload_large)

Vue.component('v_is_complete', is_complete)

Vue.component('v_resend_verify_email', resend_verify_email)
Vue.component('v_user_account_verify_email', user_account_verify_email)
Vue.component('v_user_icon', user_icon)


Vue.component('project-manager', project_manager)
Vue.component('v_profile_in_menu', profile_in_menu)
Vue.component('main_menu', main_menu)

Vue.component('v_labels_view', labels_view)
Vue.component('v_labels_new', labels_new)
Vue.component('v_labels_edit', labels_edit)

Vue.component('v_media_core', media_core)
Vue.component('v_input_view', input_view)

Vue.component('v_annotation_trainer_job_info', annotation_trainer_job_info)
Vue.component('v_annotation_trainer_menu', annotation_trainer_menu)
Vue.component('v_annotation_core', annotation_core)


Vue.component('v_collaborate_new', collaborate_new)
Vue.component('v_collaborate_list_existing', collaborate_list_existing)

Vue.component('v_sequence_list', sequence_list)

Vue.component('v_user_new_otp', user_new_otp)


Vue.component('v_video', video)
Vue.component('v_project_star', project_star)
Vue.component('v_user_follow', user_follow)
Vue.component('v_user_follow_list', user_follow_list)

Vue.component('v_search_query', search_query)
Vue.component('v_project_tags', project_tags)

Vue.component('v_export_view', export_view)

Vue.component('v_guide_new_or_edit', guide_new_or_edit)
Vue.component('v_guide_list', guide_list)

Vue.component('v_task_file_select', task_file_select)
Vue.component('v_task_file_attach', task_file_attach)
Vue.component('v_credential_type_attach_to_job', credential_type_attach_to_job)
Vue.component('v_credential_list', credential_list)
Vue.component('v_credential_type_new_or_edit', credential_type_new_or_edit)


import { route_errors } from './components/regular/regular_error_handling'
import { format_money } from './components/regular/regular'
Vue.prototype.$format_money = format_money


Vue.prototype.$route_api_errors = route_errors


import { get_sequence_color } from './components/regular/regular_annotation'
Vue.prototype.$get_sequence_color = get_sequence_color


import {addQueriesToLocation} from './components/regular/regular'
Vue.prototype.$addQueriesToLocation = addQueriesToLocation




// import {google_cloud_storage_searchbar} from './components/connectors/google_cloud_storage_searchbar.vue'
// Vue.component('google_cloud_storage_searchbar', google_cloud_storage_searchbar)

// var VueApp: any = Vue;
// this was a work around because typescript

const app = new Vue({
  el: '#app',
  vuetify: new Vuetify(vuetify_options),
  store,
  router,
  components: { App },
  template: '<App/>',
  directives: {
  }
})

if (window.Cypress) {
  // only available during E2E tests
  window.app = app
}

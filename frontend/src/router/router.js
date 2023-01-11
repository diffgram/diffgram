import Vue from 'vue'
import Router from 'vue-router'

const routerOptions = [
  {
    path: '/order/premium',
    component: 'account/billing/order_premium'
  },
  {
    path: '/order/success',
    component: 'account/billing/order_success'
  },
  {
    path: '/policies',
    component: 'company/policies',
    meta: {external_page: true}
  },
  {
    path: '/admin',
    component: 'diffgram/admin_home',
    meta: {requiresAuth: true}
  },
  {
    path: '/admin/install/info',
    component: 'diffgram/admin_install_info',
    meta: {requiresAuth: true}
  },
  {
    path: '/admin/mock',
    component: 'diffgram/admin_mock_data',
    meta: {requiresAuth: true}
  },
  {
    path: '/admin/account/overview',
    component: 'diffgram/account_admin',
    meta: {requiresAuth: true}
  },
  {
    path: '/me',
    component: 'user/home/annotator_dashboard',
    meta: {
      requiresAuth: true,
      title: "My Home"
    }
  },
  {
    path: '/projects',
    component: 'project/project_manager',
    meta: {
      requiresAuth: true,
      hide_default_menu: true,
      title: "Projects"
    }
  },
  {
    path: '/white_label_customization/edit',
    component: 'ui_schema/edit_overview_page',
    meta: {
      requiresAuth: true,
      hide_default_menu: false
    }
  },
  {
    path: '/file/:file_id_prop',
    component: 'annotation/annotation_ui_factory',
    props: true,
    meta: {
      requiresAuth: true,
      hide_default_menu: true
    }
  },
  {
    path: '/userscript',
    component: 'annotation/image_and_video_annotation/userscript/userscript',
    props: true,
    meta: {
      requiresAuth: true,
    }
  },

  {
    path: '/project/:project_string_id/events',
    alias: ['/project/:project_string_id/event/list'],
    component: 'event/event_list',
    props: true,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/task/wait',
    component: 'real_time/waiting_screen',
    props: true,
    meta: {
      requiresAuth: true
    },
    name: "task_waiting"
  },
  {
    path: '/task/:task_id_prop',
    component: 'annotation/annotation_ui_factory',
    props: true,
    meta: (route) => ({
      requiresAuth: true,
      hide_default_menu: true,
      title: "#" + route.params.task_id_prop
    }),
    name: "task_annotation"
  },
  {
    path: '/task/:task_id_prop/diff/:task_mode_data',
    component: 'task/task/task_annotation_diff',
    props: true,
    meta: {requiresAuth: true}
  },

  // must come before flow id one (otherwise it will try
  // to pass it as prop
  {
    path: '/project/:project_string_id/workflow/list',
    component: 'action/workflow_list',
    props: true,
    meta: {requiresAuth: true}
  },

  {
    // :flow_id is optional?
    path: '/project/:project_string_id/flow/:flow_id?',
    component: 'action/action_flow',
    props: true,
    meta: {requiresAuth: true}
  },
  {
    // :flow_id is optional?
    path: '/project/:project_string_id/workflow/:workflow_id?',
    component: 'action/workflow_builder',
    props: true,
    meta: {requiresAuth: true}
  },
  {
    // WIP
    path: '/project/:project_string_id/attributes',
    component: 'attribute/attribute_home',
    props: true,
    meta: {requiresAuth: true}
  },
  {
    path: '/project/:project_string_id/labels',
    component: 'labels_schema/labels_page',
    props: (route) => ({
      // why do we need this "override" again?
      project_string_id: route.params.project_string_id
    }),
    meta: (route) => ({
      requiresAuth: true,
      title: "Schema " + route.params.project_string_id
    }),
    name: 'labels'
  },

  {
    path: '/project/:project_string_id/workflow/:workflow_id/run/:workflow_run_id',
    component: 'action/action_event_list',
    props: true,
    meta: {requiresAuth: true}
  },
  {
    path: '/org/:org_id/settings',
    component: 'org/org_settings',
    props: true,
    meta: {requiresAuth: true}
  },
  {
    path: '/org/new',
    component: 'org/org_new',
    props: true,
    meta: {requiresAuth: true}
  },
  {
    path: '/org/invite',
    component: 'org/org_invite_members',
    props: true,
    meta: {requiresAuth: true}
  },
  {
    path: '/org/trainer/invite_existing_client',
    component: 'org/org_trainer_invite_existing_client',
    props: true,
    meta: {requiresAuth: true}
  },
  {
    path: '/status',
    component: 'status',
    props: true,
    meta: {requiresAuth: true}
  },

  {
    path: '/studio/annotate/:project_string_id',
    alias: ['/project/:project_string_id'],
    component: 'annotation/annotation_ui_factory',
    props: true,
    meta: (route) => ({
      requiresAuth: true,
      available_on_public_project: true,
      hide_default_menu: true,
      title: "Studio " + route.params.project_string_id
    }),
    name: 'studio'
  },
  {
    path: '/studio/annotate/:project_string_id/explorer',
    alias: ['/project/:project_string_id'],
    component: 'annotation/annotation_ui_factory',
    props: (route) => ({
      show_explorer_full_screen: true,
      project_string_id: route.params.project_string_id
    }),
    meta: {
      requiresAuth: true,
      available_on_public_project: true,
      hide_default_menu: true,

    },
    name: 'studio'
  },
  {
    path: '/project/:project_string_id/settings',
    component: 'project/settings',
    props: true, meta: {requiresAuth: true},
    name: 'settings'
  },
  {
    path: '/job/:job_id/annotate/',
    component: 'annotation/image_and_video_annotation/trainer/trainer_annotation',
    props: true,
    meta: {
      requiresAuth: true,
      hide_default_menu: true
    },
    name: "job_annotation"
  },
  {
    path: '/discussion/:discussion_id/',
    component: 'discussions/discussion_detail',
    props: (route) => ({
      discussion_id: route.params.discussion_id
    }),
    meta: {
      requiresAuth: true,
      hide_default_menu: true
    },
    name: "discussion_detail"
  },

  {
    path: '/discussions/',
    component: 'discussions/project_discussions',
    props: (route) => ({

    }),
    meta: {
      requiresAuth: true,
      hide_default_menu: true
    },
    name: "project_discussions"
  },
  {
    path: '/discussions/create',
    component: 'discussions/create_discussion',
    props: (route) => ({

    }),
    meta: {
      requiresAuth: true,
      hide_default_menu: true
    },
    name: "create_discussion"
  },
  {
    path: '/job/:task_template_id/discussion/:discussion_id/',
    component: 'discussions/discussion_detail',
    props: (route) => ({
      discussion_id: route.params.discussion_id,
      task_template_id: route.params.task_template_id
    }),
    meta: {
      requiresAuth: true,
      hide_default_menu: true
    },
    name: "discussion_detail_from_job"
  },
  {
    path: '/job/:job_id/start/',
    component: 'task/job/job_start',
    props: true,
    meta: {requiresAuth: true}
  },
  {
    path: '/job/:job_id/exam/results',
    component: 'task/job/exam_results',
    props: true,
    meta: {requiresAuth: true}
  },

  {
    path: '/project/:project_string_id/annotation_project/new',
    component: 'annotation/image_and_video_annotation/annotation_project_create',
    props: true, meta: {requiresAuth: true}
  },

  // 2 different job new, one has project ...
  {
    path: '/job/new-legacy/:job_id_route',
    component: 'task/job/job_new',
    props: true,
    meta: {
      requiresAuth: true,
      hide_default_menu: true
    }
  },
  {
    path: '/project/:project_string_id_route/job/new/:job_id_route',
    component: 'task/job/task_template_wizard_creation/task_template_new',
    props: true,
    meta: {
      requiresAuth: true,
      hide_default_menu: true
    }
  },
  {
    path: '/project/:project_string_id/exam/new/',
    component: 'exam/exam_new',
    props: true,
    meta: {
      requiresAuth: true,
      hide_default_menu: true
    }
  },
  {
    path: '/project/:project_string_id/exam/new/:exam_id_route',
    component: 'exam/exam_new',
    props: true,
    meta: {
      requiresAuth: true,
      hide_default_menu: true
    }
  },
  {
    path: '/project/:project_string_id_route/job/new-legacy',
    component: 'task/job/job_new',
    props: true,
    meta: {
      requiresAuth: true,
      hide_default_menu: true
    }
  },
  {
    path: '/project/:project_string_id_route/job/new',
    component: 'task/job/task_template_wizard_creation/task_template_new',
    props: true,
    meta: {
      requiresAuth: true,
      hide_default_menu: true,
      title: "New Tasks"
    }
  },
  {
    path: '/project/:project_string_id/task/guide/new',
    component: 'task/guide/guide_new',
    props: true,
    meta: {requiresAuth: true}
  },
  {
    path: '/welcome',
    component: 'welcome_builder',
    meta: {requiresAuth: true}
  },
  {
    path: '/welcome/social',
    component: 'welcome_social',
    meta: {requiresAuth: true}
  },
  {
    path: '/welcome/verify',
    component: 'welcome_email_verify',
    meta: {requiresAuth: true}
  },
  {
    path: '/welcome/adventure',
    component: 'welcome_choose_your_adventure',
    meta: {requiresAuth: true}
  },
  {
    path: '/project/:project_string_id/guide/list',
    component: 'task/guide/guide_list',
    props: true,
    meta: {requiresAuth: true}
  },
  {
    path: '/job/list',
    component: 'task/job/job_list',
    alias: ['/jobs/list'],
    props: false,
    meta: {
      requiresAuth: true,
      hide_default_menu: true,
      title: "Tasks"
    }
  },
  {
    path: '/job/launches',
    component: 'task/job/job_launches_list',
    alias: ['/jobs/launches'],
    props: false,
    meta: {
      requiresAuth: true,
      hide_default_menu: true,
      title: "Launch Events"
    }
  },
  {
    path: '/sync-events/list',
    component: 'sync_events/sync_events_list',
    props: false,
    meta: {
      requiresAuth: true,
      hide_default_menu: true,
      title: "Pipeline Events"
    }
  },
  {
    path: '/credential/list',
    component: 'task/credential/credential_list_page',
    alias: ['/credentials/list'],
    props: false,
    meta: {requiresAuth: true}
  },
  {
    path: '/job/:job_id/discussions',
    component: 'task/job/job_detail',
    props: true,
    meta: {requiresAuth: true},
    name: "job_detail_discussions"
  },

  {
    path: '/job/:job_id',
    component: 'task/job/job_detail',
    props: true,
    meta: (route) => ({
      requiresAuth: true,
      title: "Job #" + route.params.job_id
    }),
    name: "job_detail"
  },
  {
    path: '/:project_string_id/examination/:examination_id',
    component: 'exam/examination_detail',
    props: true,
    meta: (route) => ({
      requiresAuth: true,
      title: "Examination#" + route.params.exam_id
    }),
    name: "examination_detail"
  },
  {
    path: '/:project_string_id/exam/:exam_id',
    component: 'exam/exam_template_detail',
    props: true,
    meta: (route) => ({
      requiresAuth: true,
      title: "Exam#" + route.params.exam_id
    }),
    name: "exam_template_detail"
  },
  {
    path: '/credential/new',
    component: 'task/credential/credential_type_new_or_edit',
    props: true,
    meta: {requiresAuth: true}
  },
  {
    path: '/',
    component: 'user/home/dashboard',
    alias: ['/home/dashboard'],
    props: false,
    meta: {
      requiresAuth: true,
      title: "Dashboard"
      }
  },
  {
    path: '/user/new',
    alias: ['/user/data_platform/new'],
    component: 'user/account/user_data_platform_new',
    props: false,
    meta: {
      requiresAuth: false,
      title: "Signup Now",
      hide_default_menu: true,
    }
  },


  {
    path: '/user/builder/signup',
    component: 'user/builder/builder_signup',
    props: false,
    meta: {
      requiresAuth: true,
      title: "Signup Now"
    }
  },

  // This should come before connection single because otherwise "list" matches
  // connection
  {
    path: '/connection/list',
    alias: ['/connections/list'],  // plural
    component: 'connection/connection_list',
    meta: (route) => ({
      requiresAuth: true,
      hide_default_menu: true,
      title: "Connections"
    })
  },
  /*
   */
  {
    path: '/connection/:connection_id',
    alias: ['/connections/:connection_id'],    // plural
    props: true,
    component: 'connection/connection_page',
    meta: {
      requiresAuth: true,
      hide_default_menu: true,
      title: "Connection"
    }
  },

  // REPORT
  // This should come before report single
  // because otherwise "list" matches the single report
  {
    path: '/report/list',
    alias: ['/reports/list'],  // plural
    component: 'report/report_list',
    meta: {
      requiresAuth: true,
      hide_default_menu: true,
      title: "Report List"
    }
  },
  /*
   * Could also have alias or options that jump to a project
   * Question, do we want this to declare template
   * ie report/template/...
   */
  {
    // WIP
    path: '/report/:report_template_id',
    alias: ['/reports/:report_template_id'],    // plural
    // maybe plural should go to report list
    props: true,
    component: 'report/report',
    meta: {
      requiresAuth: true,
      hide_default_menu: true,
      title: "Report"
    }
  },


  {
    path: '/search',
    component: 'search/search'
  },
  {
    path: '/studio/upload/:project_string_id',
    component: 'upload_large',
    props: true,
    meta: {
      requiresAuth: true,
      title: "Import"
    }
  },
  {
    path: '/review/ai/new/:string_ai_id', component: 'review_ai', props: true,
    meta: {requiresAuth: true}
  },
  {
    path: '/user/login/:magic_auth?',
    component: 'user/login',
    props: true,
    meta: (route) => ({
      title: "Login"
    })
  },
  {
    path: '/user/oauth2-login/',
    component: 'user/login_oauth2_redirect',
    props: true,
    meta: (route) => ({
      title: "Login"
    })
  },
  {
    path: '/user/logout/',
    component: 'user/logout',
    props: true,
    meta: (route) => ({
      title: "Login"
    })
  },
  {
    path: '/user/account/password/set',
    component: 'user/account/user_password',
    meta: {requiresAuth: true}
  },
  {
    path: '/user/account/verify_email/:email?/:auth_code?',
    component: 'user/account/verify_email',
    alias: ['/user/verify'],
    props: true,
    meta: {requiresAuth: false}
  },
  {
    path: '/user/edit/2fa',
    component: 'user/one_time_pass/otp',
    meta: {
      requiresAuth: true,
      title: "Edit 2FA"
    }
  },
  {
    path: '/user/edit',
    component: 'user/edit',
    meta: {
      requiresAuth: true,
      title: "Edit self"
      }
  },
  {
    path: '/a/project/new',
    component: 'project/project_new_wizard',
    meta: {
      requiresAuth: true,
      title: "New Project"
    }
  },
  {
    path: '/project/:project_string_id/migrate',
    component: 'project/project_migrator_wizard',
    props: true,
    meta: {
      requiresAuth: true,
      title: "Migrate Project"
    }
  },
  {
    path: '/project/:project_string_id/project-migrations',
    component: 'project/project_migrations_list',
    props: true,
    meta: {
      requiresAuth: true,
      title: "Project Migrations"
    }
  },
  {
    path: '/project/:project_string_id/export',
    component: 'export/export_home',
    props: true,
    meta: {
      requiresAuth: true,
      title: "Export"
    }
  },

  {
    path: '*',
    component: 'other/NotFound',
    meta: {
      requiresAuth: false,
      title: "404 Not Found"
    }
  }
]

import store from '../store'
import axios from "../services/customInstance";
const fetch_public_project = async function(project_string_id){
  try{
    const response = await axios.get(`/api/project/${project_string_id}/view`);
    if(response.status === 200){
      return response.data.project
    }
    return false;

  }
  catch (error) {
    console.error(error)
  }
  return false;
}

const try_load_public_project = async function(available_on_public_project){

  if(available_on_public_project == true){
    const project_string_id = to.params.project_string_id;
    const project = await fetch_public_project(project_string_id);
    if(project){
      // If project exists, this is a public project and we can see it
      store.commit('set_current_public_project', project);
      return true
    }
    return false
  }
  return false
}

const get_meta = function(route){
  if (typeof(route.meta) === 'function') {
    return route.meta(route)
  } else {
    return route.meta
  }
}



const routes = routerOptions.map(route => {
  return {
    ...route,
    component: () => import(`@/components/${route.component}.vue`)
  }
})


Vue.use(Router)

const router = new Router({
  routes,
  mode: 'history'
})

router.beforeEach((to, from, next) => {

  const meta = get_meta(to)

  // No Auth Required
  if (!meta.requiresAuth) {
    return next()
  }

  // User is logged in already
  if (store.state.user.logged_in == true) {
    return next()
  }

  // If user is not logged in
  const loaded_valid_public_project = try_load_public_project(meta.available_on_public_project)
  if (loaded_valid_public_project == true) {
    return next()
  } else {
    // redirect
    return next({
      path: '/user/login',
      query: {redirect: to.fullPath}
    })
  }

})

const DEFAULT_TITLE = 'Diffgram';
router.afterEach((to, from) => {
    // Use next tick to handle router history correctly
    // see: https://github.com/vuejs/vue-router/issues/914#issuecomment-384477609
    Vue.nextTick(() => {
        const meta = get_meta(to)
        document.title = meta.title || DEFAULT_TITLE;
    });
});

export default router;



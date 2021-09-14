import Vue from 'vue'
import Router from 'vue-router'

const routerOptions = [
  {
    path: '/admin/account/overview',
    component: 'diffgram/account_admin',
    meta: {requiresAuth: true}
  },
  {
    path: '/projects',
    component: 'project/project_manager',
    meta: {
      requiresAuth: true,
      hide_default_menu: true
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
    component: 'annotation/userscript/userscript',
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
    meta: {
      requiresAuth: true,
      hide_default_menu: true
    },
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
    path: '/project/:project_string_id/flow/list',
    component: 'action/action_flow_list',
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
    // WIP
    path: '/project/:project_string_id/attributes',
    component: 'attribute/attribute_home',
    props: true,
    meta: {requiresAuth: true}
  },
  {
    path: '/project/:project_string_id/labels',
    component: 'annotation/labels_page',
    props: (route) => ({
      // why do we need this "override" again?
      project_string_id: route.params.project_string_id
    }),
    meta: {requiresAuth: true},
    name: 'labels'
  },

  {
    path: '/project/:project_string_id/flow/:flow_id/event/:flow_event_id',
    component: 'action/action_event_list',
    props: true,
    meta: {requiresAuth: true}
  },

  {
    path: '/join',
    component: 'hiring/hiring_home',
    props: true,
    meta: {requiresAuth: false}
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
    path: '/hiring/application/new',
    component: 'hiring/application_new',
    props: true,
    meta: {requiresAuth: true}
  },
  /*
   * Feb 13, 2020
   *  May prefer the alias to go to dashboard
   *  but would need update how we handle changing
   *  values (ie that it changes
   *  the project from the URL)
   *
   */
  {
    path: '/studio/annotate/:project_string_id',
    alias: ['/project/:project_string_id'],
    component: 'annotation/annotation_ui_factory',
    props: true, meta: {
      requiresAuth: true,
      available_on_public_project: true,
      hide_default_menu: true
    },
    name: 'studio'
  },
  {
    path: '/studio/annotate/:project_string_id/explorer',
    alias: ['/project/:project_string_id'],
    component: 'annotation/annotation_ui_factory',
    props: (route) => ({
      show_explorer_full_screen: true
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
    component: 'annotation/trainer/trainer_annotation',
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
    path: '/project/:project_string_id/ml/home/',
    component: 'machine_learning/home',
    props: true, meta: {requiresAuth: true}
  },
  {
    path: '/project/:project_string_id/version/:version_id/view/',
    component: 'machine_learning/view_version',
    props: true, meta: {requiresAuth: true}
  },
  {
    path: '/project/:project_string_id/ml/new/:video_id?',
    component: 'machine_learning/new',
    props: true, meta: {requiresAuth: true}
  },
  {
    path: '/project/:project_string_id/annotation_project/new',
    component: 'annotation/annotation_project_create',
    props: true, meta: {requiresAuth: true}
  },

  // 2 different job new, one has project ...
  {
    path: '/job/new/:job_id_route',
    component: 'task/job/job_new',
    props: true,
    meta: {
      requiresAuth: true,
      hide_default_menu: true
    }
  },
  {
    path: '/project/:project_string_id_route/job/new',
    component: 'task/job/job_new',
    props: true,
    meta: {
      requiresAuth: true,
      hide_default_menu: true
    }
  },
  {
    path: '/project/:project_string_id/task/guide/new',
    component: 'task/guide/guide_new',
    props: true,
    meta: {requiresAuth: true}
  },
  {
    path: '/welcome/builder',
    component: 'annotation/welcome_builder',
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
      hide_default_menu: true
    }
  },
  {
    path: '/job/launches',
    component: 'task/job/job_launches_list',
    alias: ['/jobs/launches'],
    props: false,
    meta: {
      requiresAuth: true,
      hide_default_menu: true
    }
  },
  {
    path: '/sync-events/list',
    component: 'sync_events/sync_events_list',
    props: false,
    meta: {
      requiresAuth: true,
      hide_default_menu: true
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
    meta: {requiresAuth: true},
    name: "job_detail"
  },
  {
    path: '/credential/new',
    component: 'task/credential/credential_type_new_or_edit',
    props: true,
    meta: {requiresAuth: true}
  },
  {
    path: '/home/dashboard',
    component: 'user/home/dashboard',
    props: false,
    meta: {requiresAuth: true}
  },
  {
    path: '/software',
    component: 'marketing/software_marketing_unbounce',
    props: false,
    meta: {requiresAuth: false}
  },
  {
    path: '/data_platform',
    component: 'marketing/data_platform_signup_marketing_unbounce',
    props: false,
    meta: {requiresAuth: false}
  },
  {
    path: '/pro',
    alias: ['/pros'],
    component: 'marketing/pro_signup_marketing_unbounce',
    props: false,
    meta: {requiresAuth: false}
  },

  {
    path: '/user/new',
    component: 'user/account/user_data_platform_new',
    props: false,
    meta: {requiresAuth: false }
  },


  {
    path: '/user/builder/signup',
    component: 'user/builder/builder_signup',
    props: false,
    meta: {requiresAuth: true}
  },

  // This should come before connection single because otherwise "list" matches
  // connection
  {
    path: '/connection/list',
    alias: ['/connections/list'],  // plural
    component: 'connection/connection_list',
    meta: {
      requiresAuth: true,
      hide_default_menu: true
    }
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
      hide_default_menu: true
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
      hide_default_menu: true
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
      hide_default_menu: true
    }
  },


  {
    path: '/search',
    component: 'search/search'
  },
  {
    path: '/studio/upload/:project_string_id',
    component: 'upload_large', props: true
  },
  {
    path: '/review/ai/new/:string_ai_id', component: 'review_ai', props: true,
    meta: {requiresAuth: true}
  },
  {
    path: '/user/login/:magic_auth?',
    component: 'user/login',
    props: true
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
    meta: {requiresAuth: true}
  },
  {
    path: '/user/edit',
    component: 'user/edit',
    meta: {requiresAuth: true}
  },
  {
    path: '/a/project/new',
    component: 'project/project_new',
    meta: {requiresAuth: true}
  },
  {
    path: '/project/:project_string_id/export',
    component: 'export/export_home',
    props: true,
    meta: {requiresAuth: true}
  },
  {
    path: '/',
    component: 'user/home/dashboard',
    props: false,
    meta: {requiresAuth: true}
  },
  {
    path: '*',
    component: 'other/NotFound'
  }
]

import store from '../store'
import axios from "axios";
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
const routes = routerOptions.map(route => {
  return {
    ...route,
    component: () => import(`@/components/${route.component}.vue`),
    beforeEnter: async (to, from, next) => {

      if (to.matched.some(record => record.meta.requiresAuth)) {
        // this route requires auth, check if logged in
        // if not, redirect to login page.

        if (store.state.user.logged_in !== true) {

          // Test if the route can be accessed on a public project
          if(to.matched.some(record => record.meta.available_on_public_project)){
            const project_string_id = to.params.project_string_id;
            const project = await fetch_public_project(project_string_id);
            if(project){
              // If project exists, this is a public project and we can see it
              store.commit('set_current_public_project', project);
              next();
            }
            else{
              // Otherwise redirect to login
              next({
                path: '/user/login',
                query: {redirect: to.fullPath}
              })
            }
          }
          else{
            next({
              path: '/user/login',
              query: {redirect: to.fullPath}
            })
          }
        }
        else {
          next()
        }
      }



        else {
        next() // make sure to always call next()!
      }
    }

  }
})


Vue.use(Router)

export default new Router({
  routes,
  mode: 'history'
})






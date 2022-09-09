import Router from 'vue-router'
import {Store} from 'vuex'

type AuthData = {
  type: string;
  user_permission_level: string;
};
export const auth_redirect = (auth: AuthData, project_string_id: string, router: Router, store: Store<any>) => {
  // TODO review more general use for this, as may be builder or trainer...
  if (auth) {
    if (auth.type == "invite_to_org") {

      if (["Admin"].includes(auth.user_permission_level)) {

        router.push('/user/builder/signup');
      }

      if (auth.user_permission_level == "Annotator") {

        router.push('/user/trainer/signup');
      }
    }
    if (auth.type == "add_to_project") {
      //this.$router.push('/studio/annotate/' + response.data.project_string_id);
      if (project_string_id) {
        router.push(`/user/builder/signup?project_string_id=${project_string_id}&role=${auth.user_permission_level}`);
      } else {
        router.push(`/user/builder/signup?role=${auth.user_permission_level}`);
      }


    }

    return
  }

  if (project_string_id == null) {
    router.push('/user/builder/signup');
  } else {
    router.push('/project/' + project_string_id);
    store.commit('set_project_string_id', project_string_id)
  }
}

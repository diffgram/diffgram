
/* expects to user regular error component
 * ie when calling it
 *
 *
 *

this.error = this.$route_api_errors(error)


This handles parsing a high level error object into the expected form
from a regular log.
Especially has Null checks, and handles Non-400 type codes like 403

No longer need to import available globally under this.$route_api_errors()

Guide

(in API call)
1) reset error
this.error = {}

2) do api call
3) run regular error and pass the result to this.error

.catch(error => {
      this.error = this.$route_api_errors(error)
    })

(in HTML)
4) Add component

<v_error_multiple :error="error">
</v_error_multiple>

in data() in JS
5)
 error: {},


 *
 *
**/
import store from '../../store';
export function route_errors (error) {
  console.log('AAAAA', error);
  if(error && error.message && error.message === 'Network Error'){
    store.commit('set_connection_error', error);
    return {
      'network_error': 'Please check your internet connection and that Diffgram services are up.',
      'message': 'Contact us if the error persists.'
    }

  }
  if (error && error.response) {

    if (error.response.status == 400) {
      if (error.response.data.log) {
        return error.response.data.log.error
      }
      else
        return { "Please try again later." : "[Technical] .log could not be found."}
    }

    if (error.response.status == 403) {
        /* replace dict
          * if just do key doesn't seem to actually work
          * unless key already happens to exist
          * prob applies to rate limit thing too
          */
      return {
          permission: "Invalid Permission.",
          project_check: "Are you in the correct project?"
        }

      /* Project check, ie in context
       * of a user being in project A when say a job is in project B
       * Assuming it's accidently helps a user perhaps get back
       * to where they want to be.
       */

    }

    if (error.response.status == 429) {

     return { rate_limit : "Too many requests, please try again later."}

    }

    if (error.response.status == 405) {

     return { method_not_allowed : "Please Try Again Later (405, Method Not Allowed)"}

    }

    if (error.response.status == 500) {

      let result = { server : "Please try again later. Contact us if this persists."}
      if (error.response.data) {
        result = {
          ...error.response.data,
          ...result
        }
      }
      return result
    }
  }
}

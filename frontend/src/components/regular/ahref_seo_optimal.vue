
<template>

  <a  :href="href"
      :target="target"
      @click="go_to_url_from_href_seo_workaround($event, href)"
      style="text-decoration: none;"
      >
    <slot> </slot>
  </a>

</template>

<script lang="ts">

/* Usage example
 *
* <ahref_seo_optimal href="/software">
 *
    <v-btn>
      Diffgram Software
    </v-btn>

  </ahref_seo_optimal>

Cautions
1) do not have an extra click inside the slot.
eg the btn element here has no @click handler (ahref_seo_optimal component handles it)

 *
 * WHY:
 * 1) Becuase need SEO as described in go_to_url_from_href_seo_workaround()
 * 2) It's annoying and error prone to have to have both the @click and href for each link (plus the decorator to hide blue default line)
 * 3) We may keep adjusting this in the future as we learn more SEO for javascript stuff
 *
 *
 * This has extra benefit that now you can right click open link in new tab for buttons
 *
 * Uses slow by default becuase we may use things other then buttons for links
 */

import Vue from "vue";

export default Vue.extend( {
  name: 'ahref_seo_optimal',
  props: {
    'href': {
        type: String
     },
    'target': {
        type: String,
        default: '_self'
     }
  },
  data() {
    return {
    }
  },
  methods: {
    go_to_url_from_href_seo_workaround(event, url) {
      // inspired by https://developers.google.com/search/docs/guides/javascript-seo-basics#use-history-api
      // essentially we want to maintain value of single page app (not whole page load)
      // but google HAS to have both the <a> tag and the href
      // so we prevent default (from the href)

      if (this.target != '_self'){ return } // eg '_blank' we want default opening in new tab

      event.preventDefault();
      this.$router.push(url)
    }
  }

}

) </script>

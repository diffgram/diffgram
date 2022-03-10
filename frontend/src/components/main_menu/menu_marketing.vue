<template>
<div>

  <v-layout>

<!--    <v-menu v-model="why_menu"-->
<!--          offset-y-->
<!--          open-on-hover-->
<!--          attach-->
<!--          >-->

<!--      <template v-slot:activator="{ on }">-->
<!--        <v-btn v-on="on"-->
<!--               color="primary"-->
<!--                text-->
<!--               style="text-transform: none !important;"-->
<!--               >-->
<!--           Product-->
<!--        </v-btn>-->
<!--      </template>-->

<!--      <v-card>-->
<!--        <v-layout column>-->

<!--          <v-flex>-->
<!--            <ahref_seo_optimal href="https://diffgram.com/main/about">-->
<!--              <v-btn color="primary"-->
<!--                     text-->
<!--                     style="text-transform: none !important;"-->
<!--                     >-->
<!--                <v-icon left> mdi-compass-rose</v-icon>-->
<!--                Our Why-->
<!--              </v-btn>-->
<!--            </ahref_seo_optimal>-->
<!--          </v-flex>-->

<!--          <v-flex>-->

<!--            <ahref_seo_optimal href="https://diffgram.com/main/product">-->
<!--              <v-btn color="primary"-->
<!--                     text style="text-transform: none !important;">-->
<!--                <v-icon left> mdi-fast-forward</v-icon>-->
<!--                Product Overview-->
<!--              </v-btn>-->
<!--            </ahref_seo_optimal>-->

<!--          </v-flex>-->


<!--          <v-flex>-->

<!--            <ahref_seo_optimal href="https://diffgram.com/main/3d-lidar">-->
<!--              <v-btn color="primary"-->
<!--                     text style="text-transform: none !important;">-->
<!--                <v-icon left> mdi-circle-slice-8</v-icon>-->
<!--                3D-->
<!--              </v-btn>-->
<!--            </ahref_seo_optimal>-->

<!--          </v-flex>-->


<!--          <v-flex>-->

<!--            <ahref_seo_optimal href="https://diffgram.com/main/image">-->
<!--              <v-btn color="primary"-->
<!--                     text style="text-transform: none !important;">-->
<!--                <v-icon left> mdi-github</v-icon>-->
<!--                 Image-->
<!--              </v-btn>-->
<!--            </ahref_seo_optimal>-->

<!--          </v-flex>-->

<!--          <v-flex>-->

<!--            <ahref_seo_optimal href="https://diffgram.com/main/video">-->
<!--              <v-btn color="primary"-->
<!--                     text style="text-transform: none !important;">-->
<!--                <v-icon left> mdi-face-agent</v-icon>-->
<!--                 Video-->
<!--              </v-btn>-->
<!--            </ahref_seo_optimal>-->

<!--          </v-flex>-->

<!--        </v-layout>-->
<!--      </v-card>-->
<!--    </v-menu>-->



<!--    <v-menu v-model="product"-->
<!--            offset-y-->
<!--            open-on-hover-->
<!--            attach-->
<!--            >-->


<!--      <template v-slot:activator="{ on }">-->
<!--        <v-btn v-on="on"-->
<!--               color="primary"-->
<!--              text style="text-transform: none !important;">-->
<!--           Resources-->
<!--        </v-btn>-->
<!--      </template>-->

<!--      <v-card>-->

<!--        <v-layout column>-->


<!--          <v-flex>-->

<!--            <ahref_seo_optimal href="https://diffgram.readme.io/docs" target="_blank">-->
<!--              <v-btn color="primary"-->
<!--                    text style="text-transform: none !important;">-->
<!--                <v-icon left> mdi-image-filter-hdr</v-icon>-->
<!--                Docs-->
<!--              </v-btn>-->
<!--            </ahref_seo_optimal>-->

<!--          </v-flex>-->

<!--          <v-flex>-->

<!--            <ahref_seo_optimal href="https://www.youtube.com/channel/UC4ZVmvMA6oa3Lwaq6Si17pg" target="_blank">-->
<!--              <v-btn color="primary"-->
<!--                    text style="text-transform: none !important;">-->
<!--                <v-icon left> mdi-check</v-icon>-->
<!--                Ease of Use-->
<!--              </v-btn>-->
<!--            </ahref_seo_optimal>-->

<!--          </v-flex>-->


<!--          <v-flex>-->

<!--            <ahref_seo_optimal href="https://diffgram-workspace.slack.com/join/shared_invite/zt-twn6529v-hhSPzpQrAxvoZB95PhfAFg#/shared-invite/email" target="_blank">-->
<!--              <v-btn color="primary"-->
<!--                    text style="text-transform: none !important;">-->
<!--                <v-icon left> mdi-puzzle-edit</v-icon>-->
<!--                Join Slack-->
<!--              </v-btn>-->
<!--            </ahref_seo_optimal>-->

<!--          </v-flex>-->


<!--          <v-flex>-->

<!--            <ahref_seo_optimal href="https://github.com/diffgram/diffgram" target="_blank">-->
<!--              <v-btn color="primary"-->
<!--                    text style="text-transform: none !important;">-->
<!--                <v-icon left> mdi-creation</v-icon>-->
<!--                Github-->
<!--              </v-btn>-->
<!--            </ahref_seo_optimal>-->

<!--          </v-flex>-->

<!--        </v-layout>-->
<!--      </v-card>-->
<!--    </v-menu>-->

<!--    <v-menu v-model="enterprise"-->
<!--            offset-y-->
<!--            open-on-hover-->
<!--            attach-->
<!--            >-->


<!--      <template v-slot:activator="{ on }">-->
<!--        <v-btn v-on="on"-->
<!--               color="primary"-->
<!--              text style="text-transform: none !important;">-->
<!--           Enterprise-->
<!--        </v-btn>-->
<!--      </template>-->

<!--      <v-card>-->

<!--        <v-layout column>-->

<!--          <v-flex>-->

<!--        <ahref_seo_optimal href="/enterprise">-->
<!--            <v-btn color="primary"-->
<!--                  text style="text-transform: none !important;">-->
<!--              <v-icon left>mdi-domain</v-icon>-->
<!--              Enterprise-->
<!--            </v-btn>-->
<!--        </ahref_seo_optimal>-->

<!--          </v-flex>-->

<!--          <v-flex>-->

<!--          <ahref_seo_optimal href="/enterprise/hub">-->
<!--            <v-btn color="primary"-->
<!--                  text style="text-transform: none !important;">-->
<!--              <v-icon left>mdi-earth</v-icon>-->
<!--              Enterprise Hub-->
<!--            </v-btn>-->
<!--          </ahref_seo_optimal>-->

<!--          </v-flex>-->

<!--          <v-divider> </v-divider>-->

<!--        </v-layout>-->
<!--      </v-card>-->
<!--    </v-menu>-->

  </v-layout>
</div>

</template>

<script lang="ts">


import menu_company from './menu_company'
import menu_learn from './menu_learn'


import Vue from "vue"; export default Vue.extend( {
  name: 'menu_marketing',

  components: {
    menu_company: menu_company,
    menu_learn: menu_learn
  },

  data() {
    return {
      solutions: false,
      compare: false,
      product: false,
      enterprise: false,
      why_menu: false

    }
  },
  computed: {

  }
}
) </script>

<script lang="ts">
import Vue from "vue";

export default Vue.extend({
  name: "UserIcon",
  props: {
    user: {
      type: Object,
      default: null,
    },
    member_id: {
      type: Number,
      default: null,
    },
    user_id: {
      type: Number,
      default: null,
    },
    show_full_name: {
      type: Boolean,
      default: false,
    },
    size: {
      type: Number,
      default: 48,
    },
    fontSize: {
      type: String,
      default: "1rem",
    },
    message: {
      //
      type: String,
      default: null,
    },
  },
  data() {
    return {
      loading: false,
    };
  },
  computed: {
    avatarName: function () {
      let name = "";

      if (
        !this.user_local ||
        !this.user_local.first_name ||
        !this.user_local.last_name
      )
        return "DG";

      name += this.user_local.first_name.slice(0, 1);
      name += this.user_local.last_name.slice(0, 1);

      return name.toUpperCase();
    },

    fullName: function () {
      return this.user_local.first_name + " " + this.user_local.last_name;
    },
    user_local: function () {
      if (this.$props.user) {
        return this.$props.user;
      }
      if (this.$props.member_id) {
        return this.$store.state.project.current.member_list.find((x) => {
          return x.member_id == this.$props.member_id;
        });
      }
      if (this.$props.user_id) {
        return this.$store.state.project.current.member_list.find((x) => {
          return x.id == this.$props.user_id;
        });
      }
    },
  },
});
</script>

<template>
  <div v-cloak>
    <!-- Case 1 User -->
    <div v-if="user_local" class="user-icon">
      <v-tooltip bottom>
        <template #activator="{ on }">
          <!-- 1.1 Expected case -->
          <div v-if="user_local.profile_image_thumb_url">
            <v-avatar :size="size" v-on="on">
              <img :src="user_local.profile_image_thumb_url" />
            </v-avatar>
          </div>

          <!-- 1.2 Fallback case -->
          <div v-else class="default-icon">
            <v-avatar :size="size" color="blue" v-on="on">
              <span class="white--text" :style="{ ['font-size']: fontSize }">
                {{ avatarName }}
              </span>
            </v-avatar>
            <span
              style="font-size: 12px; font-weight: bold"
              color="success"
              v-if="show_full_name"
            >
              {{ fullName }}
            </span>
          </div>
        </template>

        {{ fullName }}
      </v-tooltip>
    </div>

    <!-- Case 2) Message

      Perhaps this should be outside of this component
      -->
    <div v-else-if="message">
      <v-avatar color="black" :size="size">
        <span class="white--text headline">{{ message }}</span>
      </v-avatar>
    </div>
  </div>
</template>



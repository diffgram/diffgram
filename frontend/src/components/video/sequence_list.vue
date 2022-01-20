<template>
  <div v-cloak v-if="video_mode == true && !video_playing" class="pa-0 ma-0">

    <v-alert type="info" v-if="sequence_list && sequence_list.length > 200"
              max-width="600"
              dismissible
              >
      That's a lot of Sequences! We recommend less than 250 Sequences per Label in each Video.
      <br> <br>
      A Sequence may have 100s of Instances.
      Add Instances to existing Sequences instead of creating new ones.
      <br> <br>
      Where Sequences most add value is when they differentiate between sub segments.
      For example:
      <br>
      Keyframes (0, 6, 10) are part of Sequence #1
      <br>
      Keyframes (16, 21, 22...) are part of Sequence  #2.
      <br> <br>
      Note: This is for total count, the Sequence # can be anything.
      For example can start numbering at #2000 or use another numbering
      scheme.

      <br> <br>
      Export data to see more results. Need more? Contact us support@diffgram.com
    </v-alert>

    <v-card-title class="pa-0">

      <!-- Highlight current one ?
            wrap chip in this element if want
          that ... doesn't look quite right though -->

      <!--
      <v-badge overlap large right color="primary">
        <v-icon dark slot="badge"> check </v-icon>
      </v-badge>
      -->

      Sequences

      <div class="pl-4">
        <v-tooltip bottom>
          <template v-slot:activator="{ on }">
            <v-chip v-if="current_sequence"
                    :color="$get_sequence_color(current_sequence.id)"
                    text-color="white"
                    v-on="on"
                    >
              <h2> {{current_sequence_number_local}} </h2>
            </v-chip>
          </template>

          <v-spacer></v-spacer>
          Current
        </v-tooltip>

      </div>


        <!-- Given we now allow a person
            to "stay" on acurrent sequence,
            the relevant thing here is the number
            not the id -->

      <tooltip_button
          tooltip_message="New Sequence (F)"
          @click="force_new_sequence"
          :disabled="current_sequence.number == highest_sequence_number + 1
                    || sequence_list.length >= 250"
          icon="add"
          :text_style="true"
          :large="true"
          color="primary">
      </tooltip_button>

      <!-- Change sequence number

        We don't need to disable this because
        it's "changing" , ie so it handles it if it
        already exists
        -->
      <button_with_menu
        tooltip_message="Change Sequence Number"
        icon="mdi-arrow-up"
        color="primary"
        action_message="Go"
        action_icon="check"
        :commit_menu_status="true"
        :close_by_button="true"
            >

        <template slot="content">

          <v-text-field
            label="Change Sequence Number"
            type="number"
            @change="change_sequence_from_number($event)"
            v-model.number="current_sequence_number_local">
          </v-text-field>

        </template>

      </button_with_menu>


      <v-spacer></v-spacer>


      <tooltip_button
          tooltip_message="Sequence & Video Help"
          href="https://diffgram.readme.io/docs/video-introduction"
          icon="mdi-lifebuoy"
          :text_style="true"
          target="_blank"
                      >
      </tooltip_button>


      <!--
      <v-text-field v-model="search"
                    append-icon="search"
                    label="Search"
                    single-line
                    hide-details></v-text-field>
        -->
    </v-card-title>

    <v_info_multiple
        :info="info"
        @input="info = {}"
        >
    </v_info_multiple>

    <v_error_multiple
        :error="error"
        @input="error = {}"
        >
    </v_error_multiple>
    <!-- :search="search" -->


    <!--
      Overflow / layout notes
      * We purposely want to have the new sequence option available
      above overflow
      * We want the data table to overflow vertically for case of many
      sequences
      * We want the keyframe list (just the list)
      to overflow horiztonally (but use as much space as it can)

      ideally the keyframe list would be only thing that overflows?
      but in case the panels collide we can have a horiztonal
      overflow on data table too?

      TODO this is still not quite right
      for panel sliding in case

      -->
    <v-skeleton-loader
        :loading="loading"
        type="table"
      >

      <v-data-table
                    style="overflow-y:auto; max-height: 400px;"
                    :headers="header_with_perms"
                    :items="sequence_list"
                    item-key="id"
                    :options.sync="options">

        <!-- appears to have to be item for vuetify syntax-->
        <template slot="item" slot-scope="props">

          <!-- props.item == sequence -->
          <tr @mouseover="hover_index=props.index"
              @mouseleave="hover_index=-1">

            <td>
              <v-chip :color="$get_sequence_color(props.item.id)"
                      text-color="white"
                      @click="change_current_sequence(props.item)"
                      >
                {{props.item.number}}
              </v-chip>
            </td>

            <td>

              <div v-if="props.item.number == current_sequence_number_local">

                <v-badge overlap large right color="primary">
                  <v-icon dark slot="badge"> check </v-icon>
                </v-badge>

              </div>

              <div v-if="props.item.instance_preview != undefined
                      && props.item.instance_preview.preview_image_url">

                <img class="image_clickable"
                      style="max-height: 50px; max-width: 50px"
                      @click="change_current_sequence(props.item)"
                      :src="props.item.instance_preview.preview_image_url"
                      width="100%"
                      height="100%"
                      >
              </div>

              <!-- Fallback -->
              <div v-else>
                <v-icon large
                        @click="change_current_sequence(props.item)">
                  mdi-transition
                </v-icon>
              </div>

            </td>


            <td>

              <!-- TODO get max width in stronger way
                ie max of available space to left/right etc...-->

              <div >
                <v-layout v-if="props.item.keyframe_list"
                          style="max-width: 500px; overflow-x:auto;">
                  <v-flex v-for="(keyframe, index) in props.item.keyframe_list.frame_number_list"
                          :key="index">

                    <!-- Indirectly disables if video is playing -->
                    <div v-show="keyframe == current_frame || video_playing">
                      <h3 class="pl-2"> {{keyframe}}  </h3>
                    </div>
                    <div v-show="keyframe != current_frame && !video_playing">

                      <!-- Spacing for this is just awful
                        for now padding seems like best effort still-->

                      <h3 class="pl-2">
                        <a @click="$store.commit('go_to_keyframe_via_store', keyframe)">
                        {{keyframe}}
                        </a>
                      </h3>
                      <!-- Tried style="min-width: 0"
                          but didn't seem to work right...'
                        -->

                      <!--
                      <v-btn @click="go_to_keyframe(keyframe)"
                              style="min-width: 0"
                              text
                              >
                        {{keyframe}}
                      </v-btn>
                      -->

                    </div>



                  </v-flex>
                </v-layout>

              </div>



            </td>


            <td v-if="!view_only_mode">
              <!-- Actions -->

              <!-- Change label

                This is similar to implementation for image
                but beacuse it effects multiple frames we have a confirm.

                use props.item just incase we want to display sequences from
                different label files together in the future.
                -->


               <!-- We need to wrap in a div  because it's the whole "menu"
                 thing that pops out-->
              <v-layout>

                <!--
              <div v-if="props.index!=hover_index">
                <v-icon>mdi-format-paint </v-icon>
                <v-icon>archive</v-icon>
              </div>
             -->

              <div v-if="props.index==hover_index ||
                    menu_open == true &&
                    props.index == hover_click_index">
                <button_with_confirm
                    v-if="props.item.id != undefined"
                    tooltip_message="Edit Label"
                    @confirm_click="update_sequence(
                                      props.item.id,
                                      edit_label_file_selected,
                                      'update_label')"
                    confirm_message="Move Sequence to Different Label Template"
                    @menu_open="menu_open = $event,
                                hover_click_index=props.index"
                    icon="mdi-format-paint"
                    color="primary"
                    :icon_style="true"
                    :close_content_on_click="false"
                        >

                  <template slot="content">
                    <v-container>
                      Updates all instances in sequence to desired label.

                      <label_select_only
                        :label_file_list_prop=label_file_list
                        :select_this_id_at_load=props.item.label_file_id
                        @label_file="edit_label_file_selected = $event"
                                  >
                      </label_select_only>

                    </v-container>
                  </template>

                </button_with_confirm>


              <button_with_confirm
                @confirm_click="remove_sequence(props.item.id, props.index)"
                :confirm_message="'Confirm Archive Sequence #' + props.item.number"
                @menu_open="menu_open = $event,
                            hover_click_index=props.index"
                color="primary"
                icon="archive"
                tooltip_message="Archive Sequence"
                :disabled="view_only_mode"
                :icon_style="true"
                                    >

                <template slot="content">
                  <v-alert type="info">
                      Will delete all related instances.
                  </v-alert>
                </template>

              </button_with_confirm>
             </div>
            </v-layout>

            </td>


          </tr>
      </template>

      <v-alert slot="no-results"  color="error" icon="warning">
        Your search for "{{ search}}" found no results.
      </v-alert>
      <v-alert slot="no-data"  color="info" icon="info">
        No sequences yet.
      </v-alert>

    </v-data-table>
  </v-skeleton-loader>

</div>
</template>

<script lang="ts">
  // @ts-nocheck
  // it was having trouble with the computed properties thing.

import axios from 'axios';
import label_select_only from '../label/label_select_only.vue'
import Vue from "vue";
import pLimit from 'p-limit';

export default Vue.extend( {
  name: 'sequence_list',
  components: {
    label_select_only
  },
  props: {
    'project_string_id' : {},
    'video_mode' : {},

    // NOTE label / video files are different!
    'label_file_id': {
      default: null
    },
    'label_file_list': {
      default: null
    },
    'current_video_file_id' : {},
    'current_frame': {},
    'current_sequence_annotation_core_prop': {},
    'view_only_mode': {},
    'task': {},

    // we don't want to lose the other
    // label_file_id because we use it for watcher
    // the first use for this is showing name
    'current_label_file': {},
    'video_playing': {
      default: null
    },
    /*
     * hit this with an update value
     * ie force_new_sequence_request = Date.now()
     * to call force_new()
     * We want to keep the logic for that in here
     * so we can call it from other places
     * and other components don't have to know the inner workings
     * of this.
     *
     */
    'force_new_sequence_request': {
      default: null
    },
    'request_clear_sequence_list_cache': {
      default: null
    },
    'label_settings': {}

  },
  data() {
    return {

      hover_click_index: -1,
      hover_index: -1,
      menu_open: false,

      loading: false,

      log: {},

      cache_sequence_list: {},

      options : {
        'itemsPerPage': 20
      },

      info: {},
      error: {},

      current_sequence_number_local: null,

      sequence_list: [],

      current_sequence: {},

      delete_sequence_confirm_prompt: false,

      search: "",

      highest_sequence_number: 0,

      edit_label_file_selected: null,

      force_new: false,

      headers: [
        {
          text: "Number",
          align: 'left',
          sortable: true,
          value: "number"
        },
        {
          text: "Preview",
          align: 'left',
          value: "name"
        },
        {
          text: "Keyframes",
          align: 'left',
          value: "keyframe_list.frame_number_list"
        },
        {
          text: "Actions",
          align: 'left',
          value: "action",
          width: "150px", // prevents it jerking when on hover happens
          fixed: true
        }
      ],

      color_map : ["blue", "green", "pink", "orange",
        "black", "purple", "indigo", "cyan", "teal", "orange"
        ]
    }
  },
  computed: {
    header_with_perms: function(){
      const result = [];
      for(const header of this.headers){
        if(header.text === 'Actions' && this.view_only_mode){
          continue
        }
        else{
          result.push(header)
        }
      }
      return result
    }
  },
  watch: {


    current_frame: function () {
      /* Context of user playing video,
       * when we get to a new frame we want to reset it to an existing instance
       * (usually it's a new non existing instance on prior frame)
       *
       * This isn't quite right yet but should help with the default case.
       */
      if (!this.sequence_list[0]) {
        return
      }

    },

    force_new_sequence_request: function () {
      this.force_new_sequence()
    },

    current_sequence_annotation_core_prop: function (new_sequence, old) {
      /*        *
       * Context we have the prop for data flowing in /set from annotation core
       * And then we always update the "core" thing
       * from here.  Because it change from either
       *
       * See for details: https://docs.google.com/document/d/1EVvPke7Ms25KsmDKpwrQcqB1k6pgB5SNs5WDbwGmLCo/edit#heading=h.oo1xxxn8bkpp
       *
       */


      if (!new_sequence) { return }

      /*
       * Handle case of switching sequences while loading
       * Recreate by creating seqeunce label A
       * load label B (which is ok we want user to do that)
       * observe it shuld not inject the newly found prop one into it.
       *
       * Context of confusion on timing issue here
       * https://github.com/swirlingsand/ai_vision/commit/75efc7e7f9506b8b61d0aa72bd23acd56c76d700
       * https://app.hubspot.com/live-messages/5238859/inbox/300479634#reply-editor
       * Had thought it was a timing issue (which in a sense it was)
       * and it was only sorta of todo with "saving" it wrong!
       * really it was the Response handling AFTER saving (which ends up here eventually.)
       *
       */
      if (new_sequence.label_file_id != this.label_file_id){
        return  // see comment above.
      }


      // set from parent
      this.current_sequence = new_sequence

      let index = this.sequence_list.findIndex(
        s => s.id == new_sequence.id)

      // sequence already exists
      // careful index returns -1 if can't find it (not undefined)
      if (index !== -1) {
       this.sequence_list.splice(index, 1, new_sequence)
      } else {
        //creation context

        this.add_new_sequence_to_list(new_sequence)
      }

      this.emit_current_sequence()


    },

    label_file_id: function () {
      /*
       * Is this correct? Not 100% sure as changing other stuff.
       * Caution, we purposely watch the id and not the dict
       * so that we can better detect changes here...
       *
       * Note there is both a LABEL file and a VIDEO file here...
       *
       */


      this.get_sequence_list()
    },

    // watch sequence_list cache (tags for seraching)
    sequence_list: function() {
      /* assumes current video file only
       * design https://docs.google.com/document/d/1HVY_Y3NsVQgHyQAH-NfsKnVL4XZyBssLz2fgssZWFYc/edit#heading=h.121li5q14mt2
       */


      this.cache_sequence_list[this.label_file_id] =
        {
          sequence_list : this.sequence_list,
          highest_sequence_number: this.highest_sequence_number
        }

      this.$emit('sequence_list', this.sequence_list)

    },

    request_clear_sequence_list_cache: function () {
      // ie instance delete. more see -> https://docs.google.com/document/d/1HVY_Y3NsVQgHyQAH-NfsKnVL4XZyBssLz2fgssZWFYc/edit#heading=h.121li5q14mt2
      if (this.request_clear_sequence_list_cache){
        this.clear_sequence_list_cache()
      }
    }

  },
  created() {

    this.get_sequence_list()

    var self = this
    this.unwatch_sequence = this.$store.watch((state) => {
      return this.$store.state.labels.sequence_refresh },
      (new_val, old_val) => {

        self.get_sequence_list()
      },
    )

  },
  destroyed() {
    // calling unwatch_sequence() magically removes watch
    // otherwise we get a bunch of calls for unvisible elements
    // https://vuejs.org/v2/api/#vm-watch
    this.unwatch_sequence()

  },
  methods: {
    add_frame_number_to_sequence(sequence_id, frame_number){

      if(frame_number == undefined){
        return
      }
      let sequence = this.sequence_list.find(seq => seq.id === sequence_id);
      if(sequence){
        let existing_frames = sequence.keyframe_list.frame_number_list;
        if(!existing_frames.includes(frame_number)){
          existing_frames.push(frame_number);
          existing_frames.sort(function(a, b) {
            return a - b;
          });
        }
      }
    },
    remove_frame_number_from_sequence(sequence_id, frame_number){
      if(frame_number == undefined){
        return
      }
      let sequence = this.sequence_list.find(seq => seq.id === sequence_id);
      if(sequence){
        let existing_frames = sequence.keyframe_list.frame_number_list;
        let index = existing_frames.indexOf(frame_number)
        if (index !== -1) {
         existing_frames.splice(index, 1)
        }
      }
    },
    add_or_update_existing_sequence: function(new_sequence){
      let exiting_sequence = this.sequence_list.find(elm => elm.number === new_sequence.number);
      if(exiting_sequence){
        let index = this.sequence_list.indexOf(exiting_sequence);
        this.sequence_list.splice(index, 1, new_sequence)
      }
      else{
        this.add_new_sequence_to_list(new_sequence)
      }
    },
    add_new_sequence_to_list: function(new_sequence){
      this.sequence_list.push(new_sequence)

      // prior we expected to this from the response
      // same concept.
      this.highest_sequence_number = new_sequence.number
    },
    clear_sequence_list_cache: function () {
      this.cache_sequence_list = {}
    },

    update_from_sequence_list_change: function (
        sequence_list: list,
        highest_sequence_number
        ) {

      this.sequence_list = sequence_list
      this.highest_sequence_number = highest_sequence_number

      this.$emit('highest_sequence_number', this.highest_sequence_number)

      if (this.current_sequence.label_file_id !=
          this.label_file_id) {

        this.change_current_sequence(this.sequence_list[0])
      }

      else if (!this.current_sequence ||
          this.current_sequence.number == this.highest_sequence_number) {

        let highest_sequence = this.sequence_list.find(
            obj => {
              return obj.number == this.highest_sequence_number
              }
        )
        this.change_current_sequence(highest_sequence)
      }

      /* The context here is trying to detect if we should change
        * the sequence, but otherwise assuming we want to keep the one
        * the user selected. Cases:
        *
        * #1
        * IF the label file doesn't match then we assume the sequence
        * has changed in a way that requires refreshing the current sequence
        * (through change sequence)
        * To test this: Load sequence A then switch to sequence B and
        * confirm that it has changed the number correctly.
        *
        * #2
        * If we don't have a current sequence (ie init init case)
        * To test this, an open load on a new thing should have a seqeunce selected
        *
        * #3
        * And if we do and the number is equal to the highest
        * then it was the most recently added and we need to push it to refresh
        * ids (as a hacky way, in theory should be able to skip that example
        * and just say do sequence_list[0] on init)
        * Not quite sure what we want to do on testin here.
        *
        * #4 "Default" case, which is none of #1 -> 3 are true,
        * and we want to keep on the current sequence we are on.
        * To test this, while a seqeuence (ie 4), go
        * to another frame (which triggers this)
        *
        *
        * For all of this the general concept is that we are conditioning changing
        * the sequence on these cases, but otherwise changing frames does
        * not need to change the sequence.
        * This is a similar concept to how we split out the frame buffer
        * as an "on demand" feature instead of assuming we need to trigger it.
        * (And we validate other sequence logic at save time)
        *
        * General discussion:
        * https://docs.google.com/document/d/1jZwKsHqzkuXMw9j8vVwdXAd_Kt6JZZiLZmtdHocW6Ng/edit#heading=h.afgly7qne90v
        */



    },

    // (search tags) def get_sequence_list  sq
    refresh_missing_preview_images: async function(){
      if(!this.sequence_list){
        return
      }
      let sequences_with_no_preview_images = []
      for(let sequence of this.sequence_list){
        if(!sequence.instance_preview || Object.keys(sequence.instance_preview).length === 0){
          sequences_with_no_preview_images.push(sequence)
        }
      }
      const limit = pLimit(10); // 10 Max concurrent request.
      const promises = sequences_with_no_preview_images.map(sequence => {
        return limit(() => {
          let new_url =`/api/project/${this.project_string_id}/sequence/${sequence.id}/create-preview`
          return axios.post(new_url, {
            sequence_id: sequence.id,
            directory_id : this.$store.state.project.current_directory.directory_id
          })
        })
      });

      let all_responses = await Promise.all(promises);
      for(const response of all_responses){
        let data = response.data;
        const request_payload = JSON.parse(response.config.data)
        let sequence = this.sequence_list.find(seq => seq.id === request_payload.sequence_id);
        if(sequence){
          sequence.instance_preview = data.result.instance_preview;
        }
      }
      this.$forceUpdate();
    },
    get_sequence_list: async function () {

      if (!this.label_file_id || !this.current_video_file_id) {
        return
      }

      // design https://docs.google.com/document/d/1HVY_Y3NsVQgHyQAH-NfsKnVL4XZyBssLz2fgssZWFYc/edit#heading=h.hbk36ssyul56
      if (this.cache_sequence_list[this.label_file_id]) {
        this.update_from_sequence_list_change(
            this.cache_sequence_list[this.label_file_id].sequence_list,
            this.cache_sequence_list[this.label_file_id].highest_sequence_number)
        return
      }

      this.loading = true
      this.$emit('loading_sequences', this.loading);
      this.sequence_list = []
      let url = ""

      if (this.task && this.task.id) {
         url += "/api/v1/task/" + this.task.id + '/video/file_from_task'
      }
      else {
        url += '/api/project/' + this.project_string_id
        + '/video/single/' + this.current_video_file_id
      }
      url += '/label/' + this.label_file_id + '/sequence/list'
      try{
        const response = await axios.get(url);
        // assumes watcher will update cache
        this.update_from_sequence_list_change(
          response.data.sequence_list,
          response.data.highest_sequence_number)

        // No await since we don't want this block
        this.refresh_missing_preview_images()
        this.loading = false
        this.$emit('loading_sequences', this.loading);
      }
      catch(error){
        console.error(error)
      }

    },

    change_sequence_from_number: function (number) {
      /* We may want to fill in in between sequences
       * so can't rely on highest sequence number
       *
       * So we check if the sequences exists first
       * otherwise in this context we assume we want to make a new one.
       *
       * In theory this could be part of the "change_current_sequence"
       * but that function was trying to keep a context
       * ie "auto advancing" to next number
       *
       * Motivation
       *  instead of "validating" or rejecting for creating a new sequence
       *  makes it more flexible that it just "goes" to that existing
       *  sequence.
       *
       *  ie if #8 exists, I just "go to" 8
       *  instead of it rejecting or trying to validate against list
       *
       *  Note we use the term "new sequence" fairly loosely here
       *  we rely on reseting the id in combination with backend
       *  to make it work.
       *
       */

      let sequence = this.sequence_list.find(
          sequence => {return sequence.number == number}
          )

      if (sequence) {
        this.change_current_sequence(sequence)
      }
      // New sequence
      else {
        // reset
        this.current_sequence = {
           id : null
        }
        this.current_sequence.number = number
        this.emit_current_sequence()
      }

    },

    change_current_sequence: function (sequence) {
      /*
       *  Caution!!!
       *  We only want to do 1 of the following cases
       *  so we have the else if but always want to
       *  "emit" the update at the end
       *
       *  vue js can't detect refresh inside thing...
       *  so we "clear it" to recreate it.
       *
       *  The reason we have this as being fairly "arbitrary"
       *  is that a user (or system process) can request any
       *  sequence, and it may ore may not be a valid one.
       *
       */

      // careful if we assign the full object directly
      // it links it, which can create issues if we want to say increment
      // current_sequence

      // careful, this is a bit strange in that we are referencing
      // sequence which is the new sequence not this.current_sequence

      this.current_sequence = {
        id : null
      }

      if (  this.force_new == true) {
        this.current_sequence.number = this.highest_sequence_number + 1
      }

      /*  Init case
       *      Question what's the difference between
       *      using current_sequence.number and the this.highest_sequence_number + 1?
       */

      else if (sequence == undefined) {
        this.current_sequence.number = 1
      }
      /*  Single frame case
       *   If we are in the context of an event, then if it's a new one
       *   we assume it's handled by the above.
       *   Otherwise if we are on a different frame where the sequence could
       *   be valid, it would have an ID right?
       *
       *   Either way, we can check the current_sequence.is_event,
       *   and if it's true, we also force new ?
       *
       *   Somewhere we are calling sequnce_list[0] and passing it here
       *   and trusting it to handle it if it's the wrong seqeunce.
       *
       *
       */

      /*
       * Not clear what benefit that really provides
       * forcing it to next...!!!!
       *
       * Maybe better off just not doing this.
       *
       * If anything would rather have some kind of "auto advance" feature.
       *
       */
       /*
      else if (sequence.single_frame == true) {
        this.current_sequence.number = this.highest_sequence_number + 1
      }
      */

      /* Why not find the object based on the id?
       * This feels awkward...
       */

      // else we assume we are on a new frame
      // and the instance has been purposefully selected

      // I think now that we are storing the sequence here
      // it's ok to just set it directly?
      else {
        this.current_sequence = sequence
      }

      // work around for being able to update this number on demand
      // context of say a user clicking a number / loading intial number
      this.current_sequence_number_local = this.current_sequence.number

      // run for all
      this.emit_current_sequence()

      return this.current_sequence;


    },

    emit_current_sequence() {

      this.$emit('current_sequence_changed', this.current_sequence)
    },

    force_new_sequence() {
      this.force_new = true
      let newly_changed_sequence = this.change_current_sequence(null)
      this.add_new_sequence_to_list(this.current_sequence);
      this.recalculate_highest_sequence_number();
      this.force_new = false
    },

    change_instance(instance) {
      this.$emit('change_instance_request', instance)
    },
    new_instance(instance_group) {
      this.$emit('new_instance_request', instance_group)
    },

    remove_sequence(sequence_id, index = undefined) {
      if(sequence_id == undefined && index !=undefined){
        let seq_to_remove = this.sequence_list[index];
        this.sequence_list.splice(index, 1);
        this.recalculate_highest_sequence_number();
        if(seq_to_remove.number === this.current_sequence.number){
          this.current_sequence = {};
        }
        return;
      }
      this.loading = true

      let url = ""

      if (this.task && this.task.id) {
        url += "/api/v1/task/" + this.task.id + '/video/file_from_task'
      }
      else {
        url += '/api/project/' + this.project_string_id
        + '/video/single/' + this.current_video_file_id
      }

      url += '/label/' + this.label_file_id
          + '/sequence/' + sequence_id
          + '/remove'

      axios.post(url).then(response => {

          if (response.data.success == true) {

            this.remove_sequence_literal_from_frontend_list(sequence_id)

            this.$store.commit('refresh_video_buffer')  // refresh instances

          }
          this.loading = false
        })
        .catch(e => {
          console.error(e)
        })


    },

    remove_sequence_literal_from_frontend_list(sequence_id){

      for (let i in this.sequence_list) {
        if (this.sequence_list[i].id == sequence_id) {
          this.sequence_list.splice(i, 1)
          break
        }
      }

      this.change_current_sequence(this.sequence_list[0])
      this.recalculate_highest_sequence_number();

    },
    recalculate_highest_sequence_number: function(){
      let numbers_list = this.sequence_list.map(elm => elm.number);
      if(numbers_list.length === 0){
        this.highest_sequence_number = 0;
        return
      }
      this.highest_sequence_number = Math.max(...numbers_list);

    },
    may_auto_advance_sequence: function () {
      if(this.$props.label_settings.on_instance_creation_advance_sequence == true){
        this.force_new_sequence()
      }
    },

    update_sequence(sequence_id, payload, mode) {

      this.loading = true
      this.info = {}
      this.error = {}

      let url = ""

      if (this.task && this.task.id) {
        url += "/api/v1/task/" + this.task.id
      }
      else {
        url += '/api/project/' + this.project_string_id
          + '/video/single/' + this.current_video_file_id
      }

      url += '/sequence/' + sequence_id + '/update'

      axios.post(url,
        { mode: mode,
          payload : payload
        }).then(response => {

          /* We remove if the sequence was updated to something other
           * then current one?
           * This assumes that we only want to refresh list in that case right?
           *
           * not sure about checking this here vs checking before we hit
           * server.
           */
          if (mode == 'update_label') {
            if (payload.label_file_id != this.current_sequence.label_file_id) {
              this.remove_sequence_literal_from_frontend_list(sequence_id)
            }
            // not clear how 'update_label will effect it',
            // and prior assumption was that this would refresh
            // from server after, so clear cache
            this.clear_sequence_list_cache()
          }

          this.info = response.data.log.info

          this.$store.commit('refresh_video_buffer')  // refresh instances

          this.loading = false
        })
        .catch(e => {
          this.loading = false
          this.error = e.response.data.log.error
          console.error(e)
        })


    }



  }
}

) </script>

<template>
<div v-cloak>

<!--
 This is still fairly tightly coupled,
  Directionally  I would like to look at:

  1) Having the same "thumbnail" syntax for both image, video, and other media
  2) Having the fall back avatar concept + v-img backed into a single component?
    (It's strange in a sense that's actually not just part of it...)

  Two cases for failure

  A) if the url is null, then it uses v-avatar. the "lazy-src" thing does not seem to
  detect that
  B) the url can't load, in which case by having the "lazy-src" it keeps that
  (instead of switching to the new ) url.

  Tested a few different ways, but for some reason (maybe because it's a dict?)
  even though dev tools shows that it was updating 'frontend_src_load_failed'
  as expected, it just didn't seem to propgate downwards.
  (otherwise maybe prefer to say just use avatar)

  Main leave off questions is if the current b64 "preload thing"
  1) performance impact?
  2) Visual? If it prevents the screen jerking around so much that's actually a
  good thing, but not 100% sure yet...

  It does the event that it failed fine
  https://stackoverflow.com/questions/53215071/how-to-do-a-fallback-img-in-v-img-in-vuetify
  BUT it just seems bound and determined to not update after and spent enough time on this.

  Also curious what "other" stuff we may want to do in terms of error handling
  if the thumbanil is not loading... (ie metrics if nothing else...)

  https://www.base64-image.de/
  You have somewhere in code b64 conversion thing for images but this was pretty easy
  the lazy src is the loading thing...

  Also things like max-height

    TODO can we show gradient for selected on these ones too?

-->


<v-img v-if="item.image && item.image.url_signed_thumb"
      :gradient="show_selected_return_gradient(item)"
      :class="{image_clickable: true, selected_box: this.show_selected(item)}"
      :src="item.image.url_signed_thumb"
      width="100px"
      height="100px"
      max-height="100px"
      max-width="100px"
       position="center"
      lazy-src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAG8AAABUCAYAAACMeGkOAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAAGdYAABnWARjRyu0AAAMOSURBVHhe7dpJiioxHMfxPp4bcSEOIIKIunEAQdw5gAPO08bZQ3gMb+AdvEPe+xevpNS0VMV0v/yrfsJ30W0qNH667Jj0l/j7uFwu4nQ6IQaRlf34ul6v0kHI3MjMwpM9iczvdrsBj2vn8xl4nAMe44DHOOAxDniMAx7jgMc44DEOeIwDHuOAxzjgMQ54jAMe44DHOOAxDniMAx7jgMc44DGOBd7xeBTL5VIMBgPlptOpNY9sfq4Zj7darUQmkxGhUOijwuGwaDQavgI0Gm+9XotcLifFUMlvgEbjdbtdKYKX0um0SCaT96/9BGg0XrvdfoBQqVarifF47EvAQODRXLRgSaVS9+/7ATAweJTfAAOFR/kJMHB4lF8AA4lH+QEwsHjUfD5nDRhoPIozYODxqGdA+kxIe6mysSYFvH85AYGnIR14KgFPQ8B7H/AkAU9Dqni0YqTTBOcixEvA05BXvGw2KyaTycMyf7fbiVarJeLxuPQaWcDTkBe8arVqQcnmobycyANPQ27x6LSdTt3t6+jO22w2YrvdPsw3Go1ENBqVzuEMeBpyi9fpdO7XPN9hzjvycDiISqXycK0s4GnIDV4ikRCLxcIav9/vRbFYfBlD89hzNpvNl+efA56G3ODFYjFrHP17H/3Pi2yF6dxlcTMn8DTk5oV2E20023PizvuldOA5/+bRIiafz0vHOQOehj7Bi0Qi1l1mf+YjQIKUjX0OeBpSxaMdFrrWnofgyuWydKws4GlIFY9WnLTypDkIrlQqScd9F/A0pIpHb5f2HPQZUDbmXcDTkCper9ezFieU279zzoCnIVW8TwOehlTx+v0+7rz/nSoebUDbc9DuimzMu4CnIeC9z5d4tL9JJwuUl0NYO+BpaDabuTp/012hUHg5CzQxo/Foa6ter0tf4J+KflmGw6H05zEto/EoAqTjHrob7LfCn4p2Zji8XdoZj4e+D3iMAx7jgMc44DEOeIwDHuOAxzjgMQ54jAMe44DHOOAxDniMAx7jgMc44DEOeIwDHuOAxzjgse0k/gC50RU/OaqXdAAAAABJRU5ErkJggg=="
      v-on:error="on_image_error($event)"
        />

<v-img v-if="item.type=='video' && item.video.preview_image_url_thumb"
      :gradient="show_selected_return_gradient(item)"
      :class="{image_clickable: true, selected_box: selected}"
      :src="item.video.preview_image_url_thumb"
      width="100px"
      height="100px"
      max-height="100px"
      max-width="100px"
      position="center"
      lazy-src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAG8AAABUCAYAAACMeGkOAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAAGdYAABnWARjRyu0AAAMOSURBVHhe7dpJiioxHMfxPp4bcSEOIIKIunEAQdw5gAPO08bZQ3gMb+AdvEPe+xevpNS0VMV0v/yrfsJ30W0qNH667Jj0l/j7uFwu4nQ6IQaRlf34ul6v0kHI3MjMwpM9iczvdrsBj2vn8xl4nAMe44DHOOAxDniMAx7jgMc44DEOeIwDHuOAxzjgMQ54jAMe44DHOOAxDniMAx7jgMc44DGOBd7xeBTL5VIMBgPlptOpNY9sfq4Zj7darUQmkxGhUOijwuGwaDQavgI0Gm+9XotcLifFUMlvgEbjdbtdKYKX0um0SCaT96/9BGg0XrvdfoBQqVarifF47EvAQODRXLRgSaVS9+/7ATAweJTfAAOFR/kJMHB4lF8AA4lH+QEwsHjUfD5nDRhoPIozYODxqGdA+kxIe6mysSYFvH85AYGnIR14KgFPQ8B7H/AkAU9Dqni0YqTTBOcixEvA05BXvGw2KyaTycMyf7fbiVarJeLxuPQaWcDTkBe8arVqQcnmobycyANPQ27x6LSdTt3t6+jO22w2YrvdPsw3Go1ENBqVzuEMeBpyi9fpdO7XPN9hzjvycDiISqXycK0s4GnIDV4ikRCLxcIav9/vRbFYfBlD89hzNpvNl+efA56G3ODFYjFrHP17H/3Pi2yF6dxlcTMn8DTk5oV2E20023PizvuldOA5/+bRIiafz0vHOQOehj7Bi0Qi1l1mf+YjQIKUjX0OeBpSxaMdFrrWnofgyuWydKws4GlIFY9WnLTypDkIrlQqScd9F/A0pIpHb5f2HPQZUDbmXcDTkCper9ezFieU279zzoCnIVW8TwOehlTx+v0+7rz/nSoebUDbc9DuimzMu4CnIeC9z5d4tL9JJwuUl0NYO+BpaDabuTp/012hUHg5CzQxo/Foa6ter0tf4J+KflmGw6H05zEto/EoAqTjHrob7LfCn4p2Zji8XdoZj4e+D3iMAx7jgMc44DEOeIwDHuOAxzjgMQ54jAMe44DHOOAxDniMAx7jgMc44DEOeIwDHuOAxzjgse0k/gC50RU/OaqXdAAAAABJRU5ErkJggg=="
      v-on:error="on_image_error($event)"
        />

  <!-- Tested and even with a lazy-src
    doesn't handle having a null :src bound so this remains fallback
    (and if exists check on image)... -->
  <v-avatar v-if="
            item.type =='image' &&
            !item.image.url_signed_thumb
            ||
            item.type =='video' &&
            !item.video.preview_image_url_thumb
            "
            color="grey"
            size="72"
            class="image_clickable"
            >
    <v-icon>mdi-file-question</v-icon>
  </v-avatar>

</div>
</template>

<script lang="ts">

import Vue from "vue";

export default Vue.extend( {

  name: 'thumbnail',

  props: {
    'item': {
      default: null
    },
    // not sure if this is great to pass selected...
    // but some of the computed things need it...
    'selected': {
      default: null
    },

  },
  data() {
    return {
    }
  },
  computed: {

  },
  methods: {

    on_image_error: function (event) {

      // using lazy src for now
      //this.$emit('on_image_error', event)
    },

    show_selected(file){
      // This is a shallow function since the other thing
      // needs gradient returned...
      if (this.selected) {
        return this.selected.includes(file)
      }
    },

    show_selected_return_gradient(file){
      if (this.show_selected(file)) {
        //https://developer.mozilla.org/en-US/docs/Web/CSS/linear-gradient
        return "217deg, rgba(0,0,255,.8), rgba(255,0,0,0) 90%"
      }
      return null
    },
  }
}

) </script>

<style>
  .selected_box{
    border: 3px solid #2196f3;
  }
</style>

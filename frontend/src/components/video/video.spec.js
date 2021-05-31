import 'babel-polyfill';
import Vuetify from 'vuetify';
import Vuex from 'vuex'

import video from './video.vue'
import store from '../../store';

// Utilities
import {
  mount,
  createLocalVue
} from '@vue/test-utils'

const localVue = createLocalVue()
localVue.use(Vuetify);
localVue.use(Vuex);

// main
describe('video.vue', () => {
  let vuetify
  let system_under_test;
  let vue_instance

  beforeEach(() => {
    vuetify = new Vuetify({
      icons : {
        iconfont: 'mdi'
      },
      theme: {
        primary: '#2196F3'
      },

    });

    system_under_test = mount(video, {
      localVue,
      vuetify,
      store,
      propsData:{
        current_video:{
          width: 500,
        },
      },
      data(){
        return {
          primary_video:{
            addEventListener: () => {},
            play: () => {return new Promise((res, rej) => {res();})},
          }
        }
      }
    })

    // https://vue-test-utils.vuejs.org/guides/#getting-started
    vue_instance = system_under_test.vm

  })

  it('Video with no source triggers playback warning', async () => {

    // TODO need to do more mocking to get this to fully test properly

    vue_instance.$refs.video_source_ref.src = null
    await vue_instance.video_play();
    await vue_instance.$nextTick();
    expect(vue_instance.playing).to.equals(true);
    expect(vue_instance.playback_info).to.exist;
  })

})

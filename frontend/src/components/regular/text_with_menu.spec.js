import 'babel-polyfill';
import Vuetify from 'vuetify';
import Vuex from 'vuex'
import flushPromises from 'flush-promises';
import moxios from 'moxios';
import { route_errors } from './regular_error_handling'
import text_with_menu from './text_with_menu.vue'
import store from '../../store';
import {
  shallowMount,
  createLocalVue, mount
} from '@vue/test-utils'



const localVue = createLocalVue()
localVue.use(Vuetify);
localVue.use(Vuex);

describe('text_with_menu.vue', () => {
  let vuetify
  let wrapper;
  let vm;


  beforeEach(() => {
    vuetify = new Vuetify({
      icons : {
        iconfont: 'mdi'
      },
      theme: {
        primary: '#2196F3'
      }
    });
    moxios.install();
    wrapper = mount(text_with_menu, {
      localVue,
      vuetify,
      store,
      mocks:{

      },
      data() {
        return {

        }
      },
      propsData:{
      }
    })
  });
  afterEach(() =>{
    moxios.uninstall();
  })

  it('Should have a tooltip component.', () => {
    expect(wrapper.find('[data-cy=text-with-menu-tooltip]').exists()).to.equal(true);
  });

  it('Should set menu_open to false when calling close_menu.', () => {
    wrapper.vm.$data.menu_open = true;

    wrapper.vm.close_menu();
    expect(wrapper.vm.$data.menu_open).to.equal(false);
  });

})

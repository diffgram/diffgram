import 'babel-polyfill';
import Vuetify from 'vuetify';
import Vuex from 'vuex'
import flushPromises from 'flush-promises';
import moxios from 'moxios';
import { route_errors } from '../regular/regular_error_handling'
import directory_icon_selector from './directory_icon_selector.vue'
import {project} from '../../store';
import { cloneDeep } from 'lodash'
import {
  shallowMount,
  createLocalVue
} from '@vue/test-utils'



const localVue = createLocalVue()
localVue.use(Vuetify);
localVue.use(Vuex);

describe('directory_icon_selector.vue', () => {
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
    const mock_project_module = {
      ...project,
      state: {
        ...project.state,
        current:{
          directory_list:[
            {
              directory_id:1,
              id:1,
              nickname: 'test'
            }
          ]
        }
      }
    }
    const store = new Vuex.Store({modules: {project: cloneDeep(mock_project_module)}})
    wrapper = shallowMount(directory_icon_selector, {
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

  it('Should have a directories container.', () => {
    expect(wrapper.find('[data-cy=directories-container]').exists()).to.equal(true);
  });

})

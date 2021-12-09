import 'babel-polyfill';
import Vuetify from 'vuetify';
import { VSelect } from 'vuetify'
import Vuex from 'vuex'

// import { shallowMount } from '@vue/test-utils'
import account_info from './account_info.vue'
import store from '../../../store';

// Utilities
import {
  mount,
  createLocalVue
} from '@vue/test-utils'

const localVue = createLocalVue()
localVue.use(Vuetify);
localVue.use(Vuex);

describe('account_info.vue', () => {
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

    wrapper = mount(account_info, {
      localVue,
      vuetify,
      store
    })

    vm = wrapper.vm
  })

  it('Check for account balance', () => {
    expect(wrapper.find('div .balance').text()).to.equal('0')
    expect(wrapper.html()).to.contain('<span class="balance">0</span>')
  })

  it('Check for account nickname', () => {
    expect(wrapper.find('div .nickname').text()).to.equal('')
    expect(wrapper.html()).to.contain('<span class="nickname"></span>')
    expect(vm.account.nickname).to.equal(null)
  })

})

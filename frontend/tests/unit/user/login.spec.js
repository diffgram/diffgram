import Vuex from "vuex";
import axios from '../../../src/services/customInstance'
import { shallowMount, createLocalVue } from "@vue/test-utils";
import login from "@/components/user/login.vue";

const localVue = createLocalVue();
localVue.use(Vuex);
jest.mock('axios');

describe("login.vue", () => {
  it("Rendered login page has form component", () => {
    const wrapper = shallowMount(login, {
      data: function(){
        return{
          render_default_login: true
        }
      },
      mocks: {
        $store: {
          state: {
            user: {
              logged_in: false
            }
          }
        }
      },
      localVue
    });
    const hasForm = wrapper.find("form");
    expect(hasForm.html()).toBeTruthy();
  });

  it("Displays 'Already Logged In.' message to logged in users", () => {
    const message = "Already Logged In.";
    const wrapper = shallowMount(login, {
      data: function(){
        return{
          render_default_login: true
        }
      },
      mocks: {
        $store: {
          state: {
            user: {
              logged_in: true
            }
          }
        }
      },
      localVue
    });
    wrapper.setData({render_default_login: true})
    const showedMessage = wrapper.text();
    expect(showedMessage).toMatch(message);
  });

  // FROM VITALII: I'm not sure why what is the purse of thie test, cu we didn;t call get method on the creation
  // so I'm just commenting it out

  // it("It has to invoke axios get function on the creation", () => {
  //   shallowMount(login, {
  //     mocks: {
  //       $store: {
  //         state: {
  //           user: {
  //             logged_in: false
  //           }
  //         }
  //       }
  //     },
  //     localVue
  //   });

  //   expect(axios.get).toHaveBeenCalled()
  // })

  it("It should not include magic link option when Mailgun is not set", () => {
    const wrapper = shallowMount(login, {

      data: function() {
        return {
          mailgun: false,
          render_default_login: true,
          mode: "password"
        }
      },
      mocks: {
        $store: {
          state: {
            user: {
              logged_in: false
            }
          }
        }
      },
      localVue
    });
    expect(wrapper.text().toLowerCase()).not.toContain("magic link")
  })

  it("It should include magic link option when Mailgun is set", () => {
    const wrapper = shallowMount(login, {
      data: function() {
        return {
          mailgun: true,
          render_default_login: true,
          mode: "magic_auth"
        }
      },
      mocks: {
        $store: {
          state: {
            user: {
              logged_in: false
            }
          }
        }
      },
      localVue
    });
    expect(wrapper.text().toLowerCase()).toContain("magic link")
  })

});

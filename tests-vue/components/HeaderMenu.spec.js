import { shallowMount, createLocalVue } from '@vue/test-utils'
import Vuex from 'vuex'

const localVue = createLocalVue();

localVue.use(Vuex);

describe.skip('HeaderMenu.vue', () => {
  let store;

  beforeEach(() => {
    store = new Vuex.Store({
      getters: {
        config: {
          supportEmailAddress: 'boac@berkeley.edu'
        },
        user: {
          firstName: 'John',
          isAdmin: false
        }
      }
    });
  });

  it('verifies support email', () => {
    const wrapper = shallowMount(HeaderMenu, { store: store, localVue: localVue });
    expect(wrapper.text()).toContain('boac@berkeley.edu');
  });
});

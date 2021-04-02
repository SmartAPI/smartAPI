import { mount } from '@vue/test-utils'
import MetaHead from "@/components/MetaHead"

// test should be structured > Arrange, Act, Assert
// Arrange : set up the scenario for the test
// Act: simulate how a user would interact with the component
// Assert: make assertions about how we expect the current state of the component to be

describe('MetaHead', () => {
  it('dynamic metadata tags contain custom text', () => {

    let title = 'My Page';
    let description = 'Some description about my page';

    const wrapper = mount(MetaHead, {
      teleportTarget: document.body,
      props: { 
        title,
        description
      },
      global:{
        mocks: {
          $route:{fullPath: 'full/path'}
        },
      }
    })
    expect(wrapper.html()).toContain(title)
    expect(wrapper.html()).toContain(description)
  })
})

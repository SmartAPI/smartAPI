import { mount } from '@vue/test-utils'
import MetaHead from "@/components/MetaHead"
import Footer from "@/components/Footer"
import UptimeStatus from "@/components/UptimeStatus"
import SourceStatus from "@/components/SourceStatus"

// test should be structured > Arrange, Act, Assert
// Arrange : set up the scenario for the test
// Act: simulate how a user would interact with the component
// Assert: make assertions about how we expect the current state of the component to be

//TODO looking for a way to test teleportation
describe('MetaHead', () => {
  it('Dynamic metadata tags contain custom text', () => {
    //Arrange
    let title = 'My Page';
    let description = 'Some description about my page';

    const options = {
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
    }

    const wrapper = mount(MetaHead, options)
    //Assert
    expect(wrapper.html()).toContain(title)
    expect(wrapper.html()).toContain(description)
  })
})

describe('Footer', () => {
  it('Footer copyright year is current year', () => {
    //Arrange
    document.body.innerHTML = `
      <body>
        <div id="app"></div>
      </body>
    `
    const options = {
      attachTo: document.getElementById('app'),
      global:{
        //replace children components with dummies
        stubs: {
          Image: {template: '<span>image</span>'},
          'router-link': {template: '<span>link</span>'}
        },
      }
    }
    const wrapper = mount(Footer, options)
    //Assert
    expect(wrapper.get('#year').text()).toContain('2021')
  })
})

describe('UptimeStatus', () => {
  it('Uptime badge displays expected status', async () => {
    //Arrange
    const options = {
      props: { 
        api:{
          _status:{
            uptime_status: 'good'
          }
        }
      }
    }
    const wrapper = mount(UptimeStatus, options)
    await wrapper.vm.$nextTick();
    //Assert
    expect(wrapper.get('.center-align').get('small').text()).toContain('PASS')
  })
})

describe('SourceStatus', () => {
  it('Source badge displays expected status', async () => {
    //Arrange
    const options = {
      props: { 
        api:{
          _status:{
            refresh_status: 499
          }
        }
      }
    }
    const wrapper = mount(SourceStatus, options)
    await wrapper.vm.$nextTick();
    //Assert
    expect(wrapper.get('.center-align').get('small').text()).toContain('INVALID')
  })
})

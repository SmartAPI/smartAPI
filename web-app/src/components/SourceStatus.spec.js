import { mount } from '@vue/test-utils'
import SourceStatus from '@/components/SourceStatus.vue'

describe('SourceStatus.vue', () => {
  const cases = [
    { status: 200, expectedText: 'OK' },
    { status: 299, expectedText: 'OK' },
    { status: 404, expectedText: 'NOT FOUND' },
    { status: 499, expectedText: 'INVALID' },
    { status: 599, expectedText: 'BROKEN' },
    { status: undefined, expectedText: 'N/A' },
  ]

  cases.forEach(({ status, expectedText }) => {
    it(`displays "${expectedText}" when refresh_status is ${status}`, async () => {
      const wrapper = mount(SourceStatus, { props: { refresh_status: status } })

      // Wait for Vue to update the DOM after mounted()
      await wrapper.vm.$nextTick()

      // Check only the inner div with the status
      const statusDiv = wrapper.find('div.white-text.center-align')
      expect(statusDiv.text()).toBe(expectedText)
    })
  })
})

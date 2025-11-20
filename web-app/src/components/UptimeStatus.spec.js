import { mount } from '@vue/test-utils'
import UptimeStatus from '@/components/UptimeStatus.vue'

describe('UptimeStatus.vue', () => {
  const cases = [
    { status: 'pass', expectedText: 'PASS' },
    { status: 'fail', expectedText: 'FAIL' },
    { status: 'unknown', expectedText: 'UNKNOWN' },
    { status: 'incompatible', expectedText: 'INCOMPATIBLE' },
    { status: undefined, expectedText: 'N/A' },
  ]

  cases.forEach(({ status, expectedText }) => {
    it(`displays "${expectedText}" when uptime_status is ${status}`, async () => {
      const wrapper = mount(UptimeStatus, { props: { uptime_status: status } })

      // Wait for mounted() updates
      await wrapper.vm.$nextTick()

      // Only check the inner div with the status text
      const statusDiv = wrapper.find('div.white-text.center-align')
      expect(statusDiv.text()).toBe(expectedText)
    })
  })
})

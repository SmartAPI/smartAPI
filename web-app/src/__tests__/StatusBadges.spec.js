import { describe, it, expect } from 'vitest';

import { mount } from '@vue/test-utils';
import SourceStatus from '@/components/SourceStatus.vue';
import UptimeStatus from '@/components/UptimeStatus.vue';

describe('SourceStatus Component', () => {
  const statuses = [
    { status: 200, text: 'OK', clss: 'green' },
    { status: 299, text: 'OK', clss: 'green' },
    { status: 499, text: 'INVALID', clss: 'red' },
    { status: 599, text: 'BROKEN', clss: 'purple' },
    { status: 404, text: 'NOT FOUND', clss: 'orange' },
    { status: undefined, text: 'N/A', clss: 'grey darken-1' },
    { status: 123, text: '123', clss: 'black' },
  ];

  statuses.forEach(v => {
    it(`renders proper URL monitor status for status ${v.status}`, () => {
      const wrapper = mount(SourceStatus, { props: { refresh_status: v.status } });
      const statusElement = wrapper.find('.white-text.center-align');
      
      setTimeout(() => {
        expect(statusElement.text()).toBe(v.text);
        expect(statusElement.classes()).toContain(v.clss);
      }, 200);
    });
  });
});

describe('UptimeStatus Component', () => {
  const statuses = [
    { uptime_status: 'unknown', text: 'UNKNOWN', clss: 'orange' },
    { uptime_status: 'pass', text: 'PASS', clss: 'green' },
    { uptime_status: 'fail', text: 'FAIL', clss: 'red' },
    { uptime_status: 'incompatible', text: 'INCOMPATIBLE', clss: 'blue' },
    { uptime_status: undefined, text: 'N/A', clss: 'grey' },
    { uptime_status: 'other', text: 'N/A', clss: 'grey' }
  ];

  statuses.forEach(v => {
    it(`renders proper uptime status for status ${v.uptime_status}`, () => {
      const wrapper = mount(UptimeStatus, { props: { uptime_status: v.uptime_status } });
      const statusElement = wrapper.find('.white-text.center-align');

      setTimeout(() => {
        expect(statusElement.text()).toBe(v.text);
        expect(statusElement.classes()).toContain(v.clss);
      }, 200);
    });
  });
});

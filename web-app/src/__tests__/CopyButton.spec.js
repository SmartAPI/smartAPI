import { mount } from '@vue/test-utils';
import { describe, it, expect, vi } from 'vitest';
import CopyButton from '@/components/CopyButton.vue';

describe('CopyButton.vue', () => {
  it('renders slot content when not animating', () => {
    const wrapper = mount(CopyButton, {
      slots: {
        title: 'Click Me'
      }
    });
    expect(wrapper.text()).toContain('Click Me');
  });

  it('renders "Copied!" when animating', async () => {
    const wrapper = mount(CopyButton, {
      slots: {
        title: 'Click Me'
      }
    });

    await wrapper.vm.animate();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('Copied!');
  });

  it('has correct classes and attributes', () => {
    const wrapper = mount(CopyButton, {
      props: {
        copy: 'Sample text'
      }
    });

    const button = wrapper.find('button');

    expect(button.attributes('data-clipboard-text')).toBe('Sample text');
    expect(button.classes()).toContain('CopyButton');
    expect(button.classes()).toContain('copyBtn');
    expect(button.classes()).toContain(`cp${wrapper.vm.badgeID}`);
  });
});

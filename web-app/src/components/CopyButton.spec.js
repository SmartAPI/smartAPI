import { mount } from '@vue/test-utils';
import { vi, describe, it, expect } from 'vitest';
import CopyButton from '../components/CopyButton.vue';


describe('CopyButton.vue', () => {
  it('renders slot content', () => {
    const wrapper = mount(CopyButton, {
      global: {
        mocks: {
          $toast: { success: vi.fn() },
        },
      },
      slots: {
        title: 'Copy this text',
      },
    });

    expect(wrapper.text()).toContain('Copy this text');
  });

  it('shows "Copied!" when clicked', async () => {
    const toastMock = vi.fn();
    const wrapper = mount(CopyButton, {
      global: {
        mocks: {
          $toast: { success: toastMock },
        },
      },
      props: {
        copy: 'Hello world',
      },
    });

    // Simulate click
    await wrapper.find('button').trigger('click');

    // Toast called
    expect(toastMock).toHaveBeenCalledWith('Copied to Clipboard');

    // Animation toggle
    expect(wrapper.text()).toContain('Copied!');

    // Wait for the reset timeout
    await new Promise((resolve) => setTimeout(resolve, 1600));
    expect(wrapper.vm.showAnimation).toBe(false);
  });
});

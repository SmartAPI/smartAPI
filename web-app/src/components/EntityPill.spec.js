import { mount } from '@vue/test-utils';
import { describe, it, expect, vi } from 'vitest';
import EntityPill from '../components/EntityPill.vue';

describe('EntityPill.vue', () => {
  const mockStore = {
    getters: {
      getEntityColor: vi.fn(() => '#ff0000')
    }
  };

  const subjects = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];

  it('renders object name and limited subjects by default', () => {
    const wrapper = mount(EntityPill, {
      props: { object: 'Gene', subjects },
      global: { mocks: { $store: mockStore } }
    });

    // Shows the object
    expect(wrapper.text()).toContain('Gene');

    // Only 7 subjects visible by default
    const lis = wrapper.findAll('li');
    expect(lis.length).toBe(8); // 7 + 1 "See More" button
    expect(lis[0].text()).toBe('A');

    // The color getter is called
    expect(mockStore.getters.getEntityColor).toHaveBeenCalledWith('Gene');
  });

  it('shows all subjects when "See More" is clicked', async () => {
    const wrapper = mount(EntityPill, {
      props: { object: 'Protein', subjects },
      global: { mocks: { $store: mockStore } }
    });

    // Click "See More"
    const seeMore = wrapper.find('.blue-text');
    expect(seeMore.exists()).toBe(true);
    await seeMore.trigger('click');

    // Should now show all subjects
    expect(wrapper.vm.viewingAll).toBe(true);
    const lisAfter = wrapper.findAll('li');
    expect(lisAfter.length).toBe(subjects.length + 1); // all + "See Less"

    // Text should change to "See Less"
    expect(wrapper.text()).toContain('See Less');
  });

  it('hides back to limited subjects when "See Less" is clicked', async () => {
    const wrapper = mount(EntityPill, {
      props: { object: 'Protein', subjects },
      global: { mocks: { $store: mockStore } }
    });

    // Expand
    await wrapper.find('.blue-text').trigger('click');
    // Collapse
    await wrapper.find('.blue-text').trigger('click');

    expect(wrapper.vm.viewingAll).toBe(false);
    expect(wrapper.text()).toContain('See More');
  });
});

import { mount } from '@vue/test-utils';
import { describe, it, expect } from 'vitest';
import EntityPill from '@/components/EntityPill.vue';

const mockStore = {
  getters: {
    getEntityColor: (object) => {
      // Mock color logic for the object
      return object === 'Entity' ? '#FF0000' : '#00FF00';
    }
  }
};

describe('EntityPill.vue', () => {
  it('renders the correct object text', () => {
    const wrapper = mount(EntityPill, {
      props: {
        object: 'Entity',
        subjects: []
      },
      global: {
        mocks: {
          $store: mockStore
        }
      }
    });

    expect(wrapper.text()).toContain('Entity');
  });

  it('renders subjects correctly and handles "See More/Less" functionality', async () => {
    const subjects = ['Subject 1', 'Subject 2', 'Subject 3', 'Subject 4', 'Subject 5', 'Subject 6', 'Subject 7', 'Subject 8'];
    
    const wrapper = mount(EntityPill, {
      props: {
        object: 'Entity',
        subjects
      },
      global: {
        mocks: {
          $store: mockStore
        }
      }
    });

    // Check if only limited subjects are rendered initially
    const listItems = wrapper.findAll('li');
    expect(listItems).toHaveLength(8);

    // Check if the "See More" button is displayed correctly
    const seeMoreButton = wrapper.find('.blue-text.pointer');
    expect(seeMoreButton.exists()).toBe(true);
    expect(seeMoreButton.text()).toContain('See More (8)');

    // Simulate clicking "See More"
    await seeMoreButton.trigger('click');

    // Check if all subjects are rendered after clicking "See More"
    expect(wrapper.findAll('li')).toHaveLength(9);
    expect(seeMoreButton.text()).toContain('See Less');
  });
});

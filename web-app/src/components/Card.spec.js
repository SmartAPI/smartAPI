import { describe, it, expect } from 'vitest';
import { mount, RouterLinkStub } from '@vue/test-utils';
import Card from '../components/Card.vue';

// We can stub Pikaboo since we don't need to test it here
const stubs = {
  Pikaboo: {
    template: '<div class="pikaboo-stub"></div>'
  },
  RouterLink: RouterLinkStub
};

describe('Card.vue', () => {
  it('renders title properly test', () => {
    const wrapper = mount(Card, {
      props: { title: 'Hello User' },
      global: { stubs }
    });
    expect(wrapper.find('.card-title').text()).toBe('Hello User');
  });

  it('renders description as HTML', () => {
    const htmlDesc = '<strong>Bold text</strong> and normal text';
    const wrapper = mount(Card, {
      props: { description: htmlDesc },
      global: { stubs }
    });
    // v-html renders raw HTML, so innerHTML should match
    expect(wrapper.find('.card-content p').html()).toContain(htmlDesc);
  });

  it('renders Pikaboo component', () => {
    const wrapper = mount(Card, {
      props: { image: 'some-image.jpg' },
      global: { stubs }
    });
    const pikaboo = wrapper.find('.pikaboo-stub');
    expect(pikaboo.exists()).toBe(true);
  });

  it('applies inline style width from prop', () => {
    const wrapper = mount(Card, {
      props: { width: '500px' },
      global: { stubs }
    });
    const card = wrapper.find('.card');
    expect(card.attributes('style')).toContain('width: 500px;');
  });

  it('renders a router-link with the correct "to" prop', () => {
    const wrapper = mount(Card, {
      props: { link: '/details/123' },
      global: { stubs }
    });
    const routerLink = wrapper.findComponent(RouterLinkStub);
    expect(routerLink.exists()).toBe(true);
    expect(routerLink.props('to')).toBe('/details/123');
  });

  it('has proper structure', () => {
    const wrapper = mount(Card, {
      global: { stubs }
    });
    expect(wrapper.find('.card-content').exists()).toBe(true);
    expect(wrapper.find('.card-action').exists()).toBe(true);
  });
});

import { describe, it, expect } from 'vitest';
import { nextTick } from 'vue';
import { mount } from '@vue/test-utils';
import CollapsibleText from '../components/CollapsibleText.vue';

describe('CollapsibleText.vue', () => {
  const sampleMarkdown = '**Bold text** and *italic* text';

  it('renders markdown as HTML on mount', async () => {
    const wrapper = mount(CollapsibleText, {
      props: { text: sampleMarkdown }
    });

    // Wait for mounted() and DOM updates to complete
    await nextTick();

    const html = wrapper.find('.blue-grey-text').html();

    expect(html).toContain('<strong>Bold text</strong>');
    expect(html).toContain('<em>italic</em>');
  });

  it('starts collapsed by default', () => {
    const wrapper = mount(CollapsibleText, {
      props: { text: sampleMarkdown }
    });

    expect(wrapper.vm.fullTXT).toBe(false);
    expect(wrapper.find('.whiteFadeBox').exists()).toBe(true);
    expect(wrapper.find('.expandButtonMore').text()).toContain('Click to expand');
    expect(wrapper.find('.expandContainer').classes()).toContain('max-height-200');
  });

  it('expands text when "Click to expand" is clicked', async () => {
    const wrapper = mount(CollapsibleText, {
      props: { text: sampleMarkdown }
    });

    await wrapper.find('.expandButtonMore').trigger('click');

    expect(wrapper.vm.fullTXT).toBe(true);
    expect(wrapper.find('.whiteFadeBox').exists()).toBe(false);
    expect(wrapper.find('.expandContainer').classes()).toContain('max-height-none');
  });

  it('shows collapse buttons when expanded', async () => {
    const wrapper = mount(CollapsibleText, {
      props: { text: sampleMarkdown }
    });

    await wrapper.find('.expandButtonMore').trigger('click');

    const collapseButtons = wrapper.findAll('.expandButtonLess');
    expect(collapseButtons.length).toBeGreaterThan(0);
    expect(collapseButtons[0].text()).toContain('Collapse');
  });

  it('collapses again when "Collapse" is clicked', async () => {
    const wrapper = mount(CollapsibleText, {
      props: { text: sampleMarkdown }
    });

    // Expand first
    await wrapper.find('.expandButtonMore').trigger('click');
    expect(wrapper.vm.fullTXT).toBe(true);

    // Collapse
    await wrapper.find('.expandButtonLess').trigger('click');
    expect(wrapper.vm.fullTXT).toBe(false);
    expect(wrapper.find('.whiteFadeBox').exists()).toBe(true);
  });
});

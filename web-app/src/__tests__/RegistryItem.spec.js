import { shallowMount } from '@vue/test-utils';
import { describe, it, expect, beforeEach } from 'vitest';
import RegistryItem from '@/components/RegistryItem.vue';

describe('RegistryItem.vue', () => {
  let wrapper;
  const apiMock = {
    info: { title: 'Test API', version: '1.0', description: 'API Description' },
    _status: { uptime_status: 'OK', uptime_msg: 'All good' },
    _meta: { username: 'testUser', has_metakg: true, last_updated: '2024-09-01', url: 'http://api.com' },
    paths: {
      '/example': {
        get: { summary: 'Get example' }
      }
    },
    tags: [{ name: 'tag1' }, { name: 'tag2' }],
    openapi: '3.0.1'
  };
  const userMock = { login: 'testUser' };
  const mockRoute = {
    path: '/test-route',
    query: {
      tags: 'example-tag'
    }
  };

  beforeEach(() => {
    wrapper = shallowMount(RegistryItem, {
      propsData: { api: apiMock, user: userMock },
      mocks: {
        $route: mockRoute
      }
    });
  });

  it('renders the API title and version correctly', () => {
    const title = wrapper.find('.card-title span.blue-grey-text');
    const version = wrapper.find('.card-title small.grey-text');
    expect(title.text()).toBe('Test API');
    expect(version.text()).toBe('1.0');
  });

  it('shows the correct badges based on the API version', () => {
    const oasBadge = wrapper.find('.versionBadge.green');
    expect(oasBadge.exists()).toBe(true);
    expect(oasBadge.text()).toContain('OAS3');
  });

  it('renders the API operations', () => {
    const operations = wrapper.findAll('tbody tr');
    expect(operations.length).toBe(1); // Only 1 operation is defined
    expect(operations.at(0).text()).toContain('GET');
    expect(operations.at(0).text()).toContain('/example');
  });

  it('toggles the details view when clicking the Details button', async () => {
    const detailsButton = wrapper.find('button.indigo');
    await detailsButton.trigger('click');
    const detailsContent = wrapper.find('.detailsBack');
    expect(detailsContent.exists()).toBe(true); // Details should be shown
  });

  it('renders the MetaKG button and toggles view', async () => {
    const metakgButton = wrapper.find('button.purple');
    expect(metakgButton.exists()).toBe(true); // MetaKG button should be visible
    await metakgButton.trigger('click');
    const metakgView = wrapper.findComponent({ name: 'RegistryMetaKG' });
    expect(metakgView.exists()).toBe(true); // MetaKG view should be rendered
  });
});

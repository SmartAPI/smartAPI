import { mount } from '@vue/test-utils'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import MarkDown from '../components/MarkDown.vue'
import axios from 'axios'

vi.mock('axios')

// Helper to wait for all promises + Vue DOM updates
const flushAll = async () => {
  await Promise.resolve()
  await Promise.resolve()
  await new Promise((r) => setTimeout(r))
}

describe('MarkDown.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('fetches markdown and renders it as HTML', async () => {
    const fakeMarkdown = '# Hello World\nThis is **markdown**.'
    axios.get.mockResolvedValueOnce({ data: fakeMarkdown })

    const wrapper = mount(MarkDown, {
      props: { url: '/fake-url.md' }
    })

    await flushAll()

    expect(axios.get).toHaveBeenCalledWith('/fake-url.md')

    const html = wrapper.find('.white').html()
    expect(html).toContain('<h1>Hello World</h1>')
    expect(html).toContain('<strong>markdown</strong>')
  })

  it('shows an edit link when editLink prop is provided', async () => {
    axios.get.mockResolvedValueOnce({ data: 'content' })

    const wrapper = mount(MarkDown, {
      props: { url: '/fake.md', editLink: 'https://github.com/edit' }
    })

    await flushAll()

    const link = wrapper.find('a.right')
    expect(link.exists()).toBe(true)
    expect(link.attributes('href')).toBe('https://github.com/edit')
  })


  it('refetches when the url prop changes', async () => {
    axios.get.mockResolvedValue({ data: 'Initial content' })

    const wrapper = mount(MarkDown, {
      props: { url: '/first.md' }
    })

    await flushAll()

    axios.get.mockResolvedValue({ data: 'Updated content' })
    await wrapper.setProps({ url: '/second.md' })
    await flushAll()

    expect(axios.get).toHaveBeenCalledWith('/second.md')
    expect(wrapper.html()).toContain('Updated content')
  })
})

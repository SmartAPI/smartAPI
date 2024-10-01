// import { describe, expect, vi } from 'vitest';
// import { mount } from '@vue/test-utils';
// import { createRouter, createWebHistory } from 'vue-router';
// import App from '@/App.vue';
// import Egg from '@/components/Icons/Egg.vue';
// import { routes } from '../router/routes'
// import { createStore } from 'vuex';

// const router = createRouter({
//   history: createWebHistory(),
//   routes
// });

// const actions = {
//   loadTagFilters: vi.fn(),
//   loadOwnerFilters: vi.fn(),
//   loadTranslatorFilters: vi.fn(),
// };

// const store = createStore({
//   actions,
// });

// // Mock SweetAlert2
// const mockSwal = vi.fn();

// describe('renders component part of Home component via routing', async () => {
//   router.push('/');
//   await router.isReady();

//   // Create a mock element and append it to the document body
//   const cookieButton = document.createElement('button');
//   cookieButton.id = 'cookieButton';
//   document.body.appendChild(cookieButton);

//   // Create a mock element and append it to the document body
//   const yearSpan = document.createElement('span');
//   yearSpan.id = 'year';
//   document.body.appendChild(yearSpan);

//   const wrapper = mount(App, {
//     global: {
//       plugins: [router, store],
//       mocks: {
//         '$swal': mockSwal,
//       },
//     }
//   });

//   expect(wrapper.findComponent(Egg).exists()).toBe(true);
// });

// // describe('renders component part of ABOUT view via routing', async () => {
// //   router.push('/about');
// //   await router.isReady();

// //   // Create a mock element and append it to the document body
// //   const yearSpan = document.createElement('span');
// //   yearSpan.id = 'year';
// //   document.body.appendChild(yearSpan);

// //     const wrapper = mount(App, {
// //     global: {
// //       plugins: [router, store]
// //     }
// //   });

// //       setTimeout(() => {
// //         expect(wrapper).toContain("BUILDING A CONNECTED NETWORK OF FAIR APIS");
// //       }, 200);
// // });

// // describe('renders About component via routing', async () => {
// //   router.push('/about');
// //   await router.isReady();

// //   const wrapper = mount(App, {
// //     global: {
// //       plugins: [router]
// //     }
// //   });

// //   expect(wrapper.findComponent(About).exists()).toBe(true);
// // });

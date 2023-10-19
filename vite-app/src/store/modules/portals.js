import translator_img from '@/assets/img/TranslatorLogo.jpg'

export const portals = {
  state: () => ({
    portals: [
      {
        name: 'translator',
        title: 'Translator',
        link: '/portal/translator',
        image: translator_img,
        description:
          'This program focuses on building tools for massive knowledge integration in support of biomedical and translational science. <a target="_blank" rel="noreferrer" href="https://ncats.nih.gov/translator">Learn more</a>'
      }
    ]
  }),
  strict: true,
  getters: {
    portals: (state) => {
      return state.portals
    }
  }
}

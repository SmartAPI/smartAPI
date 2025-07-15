import scripps_img from '@/assets/img/scripps.svg';
import mu_img from '@/assets/img/mu.png';
import header_img from '@/assets/img/header-logo.png';

export const about = {
  state: () => ({
    otherMembers: [
      {
        name: 'Ruben Verborgh',
        organization: 'Ghent University'
      },
      {
        name: 'Paul Avillach',
        organization: 'Harvard University'
      },
      {
        name: 'Gabor Korodi',
        organization: 'Harvard University'
      },
      {
        name: 'Raymond Terryn',
        organization: 'University of Miami'
      },
      {
        name: 'Kathleen Jagodnik',
        organization: 'Mount Sinai'
      },
      {
        name: 'Pedro Assis',
        organization: 'Standford University'
      },
      {
        name: 'Marcin Pilarczyk',
        organization: 'University of Cincinnati'
      }
    ],
    contributors: [
      {
        image: scripps_img,
        name: '',
        members: [
          {
            name: 'Chunlei',
            lastname: 'Wu',
            title: 'Professor',
            work_logo: scripps_img,
            work_website: '//www.scripps.edu/',
            bio: "Chunlei Wu is a Professor in the Department of Integrative Structure and Computational Biology at Scripps Research. Prior to joining Scripps in July 2011, he was the Research Investigator II at the Genomics Institute of the Novartis Research Foundation (GNF) in San Diego, CA.  More details about Chunlei's lab are available at //wulab.io.",
            education: [
              'Ph.D., Biomathmetics and biostatistics, The University of Texas Health Science Center at Houston'
            ],
            image: '//www.gravatar.com/avatar/108605daee6b3c24d02db9753637a66b?s=200',
            personal_site: '//wulab.io/',
            links: [
              { title: 'twitter', href: '//twitter.com/chunleiwu' },
              { title: 'github', href: '//github.com/newgene' },
              { title: 'linkedin', href: '//www.linkedin.com/in/chunleiwu' }
            ]
          },
          {
            name: 'Andrew',
            lastname: 'Su',
            title: 'Professor',
            work_logo: scripps_img,
            work_website: '//www.scripps.edu/',
            bio: 'Andrew is a Professor at Scripps Research in the Department of Integrative Structure and Computational Biology. His research focuses on building and applying bioinformatics infrastructure for biomedical discovery. His research has a particular emphasis on leveraging crowdsourcing for genetics and genomics. Representative projects include the Gene Wiki, BioGPS, MyGene.Info, and Mark2Cure, each of which engages “the crowd” to help organize biomedical knowledge. These resources are collectively used millions of times every month by members of the research community, by students, and by the general public.',
            education: [
              'Ph.D., Chemistry; The Scripps Research Institute',
              'BA, Chemistry, Computing and Information Systems, and Integrated Science; Northwestern University'
            ],
            image: '//avatars0.githubusercontent.com/u/2635409?s=460&v=4',
            personal_site: '//sulab.org/',
            links: [
              { title: 'twitter', href: '//twitter.com/andrewsu' },
              { title: 'github', href: '//github.com/andrewsu' },
              { title: 'linkedin', href: '//www.linkedin.com/in/andrewsu/' }
            ]
          },
          {
            name: 'Marco',
            lastname: 'Cano',
            title: 'Research Programmer III',
            work_logo: scripps_img,
            work_website: '//www.scripps.edu/',
            bio: "I'm a full-stack web developer with a background in Web/Graphic Design and Multimedia Animation. Love to build professional modern websites using the latest technologies and the best possible UI/UX design. Currently working for the Su/Wu Lab at Scripps Research.  Current projects include: //BioThings.io and //SmartAPI.info",
            education: [
              '3D Animation and Multimedia Design -Palomar College',
              'Full Stack Web Development – UCSD'
            ],
            image: '//avatars1.githubusercontent.com/u/23092057?s=460&v=4',
            personal_site: '//www.marcodarko.com/',
            links: [
              { title: 'twitter', href: '' },
              { title: 'github', href: '//github.com/marcodarko' },
              { title: 'linkedin', href: '//www.linkedin.com/in/marco-alvarado-cano' }
            ]
          },
          {
            name: 'Nichollette',
            lastname: 'Acosta',
            title: 'Research Programmer III',
            work_logo: scripps_img,
            work_website: '//sulab.org/',
            bio: 'I am joining as a research programmer in 2021. I enjoy machine learning, bioinformatics and building software tools. Prior to this, I coded, primarily with fMRI brain data, for a Neuropsychology Ingestive Behavior lab.',
            education: ['BSc. in Computer Science, Minor in Bioinformatics, UNC at Charlotte'],
            image: '//wulab.io/content/images/2021/09/nicholla.jpg',
            personal_site: '#',
            links: [
              { title: 'twitter', href: '' },
              { title: 'github', href: '//github.com/NikkiBytes' },
              { title: 'linkedin', href: '//www.linkedin.com/in/nichollette-acosta/' }
            ]
          },
          {
            name: 'Everaldo Rodrigo',
            lastname: 'Rodolpho',
            title: 'Research Programmer III',
            work_logo: scripps_img,
            work_website: '//sulab.org/',
            bio: 'Digital Convergence of SCORM Learning Objects.',
            education: ['M.S. Computer Science'],
            image: '//wulab.io/content/images/2022/12/everaldo_rodolpho.jpeg',
            personal_site: '#',
            links: [
              { title: 'twitter', href: '' },
              { title: 'github', href: '' },
              { title: 'linkedin', href: '' }
            ]
          },
          {
            name: 'Colleen',
            lastname: 'Xu',
            title: 'Research Programmer III',
            work_logo: scripps_img,
            work_website: '//sulab.org/',
            bio: 'Colleen is a research programmer in the Department of Integrative, Structural and Computational Biology at Scripps Research.',
            education: [
              'M.S. OHSU, Bioinformatics and Computational Biomedicine',
              'B.A. Northwestern University, Biology and Chemistry'
            ],
            image: '//sulab.org/wp-content/uploads/2020/08/colleen-xu-resized-300x289.jpg',
            personal_site: '#',
            links: [
              { title: 'twitter', href: '//twitter.com/BioBabblingHere' },
              { title: 'github', href: '//github.com/colleenXu' },
              { title: 'linkedin', href: '//www.linkedin.com/in/colleenxu/' }
            ]
          }
        ]
      },
      {
        image: mu_img,
        name: '',
        members: [
          {
            name: 'Michel',
            lastname: 'Dumontier',
            title: 'Professor',
            work_logo: mu_img,
            work_website: '//www.maastrichtuniversity.nl/',
            bio: 'Dr. Michel Dumontier is a Distinguished Professor of Data Science at Maastricht University. His research focuses on the development of computational methods for scalable integration and reproducible analysis of FAIR (Findable, Accessible, Interoperable and Reusable) data across scales - from molecules, tissues, organs, individuals, populations to the environment. His group combines semantic web technologies with effective indexing, machine learning and network analysis for drug discovery and personalized medicine. ',
            education: [
              '2004 PhD, Biochemistry (Bioinformatics) from University of Toronto',
              '1998 Bachelor of Sciencee, Biochemistry from University of Manitoba'
            ],
            image: '//avatars3.githubusercontent.com/u/993852?s=460&v=4',
            personal_site: '//dumontierlab.com/#',
            links: [
              { title: 'twitter', href: '//twitter.com/micheldumontier' },
              { title: 'github', href: '//github.com/micheldumontier' },
              { title: 'linkedin', href: '//www.linkedin.com/in/dumontier' }
            ]
          }
        ]
      },
      {
        image: header_img,
        name: 'Additional Team Members',
        members: []
      }
    ],
    pastContributors: [
      {
        name: 'Jiwen (Kevin)',
        lastname: 'Xin'
      },
      {
        name: 'Xinghua (Jerry)',
        lastname: 'Zhou'
      },
      {
        name: 'Cyrus',
        lastname: 'Afrasiabi'
      },
      {
        name: 'Shima',
        lastname: 'Dastgheib'
      },
      {
        name: 'Trish',
        lastname: 'Whetzel'
      },
      {
        name: 'Amrapali',
        lastname: 'Zaveri'
      },
      {
        name: 'Alexander',
        lastname: 'Malic'
      }
    ]
  }),
  strict: true,
  getters: {
    contributors: (state) => {
      return state.contributors;
    },
    otherMembers: (state) => {
      return state.otherMembers;
    },
    pastContributors: (state) => {
      return state.pastContributors;
    }
  }
};

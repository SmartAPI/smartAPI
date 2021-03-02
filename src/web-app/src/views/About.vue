<template>
<main id="about-app" class="white" style="width: 100%;">

  <section class="container center padding20">
    <Image img_width="40%" img_name="logo-small-text.svg" class="hide-on-med-only hide-on-large-only"></Image>
    <Image img_width="45%" img_name="logo-medium-text.svg" class="hide-on-small-only hide-on-large-only"></Image>
    <Image img_width="50%" img_name="logo-large-text.svg" class="hide-on-small-only hide-on-med-only" :style="{maxWidth: '600px'}"></Image>
    <h3 class="blue-text flow-text bold">BUILDING A CONNECTED NETWORK OF FAIR APIS</h3>
    <p class="blue-grey-text flow-text">
      The SmartAPI project aims to maximize the FAIRness of web-based Application Programming Interfaces (APIs).
      Rich metadata is essential to properly describe your API so that it becomes discoverable, connected, and reusable.
      We have developed a openAPI-based specification for defining the key API metadata elements and value sets.
      SmartAPI's leverage the <a href="https://www.openapis.org/" target="_blank">Open API</a> specification v3 and <a href="https://json-ld.org/" target="_blank">JSON-LD</a> for providing semantically annotated JSON content that can be treated as Linked Data.
    </p>
    <p class="blue-grey-text flow-text">
      All of the API metadata available from the SmartAPI registry is FAIR too. <a href="https://fairsharing.org/biodbcore-001171/" target="_blank">Learn more.</a>
    </p>
  </section>

  <section class="container center padding20">
    <h2 class="blue-text flow-text bold">What is FAIR?</h2>
    <table class="fairTable">
      <tbody>
        <tr>
          <td>
            <span class="fair">F</span>
          </td>
          <td>
            <p class="blue-grey-text flow-text">
              <b>Findable:</b> The first step in (re)using data is to find it.
              Metadata and data should be easy to find for both humans and computers.
              Machine-readable metadata are essential for automatic discovery of datasets and services, so this is an essential component of the FAIRification process.
            </p>
          </td>
        </tr>
        <tr>
          <td>
            <span class="fair">A</span>
          </td>
          <td>
            <p class="blue-grey-text flow-text">
              <b>Accessible:</b> Once the user finds the required data, she/he needs to know how can they be accessed, possibly including authentication and authorization.
            </p>
          </td>
        </tr>
        <tr>
          <td>
            <span class="fair">I</span>
          </td>
          <td>
            <p class="blue-grey-text flow-text">
              <b>Interoperable:</b> The data usually need to be integrated with other data.
              In addition, the data need to interoperate with applications or workflows for analysis, storage, and processing.
            </p>
          </td>
        </tr>
        <tr>
          <td>
            <span class="fair">R</span>
          </td>
          <td>
            <p class="blue-grey-text flow-text">
              <b>Reusable:</b> The ultimate goal of FAIR is to optimise the reuse of data.
              To achieve this, metadata and data should be well-described so that they can be replicated and/or combined in different settings.
            </p>
          </td>
        </tr>
      </tbody>
    </table>
  </section>

  <section class="container center padding20">
    <h2 class="blue-text flow-text bold">Team</h2>
    <div class="contributor-container">
      <template v-for='(person, index) in contributors' :key='index'>
        <div v-if='index === 0' class="center padding20 hide-on-small-only" style="width:100%;">
          <img src="../assets/img/scripps.svg" width="400" alt="logo"/>
        </div>
        <div v-if='index === 6' class="center padding20 hide-on-small-only" style="width:100%;">
          <img src="../assets/img/mu.png" width="400" alt="logo"/>
        </div>
        <div v-if='index === 9' class="center padding20 hide-on-small-only" style="width:100%;">
          <h2 class="blue-text flow-text bold">Additional Team Members</h2>
        </div>
        <div href="#modal1" class="contributor-box contributor modal-trigger" @click='popUpDetails(index)'>
          <img class="circle scale-in-center squarePic" width="70%"  :src="person.image" :alt="person.name"/>
          <p class="bold blue-text">{{person.name}} {{person.lastname}}</p>
          <p class="blue-grey-text smallFont">{{person.title}}</p>
          <img class="hide-on-med-only hide-on-large-only" :src="person.work_logo" width="100%" alt="logo"/>
        </div>
      </template>
    </div>
    <div class="col-sm-12">
      <h5 class="flow-text bold blue-text">
        NIH Data Commons API Interoperability Working Group
      </h5>
      <ul>
        <li v-for="(person, i) in otherMembers" :key='i'>
          <span class="blue-text">{{person.name}}</span>, {{person.organization}}
        </li>
      </ul>
    </div>
  </section>

 
  <VModal v-model="showModal" @confirm="confirm">
    <template v-slot:title>{{ 'About ' + selectedPerson.name || 'About' }}</template>
    <div v-if='selectedPerson'  class="white row p-1">
      <div class="col s12 m4 l4">
        <div>
          <img class="circle aboutPic" :style="{width:'80%'}" :src="selectedPerson.image" :alt="selectedPerson.name"/>
          <p>
            <template v-for='link in selectedPerson.links' :key='link'>
              <a v-if="link.href.length > 1" :href="link.href" target="_blank" class="social-icon">
                <i v-if="link.title === 'twitter'" class="fa fa-twitter-square fa-3x" aria-hidden="true"></i>
                <i v-if="link.title === 'linkedin'" class="fa fa-linkedin-square fa-3x" aria-hidden="true"></i>
                <i v-if="link.title === 'github'" class="fa fa-github-square fa-3x" aria-hidden="true"></i>
              </a>
            </template>
          </p>
        </div>
        <p class="grey-text smallFont">
          Search SmartAPI for contributions by {{selectedPerson.name}} {{selectedPerson.lastname}}<br />
          <a class="btn blue smallFont margin20" :href="'/registry?q='+selectedPerson.name+' '+selectedPerson.lastname"><i class="fa fa-search" aria-hidden="true"></i> Search</a>
        </p>
      </div>
      <div class="col s12 m8 l8">
        <p>
          <span style="font-size: 2em;" class="blue-text bold">{{selectedPerson.name}} {{selectedPerson.lastname}}</span> <span class="grey-text">/ {{selectedPerson.title}}</span>
        </p>
        <a :href="selectedPerson.work_website" target="_blank">
          <Image :img_name="selectedPerson.work_logo" img_width="200" :alt="selectedPerson.work_logo"></Image>
        </a>
        <hr />
        <h5>
          About
        </h5>
        <p class="left-align blue-grey-text" style="font-size:.9em; border-left: #e4e4e4 solid 2px; padding: 10px;" v-html="compiledMarkdown(selectedPerson.bio || '')"></p>
        <p>
          <a :href="selectedPerson.personal_site" target="_blank">More About {{selectedPerson.name}} <i class="fa fa-external-link" aria-hidden="true"></i></a>
        </p>
        <hr />
        <h5>
          Education
        </h5>
        <ul class="collection" >
          <template v-for='item in selectedPerson.education' :key="item">
            <li class="collection-item" ><i class="fa fa-university blue-text" aria-hidden="true"></i> {{item}}</li>
          </template>
        </ul>
      </div>
    </div>
  </VModal>

  <section class="blue center" style="padding: 20px 10%;">
    <h2 class="white-text flow-text bold"><i class="fa fa-trophy" aria-hidden="true"></i> Funding Support</h2>
    <p class="white-text padding20 flow-text">
      The SmartAPI project was started in 2015 via the support of a BD2K (Big Data to Knowledge) supplementary grant awarded to Drs. Michel Dumontier and Chunlei Wu.
      It's currently supported by the <a class="underlined white-text" href="https://ncats.nih.gov/translator" target="_blank">Biomedical Data Translator program from NCATS (National Center for Advancing Translational Sciences)</a>.
    </p>
  </section>
</main>
</template>

<script>
import marked from 'marked'

export default {
  components: { },
  name: 'About',
  data: function(){
        return {
          showModal: false,
          selectedPerson:{},
          otherMembers:[
            {
              'name':'Ruben Verborgh',
              'organization':'Ghent University'
            },
            {
              'name':'Paul Avillach',
              'organization':'Harvard University'
            },
            {
              'name':'Gabor Korodi',
              'organization':'Harvard University'
            },
            {
              'name':'Raymond Terryn',
              'organization':'University of Miami'
            },
            {
              'name':'Kathleen Jagodnik',
              'organization':'Mount Sinai'
            },
            {
              'name':'Pedro Assis',
              'organization':'Standford University'
            },
            {
              'name':'Marcin Pilarczyk',
              'organization':'University of Cincinnati'
            },
          ],
          contributors:[
            {
              name:'Chunlei',
              lastname:'Wu',
              title:'Associate Professor',
              work_logo:'scripps.svg',
              work_website:'https://www.scripps.edu/',
              bio:'Chunlei Wu is an Associate Professor in the Department of Integrative Structure and Computational Biology at Scripps Research. Prior to joining Scripps in July 2011, he was the Research Investigator II at the Genomics Institute of the Novartis Research Foundation (GNF) in San Diego, CA.  More details about Chunlei\'s lab are available at https://wulab.io.',
              education:['Ph.D., Biomathmetics and biostatistics, The University of Texas Health Science Center at Houston'],
              image:'http://www.gravatar.com/avatar/108605daee6b3c24d02db9753637a66b?s=200',
              personal_site:'https://wulab.io/',
              links:[
                {title:"twitter", href:'https://twitter.com/chunleiwu'},
                {title:"github", href:'https://github.com/newgene'},
                {title:"linkedin", href:'https://www.linkedin.com/in/chunleiwu'},
              ]
            },
            {
              name:'Andrew',
              lastname:'Su',
              title:'Professor',
              work_logo:'scripps.svg',
              work_website:'https://www.scripps.edu/',
              bio:'Andrew is a Professor at Scripps Research in the Department of Integrative Structure and Computational Biology. His research focuses on building and applying bioinformatics infrastructure for biomedical discovery. His research has a particular emphasis on leveraging crowdsourcing for genetics and genomics. Representative projects include the Gene Wiki, BioGPS, MyGene.Info, and Mark2Cure, each of which engages “the crowd” to help organize biomedical knowledge. These resources are collectively used millions of times every month by members of the research community, by students, and by the general public.',
              education:['Ph.D., Chemistry; The Scripps Research Institute','BA, Chemistry, Computing and Information Systems, and Integrated Science; Northwestern University'],
              image:'https://avatars0.githubusercontent.com/u/2635409?s=460&v=4',
              personal_site:'http://sulab.org/',
              links:[
                {title:"twitter", href:'https://twitter.com/andrewsu'},
                {title:"github", href:'https://github.com/andrewsu'},
                {title:"linkedin", href:'https://www.linkedin.com/in/andrewsu/'},
              ]
            },
            {
              name:'Cyrus',
              lastname:'Afrasiabi',
              title:'Research Programmer IV',
              work_logo:'scripps.svg',
              work_website:'https://www.scripps.edu/',
              bio:'I came to the Su/Wu Lab from UC Berkeley where I worked in a phylogenomics lab primarily doing bioinformatics application development.  Before this I did work on the analysis of medical images, the analysis of animal vocalizations, and digital system design.  Besides SmartAPI project, I am also currently working on the BioThings API project: http://BioThings.io/',
              education:['2011 M. Eng. in Biomedical Engineering from Cornell University','2003 BS in Electrical and Computer Engineering from Cornell University'],
              image:'http://sulab.org/wp-content/uploads/2018/03/cyrus2.jpg',
              personal_site:'#',
              links:[
                {title:"twitter", href:'#'},
                {title:"github", href:'https://github.com/cyrus0824'},
                {title:"linkedin", href:'https://www.linkedin.com/in/cyrus-afrasiabi-b623604a'},
              ]
            },
            {
              name:'Marco',
              lastname:'Cano',
              title:'Research Programmer III',
              work_logo:'scripps.svg',
              work_website:'https://www.scripps.edu/',
              bio:"I'm a full-stack web developer with a background in Web/Graphic Design and Multimedia Animation. Love to build professional modern websites using the latest technologies and the best possible UI/UX design. Currently working for the Su/Wu Lab at Scripps Research.  Current projects include: http://BioThings.io and http://SmartAPI.info",
              education:['3D Animation and Multimedia Design -Palomar College','Full Stack Web Development – UCSD'],
              image:'https://avatars1.githubusercontent.com/u/23092057?s=460&v=4',
              personal_site:'http://www.marcodarko.com/',
              links:[
                {title:"twitter", href:''},
                {title:"github", href:'https://github.com/marcodarko'},
                {title:"linkedin", href:'https://www.linkedin.com/in/marco-alvarado-cano'},
              ]
            },
            {
              name:'Kevin',
              lastname:'Xin',
              title:'Staff Scientist',
              work_logo:'scripps.svg',
              work_website:'https://www.scripps.edu/',
              bio:"I'm currently working on projects that apply data science methodology and cloud computing technologies to facilitate biomedical discovery, through the large-scale biological data integration.  Current projects include: http://BioThings.io/Explorer and http://SmartAPI.info",
              education:['The Scripps Research Institute (second year graduate student)','Undergraduate: Fudan University'],
              image:'https://scholar.google.com/citations?view_op=medium_photo&user=zthpKooAAAAJ&citpid=1',
              personal_site:'https://scholar.google.com/citations?user=zthpKooAAAAJ&hl=en',
              links:[
                {title:"twitter", href:'#'},
                {title:"github", href:'https://github.com/kevinxin90'},
                {title:"linkedin", href:'https://www.linkedin.com/in/jiwen-xin-7a207b29/'},
              ]
            },
            {
               name:'Xinghua(Jerry)',
               lastname:'Zhou',
               title:'Research Programmer',
               work_logo:'scripps.svg',
               work_website:'https://www.scripps.edu/',
               bio:'Jerry is a research programmer in the Department of Integrative Structure and Computational Biology at Scripps Research.',
               education:['B.S., Computer Engineering, University of California San Diego'],
               image:'https://wulab.io/static/img/jerry_zhou.jpg',
               personal_site:'#',
               links:[
                   {title:"flickr", href: 'https://www.flickr.com/people/namespacestd/'},
                   {title:"github", href:'https://github.com/namespacestd0'},
                   {title:"linkedin", href:'https://www.linkedin.com/in/jerry-zhou-b48b04b1/'},
               ]
            },
            {
              name:'Michel',
              lastname:'Dumontier',
              title:'Professor',
              work_logo:'mu.png',
              work_website:'https://www.maastrichtuniversity.nl/',
              bio:"Dr. Michel Dumontier is a Distinguished Professor of Data Science at Maastricht University. His research focuses on the development of computational methods for scalable integration and reproducible analysis of FAIR (Findable, Accessible, Interoperable and Reusable) data across scales - from molecules, tissues, organs, individuals, populations to the environment. His group combines semantic web technologies with effective indexing, machine learning and network analysis for drug discovery and personalized medicine. ",
              education:['2004 PhD, Biochemistry (Bioinformatics) from University of Toronto','1998 Bachelor of Sciencee, Biochemistry from University of Manitoba'],
              image:'https://avatars3.githubusercontent.com/u/993852?s=460&v=4',
              personal_site:'http://dumontierlab.com/#',
              links:[
                {title:"twitter", href:'https://twitter.com/micheldumontier'},
                {title:"github", href:'https://github.com/micheldumontier'},
                {title:"linkedin", href:'https://www.linkedin.com/in/dumontier'},
              ]
            },
            {
              name:'Amrapali',
              lastname:'Zaveri',
              title:'Postdoctoral Researcher',
              work_logo:'mu.png',
              work_website:'https://www.maastrichtuniversity.nl/',
              bio:`I am from Pune, India where I studied Bachelors of Science and Masters in Bioinformatics. This was where my interests in science, biology and computers were born and nurtured. My training in bioinformatics took me to Singapore to work as a Senior Research Assistant at the National Neuroscience Institute. This is where I got introduced to ontologies, Semantic Web and Linked Data that could be used to solve biological problems. That brought me to Germany where I pursued my PhD in Computer Science in the University of Leipzig. My focus was on consumption of Linked Data for healthcare, educational and economic research leveraging data quality. Then I got the opportunity to pursue my research ideas further as a postdoctoral researcher at Stanford University in the Biomedical Informatics department. This is where I brought the worlds of Semantic Web and Biology together. After spending just a little over a year at Stanford, my professor got an opportunity to start a Data Science Institute at the University of Maastricht, Netherlands. I followed too and have been here since January 2017.`,
              education:['2015 PhD Philosophy from Leipzig University','2007 M.Sc, Bioinformatics from Sikkim Manipal University of Health, Medical and Technological Sciences','2005 B.Sc, Zoology from Savitribai Phule Pune University'],
              image:'https://avatars3.githubusercontent.com/u/713103?s=460&v=4',
              personal_site:'https://amrapalizaveri.com/',
              links:[
                {title:"twitter", href:'https://twitter.com/amrapaliz?lang=en'},
                {title:"github", href:'https://github.com/amrapalijz'},
                {title:"linkedin", href:'https://www.linkedin.com/in/amrapalizaveri/'},
              ]
            },
            {
              name: 'Alexander',
              lastname: 'Malic',
              title: 'Architect',
              work_logo: 'mu.png',
              work_website: 'https://www.maastrichtuniversity.nl/',
              bio: '',
              education: ['Engineering degree in Electronics and Telecommunication Technologies', 'MBA specialization in international program, project, and process management at WU Executive Academy'],
              image: 'https://www.maastrichtuniversity.nl/sites/default/files/styles/page_photo/public/profile/alexander.malic/alexander.malic_Picture%20People%20Maastricht%20%282%20of%203%29_medium.jpg?itok=aMM7lVnN&timestamp=1534186501',
              personal_site:'#',
              links: [
                {title: "github", href: 'https://github.com/amalic'},
                {title: "linkedin", href: 'https://www.linkedin.com/in/alexandermalic'}
              ]
            },
            {
              name:'Shima',
              lastname:'Dastgheib',
              title:'Data Scientist',
              work_logo:'http://numedii.com/wp-content/uploads/2017/06/NuMedii-Logo-web.png',
              work_website:'https://www.maastrichtuniversity.nl/',
              bio:`Data scientist at Numedii.`,
              education:['2017 Postdoctoral Reserach Scholar from Stanford University School of Medicine','2014 PhD Computer Science from The University of Georgia','2008 Masters in Information Technology from Shiraz University','2004 B.S. Electrical Engineering from Shiraz University'],
              image:'https://i1.rgstatic.net/ii/profile.image/544408740339712-1506808566542_Q512/Shima_Dastgheib2.jpg',
              personal_site:'https://scholar.google.com/citations?user=i5ElwboAAAAJ&hl=en',
              links:[
                {title:"twitter", href:'https://twitter.com/shimadastgheib?lang=en'},
                {title:"github", href:'https://github.com/BinaryStars'},
                {title:"linkedin", href:'https://www.linkedin.com/in/shima-dastgheib-91a51027/'},
              ]
            },
            {
              name:'Trish',
              lastname:'Whetzel',
              title:'Bioinformatician',
              work_logo:'embl-01.png',
              work_website:'https://www.ebi.ac.uk/',
              bio:`Web and Android developer. Background in bioinformatics and ontology development/management. Currently Bioinformatician at European Bioinformatics Institute | EMBL-EBI`,
              education:['2016 Full Stack Nanodegree in Python Web Developement and Databases from Udacity','2000 PhD in Immunology and Microbiology from University of Delaware'],
              image:'https://avatars0.githubusercontent.com/u/2167174?s=460&v=4',
              personal_site:'https://scholar.google.com/citations?user=2b1-ZLAAAAAJ&hl=en',
              links:[
                {title:"twitter", href:'https://twitter.com/trishwhetzel?lang=en'},
                {title:"github", href:'https://github.com/twhetzel'},
                {title:"linkedin", href:'https://www.linkedin.com/in/trishwhetzel/'},
              ]
            },
          ]
        }
      },
      methods: {
        popUpDetails: function(index){
          this.showModal = true
          this.selectedPerson = this.contributors[index];
        },
        compiledMarkdown: function (mdtext) {
            return marked(mdtext)
        },
        confirm() {
          this.showModal = false
        },
        cancel() {
          this.showModal = false
        }
      },
}
</script>

<style lang="css" scoped>
.social-icon{
  margin-right: 5px;
}
::v-deep .modal-container {
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
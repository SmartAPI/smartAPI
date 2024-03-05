export const faq = {
  state: () => ({
    faq: [
      {
        sectionName: 'SmartAPI',
        questions: [
          {
            anchor: 'smartapi',
            question: 'What is SmartAPI?',
            answer: `The SmartAPI project aims to maximize the FAIRness (Findability, Accessibility, Interoperability, and Reusability) of web-based Application Programming Interfaces (APIs). Rich metadata is essential to properly describe your API so that it becomes discoverable, connected, and reusable. We have developed a <a href="http://openapis.org" target="_blank" rel="noreferrer"></a>openAPI-based <a href="https://github.com/SmartAPI/smartAPI-Specification/blob/OpenAPI.next/versions/3.0.0.md" target="_blank" rel="noreferrer"> specification</a> for defining the key API metadata elements and value sets. SmartAPI's leverage the <a href="https://www.openapis.org/" target="_blank" rel="noreferrer">Open API specification v3 </a> and <a href="http://json-ld.org" target="_blank" rel="noreferrer">JSON-LD</a> for providing semantically annotated JSON content that can be treated as <a href="http://linkeddata.org/" target="_blank" rel="noreferrer">Linked Data</a>.`
          },
          {
            anchor: 'citation',
            question: 'How do I cite SmartAPI?',
            answer: `<p>
                    To reference SmartAPI in your work, please cite this <a target='_blank' href="https://doi.org/10.1007/978-3-319-58451-5_11">publication</a> and also the "https://smart-api.info/" URL:
                    </p>
                    <h5>Primary citation:</h5>
                    <p>Zaveri, A., Dastgheib, S., Whetzel, T., Verborgh, R., Avillach, P., Korodi, G., Terryn, R., Jagodnik, K., Assis, P., Wu, C., Dumontier, M.: smartAPI: Towards a More Intelligent Network of Web APIs. In: Blomqvist, E., Maynard, D., Gangemi, A., Hoekstra, R., Hitzler, P., and Hartig, O. (eds.) Proceedings of the 14th ESWC. pp. 154–169. Springer (2017).
                    </p>
                    <h5>Other Citations:</h5>
                    <p>
                    Shima Dastgheib, Trish Whetzel, Amrapali Zaveri, Cyrus Afrasiabi, Pedro Assis, Paul Avillach, Kathleen M. Jagodnik, Gabor Korodi, Marcin Pilarczyk, Jeff de Pons, Stephan C. Schürer, Raymond Terryn, Ruben Verborgh, Chunlei Wu, Michel Dumontier:
      The SmartAPI Ecosystem for Making Web APIs FAIR. International Semantic Web Conference (Posters, Demos & Industry Tracks) 2017
                    </p>`
          },
          {
            anchor: 'guide',
            question: 'Is there a guide to help me get started',
            answer: `If you are new to SmartAPI you can use our <a href="/guide">guide</a> to help you contribute for the first time. The guide features examples, and easy step-by-step instructions on how to get started.`
          },
          {
            anchor: 'dashboard',
            question: 'What is dashboard and how do I access it?',
            answer: `Your user <a href="/dashboard">dashboard</a> is place where you can easily manage and quickly access your registered APIs. To access it log in and click on your user image on the menu bar.`
          }
        ]
      },
      {
        sectionName: 'API Management',
        questions: [
          {
            anchor: 'slug',
            question: 'What is a slug and how do I register a custom slug for my API?',
            answer: `<p>
                            A slug is a part of a URL which identifies a particular page on a website in a form readable by users. By default SmartAPI uses an API's ID as the slug to serve an API's documentation. For example you can view your API's documentation by visiting <b>&lt;id&gt;</b>.smartapi.info. However you can register for a more readable slug so you can share your documentation under a namespace that represents your API.
                            </p>
                            <p>
                            To register a custom slug you must successfully add a new API to the <a href="/registry">registry</a>, log in to your <a href="/dashboard">dashboard</a> to see a list of your registered APIs. Click on the name of any API and go to the <b>Settings</b> tab.
                            Use the Custom Slug Registration Wizard and get a custom URL for your API's documentation. E.g. <b>&lt;slug&gt;</b>.smart-api.info
                            </p>`
          },
          {
            anchor: 'metadata',
            question: 'How often is API metadata updated automatically?',
            answer: `Our system performs daily checks for all items on our registry. If your metadata URL works and a change is found we will update the registered metadata automatically, but you can also update it manually via your <a href="/dashboard">dashboard</a> anytime.`
          },
          {
            anchor: 'github-metadata',
            question:
              'I edited my metadata on Github, but the raw Github URL does not reflect the changes. Why is that?',
            answer: `Github appears to take a little time to update it's raw links due to cache controls. Wait a little while and your changes will appear eventually. GitHub serves "raw" pages with Cache-Control: max-age=300. That's specified in seconds, meaning the pages are intended to be cached for 5 minutes.`
          },
          {
            anchor: 'refresh',
            question: 'How do I manually refresh my API metadata if I just made a change?',
            answer: `If you want to update your metadata to its latest version (must be valid) quickly manual refreshes can be triggered from your <a href="/dashboard">user dashboard</a>. Just click the green refresh button and our system will do the rest.`
          },
          {
            anchor: 'api-monitor',
            question:
              "How can I construct my API specification so SmartAPI's API monitor can track my API status",
            answer: `<p>
                    There is an API monitor running in the backend of SmartAPI to track daily the status of APIs registered in the SmartAPI registry. To make your API “trackable”, here are some guidelines to follow:
                    </p>
                    <ol>
                    <li>
                        If your API endpoints have required parameter(s), you must provide an example value for each required parameter. Our API monitor will look for the value of the example field under “Parameter” object or “Request Body” object to construct a valid API call. Instructions regarding how to create an example for “Parameter” object or “Request Body” object could be found <a target="_blank" href=' https://github.com/SmartAPI/smartAPI-Specification/blob/OpenAPI.next/versions/3.0.0.md#parameterObject and https://github.com/SmartAPI/smartAPI-Specification/blob/OpenAPI.next/versions/3.0.0.md#requestBodyObject'>here</a>.
                        <br />
                        Here is an example of a “trackable” API with example values provided: <a href='https://smart-api.info/api/metadata/mygene' target="_blank">https://smart-api.info/api/metadata/mygene</a> (search for <code>"example":</code>).
                    </li>
                    <li>
                        If your API endpoints don’t have required parameter(s), you’re all set. No example is needed. We will automatically construct an API call with the paths and server information provided.
                    </li>
                    </ol>`
          },
          {
            anchor: 'api-status',
            question: 'What does my API status mean?',
            answer: `<p>
                                Your API status can indicate one of the following things:
                            </p>
                            <table>
                                <tbody>
                                <tr>
                                    <td class='green-text'>
                                    <b>PASS</b>
                                    </td>
                                    <td class="blue-grey-text">
                                    Your OpenAPI V3 API endpoints provide examples and all return code 200.
                                    </td>
                                </tr>
                                <tr>
                                    <td class='red-text'>
                                    <b>FAIL</b>
                                    </td>
                                    <td class="blue-grey-text">
                                    Your OpenAPI V3 API endpoints provide examples but return code other than 200.
                                    </td>
                                </tr>
                                <tr>
                                    <td class='orange-text'>
                                    <b>UNKNOWN</b>
                                    </td>
                                    <td class="blue-grey-text">
                                    None of your OpenAPI V3 API endpoints provide examples and cannot be tested. <a href='/faq#api-monitor' >Learn more about how to to enable API status check </a>.
                                    </td>
                                </tr>
                                <tr>
                                    <td class='blue-text'>
                                    <b>INCOMPATIBLE</b>
                                    </td>
                                    <td class="blue-grey-text">
                                    Your API's specification does not match OpenAPI V3 specification and will not be tested. Use our guide to learn how to upgrade your metadata to OpenAPI V3 <a href="/guide" target="_blank">here</a>.
                                    </td>
                                </tr>
                                </tbody>
                            </table>`
          },
          {
            anchor: 'source-status',
            question: 'What does my Source URL status mean?',
            answer: `<p>
                                Your API's Source URL status can indicate one of the following things:
                            </p>
                            <table>
                                <thead>
                                <tr>
                                    <td colspan="2" class='grey-text center'>
                                    <b>Source URL Metadata Status</b>
                                    </td>
                                </tr>
                                </thead>
                                <tbody>
                                <tr>
                                    <td class='green-text center'>
                                    <b>OK</b>
                                    </td>
                                    <td class="blue-grey-text">
                                    Source URL is working and returns valid metadata.
                                    </td>
                                </tr>
                                <tr>
                                    <td class='orange-text center'>
                                    <b>NOT FOUND</b>
                                    </td>
                                    <td class="blue-grey-text">
                                    Source URL returns not found.
                                    </td>
                                </tr>
                                <tr>
                                    <td class='red-text center'>
                                    <b>INVALID</b>
                                    </td>
                                    <td class="blue-grey-text">
                                    Source URL works but contains invalid metadata.
                                    </td>
                                </tr>
                                <tr>
                                    <td class='purple-text center'>
                                    <b>BROKEN</b>
                                    </td>
                                    <td class="blue-grey-text">
                                    Source URL is broken.
                                    </td>
                                </tr>
                                <tr>
                                    <td colspan='2' class='blue-grey-text'>
                                    <p>
                                        <b>What does this mean? </b> API metadata cannot be synchronized with its source URL if the status is not <b class='green-text'>OK</b>. 
                                    </p>
                                    <p>
                                        <b>How to fix:</b> From your <a href="/dashboard">User Dashboard</a> &gt; <b class='indigo-text'>Validate Only</b> to see issues then <b class='green-text'>Refresh</b> once all issues have been resolved.
                                    </p>
                                    </td>
                                </tr>
                                </tbody>
                            </table>`
          },
          {
            anchor: 'transfer',
            question: 'How can I transfer/claim the ownership of an API entry?',
            answer: `<p>
                    A transfer of ownership requests can be initiated by filling out a form. You will need the current <b>Responsible Developer</b>'s GitHub handle (located in the 'Details' section on the <a href="/registry">registry</a>), new recipient's GitHub handle, reason and any other relevant information to this transfer.
                    </p>
                    <p>
                        If you would like to transfer ownership to someone else or claim ownership of an API please click <a target="_blank" rel="noreferrer" href="https://github.com/SmartAPI/smartAPI/issues/new?template=transfer.md">here</a>.
                    </p>`
          },
          {
            anchor: 'swagger',
            question: 'My API uses Swagger V2 specification, does SmartAPI support it?',
            answer: `<p>
                    You can submit Swagger V2 APIs and they will appear on our registry, however they will not experience full functionality on SmartAPI and BioThings Explorer.
                    </p>
                    <p>
                    If you use our <a href="/guide">guide</a> you can upgrade your Swagger V2 data to <a target="_blank" rel="noreferrer" rel="noreferrer" href="https://github.com/SmartAPI/smartAPI-Specification/blob/OpenAPI.next/versions/3.0.0.md">OpenAPI V3 Specification <i class="fa fa-external-link-square" aria-hidden="true"></i></a>
                    </p>`
          },
          {
            anchor: 'delete',
            question: 'How do I delete an API?',
            answer: `To delete an API you must be the registered owner of that API. Log in to access the user <a href="/dashboard">dashboard</a> and see a list of the APIs you have registered. Click on the delete button of the API you want to delete and follow the instructions to delete.`
          }
        ]
      },
      {
        sectionName: 'Other',
        questions: [
          {
            anchor: 'branding',
            question: "Can I use SmartAPI's branding on my project?",
            answer: `For most cases yes as long as proper credit is given to our services. For more information please read our guidelines on our <a href="/branding">branding</a> page.`
          },
          {
            anchor: 'contact',
            question: 'I need additional help, how do I contact SmartAPI?',
            answer: `If you need to contact us you can <a target="_blank" rel="noreferrer" href="mailto:api-interoperability@googlegroups.com">email us</a> or if you spot a bug or have any suggestions you may open an <a target="_blank" rel="noreferrer" href="https://github.com/SmartAPI/smartAPI/issues">issue</a> on GitHub.`
          }
        ]
      }
    ]
  }),
  strict: true,
  getters: {
    faq: (state) => {
      return state.faq;
    }
  }
};
